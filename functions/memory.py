memory = {}

def put(key: object, value: object):
    memory[key] = value

def get(key: object, default: object=None) -> object:
    return memory.get(key, default)