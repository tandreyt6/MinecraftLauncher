# Файл отвечает за классы такие как MinecraftInstaller, FabricInstaller, ForgeInstaller. Они нужны для установки
# майнкрафта необходимой версии
import subprocess
from datetime import datetime
from typing import List, TypedDict, Dict
import minecraft_launcher_lib
import minecraft_launcher_lib.natives
import os, sys

from minecraft_launcher_lib.types import FabricLoader, MinecraftVersionInfo, QuiltLoader

from functions.VersionErrors import VersionNotSupportedError


class MinecraftInstaller:
    def __init__(self, path: str = None, version: str = None, java=None):
        """
        Класс, нужен для загрузки ванильной версии майнкрафта со всеми необходимыми библиотеками!

        :param path: Путь до папки лаунчера, библиотек и тп;
        :param version: Версия майнкрафт, которая будет установленна!
        """
        self.java = java if java else "java"
        self.path = path
        self.version = version
        self.status = ""
        self.progress = 0
        self.max = 1
        self.callback = {
            "setStatus": self.setStatus,
            "setProgress": self.setProgress,
            "setMax": self.setMax,
        }

    def setStatus(self, status: str):
        self.status = status

    def setProgress(self, progress: int):
        self.progress = progress

    def setMax(self, max: int):
        self.max = max

    def install_version(self, forceInstall=False) -> bool:
        """
        Метод запускает установку версии майнкрафт, если такова не установлена!
        Возвращает True, если версия была установленна и False если изменений не последовало!

        :param forceInstall: Установить принудительно если True, Иначе будет проверка установки!

        :ivar self.status: Параметр, хронящий статус загрузки, а если быть конкретнее то статус файла.
        :ivar self.max: Параметр, хронящий максимальный прогресс.
        :ivar self.progress: Параметр, хронящий текущий прогресс.
        """
        installed_versions = minecraft_launcher_lib.utils.get_installed_versions(self.path)
        if not any(v['id'] == self.version for v in installed_versions) or forceInstall:
            minecraft_launcher_lib.install.install_minecraft_version(self.version, self.path, callback=self.callback)
            print(f"Версия Minecraft {self.version} успешно установлена!")
            return True
        print(f"Версия Minecraft {self.version} уже установлена.")
        return False

    @staticmethod
    def list_versions(onlyRelease=True) -> list[MinecraftVersionInfo]:
        """
        :param onlyRelease: Если True вернет только версии типом release, иначе все доступные!
        :return: list[MinecraftVersionInfo] Список версий Minecraft.
        """
        if not onlyRelease:
            return minecraft_launcher_lib.utils.get_version_list()
        return [_ for _ in minecraft_launcher_lib.utils.get_version_list() if _["type"] == "release"]


class FabricInstaller:
    def __init__(self, path: str = "./", version: str = "1.20.1", loaderVersion: str = "0.16.7", java=None):
        self.java = java if java else "java"
        self.path = path
        self.version = version
        self.loader = loaderVersion
        self.status = ""
        self.progress = 0
        self.max = 1
        self.callback = {
            "setStatus": self.setStatus,
            "setProgress": self.setProgress,
            "setMax": self.setMax,
        }

    def setStatus(self, status: str):
        self.status = status

    def setProgress(self, progress: int):
        self.progress = progress

    def setMax(self, max: int):
        self.max = max

    def install_version(self, forceInstall=False) -> bool:
        """
        Метод запускает установку версии майнкрафт, если такова не установлена!
        Возвращает True, если версия была установленна и False если изменений не последовало!
        :raises VersionNotSupportedError: Если ядро Fabric не поддерживает данную версию майнкрафт.

        :param forceInstall: Установить принудительно если True, Иначе будет проверка установки!

        :ivar self.status: Параметр, хронящий статус загрузки, а если быть конкретнее то статус файла.
        :ivar self.max: Параметр, хронящий максимальный прогресс.
        :ivar self.progress: Параметр, хронящий текущий прогресс.
        """
        if not minecraft_launcher_lib.fabric.is_minecraft_version_supported(self.version):
            raise VersionNotSupportedError(f"Fabric {self.loader} не поддерживает майнкрафт {self.version}!")
        if not os.path.exists(
                self.path +
                f"/versions/fabric-loader-{self.loader}-{self.version}/fabric-loader-{self.loader}-{self.version}.jar"
                .replace("\\", "/").replace("//", "/")) \
                or not os.path.exists(
                self.path +
                f"/versions/fabric-loader-{self.loader}-{self.version}/fabric-loader-{self.loader}-{self.version}.json"
                .replace("\\", "/").replace("//", "/")) \
                or forceInstall:

            minecraft_launcher_lib.fabric.install_fabric(self.version, self.path, self.loader, callback=self.callback, hasInstallVanilla=False, java=self.java)
            print(f"Fabric {self.loader} был установлен!")
            return True
        print("Изменений не внесено!")
        return False

    @staticmethod
    def list_versions(onlyStable: bool = False, currentVersion: str = None) -> list[FabricLoader]:
        """
        :param onlyStable: Если True вернет только stable версии, иначе все доступные!
        :param currentVersion: Фильтр
        для версии майнкрафт! Например если указать 1.20.1 то вернет список тех ядер, которые потдерживают данную
        версию
        :return: list[FabricLoader] Список версий ядер fabric!
        """
        if not onlyStable:
            return [_ for _ in minecraft_launcher_lib.fabric.get_all_loader_versions() if
                not currentVersion or minecraft_launcher_lib.fabric.is_minecraft_version_supported(currentVersion)]
        data = [_ for _ in minecraft_launcher_lib.fabric.get_all_loader_versions() if
                not currentVersion or minecraft_launcher_lib.fabric.is_minecraft_version_supported(currentVersion)]
        data = [_ for _ in data if _['stable']]
        return data


class ForgeInstaller:
    def __init__(self, path: str = "./", version: str = "1.20.1", loaderVersion: str = "0.16.7", java=None):
        self.java = java if java else "java"
        self.path = path
        self.version = version
        self.loader = loaderVersion
        self.status = ""
        self.progress = 0
        self.max = 1
        self.callback = {
            "setStatus": self.setStatus,
            "setProgress": self.setProgress,
            "setMax": self.setMax,
        }

    def setStatus(self, status: str):
        self.status = status

    def setProgress(self, progress: int):
        self.progress = progress

    def setMax(self, max: int):
        self.max = max

    def install_version(self, forceInstall: bool = False) -> bool:
        """
        Метод запускает установку версии майнкрафт, если такова не установлена!
        Возвращает True, если версия была установленна и False если изменений не последовало!
        :raises VersionNotSupportedError: Если ядро Forge не поддерживает данную версию майнкрафт.

        :param forceInstall: Установить принудительно если True, Иначе будет проверка установки!

        :ivar self.status: Параметр, хронящий статус загрузки, а если быть конкретнее то статус файла.
        :ivar self.max: Параметр, хронящий максимальный прогресс.
        :ivar self.progress: Параметр, хронящий текущий прогресс.
        """
        validate_versions = [_.split("-")[1] for _ in minecraft_launcher_lib.forge.list_forge_versions() if
                             _.split("-")[0] == self.version]
        if not self.loader in validate_versions:
            raise VersionNotSupportedError(f"Forge {self.loader} не поддерживает майнкрафт {self.version}!")
        if not os.path.exists(
                self.path + f"/versions/{self.version}-forge-{self.loader}/{self.version}-forge-{self.loader}.jar"
                .replace("\\", "/").replace("//", "/")) \
                or not os.path.exists(
                self.path + f"/versions/{self.version}-forge-{self.loader}/{self.version}-forge-{self.loader}.json"
                .replace("\\", "/").replace("//", "/")) \
                or forceInstall:
            minecraft_launcher_lib.forge.install_forge_version(self.version+"-"+self.loader, self.path, self.callback, hasInstallVanilla=False, java=self.java)
            print(f"Forge {self.loader} был установлен!")
            return True
        print("Изменений не внесено!")
        return False

    @staticmethod
    def list_versions(currentVersion: str = None) -> list[str]:
        """
        :param currentVersion: Фильтр
        для версии майнкрафт! Например если указать 1.20.1 то вернет список тех ядер, которые потдерживают данную
        версию
        :return: list[FabricLoader] Список версий ядер fabric!
        """
        data = [_ for _ in minecraft_launcher_lib.forge.list_forge_versions() if not currentVersion or _.split("-")[0]==currentVersion]
        return data


class QuiltInstaller:
    def __init__(self, path: str = "./", version: str = "1.20.1", loaderVersion: str = "0.26.4", java=None):
        self.java = java if java else "java"
        self.path = path
        self.version = version
        self.loader = loaderVersion
        self.status = ""
        self.progress = 0
        self.max = 1
        self.callback = {
            "setStatus": self.setStatus,
            "setProgress": self.setProgress,
            "setMax": self.setMax,
        }

    def setStatus(self, status: str):
        self.status = status

    def setProgress(self, progress: int):
        self.progress = progress

    def setMax(self, max: int):
        self.max = max

    def install_version(self, forceInstall=False) -> bool:
        """
        Метод запускает установку версии майнкрафт, если такова не установлена!
        Возвращает True, если версия была установленна и False если изменений не последовало!
        :raises VersionNotSupportedError: Если ядро Quilt не поддерживает данную версию майнкрафт.

        :param forceInstall: Установить принудительно если True, Иначе будет проверка установки!

        :ivar self.status: Параметр, хронящий статус загрузки, а если быть конкретнее то статус файла.
        :ivar self.max: Параметр, хронящий максимальный прогресс.
        :ivar self.progress: Параметр, хронящий текущий прогресс.
        """
        if not minecraft_launcher_lib.quilt.is_minecraft_version_supported(self.version):
            raise VersionNotSupportedError(f"Quilt {self.loader} не поддерживает майнкрафт {self.version}!")
        if not os.path.exists(
                self.path +
                f"/versions/quilt-loader-{self.loader}-{self.version}/quilt-loader-{self.loader}-{self.version}.jar"
                .replace("\\", "/").replace("//", "/"))\
                or not os.path.exists(
                self.path +
                f"/versions/quilt-loader-{self.loader}-{self.version}/quilt-loader-{self.loader}-{self.version}.json"
                .replace("\\", "/").replace("//", "/")) \
                or forceInstall:

            minecraft_launcher_lib.quilt.install_quilt(self.version, self.path, self.loader, callback=self.callback, java=self.java, hasInstallVanilla=False)
            print(f"Quilt {self.loader} был установлен!")
            return True
        print("Изменений не внесено!")
        return False

    @staticmethod
    def list_versions(currentVersion: str = None) -> list[QuiltLoader]:
        """
        :param currentVersion: Фильтр
        для версии майнкрафт! Например если указать 1.20.1 то вернет список тех ядер, которые потдерживают данную
        версию
        :return: list[FabricLoader] Список версий ядер Quilt!
        """
        data = [_ for _ in minecraft_launcher_lib.quilt.get_all_loader_versions() if
                not currentVersion or minecraft_launcher_lib.quilt.is_minecraft_version_supported(currentVersion)]
        return data

