import os
import sys
import win32com.client

def create_shortcut(target_path, shortcut_path, icon_path=None, arguments=""):
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(shortcut_path)
    shortcut.TargetPath = target_path  # Путь к исполняемому файлу или командному файлу
    shortcut.Arguments = arguments  # Аргументы, которые передаются при запуске
    shortcut.WorkingDirectory = os.path.dirname(target_path)  # Рабочая папка
    if icon_path:
        shortcut.IconLocation = icon_path.replace("/", "\\")
        print(shortcut.IconLocation)
    shortcut.Save()

# Пример использования
# exe_path = r"C:\Program Files\Java\jdk-17\bin\javaw.exe"  # Путь к исполняемому файлу
# shortcut_file = os.path.join(os.path.expanduser("~"), "Desktop", "MinecraftLauncher.lnk")  # Ярлык на рабочем столе
# icon_file = r"./UI/Icons/MinecraftIcon.ico"  # Путь к иконке
# command_args = '-jar "C:\\Path\\To\\MinecraftLauncher.jar"'  # Команда, которую будет выполнять ярлык
#
# create_shortcut(exe_path, shortcut_file, icon_file, command_args)