import ctypes
import shutil
import signal
import time
import zipfile

import requests
from PyQt6.QtNetwork import QTcpSocket

from functions.Core import SingleInstanceApp
from functions.createShortcut import create_shortcut

app = SingleInstanceApp([])

import datetime
import io
import json
import os
import subprocess
import sys
import psutil
import buildParams

from UI.PyQt6 import MainWindow, QTCSS, VersionsPage, SettingsPage, dialog, ProfilePage
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from UI.PyQt6.ConsoleWidget import ConsoleWidget
from UI.PyQt6.VersionsPage import VersionItem
from functions import http_requests, installer, settings, runner, memory, translate


def qt_message_handler(mode, context, message):
    print(f"Qt Error: {message}")


qInstallMessageHandler(qt_message_handler)


class UIUpdateThread(QThread):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(QApplication.processEvents)

    def run(self):
        self.timer.start()
        self.exec()

    def stop(self):
        self.timer.stop()
        self.quit()


class Worker(QObject):
    finished = pyqtSignal()

    def method(self):
        pass

    def run(self):
        self.method()
        self.finished.emit()


class LauncherThread(QThread):
    finish = pyqtSignal()

    def setParams(self, runer, dir):
        self.run = runer
        self.dir = dir

    def run(self):
        self.run.run(False)
        print(self.run)
        self.finish.emit()
        proc: subprocess.CompletedProcess = self.run.procces
        if proc:
            print("An error occurred when launching minecraft! Error code: " + str(proc.returncode))
        return


memory.put("VersionProgramm", buildParams.VERSION)
memory.put("AuthorProgramm", buildParams.AUTHOR)

GITHUB_REPO = 'tandreyt6/MinecraftLauncher'

class Main:

    def __init__(self):
        self.MainObject = QObject()
        self.runs = {}
        # self.MineVersionsFolder = "./MinecraftBuilds"
        self.installFolder = os.getcwd()
        self.minecraftCoresFolder = os.getcwd() + "/versions"
        self.settingsPath = os.getcwd() + "/LauncherSettings.json"
        self.buildsPath = os.getcwd() + "/builds"
        self.javaMemoryControlArg = "-Xmx{memory}m"
        settings.load(self.settingsPath)
        self.javaPath = settings.getData("javaPath", "java")
        memory.put("needRestartAppRu", "Для изменения языка требуется перезапуск приложения!")
        memory.put("needRestartAppEn", "Restarting the application is required to change the language!")
        print(settings.getData("lang", "en"))
        if settings.getData("lang", "en") == "ru":
            memory.put("translate", translate.ru)
            memory.put("lang", "ru")
        else:
            memory.put("lang", "en")
            memory.put("translate", translate.en)
        os.makedirs(self.buildsPath, exist_ok=True)
        os.makedirs(self.minecraftCoresFolder, exist_ok=True)
        self.buildVersions = []
        self.availdCores = self.find_minecraft_versions(self.minecraftCoresFolder)
        print(self.availdCores)
        self.dil: dialog.CoreSelectionDialog = None
        self.modsDil: dialog.ModManager = None
        self.playIcon = QIcon("./UI/Icons/PlayIcon.png")
        self.stopIcon = QIcon("./UI/Icons/StopIcon.png")
        self.setting = {"qtcss": QTCSS.main_dark,
                        "minecraftIcon": "./UI/Icons/MinecraftIcon.png",
                        "minecraftIconIco": os.getcwd() + "/UI/Icons/MinecraftIcon.ico",
                        "profileIcon": "./UI/Icons/ProfileIcon.png",
                        "versionsIcon": "./UI/Icons/versionsIcon.png",
                        "newsIcon": "./UI/Icons/NewsIcon.png",
                        "settingsIcon": "./UI/Icons/SettingsIcon.png",
                        "russianIcon": "./UI/Icons/RussianIcon.png",
                        "englishIcon": "./UI/Icons/EnglishIcon.png",
                        "playIcon": "./UI/Icons/PlayIcon.png",
                        "folderIcon": "./UI/Icons/FolderIcon.png",
                        "modsIcon": "./UI/Icons/ModsIcon.png",
                        "createIcon": "./UI/Icons/CreateIcon.png",
                        "reloadIcon": "./UI/Icons/ReloadIcon.png",
                        "deleteIcon": "./UI/Icons/trashIcon.png"
                        }

        self.initUI()
        self.settingsWidget.changeValueMemory(settings.getData("javaMemory", 8000))
        self.timer = QTimer(self.MainObject)
        self.timer.timeout.connect(self.update)
        self.timer.start(100)

        self.consoleDil.closeSignal.connect(self.closeConsoleWidget)

    def closeConsoleWidget(self):
        self.settingsWidget.console_checkbox.setChecked(False)
        settings.setData("showConsole", False)

    def update(self):
        # print(settings.getData("showConsole", False), self.consoleDil.isVisible())
        if settings.getData("showConsole", False) != self.consoleDil.isVisible():
            self.consoleDil.setVisible(settings.getData("showConsole", False))
        logText = thisStdout.getvalue()
        self.consoleDil.set_console_text(logText)
        if len(self.runs) > 0:
            self.ui.closeBtn.setText("-")
        else:
            self.ui.closeBtn.setText("X")
        if self.versionWidget.selectedItem is not None:
            self.versionWidget.playBtn.setEnabled(True)
            self.versionWidget.modsBtn.setEnabled(True)
            self.versionWidget.openFolderBtn.setEnabled(True)
            if not self.versionWidget.selectedItem.data.get("path") in self.runs:
                self.versionWidget.playBtn.setText(memory.get("translate", {}).get("Play", "Play"))
                self.versionWidget.playBtn.setIcon(self.playIcon)
                self.versionWidget.delButton.setEnabled(True)
            else:
                self.versionWidget.playBtn.setText(memory.get("translate", {}).get("Terminate", "Terminate"))
                self.versionWidget.playBtn.setIcon(self.stopIcon)
                self.versionWidget.delButton.setEnabled(False)
        else:
            self.versionWidget.delButton.setEnabled(False)
            self.versionWidget.playBtn.setEnabled(False)
            self.versionWidget.modsBtn.setEnabled(False)
            self.versionWidget.openFolderBtn.setEnabled(False)
        app.processEvents()

    def cleanupUI(self):
        pass

    def find_build_settings(self, path_to_folder):
        self.buildVersions.clear()
        if not os.path.exists(path_to_folder):
            print(f"Select path {path_to_folder} is not folder.")
            return

        for folder_name in os.listdir(path_to_folder):
            full_path = os.path.join(path_to_folder, folder_name)
            if os.path.isdir(full_path):
                target_file = os.path.join(full_path, "BuildSettings.json")
                if os.path.isfile(target_file):
                    with open(target_file, "r", encoding="utf-8") as e:
                        try:
                            data = json.load(e)
                        except:
                            continue
                        if data.get("type") == "ForMinecraftLauncher":
                            data["path"] = full_path.replace("/", "\\")
                            self.buildVersions.append(data)

        if len(self.buildVersions) == 0:
            print("Files BuildSettings.json is not found.")

    def find_minecraft_versions(self, folder_path):
        versions = {"forge": [], "fabric": [], "vanilla": [], "quilt": []}

        if not os.path.exists(folder_path):
            return versions

        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)

            if os.path.isdir(item_path):
                jar_file = os.path.join(item_path, f"{item}.jar")
                json_file = os.path.join(item_path, f"{item}.json")
                if not (os.path.isfile(jar_file) and os.path.isfile(json_file)):
                    continue
            if "forge" in item.lower():
                parts = item.split("-forge-")
                if len(parts) == 2:
                    minecraft_version, core_version = parts
                    versions["forge"].append({"minecraftVersion": minecraft_version, "coreVersion": core_version})
            elif "fabric-loader" in item.lower():
                parts = item.split("-")
                if len(parts) >= 3:
                    core_version = parts[2]
                    minecraft_version = parts[-1]
                    versions["fabric"].append({"minecraftVersion": minecraft_version, "coreVersion": core_version})
            elif "quilt-loader" in item.lower():
                parts = item.split("-")
                if len(parts) >= 3:
                    core_version = parts[2]
                    minecraft_version = parts[-1]
                    versions["quilt"].append({"minecraftVersion": minecraft_version, "coreVersion": core_version})
            elif item[0].isdigit() and all(part.isdigit() for part in item.split(".")):
                versions["vanilla"].append({"minecraftVersion": item, "coreVersion": ""})

        return versions

    def delBuild(self):
        path = self.versionWidget.selectedItem.data.get("path")
        if path in self.runs:
            self.showInfoDil("Error", memory.get("translate", {}).get("buildRunning", "build is now running!"))
            return
        res = self.ask_question("Build remove",
                                memory.get("translate", {}).get("confirmDeleteBuild", "Build remove?"),
                                memory.get("translate", {}).get("Delete", "Delete"),
                                memory.get("translate", {}).get("Cancel", "Cancel"))
        if res:
            if self.versionWidget.selectedItem is not None:
                if path and os.path.exists(path):
                    shutil.rmtree(path)
                self.refreshVersions()


    def get_latest_version(self):
        url = f'https://api.github.com/repos/{GITHUB_REPO}/releases/latest'
        response = requests.get(url)
        if response.status_code == 200:
            release = response.json()
            return release['tag_name']
        else:
            print('Error fetching latest version.')
            return None

    def show_update_dialog(self, noShowIfNoUpdates=False):
        def update():
            print("update...")
            if self.close(True):
               subprocess.Popen([os.getcwd()+"/updater.exe", memory.get("lang", "en")])
               app.closeAllWindows()
               app.exit(0)
               sys.exit(0)
        ver = self.get_latest_version()
        update_available = False
        print("Last version:", ver, buildParams.VERSION)
        if ver:
            update_available = buildParams.VERSION != ver

        dialog = QDialog()
        dialog.setStyleSheet(QTCSS.dil_dark)
        dialog.setWindowTitle("Update Check")
        dialog.setFixedSize(370, 150)

        layout = QVBoxLayout(dialog)

        if update_available:
            label = QLabel(memory.get("translate", {}).get("updateAvailable", "Update available!").format(version=ver))
            layout.addWidget(label)

            h1 = QHBoxLayout()

            update_button = QPushButton(memory.get("translate", {}).get("Update", "Update"))
            update_button.clicked.connect(update)
            h1.addWidget(update_button)

            cancel_button = QPushButton(memory.get("translate", {}).get("Cancel", "Cancel"))
            cancel_button.clicked.connect(dialog.close)
            h1.addWidget(cancel_button)

            layout.addLayout(h1)
        else:
            if noShowIfNoUpdates: return
            label = QLabel(memory.get("translate", {}).get("noUpdateAvailable", "No update available!"))
            layout.addWidget(label)

            close_button = QPushButton(memory.get("translate", {}).get("Close", "Close"))
            close_button.clicked.connect(dialog.close)
            layout.addWidget(close_button)

        dialog.exec()

    def initUI(self):
        self.WindowIcon = QIcon("./UI/Icons/MinecraftIcon.ico")
        self.ui = MainWindow.Window(self.setting)
        self.ui.setWindowIcon(self.WindowIcon)
        # self.showUiWindow.connect(self.ui.show)
        self.ui.closeSignal.connect(self.close)
        self.ui.closeBtn.clicked.connect(self.close)

        self.consoleDil = ConsoleWidget()
        self.consoleDil.setWindowIcon(self.WindowIcon)

        self.modsDil = dialog.ModManager()
        self.modsDil.setStyleSheet(QTCSS.dil_dark)
        self.modsDilIndex = self.ui.addCentralWidget(self.modsDil)

        versions = {
            "Fabric": ["loading..."],
            "Forge": [{"minecraft": "-_-", "forge": "loading..."}],
            "Quilt": ["loading..."],
            "Vanilla": ["loading..."],
        }

        self.dil = dialog.CoreSelectionDialog(versions)
        self.dil.setWindowIcon(self.WindowIcon)
        self.dil.install_button.clicked.connect(self.installCore)
        self.dil.setStyleSheet(QTCSS.dil_dark)
        self.dil.btns["Vanilla"].click()
        self.dilIndex = self.ui.addCentralWidget(self.dil)

        self.profileWidget = ProfilePage.ProfilePage(self.ui, QTCSS.main_dark, self.setting)
        self.profileWidget.profiles = settings.getData("profiles", [])
        print(self.profileWidget.profiles)
        self.profileWidget.loadProfiles()
        # self.profileWidget.nickname_input.setText(settings.getData("username", "Player"))
        indexProfile = self.ui.addCentralWidget(self.profileWidget)
        self.ui.profileBtn.clicked.connect(lambda: self.ui.setCurrentCentralIndex(indexProfile))

        self.ui.reloadBtn.clicked.connect(self.qReload)

        self.newsList = None

        self.versionWidget = VersionsPage.VersionsPage(self.ui, QTCSS.main_dark, self.setting, self.availdCores)
        self.versionWidget.delButton.clicked.connect(self.delBuild)
        self.versionWidget.createShortcutBtn.clicked.connect(self.createShortcutBtn)
        self.versionWidget.createBtn.clicked.connect(self.createBuild)
        self.versionWidget.settingBtn.clicked.connect(self.settingsBuild)
        self.versionWidget.playBtn.clicked.connect(self.playBuild)
        self.versionWidget.modsBtn.clicked.connect(self.modsBuild)
        self.versionWidget.coresBtn.clicked.connect(self.coresBtn)
        self.versionWidget.openFolderBtn.clicked.connect(self.openFolderBuild)
        self.versionWidget.openFolderBtnVersions.clicked.connect(self.openFolderBuildVers)
        self.versionWidget.refresh.clicked.connect(self.refreshVersions)
        index = self.ui.addCentralWidget(self.versionWidget)
        self.ui.versionsBtn.clicked.connect(lambda: self.ui.setCurrentCentralIndex(index))
        self.modsDil.backButton.clicked.connect(lambda: self.ui.setCurrentCentralIndex(index))
        self.dil.backButton.clicked.connect(lambda: self.ui.setCurrentCentralIndex(index))
        self.refreshVersions()

        self.settingsWidget = SettingsPage.SettingsWidget(self.ui, QTCSS.main_dark, self.setting, self)
        index2 = self.ui.addCentralWidget(self.settingsWidget)
        self.ui.settingsBtn.clicked.connect(lambda: self.ui.setCurrentCentralIndex(index2))

        self.ui.checkUpdatesBtn.clicked.connect(self.show_update_dialog)

        self.ui.allMomentalClose()
        self.ui.openMomentalIndex(0)

        self.loadFonts()

        self.thread = QThread(self.ui)
        self.worker = Worker()
        self.worker.method = self.loadLastNews
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def createShrtucut(self, seleceVersion: str, icon: str):
        version = seleceVersion

    def createShortcutBtn(self):
        dil = QDialog()
        dil.setStyleSheet(QTCSS.dil_dark)
        dil.setWindowTitle(
            memory.get("translate", {}).get("createShortcut", "Create Shortcut"))
        dil.setWindowIcon(self.WindowIcon)

        layout = QVBoxLayout(dil)

        info_label = QLabel(
            memory.get("translate", {}).get("selectBuild", "Select a Minecraft build to create a shortcut"))
        layout.addWidget(info_label)

        build_combo = QComboBox(dil)
        print(self.buildVersions)
        verList = []
        for i in self.buildVersions:
            name = i["path"].split("\\")
            verList.append("./" + name[-1])
        print(verList)
        build_combo.addItems(verList)
        layout.addWidget(build_combo)

        self.selectIcoShortcut = None

        def choose_ico():
            ico_path, _ = QFileDialog.getOpenFileName(dil, "Select Icon", "", "ICO Files (*.ico)")
            if ico_path:
                ico_path2 = ico_path
                if len(ico_path) > 50:
                    ico_path2 = "..." + ico_path[-50:]
                choose_button.setText(f"{ico_path2}")
                self.selectIcoShortcut = ico_path

        def create():
            dil.close()
            if len(build_combo.currentText()) < 1:
                self.showInfoDil("Error", memory.get("translate", {}).get("noBuildSelected", "No selected build"))
                return
            shortcut_file = os.path.join(os.path.expanduser("~"), "Desktop", build_combo.currentText() + ".lnk")
            if os.path.exists(shortcut_file):
                create_shortcut(sys.executable, shortcut_file, self.setting[
                    "minecraftIconIco"] if self.selectIcoShortcut is None else self.selectIcoShortcut,
                                "nogui run " + build_combo.currentText())
                self.showInfoDil("Done",
                                 memory.get("translate", {}).get("shortcutCreateDesktop", "Shortcut -> desktop"))
            else:
                t = build_combo.currentText().split("/")[-1]
                shortcut_file = self.buildsPath + "/" + t + "/" + t + ".lnk"
                create_shortcut(sys.executable, shortcut_file, self.setting[
                    "minecraftIconIco"] if self.selectIcoShortcut is None else self.selectIcoShortcut,
                                "nogui run " + build_combo.currentText())
                self.showInfoDil("Done",
                                 memory.get("translate", {}).get("shortcutCreateBuild", "Shortcut -> build folder"))
            print("create shortcut " + shortcut_file)

        choose_button = QPushButton(memory.get("translate", {}).get("selectIcoFile", "Select an icon file"))
        choose_button.clicked.connect(choose_ico)
        layout.addWidget(choose_button)

        buttons_layout = QHBoxLayout()

        create_button = QPushButton(memory.get("translate", {}).get("createShortcut", "Create shortcut"))
        create_button.clicked.connect(create)
        buttons_layout.addWidget(create_button)

        cancel_button = QPushButton(memory.get("translate", {}).get("Cancel", "Cancel"))
        cancel_button.clicked.connect(dil.reject)
        buttons_layout.addWidget(cancel_button)

        layout.addLayout(buttons_layout)

        dil.exec()

    def refreshVersions(self):
        self.versionWidget.display_info(None)
        self.buildVersions.clear()
        self.find_build_settings(self.buildsPath)
        print(self.buildVersions)
        self.versionWidget.versions = self.buildVersions
        self.versionWidget.loadVersions()
        self.availdCores = self.find_minecraft_versions(self.minecraftCoresFolder)
        print(self.availdCores)

    def qReload(self):
        msg_box = QMessageBox()
        msg_box.setWindowIcon(self.WindowIcon)
        msg_box.setStyleSheet(QTCSS.dil_dark)
        msg_box.setWindowTitle("Launcher")
        msg_box.setText(self.setting.get("translate", {}).get("qReload", "Are you really reload launcher?"))
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        response = msg_box.exec()

        if response == QMessageBox.StandardButton.Yes:
            # self.ui.close()
            self.ui.hide()
            self.cleanupUI()
            app.processEvents()
            # time.sleep(1)
            self.initUI()
            self.ui.show()

    def checkFreeSpace(self):
        hdd = psutil.disk_usage('/')
        return (hdd.free / (2 ** 30)) >= 5

    def showInfoDil(self, title, text):
        d = QDialog(self.ui)
        d.setWindowTitle(title)
        d.setWindowIcon(self.WindowIcon)
        d.setStyleSheet(QTCSS.dil_dark)
        v = QVBoxLayout(d)
        lbl = QLabel(text)
        h = QHBoxLayout()
        h.addStretch()
        btn = QPushButton("ok")
        btn.clicked.connect(d.close)
        h.addWidget(btn)
        v.addWidget(lbl)
        v.addLayout(h)
        d.show()
        d.exec()

    def createBuild(self):
        def create():
            namepath = name.text().replace(" ", "_".replace("\\", "").replace("/", ""))
            if len(name.text().strip()) < 5:
                self.showInfoDil("Error", memory.get("translate", {}).get("nameTooShort", "name Too Short"))
                return

            path = self.buildsPath + "/" + namepath
            os.makedirs(path, exist_ok=True)
            if os.path.exists(path) and os.path.exists(path + "/BuildSettings.json"):
                with open(path + "/BuildSettings.json", "r", encoding="utf-8") as file:
                    data = json.load(file)
                    if data.get("type") == "ForMinecraftLauncher":
                        self.showInfoDil("Creator", memory.get("translate", {}).get("buildExists", "Build exists!"))
                        return
            dil.close()
            with open(path + "/BuildSettings.json", "w", encoding="utf-8") as file:
                data = {
                    "type": "ForMinecraftLauncher",
                    "title": name.text(),
                    "CoreType": "[no select]",
                    "CoreVersion": "[no select]",
                    "minecraftVersion": "[no select]"
                }
                json.dump(data, file, indent=4)
                data["path"] = path
                data["func"] = self.versionWidget.display_info
                item = self.versionWidget.addWidget(data)
                self.versionWidget.display_info(item)

        def keyPressEvent(event):
            print(event.key(), Qt.Key.Key_Enter, Qt.Key.Key_Return)
            if event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
                okbtn.click()
            elif event.key() == Qt.Key.Key_Escape:
                closebtn.click()
            else:
                oldkb(event)

        dil = QDialog(self.ui)
        dil.setWindowIcon(self.WindowIcon)
        oldkb = dil.keyPressEvent
        dil.keyPressEvent = keyPressEvent
        dil.setStyleSheet(QTCSS.dil_dark)
        dil.setWindowTitle("Creator")
        dil.setFixedHeight(80)
        form = QFormLayout(dil)
        name = QLineEdit()
        form.addRow(QLabel(memory.get("translate", {}).get("BuildName", "Build name")), name)
        okbtn = QPushButton(memory.get("translate", {}).get("Create", "Create"))
        okbtn.clicked.connect(create)
        closebtn = QPushButton(memory.get("translate", {}).get("Cancel", "Cancel"))
        closebtn.clicked.connect(dil.close)
        form.addRow(closebtn, okbtn)
        dil.show()
        dil.exec()

    def coresBtn(self):
        if True:
            self.ui.setCurrentCentralIndex(self.dilIndex)
            app.processEvents()
            try:
                fabricVersions = installer.FabricInstaller.list_versions()
                app.processEvents()
                forgeVersions = installer.ForgeInstaller.list_versions()
                app.processEvents()
                quiltVersions = installer.QuiltInstaller.list_versions()
                app.processEvents()
                minecraftVersions = installer.MinecraftInstaller.list_versions()
                app.processEvents()
            except:
                fabricVersions = []
                forgeVersions = []
                quiltVersions = []
                minecraftVersions = []
            print(fabricVersions)
            print(forgeVersions)
            print(quiltVersions)
            print(minecraftVersions)
            versions = {
                "Fabric": [_["version"] for _ in fabricVersions],
                "Forge": [{"minecraft": _.split("-")[0], "forge": _.split("-")[1]} for _ in forgeVersions],
                "Quilt": [_["version"] for _ in quiltVersions],
                "Vanilla": [_["id"] for _ in minecraftVersions],
            }

            self.dil.versions = versions
            self.dil.alt_installed = self.availdCores
            self.dil.btns["Vanilla"].click()
            self.dil.alt_btns["Vanilla"].click()

        else:
            self.dil.raise_()

    def installCore(self):
        if self.dil is not None:
            print(self.dil.selectedItem.game_version, "|", self.dil.selectedItem.core_version, "|",
                  self.dil.selectedItem.coreType)

            coretype = self.dil.selectedItem.coreType
            gameversion = self.dil.selectedItem.game_version
            coreversion = self.dil.selectedItem.core_version if self.dil.selectedItem.core_version is not None else "Any"

            def start(ver1, core1, type1):
                command = ["./InsAr5Con.exe", self.installFolder, ver1, core1, type1, "true", self.javaPath]
                print(command)
                proc = subprocess.Popen(command, creationflags=subprocess.CREATE_NEW_CONSOLE)

            if gameversion == "Any":
                def install():
                    dil.close()
                    start(ver.currentText(), coreversion, coretype)

                dil = QDialog(self.ui)
                dil.setWindowIcon(self.WindowIcon)
                dil.setStyleSheet(QTCSS.dil_dark)
                v = QVBoxLayout(dil)
                dil.setWindowTitle("Installer")
                v.addWidget(
                    QLabel(memory.get("translate", {}).get("specifyMinecraftVersion", "select minecraft version")))
                minecraftVersions = [_["id"] for _ in installer.MinecraftInstaller.list_versions()]
                print(minecraftVersions)
                ver = QComboBox()
                ver.addItems(minecraftVersions)
                okbtn = QPushButton(memory.get("translate", {}).get("Install", "Install"))
                okbtn.clicked.connect(lambda: install())
                canclebtn = QPushButton(memory.get("translate", {}).get("Cancel", "Cancel"))
                canclebtn.clicked.connect(dil.close)
                h = QHBoxLayout()
                h.addWidget(canclebtn)
                h.addWidget(okbtn)
                v.addWidget(ver)
                v.addLayout(h)
                dil.show()
                dil.exec()
                return

            start(gameversion, coreversion, coretype)

    def settingsBuild(self):
        print("settings btn")

    def ask_question(self, title: str, text: str, btn1_text: str = "Yes", btn2_text: str = "No") -> bool:
        dialog = QDialog()
        dialog.setWindowIcon(self.WindowIcon)
        dialog.setStyleSheet(QTCSS.dil_dark)
        dialog.setWindowTitle(title)

        layout = QVBoxLayout()
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        button_layout = QHBoxLayout()

        btn_yes = QPushButton(btn1_text)
        btn_no = QPushButton(btn2_text)

        btn_yes.setDefault(True)

        btn_yes.clicked.connect(lambda: dialog.done(2))
        btn_no.clicked.connect(lambda: dialog.done(1))

        button_layout.addWidget(btn_yes)
        button_layout.addWidget(btn_no)

        layout.addLayout(button_layout)
        dialog.setLayout(layout)

        res = dialog.exec()
        if res == 2:
            return True
        elif res == 1:
            return False
        else:
            return None

    def playBuild(self):
        if self.versionWidget.selectedItem is None: return
        version = self.versionWidget.selectedItem.data.get("minecraftVersion")
        coreVersion = self.versionWidget.selectedItem.data.get("CoreVersion")
        gameDir = self.versionWidget.selectedItem.data.get("path")
        if gameDir in self.runs:
            trans = memory.get("translate", {})
            if self.ask_question("Terminate", trans.get("youAlsoTerminate", "Terminate?"),
                                 trans.get("Yes", "Yes"), trans.get("No", "No")):
                x: LauncherThread = self.runs.get(gameDir)
                process = x.run.procces
                if process:
                    process = psutil.Process(process.pid)
                    for child in process.children(recursive=True):
                        child.kill()
                    process.kill()
                x.terminate()
                del self.runs[gameDir]
            return

        nickname = self.profileWidget.get_current_index()
        if nickname is None or nickname == -1:
            self.showInfoDil("Nickname Error", memory.get("translate", {}).get("NoSelectProfileErr", "Profile error!"))
            return
        nickname = self.profileWidget.profiles[nickname]["nickname"]
        print(nickname)
        if len(nickname) < 7:
            self.showInfoDil("Nickname Error", memory.get("translate", {}).get("nicknameLongError", "Profile error!"))
            return
        uuid = settings.getData("uuid", "3f69c852b89645ca81e05f5952d9d8e9 ")
        token = settings.getData("token", "null")
        argv = [self.javaMemoryControlArg.format(memory=self.settingsWidget.MemorySpin.value()),
                "-Dminecraft.api.env=custom",
                "-Dminecraft.api.auth.host=https://invalid.invalid",
                "-Dminecraft.api.account.host=https://invalid.invalid",
                "-Dminecraft.api.session.host=https://invalid.invalid",
                "-Dminecraft.api.services.host=https://invalid.invalid"]
        print("Argv", argv)
        run = None
        consoleEnable = settings.getData("javaConsoleEnable", False)
        if self.versionWidget.selectedItem.data.get("CoreType").lower() == "vanilla":
            run = runner.VanillaLauncher(version, self.installFolder, self.javaPath, gameDir, nickname, token=token,
                                         uuid=uuid, javaArgv=argv, consoleEnable=consoleEnable)
        elif self.versionWidget.selectedItem.data.get("CoreType").lower() == "forge":
            run = runner.ForgeLauncher(version, coreVersion, self.installFolder, self.javaPath, gameDir, nickname,
                                       token=token, uuid=uuid, javaArgv=argv, consoleEnable=consoleEnable)
        elif self.versionWidget.selectedItem.data.get("CoreType").lower() == "fabric":
            run = runner.FabricLauncher(version, coreVersion, self.installFolder, self.javaPath, gameDir, nickname,
                                        token=token, uuid=uuid, javaArgv=argv, consoleEnable=consoleEnable)
        elif self.versionWidget.selectedItem.data.get("CoreType").lower() == "quilt":
            run = runner.QuiltLauncher(version, coreVersion, self.installFolder, self.javaPath, gameDir, nickname,
                                       token=token, uuid=uuid, javaArgv=argv, consoleEnable=consoleEnable)
        if run:
            if settings.getData("isHideForLaunch", True):
                if self.dil:
                    self.dil.close()
                if self.ui:
                    self.ui.hide()

            def show():
                self.ui.show()
                del self.runs[gameDir]

            tr = LauncherThread(self.MainObject)
            tr.finish.connect(show)
            tr.setParams(run, gameDir)
            tr.start()
            self.runs[gameDir] = tr

    def runBuild(self, version, coreVersion, gameDir, coretype):
        # version = self.versionWidget.selectedItem.data.get("minecraftVersion")
        # coreVersion = self.versionWidget.selectedItem.data.get("CoreVersion")
        # gameDir = self.versionWidget.selectedItem.data.get("path")
        if gameDir in self.runs:
            trans = memory.get("translate", {})
            self.showInfoDil("Run", trans.get("notAlltarnateStart", "Terminate?"))
            return

        nickname = self.profileWidget.get_current_index()
        if nickname is None or nickname == -1:
            self.showInfoDil("Nickname Error",
                             memory.get("translate", {}).get("NoSelectProfileErr", "Profile error!"))
            return
        nickname = self.profileWidget.profiles[nickname]["nickname"]
        print(nickname)
        if len(nickname) < 7:
            self.showInfoDil("Nickname Error",
                             memory.get("translate", {}).get("nicknameLongError", "Profile error!"))
            return
        uuid = settings.getData("uuid", "3f69c852b89645ca81e05f5952d9d8e9 ")
        token = settings.getData("token", "null")
        argv = [self.javaMemoryControlArg.format(memory=self.settingsWidget.MemorySpin.value()),
                "-Dminecraft.api.env=custom",
                "-Dminecraft.api.auth.host=https://invalid.invalid",
                "-Dminecraft.api.account.host=https://invalid.invalid",
                "-Dminecraft.api.session.host=https://invalid.invalid",
                "-Dminecraft.api.services.host=https://invalid.invalid"]
        print("Argv", argv)
        run = None
        consoleEnable = settings.getData("javaConsoleEnable", False)

        if coretype.lower() == "vanilla":
            run = runner.VanillaLauncher(version, self.installFolder, self.javaPath, gameDir, nickname, token=token,
                                         uuid=uuid, javaArgv=argv, consoleEnable=consoleEnable)
        elif coretype.lower() == "forge":
            run = runner.ForgeLauncher(version, coreVersion, self.installFolder, self.javaPath, gameDir, nickname,
                                       token=token, uuid=uuid, javaArgv=argv, consoleEnable=consoleEnable)
        elif coretype.lower() == "fabric":
            run = runner.FabricLauncher(version, coreVersion, self.installFolder, self.javaPath, gameDir, nickname,
                                        token=token, uuid=uuid, javaArgv=argv, consoleEnable=consoleEnable)
        elif coretype.lower() == "quilt":
            run = runner.QuiltLauncher(version, coreVersion, self.installFolder, self.javaPath, gameDir, nickname,
                                       token=token, uuid=uuid, javaArgv=argv, consoleEnable=consoleEnable)
        if run:
            def show():
                del self.runs[gameDir]
                self.checkRuns()

            tr = LauncherThread(self.MainObject)
            tr.finish.connect(show)
            tr.setParams(run, gameDir)
            tr.start()
            self.runs[gameDir] = tr

    def checkRuns(self):
        if not self.ui.isVisible() and "nogui" in sys.argv:
            if len(self.runs) == 0:
                self.close()

    def modsBuild(self):
        if self.versionWidget.selectedItem is None: return
        path = self.versionWidget.selectedItem.data.get("path")
        self.ui.setCurrentCentralIndex(self.modsDilIndex)
        self.modsDil.setPath(path)
        self.modsDil.refresh_mod_list()

    def openFolderBuild(self):
        if self.versionWidget.selectedItem is None: return
        os.startfile(self.versionWidget.selectedItem.data.get("path", "explorer"))

    def openFolderBuildVers(self):
        os.startfile(self.buildsPath)

    def loadFonts(self):
        try:
            font_id = QFontDatabase.addApplicationFont("./UI/fonts/minecraftTen.ttf")
            if font_id != -1:
                self.font_families = QFontDatabase.applicationFontFamilies(font_id)
            else:
                self.font_families = ["Simple"]
        except:
            self.font_families = ["Simple"]

    def loadLastNews(self):
        print(self.font_families)
        try:
            self.ui.main_area.loadHtml(f"<a href='{http_requests.minecraft_url}'>Download the latest news from"
                                       f" {http_requests.minecraft_url}</a>",
                                       QTCSS.SiteCss.replace("{custom}", f"'{self.font_families[0]}',"))
            self.newsList = http_requests.getJsonNews()
            self.ui.main_area.loadHtml(f"<h1>Minecraft news!</h1><br>{self.newsList[0].get('content_html', '')}"
                                       f"<br>{self.newsList[1].get('content_html', '')}"
                                       f"<br>{self.newsList[2].get('content_html', '')}",
                                       QTCSS.SiteCss.replace("{custom}", f"'{self.font_families[0]}',"))
        except:
            self.ui.main_area.loadHtml("<h1>Couldn't download the data!</h1>")

    def close(self, noExit=False):
        if len(self.runs) > 0:
            trans = memory.get("translate", {})
            res = self.ask_question("Close application", trans.get("whenCloseCloseAll", "Close or Hide?"),
                                    trans.get("Hide", "Hide"), trans.get("Close", "Close"))
            if res:
                self.ui.hide()
                return False
            elif res == False:
                pass
            else:
                return False

        for gameDir in self.runs:
            x: LauncherThread = self.runs.get(gameDir)
            process = x.run.procces
            if process:
                process = psutil.Process(process.pid)
                for child in process.children(recursive=True):
                    child.kill()
                process.kill()
            x.terminate()
        self.ui.hide()
        app.processEvents()
        time.sleep(0.5)
        if noExit:
            return True
        app.closeAllWindows()
        app.exit(0)
        sys.exit(0)


def setup_logging():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(log_dir, f"app_log_{timestamp}.log")

    log = open(log_file, "a", encoding="utf-8")

    sys.stdout = log
    sys.stderr = log
    print(f"Logs is writen in {log_file}")


def checkShortcutAndStart(argv):
    if "run" not in argv:
        return

    try:
        index = argv.index("run") + 1
        path = os.path.normpath(argv[index].replace("./", win.buildsPath.replace("./", os.getcwd()) + "/"))
        print(path)

        win.find_build_settings(win.buildsPath)

        data = next((b for b in win.buildVersions if os.path.normpath(b["path"]) == path), None)

        if not data:
            win.showInfoDil("Build", "Build do not exist!")
            return

        print(data)
        core_list = win.availdCores.get(data.get("CoreType", "").lower(), [])
        core = any(
            i["coreVersion"] == data["CoreVersion"] and i["minecraftVersion"] == data["minecraftVersion"] for i in
            core_list)

        if not core:
            win.showInfoDil("Core", "Core do not exist!")
            return

        win.runBuild(data["minecraftVersion"], data["CoreVersion"], data["path"], data["CoreType"])
        print("run")

    except (IndexError, KeyError) as e:
        print(f"Error: {e}")
        win.showInfoDil("Error", "Invalid build configuration!")


def handle_ping(packet):
    print("Handle ping")
    if packet.get("type", "") == "alt_start":
        if not "nogui" in packet.get("argv", []):
            win.ui.show()
            win.ui.setWindowState(Qt.WindowState.WindowActive)
        checkShortcutAndStart(packet.get("argv", []))


# setup_logging()
app.handle_packet = handle_ping
# app.setStyle("Fusion")

print("Logging to console ->")
mainStdout = sys.__stdout__
thisStdout = io.StringIO()
if not "debug" in sys.argv:
    sys.stdout = thisStdout
    sys.stderr = thisStdout
    if sys.platform == "win32":
        ctypes.windll.kernel32.FreeConsole()

client_socket = QTcpSocket()
client_socket.connectToHost("127.0.0.1", app.PORT)
data = {"argv": sys.argv, "type": "alt_start"}
if client_socket.waitForConnected(100):
    print("connected!")
    message = json.dumps(data)
    client_socket.write(message.encode())
    client_socket.flush()
    client_socket.waitForBytesWritten(1000)
    client_socket.disconnectFromHost()
    print("send:", data)
    sys.exit(0)
else:
    print("NoConnected!")

win = Main()
print(sys.argv, "argv")
if "end_update" in sys.argv:
    update_zip = "./update.zip"
    if os.path.exists(update_zip):
        dil = QDialog()
        dil.setStyleSheet(QTCSS.dil_dark)
        dil.setFixedSize(100, 50)
        dil.setWindowTitle("Update")
        dil.setWindowIcon(win.WindowIcon)

        v = QVBoxLayout(dil)
        lbl = QLabel(memory.get("translate", {}).get("finishingUpdate", "finishing..."))
        v.addWidget(lbl)

        close = QPushButton(memory.get("translate", {}).get("Close", "Close"))
        close.clicked.connect(dil.close)
        v.addWidget(close)
        close.setVisible(False)

        dil.show()
        app.processEvents()

        with zipfile.ZipFile(update_zip, 'r') as zip_ref:
            zip_ref.extract("updater.exe", "./")
            print("File `updater.exe` extracted.")

        os.remove(update_zip)
        print(f"{update_zip} removed.")

        lbl.setText(memory.get("translate", {}).get("finishedUpdate", "Update finished!"))
        close.setVisible(True)

        dil.exec()
    else:
        print("not found `update.zip`")

app.startServer()
print(sys.executable)

checkShortcutAndStart(sys.argv)

if not "nogui" in sys.argv:
    win.ui.show()
    app.processEvents()

if not win.checkFreeSpace():
    msg_box = QMessageBox()
    msg_box.setStyleSheet(QTCSS.dil_dark)
    msg_box.setWindowTitle("Warning")
    msg_box.setText("Free disk space is less than 5 GB! This may lead to errors about lack of space!")
    msg_box.setStandardButtons(QMessageBox.StandardButton.Yes)
    msg_box.exec()

app.processEvents()
if settings.getData("autoCheckUpdate", True):
    win.show_update_dialog(True)
app.exec()
