import os
import shutil
import threading

from PIL.ImageQt import ImageQt
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PIL import Image
from io import BytesIO
import sys
import zipfile
import json
import toml

from UI.PyQt6 import QTCSS
from UI.PyQt6.buttons import AnimatedToggle
from functions import memory


# import faulthandler
#
#
# faulthandler.enable()

class HighlightDelegate(QStyledItemDelegate):
    """Delegate for rendering matches in bold."""

    def __init__(self, pattern, parent=None):
        super().__init__(parent)
        self.pattern = pattern.lower()  # Current search pattern

    def setPattern(self, pattern):
        """Set the search pattern and update the view."""
        self.pattern = pattern.lower()

    def paint(self, painter, option, index):
        """Override paint method for custom rendering."""
        text = index.data()
        if not self.pattern:
            super().paint(painter, option, index)
            return

        # Highlight matches
        highlighted_text = ""
        last_index = 0
        for i in range(len(text) - len(self.pattern) + 1):
            if text[i:i + len(self.pattern)].lower() == self.pattern:
                highlighted_text += text[last_index:i] + f"<b>{text[i:i + len(self.pattern)]}</b>"
                last_index = i + len(self.pattern)
        highlighted_text += text[last_index:]

        # Use QTextDocument to render HTML
        doc = QTextDocument()
        doc.setHtml(highlighted_text)
        doc.setTextWidth(option.rect.width())

        # Render the text
        painter.save()
        painter.translate(option.rect.topLeft())
        doc.drawContents(painter)
        painter.restore()

    def sizeHint(self, option, index):
        """Return the recommended size for an item."""
        doc = QTextDocument()
        doc.setHtml(index.data())
        doc.setTextWidth(option.rect.width())
        return doc.size().toSize()


class SearchableComboBox(QWidget):
    def __init__(self, items, parent=None):
        super().__init__(parent)

        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.setReadOnly(True)

        self.list_widget = QListWidget(self)
        self.list_widget.hide()
        self.list_widget.setFrameShape(QFrame.Shape.Box)

        self.delegate = HighlightDelegate("")
        self.list_widget.setItemDelegate(self.delegate)

        self.items = items
        self.update_list(items)

        layout = QVBoxLayout(self)
        layout.addWidget(self.search_bar)
        layout.addWidget(self.list_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        # Connect signals
        self.search_bar.textChanged.connect(self.filter_list)
        self.search_bar.mousePressEvent = self.toggle_list
        self.list_widget.itemClicked.connect(self.select_item)

    def update_list(self, items, search_text=""):
        """Update the list with search filter."""
        self.list_widget.clear()
        self.delegate.setPattern(search_text)
        for item_text in items:
            list_item = QListWidgetItem(item_text)
            self.list_widget.addItem(list_item)
        self.list_widget.setVisible(bool(items))

    def filter_list(self, text):
        """Filter list based on search bar input."""
        filtered_items = [item for item in self.items if text.lower() in item.lower()]
        self.update_list(filtered_items, text)

    def toggle_list(self, event):
        """Toggle list visibility on search bar click."""
        if self.list_widget.isVisible():
            self.list_widget.hide()
        else:
            self.search_bar.setReadOnly(False)
            self.list_widget.setFixedWidth(self.search_bar.width())
            self.list_widget.show()
            self.list_widget.setFocus()

    def select_item(self, item):
        """Handle item selection from list."""
        self.search_bar.setText(item.text())
        self.list_widget.hide()
        self.search_bar.setReadOnly(True)

    def focusOutEvent(self, event):
        """Close the dropdown when focus is lost."""
        if not self.list_widget.hasFocus():
            self.list_widget.hide()
        super().focusOutEvent(event)


class RoundedModalWidget(QWidget):
    def __init__(self, parent=None, xRadius=50, yRadius=50):
        super().__init__(parent)
        self.xRadius = xRadius
        self.yRadius = yRadius
        self.contentWidth = 300
        self.contentHeight = 300
        self.bgContentWidth = 300
        self.bgContentHeight = 300
        self.setMinimumSize(0, 0)
        # Окно без рамки с прозрачным фоном
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(self.parent().geometry())

        self.setAutoFillBackground(False)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateGeometry)

        self.showBgSquare = True
        self.canClose = False
        self.contentWidget = None

    def closeEvent(self, a0: QCloseEvent):
        if self.canClose:
            return super().closeEvent(a0)
        a0.setAccepted(False)

    def setWidget(self, widget):
        """Устанавливаем виджет, который будет отображаться в центре."""
        if self.contentWidget is not None:
            # Удаляем предыдущий виджет перед добавлением нового
            self.layout().removeWidget(self.contentWidget)
            self.contentWidget.deleteLater()

        self.contentWidget = QWidget()
        self.contentWidget.setLayout(QVBoxLayout())
        self.contentWidget.layout().addWidget(widget)
        layout = self.layout()
        if layout is None:
            layout = QVBoxLayout(self)
        layout.addWidget(self.contentWidget, 0, Qt.AlignmentFlag.AlignCenter)

        self.adjustSize()

    def setContentSize(self, width=100, height=100):
        self.contentWidth = width
        self.contentHeight = height
        self.updateGeometry()

    def setBgContentSize(self, width=100, height=100):
        self.bgContentWidth = width
        self.bgContentHeight = height
        self.updateGeometry()

    def paintEvent(self, event):
        """Рисуем полупрозрачный черный фон и округлое окно."""
        if self.parent() == None or not self.parent().isVisible():
            self.timer.stop()
            self.close()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(0, 0, 0, 155)))
        painter.drawRect(self.rect())

        path = QPainterPath()
        if self.showBgSquare:
            center = self.rect().center()
            width = self.bgContentWidth if isinstance(self.bgContentWidth, int) else int(
                self.parent().geometry().width() / 100 * float(self.bgContentWidth))
            height = self.bgContentHeight if isinstance(self.bgContentHeight, int) else int(
                self.parent().geometry().height() / 100 * float(self.bgContentHeight))

            top_left = QPointF(center.x() - width / 2, center.y() - height / 2)
            rect = QRectF(top_left, QSizeF(width, height))
            path.addRoundedRect(rect, self.xRadius, self.yRadius)
            painter.setBrush(QBrush(self.palette().color(QPalette.ColorRole.Window)))
            painter.drawPath(path)

        super().paintEvent(event)

    def openModalWidget(self):
        """Плавно открываем модальное окно."""
        self.updateGeometry()
        self.show()
        self.fadeIn()

    def closeModalWidget(self):
        """Плавно закрываем модальное окно."""
        self.fadeOut()

    def deleteLater(self) -> None:
        return super().deleteLater()

    def close(self):
        self.timer.stop()
        return super().close()

    def fadeIn(self):
        """Анимация появления."""
        if self.contentWidget:
            self.contentWidget.setEnabled(True)
        self.timer.start(1)
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(200)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.finished.connect(lambda: self.setWindowOpacity(1))
        self.animation.start()

    def fadeOut(self):
        """Анимация исчезновения."""
        if self.contentWidget:
            self.contentWidget.setEnabled(False)
        self.timer.stop()
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(200)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.finished.connect(self.closeModal)
        self.animation.start()

    def closeModal(self):
        """Закрытие модального окна."""
        self.hide()

    def updateGeometry(self):
        """Обновляем геометрию модального окна в зависимости от главного окна."""
        if self.parent() == None or not self.parent().isVisible():
            self.timer.stop()
            self.close()
        self.setGeometry(self.parent().geometry())
        if self.contentWidget:
            self.adjustSize()  # Обновляем размеры, чтобы избежать выхода за пределы окна

    def adjustSize(self):
        """Корректируем размеры внутреннего виджета и модального окна."""
        width = self.contentWidth if isinstance(self.contentWidth, int) else int(
            self.parent().geometry().width() / 100 * float(self.contentWidth))
        height = self.contentHeight if isinstance(self.contentHeight, int) else int(
            self.parent().geometry().height() / 100 * float(self.contentHeight))
        # print(width,height)
        self.contentWidget.setFixedSize(width, height)
        self.update()


class CustomTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, game_version: str, core_version: str, text: str, coreType: str, mineVesible: bool = True):
        super().__init__([f"{text}" + (f" ({game_version})" if mineVesible else "")])
        self.game_version = game_version
        self.core_version = core_version
        self.coreType = coreType


class CoreSelectionDialog(QWidget):
    def __init__(self, versions={}):
        super().__init__()

        self.setStyleSheet(QTCSS.dil_dark)

        self.selectedItem: CustomTreeWidgetItem = None

        self.tabs = QTabWidget()
        self.versions = versions

        self.tab_one = self.create_first_tab()
        self.tab_two = self.create_second_tab()

        self.tabs.addTab(self.tab_one, memory.get("translate", {}).get("NetworkLoading", "Network Loading"))
        self.tabs.addTab(self.tab_two, memory.get("translate", {}).get("Loaded", "Loaded"))

        main_layout = QVBoxLayout(self)
        self.backButton = QPushButton(memory.get("translate", {}).get("Back", "Back"))
        self.top_h = QHBoxLayout()
        self.top_h.addWidget(self.backButton)
        self.top_h.addStretch()
        main_layout.addLayout(self.top_h)
        main_layout.addWidget(self.tabs)


    def create_first_tab(self):
        """Create the first tab with standard loading"""
        tab = QWidget()
        layout = QHBoxLayout()

        self.modalWidget = RoundedModalWidget(self)

        left_panel = QWidget()
        left_layout = QVBoxLayout()

        self.btns = {}

        core_buttons = ["Vanilla", "Fabric", "Forge", "Quilt"]
        for core in core_buttons:
            button = QPushButton(core)
            button.clicked.connect(lambda _, core=core: self.load_versions(core))
            self.btns[core] = button
            left_layout.addWidget(button)

        self.game_version_filter = QLineEdit()
        self.game_version_filter.setPlaceholderText(memory.get("translate", {}).get("GameVersionFilter", "game version"))
        self.game_version_filter.textChanged.connect(self.filter_tree)

        self.core_version_filter = QLineEdit()
        self.core_version_filter.setPlaceholderText(memory.get("translate", {}).get("CoreVersionFilter", "core version"))
        self.core_version_filter.textChanged.connect(self.filter_tree)

        left_layout.addWidget(self.game_version_filter)
        left_layout.addWidget(self.core_version_filter)

        left_layout.addStretch()
        left_panel.setLayout(left_layout)

        self.version_list = QTreeWidget()
        self.version_list.setHeaderHidden(True)
        self.version_list.itemClicked.connect(self.show_version_info)

        self.version_details = QWidget()
        details_layout = QVBoxLayout()
        self.details_label = QLabel(memory.get("translate", {}).get("SelectCoreVersion", "select core"))
        self.install_button = QPushButton(memory.get("translate", {}).get("Install", "Install"))
        self.install_button.clicked.connect(self.InstallClicked)
        self.install_button.setEnabled(False)
        details_layout.addWidget(self.details_label)
        details_layout.addWidget(self.install_button)

        details_layout.addStretch()
        self.version_details.setLayout(details_layout)

        layout.addWidget(left_panel)
        layout.addWidget(self.version_list)
        layout.addWidget(self.version_details)
        tab.setLayout(layout)

        return tab

    def create_second_tab(self):
        """Create the second tab with alternative loading"""
        tab = QWidget()
        layout = QHBoxLayout()

        left_panel = QWidget()
        left_layout = QVBoxLayout()

        self.alt_btns = {}
        self.alt_installed = []

        core_buttons = ["Vanilla", "Fabric", "Forge", "Quilt"]
        for core in core_buttons:
            button = QPushButton(core)
            button.clicked.connect(lambda _, core=core: self.alt_load_versions(core))
            self.alt_btns[core] = button
            left_layout.addWidget(button)

        self.alt_game_version_filter = QLineEdit()
        self.alt_game_version_filter.setPlaceholderText(memory.get("translate", {}).get("GameVersionFilter", "game version"))
        self.alt_game_version_filter.textChanged.connect(self.filter_tree)

        self.alt_core_version_filter = QLineEdit()
        self.alt_core_version_filter.setPlaceholderText(memory.get("translate", {}).get("CoreVersionFilter", "core version"))
        self.alt_core_version_filter.textChanged.connect(self.filter_tree)

        left_layout.addWidget(self.alt_game_version_filter)
        left_layout.addWidget(self.alt_core_version_filter)

        left_layout.addStretch()
        left_panel.setLayout(left_layout)

        self.alt_version_list = QTreeWidget()
        self.alt_version_list.setHeaderHidden(True)
        self.alt_version_list.itemClicked.connect(self.show_version_info)

        layout.addWidget(left_panel)
        layout.addWidget(self.alt_version_list)
        tab.setLayout(layout)

        return tab

    def load_versions(self, core_type):
        """Load versions for the first tab"""
        self.version_list.clear()
        print(core_type)
        if core_type in ["Fabric", "Quilt"]:
            for core_version in self.versions[core_type]:
                item = CustomTreeWidgetItem("Any", core_version, f"{core_type} - {core_version}", core_type, False)
                self.version_list.addTopLevelItem(item)
        elif core_type == "Forge":
            for version_info in self.versions["Forge"]:
                game_version = version_info["minecraft"]
                core_version = f"Forge - {version_info['forge']}"
                item = CustomTreeWidgetItem(game_version, version_info['forge'], core_version, core_type)
                self.version_list.addTopLevelItem(item)
        elif core_type == "Vanilla":
            for game_version in self.versions["Vanilla"]:
                item = CustomTreeWidgetItem(game_version, None, f"Vanilla - {game_version}", core_type, False)
                self.version_list.addTopLevelItem(item)

        self.filter_tree()

    def alt_load_versions(self, core_type):
        """Alternative method for loading versions for the second tab"""
        self.alt_version_list.clear()
        print("Alternative loading", core_type)
        core_type = core_type.lower()
        if core_type in ["fabric", "quilt"]:
            for core_version in reversed(self.alt_installed[core_type]):
                item = CustomTreeWidgetItem("Any", core_version['coreVersion'],
                                            f"{core_type} - {core_version['coreVersion']}", core_type, False)
                self.alt_version_list.addTopLevelItem(item)
        elif core_type == "forge":
            for version_info in reversed(self.alt_installed["forge"]):
                game_version = version_info["minecraftVersion"]
                core_version = f"Forge - {version_info['coreVersion']}"
                item = CustomTreeWidgetItem(game_version, version_info['coreVersion'], core_version, core_type)
                self.alt_version_list.addTopLevelItem(item)
        elif core_type == "vanilla":
            for game_version in reversed(self.alt_installed["vanilla"]):
                item = CustomTreeWidgetItem(game_version['minecraftVersion'], None,
                                            f"Vanilla - {game_version['minecraftVersion']}", core_type, False)
                self.alt_version_list.addTopLevelItem(item)

        self.filter_tree()

    def filter_tree(self):
        """Filter items in both tabs"""
        game_version_text = self.game_version_filter.text().lower()
        core_version_text = self.core_version_filter.text().lower()

        for i in range(self.version_list.topLevelItemCount()):
            item = self.version_list.topLevelItem(i)
            game_version_matches = game_version_text in (
                item.game_version.lower() if item.game_version is not None else "")
            core_version_matches = core_version_text in (
                item.core_version.lower() if item.core_version is not None else "")
            item.setHidden(not (game_version_matches and core_version_matches))

        alt_game_version_text = self.alt_game_version_filter.text().lower()
        alt_core_version_text = self.alt_core_version_filter.text().lower()

        for i in range(self.alt_version_list.topLevelItemCount()):
            item = self.alt_version_list.topLevelItem(i)
            game_version_matches = alt_game_version_text in (
                item.game_version.lower() if item.game_version is not None else "")
            core_version_matches = alt_core_version_text in (
                item.core_version.lower() if item.core_version is not None else "")
            item.setHidden(not (game_version_matches and core_version_matches))

    def show_version_info(self, item):
        if isinstance(item, CustomTreeWidgetItem):
            self.details_label.setText(
                f"Minecraft {item.game_version} {item.core_version}"
            )
            self.install_button.setEnabled(True)
            self.selectedItem = item
        else:
            self.details_label.setText(memory.get("translate", {}).get("SelectCoreVersion", "select core"))
            self.install_button.setEnabled(False)

    def InstallClicked(self):
        pass


class ModWidget(QFrame):
    def __init__(self, mod_name, mod_path, toggle_callback, delete_callback, expand_callback, parent=None):
        super().__init__(parent)
        self.setObjectName("mod_frame")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFixedHeight(90)

        self.mod_path = mod_path
        self.toggle_callback = toggle_callback
        self.delete_callback = delete_callback
        self.expand_callback = expand_callback

        v = QVBoxLayout(self)

        panel = QWidget()
        panel.setFixedHeight(70)
        layout = QHBoxLayout(panel)
        v.addWidget(panel)
        v.addStretch()

        self.descript_label = QPlainTextEdit()
        self.descript_label.setObjectName("TextPlain")
        self.descript_label.setReadOnly(True)
        self.descript_label.setFixedHeight(0)
        self.descript_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        v.addWidget(self.descript_label)

        self.icon_label = QLabel(self)
        layout.addWidget(self.icon_label)

        self.mod_label = QLabel(mod_name)
        self.mod_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.mod_label)

        layout.addStretch()

        self.toggle_checkbox = AnimatedToggle()
        self.toggle_checkbox.setChecked(not mod_path.endswith(".disabled"))
        self.toggle_checkbox.toggled.connect(self.on_toggle)
        layout.addWidget(self.toggle_checkbox)

        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self.on_delete)
        self.delete_button.setFixedWidth(55)
        layout.addWidget(self.delete_button)

        self.openBtn = QPushButton("...")
        self.openBtn.setFixedWidth(30)
        self.openBtn.clicked.connect(self.on_click)
        layout.addWidget(self.openBtn)
        try:
            mod_info = get_mod_info(mod_path)
            # print(mod_info)
            self.mod_label.setText(mod_info.get("name", mod_name))
            self.descript_label.setPlainText(mod_info.get("description", "No description"))
            if 'icon_data' in mod_info and mod_info['icon_data']:
                icon_data = mod_info['icon_data']
                icon_image = Image.open(BytesIO(icon_data))
                buffer = BytesIO()
                icon_image.save(buffer, format="PNG")
                buffer.seek(0)
                byte_array = QByteArray(buffer.read())
                icon_pixmap = QPixmap()
                icon_pixmap.loadFromData(byte_array)
                max_size = 64
                original_width = icon_pixmap.width()
                original_height = icon_pixmap.height()
                if original_width > original_height:
                    scale_factor = max_size / original_width
                    scaled_width = max_size
                    scaled_height = int(original_height * scale_factor)
                else:
                    scale_factor = max_size / original_height
                    scaled_height = max_size
                    scaled_width = int(original_width * scale_factor)
                print(scaled_height, scaled_width)
                assert icon_pixmap is not None, "icon_pixmap is None"
                assert not icon_pixmap.isNull(), "icon_pixmap is null"
                assert scaled_width > 0 and scaled_height > 0, "Width and height must be positive"
                icon_pixmap = icon_pixmap.scaled(
                    scaled_width, scaled_height,
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                print(1)
                self.icon_label.setPixmap(icon_pixmap)
            else:
                self.icon_label.setFixedWidth(64)
        except:
            pass

    def on_toggle(self, checked):
        self.toggle_callback(checked, self.mod_path, self)

    def on_delete(self):
        self.delete_callback(self.mod_path, self)

    def on_click(self):
        self.expand_callback(self)

    def mousePressEvent(self, a0):
        self.on_click()
        return super().mousePressEvent(a0)


def get_mod_info(jar_file_path):
    with zipfile.ZipFile(jar_file_path, 'r') as jar:
        if 'fabric.mod.json' in jar.namelist():
            core = 'Fabric'
            info_file = 'fabric.mod.json'
        elif 'quilt.mod.json' in jar.namelist():
            core = 'Quilt'
            info_file = 'quilt.mod.json'
        elif 'META-INF/mods.toml' in jar.namelist():
            core = 'Forge'
            info_file = 'META-INF/mods.toml'
        else:
            return {"error": "Unknown mod type"}

        with jar.open(info_file) as file:
            if core in ['Fabric', 'Quilt']:
                mod_info = json.load(file)
                name = mod_info.get('name', 'Unknown')
                description = mod_info.get('description', 'No description')
                authors = mod_info.get('authors', 'Unknown')
                contact = mod_info.get('contact', {})
                icon_path = mod_info.get('icon')
            elif core == 'Forge':
                content = file.read().decode('utf-8')
                mod_info = toml.loads(content)
                mod = mod_info['mods'][0]
                name = mod.get('displayName', 'Unknown')
                description = mod.get('description', 'No description')
                authors = mod.get('authors', 'Unknown')
                contact = {}
                if 'issueTrackerURL' in mod:
                    contact['issueTrackerURL'] = mod['issueTrackerURL']
                icon_path = mod.get('logoFile')

        icon_data = None
        if icon_path and icon_path in jar.namelist():
            with jar.open(icon_path) as icon_file:
                icon_data = icon_file.read()

        return {
            "core": core,
            "name": name,
            "description": description,
            "authors": authors,
            "contact": contact,
            "icon_data": icon_data,
        }


class ModManager(QWidget):
    def __init__(self):
        super().__init__()
        self.mods_directory = "./"
        self.scrollarea = QScrollArea()
        self.scrollarea.setWidgetResizable(True)
        self.scrollwidget = QWidget()
        self.scrollarea.setWidget(self.scrollwidget)
        self.mods_layout = QVBoxLayout()
        self.scrollwidget.setLayout(self.mods_layout)
        self.expanded_widget = None
        self.v = QVBoxLayout(self)
        self.backButton = QPushButton(memory.get("translate", {}).get("Back", "Back"))
        self.top_h = QHBoxLayout()
        self.top_h.addWidget(self.backButton)
        self.top_h.addStretch()
        self.v.addLayout(self.top_h)
        self.v.addWidget(self.scrollarea)
        self.refresh_mod_list()

        # Настройка для Drag-and-Drop
        self.setAcceptDrops(True)

    def setPath(self, path):
        self.mods_directory = os.path.join(path, "mods")

    def add_mod_widget(self, mod_name, mod_path):
        print(mod_name)
        mod_widget = ModWidget(
            mod_name,
            mod_path,
            self.toggle_mod,
            self.delete_mod,
            self.expand_or_collapse,
            self
        )
        self.mods_layout.addWidget(mod_widget)

    def toggle_mod(self, is_checked, mod_path, item: ModWidget = None):
        new_mod_path = mod_path
        print(new_mod_path, is_checked)
        if is_checked:
            if mod_path.endswith(".disabled"):
                new_mod_path = mod_path.rsplit(".disabled", 1)[0]
        else:
            if not mod_path.endswith(".disabled"):
                new_mod_path = mod_path + ".disabled"
        item.mod_path = new_mod_path
        try:
            os.rename(mod_path, new_mod_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to toggle mod: {e}")

    def delete_mod(self, mod_path, item: ModWidget):
        confirm = QMessageBox.question(self, "Confirm Delete",
                                       f"Are you sure you want to delete {os.path.basename(mod_path)}?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                os.remove(mod_path)
                self.refresh_mod_list()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete mod: {e}")

    def expand_or_collapse(self, widget: ModWidget):
        if self.expanded_widget and self.expanded_widget != widget:
            self.animate_height(self.expanded_widget, self.expanded_widget.height(), 90)
            self.expanded_widget = None

        if self.expanded_widget == widget:
            self.expanded_widget = None
            self.animate_height(widget, widget.height(), 90)
        else:
            self.expanded_widget = widget
            self.animate_height(widget, widget.height(), 250)

    def animate_height(self, widget, start_height, end_height):
        def ch(value):
            widget.setFixedHeight(value)

        def ch2(value):
            widget.descript_label.setFixedHeight(value)

        animation = QVariantAnimation(widget)
        animation.setDuration(300)
        animation.setStartValue(start_height)
        animation.setEndValue(end_height)
        animation.valueChanged.connect(ch)
        animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        animation.start()

        if isinstance(widget, ModWidget):
            animation2 = QVariantAnimation(widget.descript_label)
            animation2.setDuration(300)
            animation2.setStartValue(widget.descript_label.height())
            animation2.setEndValue(end_height - 90)
            animation2.valueChanged.connect(ch2)
            animation2.setEasingCurve(QEasingCurve.Type.InOutCubic)
            animation2.start()

    def find_mods(self):
        if not os.path.exists(self.mods_directory):
            # os.makedirs(self.mods_directory, exist_ok=True)
            return []

        mods = []
        for file in os.listdir(self.mods_directory):
            if file.endswith(".jar") or file.endswith(".jar.disabled"):
                mods.append(os.path.join(self.mods_directory, file))
        return mods

    def refresh_mod_list(self):
        mods = self.find_mods()
        for i in reversed(range(self.mods_layout.count())):
            widget = self.mods_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        for mod_path in mods:
            mod_name = os.path.basename(mod_path)
            try:
                self.add_mod_widget(mod_name, mod_path)
            except:
                QMessageBox.warning(self, "Error load",
                                    "The mod " + mod_name + " could not be read, it will be skipped!")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            try:
                if os.path.isfile(path) and path.endswith(".jar"):
                    dest_path = os.path.join(self.mods_directory, os.path.basename(path))
                    if os.path.exists(dest_path):
                        confirm = QMessageBox.question(self, "File Exists",
                                                       f"{os.path.basename(path)} already exists. Replace it?",
                                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                        if confirm == QMessageBox.StandardButton.No:
                            continue
                    shutil.copy(path, dest_path)
                elif os.path.isdir(path):
                    for root, _, files in os.walk(path):
                        for file in files:
                            if file.endswith(".jar") or file.endswith(".jar.disabled"):
                                source_file = os.path.join(root, file)
                                dest_file = os.path.join(self.mods_directory, file)
                                if os.path.exists(dest_file):
                                    confirm = QMessageBox.question(self, "File Exists",
                                                                   f"{file} already exists. Replace it?",
                                                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                                    if confirm == QMessageBox.StandardButton.No:
                                        continue
                                shutil.copy(source_file, dest_file)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to process {path}: {e}")
        self.refresh_mod_list()

