import os
import sys
import requests
import shutil
import subprocess
from zipfile import ZipFile
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QProgressBar, QLabel

# os.chdir("./test/")

GITHUB_REPO = 'tandreyt6/MinecraftLauncher'
CURRENT_VERSION = '1.2.1'
IGNORE_FILES = ["updater.exe"]

translations = {
    'en': {
        'ready_to_update': 'Ready for update.',
        'checking_updates': 'Checking for updates...',
        'downloading': 'Downloading: {downloaded_mb} MB of {total_mb} MB',
        'version_match': 'Versions match, no update required.',
        'update_completed': 'Download completed!',
        'no_files_found': 'No files found to download.',
        'launching_launcher': 'Launching Launcher.exe...',
    },
    'ru': {
        'ready_to_update': 'Готов к обновлению.',
        'checking_updates': 'Проверка обновлений...',
        'downloading': 'Загружается: {downloaded_mb} МБ из {total_mb} МБ',
        'version_match': 'Версии совпадают, обновление не требуется.',
        'update_completed': 'Загрузка завершена!',
        'no_files_found': 'Файлы для загрузки не найдены.',
        'launching_launcher': 'Запуск Launcher.exe...',
    }
}

language = sys.argv[1] if len(sys.argv) > 1 else 'en'
translations_used = translations.get(language, translations['en'])

def get_latest_release():
    url = f'https://api.github.com/repos/{GITHUB_REPO}/releases/latest'
    response = requests.get(url)
    if response.status_code == 200:
        release = response.json()
        return release['tag_name'], release['assets']
    else:
        print('error get last updates.')
        return None, None

def download_and_update(assets, progress_callback):
    update_asset = None
    for asset in assets:
        print(f'File: {asset["name"]}, URL: {asset["browser_download_url"]}')
        if asset["name"] == "update.zip":
            update_asset = asset
            break
    if not update_asset:
        print(translations_used['no_files_found'])
        return
    download_url = update_asset['browser_download_url']
    print(f'Downloading {update_asset["name"]}...')
    response = requests.get(download_url, stream=True)
    if response.status_code == 200:
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        total_size_mb = total_size / (1024 * 1024)
        with open(update_asset['name'], 'wb') as f:
            for data in response.iter_content(chunk_size=1024):
                downloaded_size += len(data)
                f.write(data)
                progress_callback(downloaded_size, total_size)
        downloaded_size_mb = downloaded_size / (1024 * 1024)
        print(f'File {update_asset["name"]} has been downloaded. File size: {downloaded_size_mb:.2f} MB.')
        if update_asset['name'].endswith('.zip'):
            with ZipFile(update_asset['name'], 'r') as zip_ref:
                zip_ref.extractall('.')
            print(f'File {update_asset["name"]} extracted.')
    else:
        print(f'Error download file {update_asset["name"]}')

def launch_launcher():
    launcher_path = "Launcher.exe"
    if os.path.exists(launcher_path):
        print(translations_used['launching_launcher'])
        subprocess.Popen([launcher_path, "end_update", "debug"])
        print("Launcher.exe is started.")
        os._exit(0)

class UpdateThread(QThread):
    progress = pyqtSignal(int, int)
    finished_update = pyqtSignal(str)
    def run(self):
        latest_version, assets = get_latest_release()
        if latest_version is None:
            self.finished_update.emit("error get updates.")
            return
        print(f'Last version: {latest_version}')
        if True:
            print('update...')
            if assets:
                download_and_update(assets, self.update_progress)
            else:
                print(translations_used['no_files_found'])
            self.finished_update.emit(translations_used['update_completed'])
            launch_launcher()

    def update_progress(self, downloaded, total):
        if total == 0:
            progress_value = 100
        else:
            progress_value = int((downloaded / total) * 100)
        self.progress.emit(downloaded, total)

class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Minecraft Launcher Updater')
        self.setMinimumSize(400, 200)
        self.setFixedSize(self.minimumSize())
        self.layout = QVBoxLayout()
        self.status_label = QLabel(translations_used['ready_to_update'])
        self.layout.addWidget(self.status_label)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.layout.addWidget(self.progress_bar)
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)
        self.update_thread = UpdateThread()
        self.update_thread.progress.connect(self.on_progress)
        self.update_thread.finished_update.connect(self.on_finished_update)
        self.start_update()
    def start_update(self):
        self.status_label.setText(translations_used['checking_updates'])
        self.progress_bar.setValue(0)
        self.update_thread.start()
    def on_progress(self, downloaded, total):
        if total == 0:
            progress = 100
        else:
            progress = int((downloaded / total) * 100)
        self.progress_bar.setValue(progress)
        downloaded_mb = downloaded / (1024 * 1024)
        total_mb = total / (1024 * 1024)
        self.status_label.setText(translations_used["downloading"].format(downloaded_mb=f"{downloaded_mb:.1f}", total_mb=f"{total_mb:.1f}"))
    def on_finished_update(self, message):
        self.status_label.setText(message)

dil_dark = """
QWidget {
    background-color: #2b2b2b;
    color: #d3d3d3;
    font-family: Arial, sans-serif;
}

QLabel {
    font-size: 14px;
    color: #d3d3d3;
}

QProgressBar {
    border: 2px solid #3a3a3a;
    border-radius: 5px;
    background-color: #444;
    text-align: center;
    height: 25px;
}

QProgressBar::chunk {
    background-color: #a1d68b;
    width: 20px;
    margin: 0px;
}
"""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(dil_dark)
    window = AppWindow()
    window.show()
    app.exec()
