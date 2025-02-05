import sys
import webbrowser
from typing import List

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

from functions import settings, memory

minecraft_url = "https://www.minecraft.net"

class ArticleViewer(QWidget):
    htmlSignal = pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent)

        self.lasthtml = None

        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)

        self.text_browser.anchorClicked.connect(self.open_link)
        self.htmlSignal.connect(self.text_browser.setHtml)

        layout = QVBoxLayout()
        layout.addWidget(self.text_browser)
        self.setLayout(layout)

    def loadHtml(self, html="", css=""):
        if html:
            html = f"<meta name='viewport' content='width=device-width, initial-scale=1.0'>{html}"
            if css.strip() != "":
                html = f"<style>{css}</style>{html}"
            self.lasthtml = html
            self.htmlSignal.emit(html)
    def open_link(self, url: QUrl):
        if url.toString().startswith("http"):
            webbrowser.open(url.toString())
        else:
            webbrowser.open(minecraft_url+url.toString())
            self.text_browser.setHtml(self.lasthtml)
class ExpandableWidget(QWidget):
    frame_updated = pyqtSignal(int)

    def __init__(self, parent=None, collapse_value=0, expand_value=300, isExpanded=True):
        super().__init__(parent)
        self.is_expanded = isExpanded
        self.minval = collapse_value
        self.maxval = expand_value
        self.setFixedWidth(expand_value if isExpanded else collapse_value)

        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.animation.valueChanged.connect(self.on_value_changed)

    @pyqtSlot()
    def toggle(self):
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()

    def expand(self):
        self.is_expanded = True
        self.animation.stop()
        start_width = self.width()
        self.animation.setStartValue(start_width)
        self.animation.setEndValue(self.maxval)
        self.animation.start()

    def collapse(self):
        self.is_expanded = False
        self.animation.stop()
        start_width = self.width()
        self.animation.setStartValue(start_width)
        self.animation.setEndValue(self.minval)
        self.animation.start()

    @pyqtSlot(QVariant)
    def on_value_changed(self, value):
        self.setFixedWidth(int(value))
        self.frame_updated.emit(int(value))


class Window(QMainWindow):
    closeSignal = pyqtSignal()
    def __init__(self, settings={}):
        super().__init__()
        self.setWindowTitle("MinecraftLauncher")
        self.setGeometry(100, 100, 1000, 700)
        self.setFixedWidth(1000)
        self.setFixedHeight(700)

        self.settings = settings if settings is not None else {}
        self.setStyleSheet(self.settings.get("qtcss"))

        self.centralWidgets: List[QWidget] = []
        self.selectedWidget = None

        self.central_widget = None
        self.main_layout = None
        self.horizontal_layout = None
        self.lpBGPanel = None
        self.left_panel = None
        self.main_area: ArticleViewer = None
        self.bottom_panel = None
        self.playBtn = None
        self.comboVersionList = None
        self.closeBtn = None

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.is_dragging = False
        self.drag_start_position = QPoint()
        self.initUI()

    def position_button(self):
        button_x = self.width() - self.closeBtn.width() - 5
        self.closeBtn.move(button_x, 5)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rounded_rect = self.rect()
        color = QColor(50, 50, 50)
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rounded_rect, 15, 15)
        self.position_button()
        super().paintEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_start_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            self.move(event.globalPosition().toPoint() - self.drag_start_position)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False

    def addCentralWidget(self, widget):
        self.centralWidgets.append(widget)
        self.centralPageLayout.addWidget(widget)
        return len(self.centralWidgets)-1

    def animate_width(self, widget, start_width, end_width):
        def ch(value):
            widget.setMaximumWidth(value)

        animation = QVariantAnimation(widget)
        animation.setDuration(300)
        animation.setStartValue(start_width)
        animation.setEndValue(end_width)
        animation.valueChanged.connect(ch)
        animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        animation.start()

    def setCurrentCentralIndex(self, index: int):
        # print("open page", index)
        if not bool(settings.getData("canUseAnimPage", True)):
            self.openMomentalIndex(index)
            return
        widget = self.centralWidgets[index]
        if self.selectedWidget == widget: return
        if self.selectedWidget is not None:
            self.animate_width(self.selectedWidget, self.selectedWidget.width(), 0)
        self.animate_width(widget, widget.width(), 1000)
        self.selectedWidget = widget


    def allMomentalClose(self):
        for widget in self.centralWidgets:
            widget.setMaximumWidth(0)

    def openMomentalIndex(self, index: int):
        widget = self.centralWidgets[index]
        if self.selectedWidget is not None:
            self.selectedWidget.setMaximumWidth(0)
        self.selectedWidget = widget
        widget.setMaximumWidth(1300)

    def initUI(self):
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet(self.settings.get("qtcss"))
        self.centralPageLayout = QHBoxLayout()
        self.setCentralWidget(self.central_widget)
        self.central_layout = QHBoxLayout()
        self.central_widget.setLayout(self.central_layout)
        self.central_layout.setContentsMargins(0, 0, 0, 0)

        self.NewsPage = QWidget(self)
        self.addCentralWidget(self.NewsPage)
        self.main_layout = QVBoxLayout(self.NewsPage)

        self.closeBtn = QPushButton(self)
        self.closeBtn.setText("X")
        self.closeBtn.setFixedSize(30, 30)

        self.horizontal_layout = QHBoxLayout()
        self.main_layout.addLayout(self.horizontal_layout)

        self.lpBGPanel = ExpandableWidget(self, 40, 110, False)
        self.central_layout.addWidget(self.lpBGPanel)
        self.right_panel = QWidget()
        self.lpBGPanel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.right_layout = QHBoxLayout(self.right_panel)
        self.right_layout.addLayout(self.centralPageLayout)
        self.central_layout.addWidget(self.right_panel)

        def expandLeftPanel(e):
            self.lpBGPanel.expand()
            oldEnterEvent(e)

        oldEnterEvent = self.lpBGPanel.enterEvent
        self.lpBGPanel.enterEvent = expandLeftPanel

        def collapseLeftPanel(e):
            self.lpBGPanel.collapse()
            oldLeaveEvent(e)

        oldLeaveEvent = self.lpBGPanel.leaveEvent
        self.lpBGPanel.leaveEvent = collapseLeftPanel

        lpBGlayout = QHBoxLayout(self.lpBGPanel)
        lpBGlayout.setSpacing(0)
        lpBGlayout.setContentsMargins(0, 0, 0, 0)

        self.left_panel = QWidget(self.lpBGPanel)
        self.left_panel.setObjectName("leftPanel")
        lpBGlayout.addWidget(self.left_panel)

        self.left_panel_layout = QVBoxLayout(self.left_panel)
        self.left_panel_layout.setContentsMargins(0, 0, 0, 0)

        self.profileBtn = QPushButton(f"{memory.get('translate', {}).get('profileBtn', '      Profile ')}")
        self.profileBtn.setStyleSheet("text-align: left; padding-left: 10px;")
        self.lpBGPanel.frame_updated.connect(self.profileBtn.setFixedWidth)
        self.profileBtn.setIcon(QIcon(self.settings.get("profileIcon")))
        self.profileBtn.setFixedWidth(100)
        self.profileBtn.setIconSize(QSize(20,20))
        self.left_panel_layout.addWidget(self.profileBtn)

        self.newsBtn = QPushButton(f"{memory.get('translate', {}).get('newsBtn', '      News   ')}")
        self.newsBtn.setStyleSheet("text-align: left; padding-left: 10px;")
        self.lpBGPanel.frame_updated.connect(self.newsBtn.setFixedWidth)
        self.newsBtn.setIcon(QIcon(self.settings.get("newsIcon")))
        self.newsBtn.setFixedWidth(100)
        self.newsBtn.setIconSize(QSize(20, 20))
        self.newsBtn.clicked.connect(lambda: self.setCurrentCentralIndex(0))
        self.left_panel_layout.addWidget(self.newsBtn)

        self.versionsBtn = QPushButton(f"{memory.get('translate', {}).get('versionsBtn', '    Versions')}")
        self.versionsBtn.setStyleSheet("text-align: left; padding-left: 10px;")
        self.lpBGPanel.frame_updated.connect(self.versionsBtn.setFixedWidth)
        self.versionsBtn.setIcon(QIcon(self.settings.get("versionsIcon")))
        self.versionsBtn.setFixedWidth(100)
        self.versionsBtn.setIconSize(QSize(20, 20))
        self.left_panel_layout.addWidget(self.versionsBtn)

        self.settingsBtn = QPushButton(f"{memory.get('translate', {}).get('settingsBtn', '    Settings')}")
        self.settingsBtn.setStyleSheet("text-align: left; padding-left: 10px;")
        self.lpBGPanel.frame_updated.connect(self.settingsBtn.setFixedWidth)
        self.settingsBtn.setIcon(QIcon(self.settings.get("settingsIcon")))
        self.settingsBtn.setFixedWidth(100)
        self.settingsBtn.setIconSize(QSize(20, 20))
        self.left_panel_layout.addWidget(self.settingsBtn)

        self.left_panel_layout.addStretch()

        self.reloadBtn = QPushButton(f"{memory.get('translate', {}).get('reloadBtn', '    Reload  ')}")
        self.reloadBtn.setStyleSheet("text-align: left; padding-left: 10px;")
        self.lpBGPanel.frame_updated.connect(self.reloadBtn.setFixedWidth)
        self.reloadBtn.setIcon(QIcon(self.settings.get("reloadIcon")))
        self.reloadBtn.setFixedWidth(100)
        self.reloadBtn.setIconSize(QSize(20, 20))
        # self.left_panel_layout.addWidget(self.reloadBtn)
        # self.horizontal_layout.addWidget(self.lpBGPanel)

        self.lpBGPanel.expand()
        self.lpBGPanel.collapse()

        self.main_area = ArticleViewer(self)
        palette = self.main_area.text_browser.palette()
        palette.setColor(QPalette.ColorRole.Base, QColor("#2b2b2b"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#cccccc"))
        self.main_area.text_browser.setPalette(palette)
        self.horizontal_layout.addWidget(self.main_area)

        self.bottom_panel = QWidget()
        self.bottom_panel.setObjectName("bottomPanel")
        self.bottom_panel.setFixedHeight(50)

        bottom_layout = QHBoxLayout(self.bottom_panel)
        bottom_layout.addStretch()

        self.comboVersionList = QPushButton(self.settings.get('lastVersion', "Not selected"))
        self.comboVersionList.setObjectName("comboVersionList")
        self.comboVersionList.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        bottom_layout.addWidget(self.comboVersionList)

        self.playBtn = QPushButton(memory.get('translate', {}).get('Play', "Play"))
        self.playBtn.setMinimumWidth(100)
        bottom_layout.addWidget(self.playBtn)

        # self.main_layout.addWidget(self.bottom_panel)

    def closeEvent(self, a0):
        self.closeSignal.emit()
        return super().closeEvent(a0)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = Window()
    window.show()
    sys.exit(app.exec())
