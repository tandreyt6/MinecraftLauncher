from PyInstaller.utils.hooks import collect_submodules, collect_data_files
from PyInstaller import config

main = "installer.py"
name = "InsAr5Con"

a = Analysis(
    [main],
    pathex=['.'],
    binaries=[],
    hookspath=[],
    runtime_hooks=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name=name,
    debug=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=True,
    icon="./UI/Icons/MinecraftIcon.ico"
)

