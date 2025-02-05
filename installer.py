import os
import traceback

from functions import installer
import sys
class items:
    def __init__(self, path, game_version, core_version, coreType, java):
        self.installFolder = path
        self.game_version = game_version
        self.core_version = core_version
        self.coreType = coreType
        self.java = java

def installCore(item: items):
    print(item.game_version, "|", item.core_version, "|",
          item.coreType)
    if item.coreType.lower() == "vanilla":
        mineinstaller = installer.MinecraftInstaller(item.installFolder, item.game_version, java=item.java)
    elif item.coreType.lower() == "forge":
        mineinstaller = installer.ForgeInstaller(item.installFolder, item.game_version,
                                                 item.core_version, java=item.java)
    elif item.coreType.lower() == "fabric":
        mineinstaller = installer.FabricInstaller(item.installFolder, item.game_version,
                                                  item.core_version, java=item.java)
    elif item.coreType.lower() == "quilt":
        mineinstaller = installer.QuiltInstaller(item.installFolder, item.game_version,
                                                 item.core_version, java=item.java)
    else:
        raise ValueError(f"Core type {str(item.coreType)} do not exist!")

    def setProgress(e):
        mineinstaller.setProgress(e)
        print(f"{mineinstaller.status} - {str(mineinstaller.progress)}/{str(mineinstaller.max + 1)}")

    mineinstaller.callback["setProgress"] = setProgress

    mineinstaller.install_version(True)

try:
    argv = sys.argv.copy()
    argv.pop(0)
    item = items(
        path=argv[0],
        game_version=argv[1],
        core_version=argv[2],
        coreType=argv[3],
        java=argv[5]
    )
    os.system(f"title \"Load minecraft {argv[1]} {argv[3]} {argv[2]}\"")
    isClose = bool(argv[4])
    installCore(item)
    if not isClose:
        os.system("pause")
    sys.exit(0)
except Exception as e:
    traceback.print_exception(e)
    os.system("pause")