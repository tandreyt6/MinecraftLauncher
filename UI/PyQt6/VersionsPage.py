import json
import os

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QPixmap, QMouseEvent
from PyQt6.QtCore import Qt

from functions import memory


class VersionItem(QWidget):
    def __init__(self, image_path: str, name: str, index: int, params: dict, data: dict, parent=None):
        super().__init__(parent)
        self.main = None

        self.index = index
        self.params = params
        self.data = data

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.image_label = QLabel()
        self.image_label.setFixedSize(100, 100)
        self.image_label.setStyleSheet("border-radius: 10px; border: 2px solid black;")

        image_path = image_path if image_path is not None else self.params.get("minecraftIcon")

        pixmap = QPixmap(image_path).scaled(self.image_label.size(),
                                            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                            Qt.TransformationMode.SmoothTransformation)
        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(True)

        self.text_label = QLabel(name)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.image_label)
        layout.addWidget(self.text_label)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_click()

    def on_click(self):
        self.main(self)


class VersionsPage(QWidget):
    def __init__(self, parent=None, css="", settings={}, availdCores={}):
        super().__init__(parent)
        self.coreTypes = ["[no select]", "Vanilla", "Forge", "Fabric", "Quilt"]
        self.setStyleSheet(css)

        self.settings = settings
        self.versions = self.settings.get("versions", [])
        self.availdCores = availdCores

        self.selectedItem = None
        self.centralPanel = None
        self.centralWidget = None
        self.flowLayout = None
        self.topPanel = None
        self.topPanelLayout = None
        self.settingBtn = None
        self.openFolderBtn = None
        self.modsBtn = None
        self.createBtn = None
        self.playBtn = None
        self.rightPanel = None
        self.titleLabel = None
        self.rightPanelLayout = None
        self.spliter = None

        self.mainLayout = QVBoxLayout(self)
        self.initUI()

    def initUI(self):
        self.centralPanel = QScrollArea()
        self.centralPanel.setWidgetResizable(True)

        self.centralWidget = QWidget()
        self.centralWidget.setObjectName("versionsWidget")
        self.flowLayout = QFlowLayout(self.centralWidget)
        self.centralPanel.setWidget(self.centralWidget)

        self.topPanel = QFrame()
        self.topPanel.setFixedHeight(50)
        self.topPanelLayout = QGridLayout(self.topPanel)

        self.settingBtn = QPushButton("Settings")
        self.settingBtn.setIcon(QIcon(self.settings.get("settingsIcon")))
        # self.topPanelLayout.addWidget(self.settingBtn, 0, 0)
        self.openFolderBtn = QPushButton(memory.get("translate", {}).get("openBuildFolder", "Open build folder"))
        self.openFolderBtn.setIcon(QIcon(self.settings.get("folderIcon")))
        # self.topPanelLayout.addWidget(self.openFolderBtn, 0, 0)
        self.openFolderBtnVersions = QPushButton(memory.get("translate", {}).get("openFolder", "Open folder"))
        self.openFolderBtnVersions.setIcon(QIcon(self.settings.get("folderIcon")))
        self.topPanelLayout.addWidget(self.openFolderBtnVersions, 0, 0)
        self.modsBtn = QPushButton(memory.get("translate", {}).get("Mods", "Mods"))
        self.modsBtn.setIcon(QIcon(self.settings.get("modsIcon")))
        # self.topPanelLayout.addWidget(self.modsBtn, 0, 1)
        self.createBtn = QPushButton(memory.get("translate", {}).get("createBuild", "Create build"))
        self.createBtn.setIcon(QIcon(self.settings.get("createIcon")))
        self.topPanelLayout.addWidget(self.createBtn, 0, 1)
        self.coresBtn = QPushButton(memory.get("translate", {}).get("Cores", "Core`s"))
        self.coresBtn.setIcon(QIcon(self.settings.get("settingsIcon")))
        self.topPanelLayout.addWidget(self.coresBtn, 0, 3)
        self.refresh = QPushButton(memory.get("translate", {}).get("Refresh", "Refresh"))
        self.refresh.setIcon(QIcon(self.settings.get("reloadIcon")))
        self.topPanelLayout.addWidget(self.refresh, 0, 4)
        self.createShortcutBtn = QPushButton(memory.get("translate", {}).get("createShortcut", "Create Shortcut"))
        self.createShortcutBtn.setIcon(QIcon(self.settings.get("createIcon")))
        self.topPanelLayout.addWidget(self.createShortcutBtn, 0, 2)
        self.playBtn = QPushButton(memory.get("translate", {}).get("Play", "Play"))
        self.playBtn.setIcon(QIcon(self.settings.get("playIcon")))
        self.delButton = QPushButton(memory.get("translate", {}).get("Delete", "Delete"))
        self.delButton.setIcon(QIcon(self.settings.get("deleteIcon")))

        self.rightPanel = QFrame()
        self.rightPanel.setFixedWidth(300)
        self.titleLabel = QLabel()
        self.pathTitle = QLabel()
        fontTitle = QFont()
        fontTitle.setPixelSize(21)
        self.titleLabel.setFont(fontTitle)
        self.coreType = QComboBox()
        self.coreType.addItems(self.coreTypes)
        self.coreType.setCurrentIndex(0)
        self.coreType.currentTextChanged.connect(lambda: self.changeDataBuild())
        self.coreVersionCombo = QComboBox()
        self.coreVersionCombo.currentTextChanged.connect(lambda: self.changeDataBuild())
        self.minecraftVersionsCombo = QComboBox()
        self.minecraftVersionsCombo.currentTextChanged.connect(lambda: self.changeDataBuild())
        self.rightPanelLayout = QFormLayout(self.rightPanel)
        self.rightPanelLayout.addRow(self.titleLabel)
        self.rightPanelLayout.addRow(self.pathTitle)
        self.rightPanelLayout.addRow(QLabel(memory.get("translate", {}).get("coreType", "Core type")), self.coreType)
        self.rightPanelLayout.addRow(QLabel(memory.get("translate", {}).get("coreVersion", "Core version")), self.coreVersionCombo)
        self.rightPanelLayout.addRow(QLabel(memory.get("translate", {}).get("mineVersion", "Minecraft version")), self.minecraftVersionsCombo)
        self.rightPanelLayout.addRow(self.modsBtn)
        self.rightPanelLayout.addRow(self.openFolderBtn)
        self.rightPanelLayout.addRow(self.playBtn)
        stretch = QLabel()
        stretch.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.rightPanelLayout.addRow(stretch)
        self.rightPanelLayout.addRow(self.delButton)

        self.spliter = QSplitter(Qt.Orientation.Horizontal)
        self.spliter.addWidget(self.centralPanel)
        self.spliter.addWidget(self.rightPanel)

        self.mainLayout.addWidget(self.topPanel)
        self.mainLayout.addWidget(self.spliter)
        self.setLayout(self.mainLayout)

        self.display_info(None)

    def changeDataBuild(self):
        type = self.coreType.currentText()
        CVer = self.coreVersionCombo.currentText()
        MVer = self.minecraftVersionsCombo.currentText()
        if self.selectedItem:
            self.selectedItem.data["CoreType"] = type
            self.selectedItem.data["CoreVersion"] = CVer
            self.selectedItem.data["minecraftVersion"] = MVer
            oldp = self.selectedItem.data.get("path")
            with open(oldp+"/BuildSettings.json", "w", encoding="utf-8") as e:
                data = {}
                data["type"] = "ForMinecraftLauncher"
                data["title"] = self.selectedItem.data["title"]
                data["CoreType"] = type
                data["CoreVersion"] = CVer
                data["minecraftVersion"] = MVer
                json.dump(data, e, indent=4)
        self.display_info(self.selectedItem)

    def coreVersionFromCoreType(self, type: str):
        s = []
        for core in self.availdCores.get(type, []): s.append(core["coreVersion"])
        return s

    def mineVersionUpdate(self, type: str, version: str | None):
        s = []
        type = type.lower()
        if version:
            for core in self.availdCores.get(type, []):
                if core["coreVersion"] == version:
                    s.append(core["minecraftVersion"])
            return s
        for core in self.availdCores.get(type, []): s.append(core["minecraftVersion"])
        return s

    def display_info(self, item: VersionItem):
        self.coreVersionCombo.blockSignals(True)
        self.minecraftVersionsCombo.blockSignals(True)
        self.coreType.blockSignals(True)
        self.coreVersionCombo.clear()
        self.minecraftVersionsCombo.clear()
        self.coreVersionCombo.setDisabled(True)
        self.minecraftVersionsCombo.setDisabled(True)
        self.coreType.setDisabled(True)
        self.modsBtn.setText(memory.get("translate", {}).get("Mods", "Mods"))
        self.coreVersionCombo.addItem("[no select]")
        self.minecraftVersionsCombo.addItem("[no select]")
        self.titleLabel.setText("[no select]")
        self.pathTitle.setText("[no select]")
        self.pathTitle.setToolTip("")
        if item:
            item.image_label.setStyleSheet("border-radius: 10px; border: 2px solid #00BFFF;")
        if self.selectedItem:
            self.selectedItem.image_label.setStyleSheet("border-radius: 10px; border: 2px solid black;")
        self.selectedItem = item
        if item is None: return 
        self.titleLabel.setText(str(item.data.get("title", "no title")))
        self.pathTitle.setText(str(item.data.get("path", "")))
        self.pathTitle.setToolTip(str(item.data.get("path", "")))
        self.coreType.setDisabled(False)
        if not item.data.get("CoreType", "None") in self.coreTypes:
            self.coreType.setCurrentIndex(0)
        else:
            self.coreType.setCurrentIndex(self.coreTypes.index(item.data.get("CoreType", "None")))
            if item.data.get("CoreType", "None").lower() != "vanilla":
                self.coreVersionCombo.setDisabled(False)
                cores = self.coreVersionFromCoreType(item.data.get("CoreType", "None").lower())
                self.coreVersionCombo.addItems(cores)
                if item.data.get("CoreVersion", "None") in cores:
                    self.coreVersionCombo.setCurrentIndex(cores.index(item.data.get("CoreVersion", "None")) + 1)
                else:
                    self.coreVersionCombo.setCurrentIndex(0)

                vers = self.mineVersionUpdate(item.data.get("CoreType", "None"), item.data.get("CoreVersion", "None"))
            else:
                vers = self.mineVersionUpdate(item.data.get("CoreType", "None"), None)
            self.minecraftVersionsCombo.setDisabled(False)
            self.minecraftVersionsCombo.addItems(vers)
            if item.data.get("minecraftVersion", "None") in vers:
                self.minecraftVersionsCombo.setCurrentIndex(vers.index(item.data.get("minecraftVersion", "None")) + 1)
        modsCount = len(self.find_mods(item.data.get("path", "./")+"/mods"))
        self.modsBtn.setText(memory.get("translate", {}).get("Mods", "Mods")+" - "+str(modsCount))
        self.coreVersionCombo.blockSignals(False)
        self.minecraftVersionsCombo.blockSignals(False)
        self.coreType.blockSignals(False)

    def find_mods(self, path):
        if not os.path.exists(path):
            return []

        mods = []
        for file in os.listdir(path):
            if file.endswith(".jar") or file.endswith(".jar.disabled"):
                mods.append(os.path.join(path, file))
        return mods

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clearLayout(child.layout())

    def loadVersions(self):
        self.clearLayout(self.flowLayout)
        for i in self.versions:
            i["func"] = self.display_info
            self.addWidget(i)

    def addWidget(self, data: dict):
        version_item = VersionItem(
            data.get("icon"),
            data.get("title"), data.get("index", -1),
            self.settings, data)
        version_item.main = data.get("func")
        self.flowLayout.addWidget(version_item)
        return version_item


class QFlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self.itemList = []

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size

    def doLayout(self, rect, testOnly):
        x, y, lineHeight = rect.x(), rect.y(), 0

        for item in self.itemList:
            widget = item.widget()
            spaceX = self.spacing() + widget.style().layoutSpacing(
                QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton, Qt.Orientation.Horizontal
            )
            spaceY = self.spacing() + widget.style().layoutSpacing(
                QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton, Qt.Orientation.Vertical
            )
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y += lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()


if __name__ == "__main__":
    app = QApplication([])
    app.setStyle("Fusion")
    window = VersionsPage()
    window.resize(700, 400)
    window.show()
    app.exec()
