import os
import shutil

if os.path.exists("./dist/Launcher"):
    shutil.rmtree("./dist/Launcher")

p = r"C:\Users\vovbo\appdata\local\packages\pythonsoftwarefoundation.python.3.11_qbz5n2kfra8p0\localcache\local-packages\python311\Scripts\pyinstaller.exe"
os.system(p+" main.spec")

shutil.copytree("./UI/fonts", "./dist/Launcher/UI/fonts")
shutil.copytree("./UI/Icons", "./dist/Launcher/UI/Icons")

os.system(p+" install.spec")

shutil.copy("./dist/InsAr5Con.exe", "./dist/Launcher/InsAr5Con.exe")