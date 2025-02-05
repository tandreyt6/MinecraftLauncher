from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from functions import settings, memory


class ProfilePage(QWidget):
    def __init__(self, parent=None, css="", settings={}):
        super().__init__(parent)
        self.setStyleSheet(css)

        self.currentProfileIndex = -1
        self.profiles = []
        self.checkIndex = []
        self.nicknameIndex = []

        layout = QVBoxLayout()

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setObjectName("ProfileArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_widget.setObjectName("ProfileArea")
        self.scroll_layout = QVBoxLayout(self.scroll_widget)

        self.scroll_area.setWidget(self.scroll_widget)

        self.create_button = QPushButton(memory.get("translate", {}).get("createNewProfile", "Create new profile"), self)
        self.create_button.clicked.connect(self.createProfile)
        self.delete_button = QPushButton(memory.get("translate", {}).get("deleteSelectProfile", "Delete selected profile"), self)
        self.delete_button.clicked.connect(self.deleteProfile)

        layout.addWidget(self.scroll_area)
        layout.addWidget(self.create_button)
        layout.addWidget(self.delete_button)

        self.setLayout(layout)

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clearLayout(child.layout())

    def loadProfiles(self):
        self.checkIndex.clear()
        self.nicknameIndex.clear()
        self.currentProfileIndex = -1
        self.profiles = self.getProfilesFromStorage()
        self.clearLayout(self.scroll_layout)

        for index, profile in enumerate(self.profiles):
            profile_widget = self.createProfileWidget(profile, index)
            self.scroll_layout.addWidget(profile_widget)
        self.scroll_layout.addStretch()

    def createProfileWidget(self, profile, index):
        profile_widget = QWidget()
        profile_layout = QFormLayout(profile_widget)

        nickname_input = QLineEdit(profile["nickname"])
        nickname_input.setStyleSheet("QLineEdit { border: 2px solid white; border-radius: 2px;}")
        nickname_input.textChanged.connect(lambda: self.updateProfileNickname(index, nickname_input.text()))
        self.nicknameIndex.append(nickname_input)

        use_checkbox = QCheckBox(memory.get("translate", {}).get("useThisProfile", "Use this profile"))
        use_checkbox.setChecked(profile["is_active"])
        use_checkbox.stateChanged.connect(lambda state, idx=index: self.setActiveProfile(idx, state))
        if profile["is_active"]:
            for chb in self.checkIndex:
                if chb.isChecked():
                    chb.setChecked(False)
            self.currentProfileIndex = len(self.checkIndex)
        self.checkIndex.append(use_checkbox)

        profile_layout.addRow(memory.get("translate", {}).get("nicknameInGame", "Nickname"), nickname_input)
        profile_layout.addRow(use_checkbox)

        return profile_widget

    def get_current_index(self):
        return self.currentProfileIndex

    def createProfile(self):
        new_profile = {
            "nickname": "",
            "is_active": False
        }
        self.profiles.append(new_profile)
        self.saveProfilesToStorage()
        self.loadProfiles()

    def deleteProfile(self):
        if self.profiles:
            self.profiles.pop(self.currentProfileIndex)
            self.saveProfilesToStorage()
            self.loadProfiles()

    def updateProfileNickname(self, index, new_nickname):
        self.profiles[index]["nickname"] = new_nickname
        self.saveProfilesToStorage()

    def setActiveProfile(self, index, state):
        if len(self.profiles)-1 >= self.currentProfileIndex and len(self.checkIndex)-1 >= self.currentProfileIndex \
                and self.currentProfileIndex != index and self.currentProfileIndex != -1:
            self.profiles[self.currentProfileIndex]["is_active"] = False
            self.checkIndex[self.currentProfileIndex].setChecked(False)
        print(self.checkIndex[index].isChecked(), index, self.checkIndex, self.currentProfileIndex)
        if self.checkIndex[index].isChecked():
            self.profiles[index]["is_active"] = True
            self.currentProfileIndex = index
        else:
            self.profiles[index]["is_active"] = False
            self.currentProfileIndex = -1
        self.saveProfilesToStorage()


    def getProfilesFromStorage(self):
        return settings.getData("profiles", [])

    def saveProfilesToStorage(self):
        settings.setData("profiles", self.profiles)
        print("save", self.profiles)

