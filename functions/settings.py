import json
import os

settings = {}
path = "./settings.json"

def setPath(p: str):
    global path
    path = p

def load(p="./settings.json"):
    global settings
    setPath(p)
    if not os.path.exists(p): return
    with open(path, "r", encoding="utf-8") as file:
        settings = json.load(file)


def setData(key, value):
    settings[key] = value
    with open(path, "w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)


def getData(key, default=None):
    return settings.get(key, default)
