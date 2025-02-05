from PyInstaller.utils.hooks import collect_submodules, collect_data_files
from PyInstaller import config

main = "main.py"
name = "Launcher"

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
    [],
    exclude_binaries=True,
    name=name,
    debug=False,
    bootloader_ignore_signals=True,
    strip=False,
    upx=False,
    console=True,
    icon='./UI/Icons/MinecraftIcon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name=name
)