import os
import shutil
import zipfile

if os.path.exists("./dist/Launcher"):
    shutil.rmtree("./dist/Launcher")

p = r"pyinstaller"
os.system(p+" main.spec")

shutil.copytree("./UI/fonts", "./dist/Launcher/UI/fonts")
shutil.copytree("./UI/Icons", "./dist/Launcher/UI/Icons")

os.system(p+" install.spec")

shutil.copy("./dist/InsAr5Con.exe", "./dist/Launcher/InsAr5Con.exe")

try: import gitbuild
except: print("no git`s build!")