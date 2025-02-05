from PyQt6.QtGui import QFontDatabase
dil_dark = """
    QWidget {
        background-color: #2b2b2b;
        color: white;
    }
    QMessageBox {
        background-color: #2b2b2b;
        color: white;
    }
    QPushButton {
        background-color: #3a3a3a;
        color: #a1d68b;
        border-radius: 5px;
        padding: 8px;
        text-align: left; padding-left: 10px;
    }
    QPushButton:checked {
        background-color: #4a4a4a;
    }
    QPushButton:hover {
        background-color: #4a4a4a;
    }
    QPlainTextEdit {
        background-color: #2b2b2b;
        color: white;
    }
    QTabWidget::pane { 
        border-top: 2px solid #a1d68b;
        background-color: #2b2b2b;
    }
    #TextPlain {
        border: none;
    }
    #mod_frame {
        border: 2px solid #3a3a3a;
        border-radius: 5px;
    }
    QTabBar::tab {
        background: #3a3a3a;
        color: #a1d68b;
        padding: 10px;
        border-top-left-radius: 5px;
        border-top-right-radius: 5px;
        margin-right: 5px;
    }
    QTabBar::tab:selected {
        background: #4a4a4a;
        color: white;
    }
    QPlainTextEdit{
        background-color: #2b2b2b;
        color: white;
    }
    QScrollArea {
        background-color: #2b2b2b;
    }
    QTabBar::tab:hover {
        background: #5a5a5a;
    }
    """
main_dark = """
    QTabWidget::pane { 
        border-top: 2px solid #a1d68b;
        background-color: #2b2b2b;
    }
    QTabBar::tab {
        background: #3a3a3a;
        color: #a1d68b;
        padding: 10px;
        border-top-left-radius: 5px;
        border-top-right-radius: 5px;
        margin-right: 5px;
    }
    QTabBar::tab:selected {
        background: #4a4a4a;
        color: white;
    }
    QTabBar::tab:hover {
        background: #5a5a5a;
    }
    QMainWindow {
        background-color: #1a1a1a;
    }
    QWidget#mainArea {
        background-color: #2b2b2b;
        color: white;
    }
    QWidget#leftPanel {
        background-color: #2b2b2b;
        border-radius: 10px;
    }
    QWidget#bottomPanel {
        background-color: #2b2b2b;
        border-radius: 10px;
    }
    QWidget#settingsArea {
        background-color: #2b2b2b;
    }
    QWidget#versionsWidget {
        background-color: #2b2b2b;
    }
    QPushButton#comboVersionList {
        background-color: #3a3a3a;
        color: #a1d68b;
        border-radius: 5px;
        padding: 8px;
    }
    QPushButton#comboVersionList:hover {
        background-color: #4a4a4a;
    }
    QPushButton {
        background-color: #3a3a3a;
        color: #a1d68b;
        border-radius: 5px;
        padding: 8px;
    }
    QPushButton:checked {
        background-color: #4a4a4a;
    }
    QPushButton:hover {
        background-color: #4a4a4a;
    }
    QLabel {
        color: #a1d68b;
    }
    QPlainTextEdit{
        background-color: #2b2b2b;
        color: white;
    }
    QCheckBox {
        color: #a1d68b;
    }
    QComboBox {
        background-color: #3a3a3a;
        color: #a1d68b;
        border-radius: 5px;
        padding: 5px;
    }
    QComboBox QAbstractItemView {
        background-color: #3a3a3a;
        color: #a1d68b;
        selection-background-color: #4a4a4a;
    }
    QScrollBar:vertical {
        background: #2b2b2b;
        width: 12px;
        margin: 16px 0 16px 0;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical {
        background: #a1d68b;
        min-height: 20px;
        border-radius: 5px;
    }
    QScrollBar::handle:vertical:hover {
        background: #91c779;
    }
    #ProfileArea {
        background-color: #2b2b2b;
    }
    #VersionProgramm {
        background-color: #2b2b2b;
    }
"""

SiteCss = """
    a { 
        color: #6CC349; 
    }
    
    p {
        font-size: 16px;
    }

    h1 { 
        font-family: {custom}"Noto Sans","Helvetica Neue","Helvetica","Arial","sans-serif";
    }
    
    h2 { 
        font-family: {custom}"Noto Sans","Helvetica Neue","Helvetica","Arial","sans-serif";
    }
"""
