import shutil
import zipfile, os

p = r"pyinstaller"
os.system(p+" updater.spec")
shutil.copy("./dist/updater.exe", "./dist/Launcher/updater.exe")

def zip_folder(folder_path, zip_name):
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)

    print(f"`{zip_name}` has been created.")

folder_path = './dist/Launcher'
zip_name = './dist/update.zip'

zip_folder(folder_path, zip_name)