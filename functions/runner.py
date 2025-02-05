# Файл отвечает за запуски клиента
import sys
import threading

import minecraft_launcher_lib
import subprocess
from minecraft_launcher_lib import fabric, forge, quilt, utils

class VanillaLauncher:
    def __init__(self, version, path=None, java="java", game_dir=None, username="Player", token=None, uuid="123e4567-e89b-12d3-a456-426614174000", server="0000000000000000000", port=None, javaArgv=[]):
        self.version = version
        self.path = path
        self.java = java
        self.game_dir = game_dir
        self.username = username
        self.token = token
        self.uuid = uuid if uuid else token
        self.server = server
        self.port = port
        self.procces = None
        self.javaArgv = javaArgv

    def run(self, inThread=True):
        def launch():
            options = {"username": self.username}

            if self.token:
                options["token"] = self.token
            if self.uuid:
                options["uuid"] = self.uuid
            if self.server:
                options["server"] = self.server
            if self.port:
                options["port"] = str(self.port)
            if self.java:
                options["executablePath"] = self.java
            if self.game_dir:
                options["gameDirectory"] = self.game_dir
            options["user_type"] = "mojang"
            options["launcherName"] = "MCLauncher"
            options["launcherVersion"] = "1.0"
            options["jvmArguments"] = self.javaArgv

            cmd = minecraft_launcher_lib.command.get_minecraft_command(self.version.split("-")[0], self.path, options)
            print(cmd)
            try:
                self.procces = subprocess.Popen(cmd)
                self.procces.wait()
            except Exception as e:
                print(f"Error launch minecraft client: {e}")

        if inThread:
            thread = threading.Thread(target=launch)
            thread.daemon = True
            thread.start()
        else:
            launch()


class FabricLauncher(VanillaLauncher):
    def __init__(self, version, fabric_version, path=None, java="java", game_dir=None, username="Player", token=None, uuid="123e4567-e89b-12d3-a456-426614174000", server=None,
                 port=None, javaArgv=[]):
        super().__init__(version, path, java, game_dir, username, token, uuid, server, port, javaArgv)
        self.fabric_version = fabric_version
        self.procces = None

    def run(self, inThread=True):
        def launch():
            options = {"username": self.username}
            if self.token:
                options["token"] = self.token
            if self.uuid:
                options["uuid"] = self.uuid
            if self.server:
                options["server"] = self.server
            if self.port:
                options["port"] = self.port
            if self.java:
                options["executablePath"] = self.java
            if self.game_dir:
                options["gameDirectory"] = self.game_dir
            options["user_type"] = "mojang"
            options["launcherName"] = "MCLauncher"
            options["launcherVersion"] = "1.0"
            options["jvmArguments"] = self.javaArgv

            cmd = minecraft_launcher_lib.command.get_minecraft_command(f"fabric-loader-{self.fabric_version}-{self.version}", self.path, options)
            print(cmd)
            try:
                self.procces = subprocess.Popen(cmd)
                self.procces.wait()
            except Exception as e:
                print(f"Error launch minecraft client: {e}")

        if inThread:
            thread = threading.Thread(target=launch)
            thread.daemon = True
            thread.start()
        else:
            launch()


class ForgeLauncher(VanillaLauncher):
    def __init__(self, version, forge_version, path=None, java="java", game_dir=None, username="Player", token=None, uuid="123e4567-e89b-12d3-a456-426614174000", server=None,
                 port=None, javaArgv=[]):
        super().__init__(version, path, java, game_dir, username, token, uuid, server, port, javaArgv)
        self.forge_version = forge_version
        self.procces = None

    def run(self, inThread=True):
        def launch():
            options = {"username": self.username}
            if self.token:
                options["token"] = self.token
            if self.uuid:
                options["uuid"] = self.uuid
            if self.server:
                options["server"] = self.server
            if self.port:
                options["port"] = self.port
            if self.java:
                options["executablePath"] = self.java
            if self.game_dir:
                options["gameDirectory"] = self.game_dir
            options["user_type"] = "mojang"
            options["launcherName"] = "MCLauncher"
            options["launcherVersion"] = "1.0"
            options["jvmArguments"] = self.javaArgv

            cmd = minecraft_launcher_lib.command.get_minecraft_command(
                f"{self.version}-forge-{self.forge_version}", self.path, options)
            print(cmd)
            try:
                self.procces = subprocess.Popen(cmd)
                self.procces.wait()
            except Exception as e:
                print(f"Error launch minecraft client: {e}")

        if inThread:
            thread = threading.Thread(target=launch)
            thread.daemon = True
            thread.start()
        else:
            launch()


class QuiltLauncher(VanillaLauncher):
    def __init__(self, version, quilt_version, path=None, java="java", game_dir=None, username="Player", token=None, uuid="123e4567-e89b-12d3-a456-426614174000", server=None,
                 port=None, javaArgv=[]):
        super().__init__(version, path, java, game_dir, username, token, uuid, server, port, javaArgv)
        self.quilt_version = quilt_version
        self.procces = None

    def run(self, inThread=True):
        def launch():
            options = {"username": self.username, "version": self.version}
            if self.token:
                options["token"] = self.token
            if self.uuid:
                options["uuid"] = self.uuid
            if self.server:
                options["server"] = self.server
            if self.port:
                options["port"] = self.port
            if self.java:
                options["executablePath"] = self.java
            if self.game_dir:
                options["gameDirectory"] = self.game_dir
            options["user_type"] = "mojang"
            options["launcherName"] = "MCLauncher"
            options["launcherVersion"] = "1.0"
            options["jvmArguments"] = self.javaArgv

            cmd = minecraft_launcher_lib.command.get_minecraft_command(
                f"quilt-loader-{self.quilt_version}-{self.version}", self.path, options)
            print(cmd)
            try:
                self.procces = subprocess.Popen(cmd)
                self.procces.wait()
            except Exception as e:
                print(f"Error launch minecraft client: {e}")

        if inThread:
            thread = threading.Thread(target=launch)
            thread.daemon = True
            thread.start()
        else:
            launch()


# vanilla_launcher = VanillaLauncher("1.12.2", "./minecraft/", username="Player123",
#                                    server="donator23.gamely.pro", port=20976)
# vanilla_launcher.run()
#
# fabric_launcher = FabricLauncher("1.20.1", "0.16.5", "./minecraft/", username="Player123")
# fabric_launcher.run()
#
# forge_launcher = ForgeLauncher("1.20.1", "47.1.19", "./minecraft/")
# forge_launcher.run()
#
# quilt_launcher = QuiltLauncher("1.20.1", "0.26.4", "./minecraft/", username="Player123")
# quilt_launcher.run()
#
# while 1:
#     pass