import os
import shutil
import zipfile

if os.path.exists("./dist/Launcher"):
    shutil.rmtree("./dist/Launcher")

p = r"C:\Users\vovbo\appdata\local\packages\pythonsoftwarefoundation.python.3.11_qbz5n2kfra8p0\localcache\local-packages\python311\Scripts\pyinstaller.exe"
os.system(p+" main.spec")

shutil.copytree("./UI/fonts", "./dist/Launcher/UI/fonts")
shutil.copytree("./UI/Icons", "./dist/Launcher/UI/Icons")

os.system(p+" install.spec")

shutil.copy("./dist/InsAr5Con.exe", "./dist/Launcher/InsAr5Con.exe")

def zip_folder(folder_path, zip_name):
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)

    print(f"{zip_name} has been created.")

folder_path = './dist/Launcher'
zip_name = './dist/update.zip'

zip_folder(folder_path, zip_name)