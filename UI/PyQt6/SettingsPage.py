import psutil
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import sys

from UI.PyQt6.TextSlider import SliderTicksLables
from UI.PyQt6.buttons import AnimatedToggle
from functions import settings, memory


class SettingsWidget(QWidget):
    def __init__(self, parent=None, css="", settings={}, main=None):
        super().__init__(parent)
        self.java_input: QLineEdit = None
        self.setStyleSheet(css)
        self.css = css
        self.main = main
        main_layout = QHBoxLayout(self)

        self.settings = settings

        tabs_layout = QVBoxLayout()
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget(self)
        scroll_widget.setObjectName("settingsArea")
        scroll_widget.setLayout(tabs_layout)
        self.scroll_area.setWidget(scroll_widget)

        self.tab_buttons = []
        self.create_tab_button(memory.get("translate", {}).get("General", "General"), tabs_layout)
        self.create_tab_button(memory.get("translate", {}).get("GameSettings", "Game settings"), tabs_layout)
        self.create_tab_button(memory.get("translate", {}).get("Advanced", "Advanced"), tabs_layout)
        self.create_tab_button(memory.get("translate", {}).get("About", "About"), tabs_layout)
        tabs_layout.addStretch()

        main_layout.addWidget(self.scroll_area, 1)

        self.settings_stack = QStackedWidget()
        main_layout.addWidget(self.settings_stack, 3)

        self.add_general_settings()
        self.add_game_settings()
        self.add_advanced_settings()
        self.add_about_info()

        self.tab_buttons[0].click()

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateTime)
        self.timer.start(1000)

    def updateTime(self):
        if settings.getData("javaMemory", 8000) != self.MemorySpin.value():
            settings.setData("javaMemory", self.MemorySpin.value())

    def create_tab_button(self, name, layout):
        button = QPushButton(name)
        button.setCheckable(True)
        button.clicked.connect(lambda: self.display_settings(name))
        layout.addWidget(button)
        self.tab_buttons.append(button)

    def display_settings(self, name):
        for button in self.tab_buttons:
            button.setChecked(False)

        button = next(b for b in self.tab_buttons if b.text() == name)
        button.setChecked(True)

        index = self.tab_buttons.index(button)
        self.settings_stack.setCurrentIndex(index)

    def toggle_anim_page(self, checked):
        settings.setData("canUseAnimPage", checked)

    def showConsoleToggle(self, checked):
        settings.setData("showConsole", checked)

    def showJavaConsoleToggle(self, checked):
        settings.setData("javaConsoleEnable", checked)

    def setCheckUpdate(self, checked):
        settings.setData("autoCheckUpdate", checked)

    def langChange(self):
        lang = "ru" if self.language_combo.currentIndex() == 0 else "en"
        print(lang)
        settings.setData("lang", lang)
        if lang == "ru":
            self.langTitle.setText(memory.get("needRestartAppRu"))
        else:
            self.langTitle.setText(memory.get("needRestartAppEn"))
        self.langTitle.setFixedHeight(20)

    def add_general_settings(self):
        widget = QWidget()
        layout = QFormLayout(widget)

        # layout.addWidget(QLabel("Language:"))
        self.langTitle = QLabel()
        self.langTitle.setFixedHeight(0)
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Русский", "English"])
        self.language_combo.setItemIcon(0, QIcon(self.settings.get("russianIcon")))
        self.language_combo.setItemIcon(1, QIcon(self.settings.get("englishIcon")))
        if settings.getData("lang", "en") == "ru":
            self.language_combo.setCurrentIndex(0)
        else:
            self.language_combo.setCurrentIndex(1)
        layout.addRow(self.langTitle)
        layout.addRow(QLabel(memory.get('translate', {}).get("Language", "Language")), self.language_combo)
        self.language_combo.currentTextChanged.connect(self.langChange)

        self.toggle_use_tans_anim = AnimatedToggle()
        self.toggle_use_tans_anim.setChecked(settings.getData("canUseAnimPage", True))
        self.toggle_use_tans_anim.toggled.connect(self.toggle_anim_page)

        self.toggle_check_updates = AnimatedToggle()
        self.toggle_check_updates.setChecked(settings.getData("autoCheckUpdate", True))
        self.toggle_check_updates.toggled.connect(self.setCheckUpdate)

        layout.addRow(self.toggle_use_tans_anim, QLabel(memory.get('translate', {}).get("toggleUsePageAnim",
                                                                                        "Use transition animation (experimental)")))
        layout.addRow(self.toggle_check_updates, QLabel(memory.get('translate', {}).get("toggleSetCheckUpdate",
                                                                                        "auto check update")))

        # layout.addStretch()

        self.settings_stack.addWidget(widget)

    def selectJavaDil(self):
        dil,_ = QFileDialog.getOpenFileName(self, "Select java", "C:/Program Files/Java/", "exe files (*.exe)")
        if dil:
            self.java_input.setText(dil)

    def setJavaPathText(self, text):
        settings.setData("javaPath", text)
        self.main.javaPath = text
    def add_advanced_settings(self):
        widget = QWidget()
        layout = QFormLayout(widget)

        self.console_checkbox = AnimatedToggle()
        self.console_checkbox.setChecked(settings.getData("showConsole", False))
        self.console_checkbox.toggled.connect(self.showConsoleToggle)

        self.console_checkbox_java = AnimatedToggle()
        self.console_checkbox_java.setChecked(settings.getData("javaConsoleEnable", False))
        self.console_checkbox_java.toggled.connect(self.showJavaConsoleToggle)

        # layout.addWidget()
        self.javaHelp = QLabel(memory.get('translate', {}).get("javaSettingsHelp", ""))

        self.java_input = QLineEdit()
        self.java_input.setText(str(settings.getData("javaPath", "java")))
        self.java_input.textChanged.connect(self.setJavaPathText)
        self.java_input.setFixedHeight(30)
        self.select_java = QPushButton(memory.get('translate', {}).get("SelectView", "Select"))
        self.select_java.clicked.connect(self.selectJavaDil)
        self.select_java.setFixedHeight(30)
        # layout.addRow(QLabel(memory.get('translate', {}).get("javaV", "Java Version")), self.java_input)
        layout.addRow(self.javaHelp)
        layout.addRow(self.select_java, self.java_input)
        layout.addRow(self.console_checkbox, QLabel(memory.get('translate', {}).get("showConsole", "Show console")))
        layout.addRow(self.console_checkbox_java, QLabel(memory.get('translate', {}).get("showJavaConsole", "Show console java")))

        # layout.addStretch()

        self.settings_stack.addWidget(widget)

    def changeValueMemory(self, value):
        self.MemorySlider.blockSignals(True)
        self.MemorySpin.blockSignals(True)
        self.MemorySlider.slider.setValue(value)
        self.MemorySpin.setValue(value)
        self.MemorySlider.blockSignals(False)
        self.MemorySpin.blockSignals(False)

    def checkCloseUi(self):
        settings.setData("isHideForLaunch", self.close_ui_toggle.isChecked())

    def add_game_settings(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        memoryS = psutil.virtual_memory()
        memoryV = (memoryS.total / (2 ** 20))
        self.MemorySlider = SliderTicksLables()
        self.MemorySlider.slider.setStyleSheet(self.css)
        self.MemorySlider.dlsText = " Mb"
        self.MemorySlider.isLeftOffest = True
        self.MemorySlider.slider.valueChanged.connect(self.changeValueMemory)
        self.MemorySlider.setRange(1000, int(memoryV), 5)

        self.MemorySpin = QSpinBox()
        self.MemorySpin.setRange(1000, int(memoryV))
        self.MemorySpin.valueChanged.connect(self.changeValueMemory)
        self.MemorySpin.setFixedWidth(100)

        self.close_ui_toggle = AnimatedToggle()
        self.close_ui_toggle.setChecked(settings.getData("isHideForLaunch", True))
        self.close_ui_toggle.toggled.connect(self.checkCloseUi)

        memoryHelp = QLabel(memory.get('translate', {}).get("memoryHelp", ""))
        memoryHelp.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        stretch = QLabel()
        stretch.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        h1 = QHBoxLayout()
        h1.addWidget(self.MemorySlider)
        h1.addWidget(self.MemorySpin)
        layout.addRow(memoryHelp)
        layout.addRow(h1)
        layout.addRow(self.close_ui_toggle, QLabel(memory.get('translate', {}).get("closeUiToggle", "Hide launcher when start game.")))
        layout.addRow(stretch)

        self.settings_stack.addWidget(widget)

    def add_about_info(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.about_text = QPlainTextEdit()
        self.about_text.setObjectName("VersionProgramm")
        self.about_text.setReadOnly(True)
        self.about_text.setStyleSheet(self.css)
        ver = memory.get("VersionProgramm")
        author = memory.get("AuthorProgramm")
        about_info = memory.get("translate", {}).get("aboutInfo", "").format(version=ver, author=author)

        self.about_text.setPlainText(about_info)

        layout.addWidget(self.about_text)
        self.settings_stack.addWidget(widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    settings_widget = SettingsWidget()
    settings_widget.show()
    sys.exit(app.exec())
