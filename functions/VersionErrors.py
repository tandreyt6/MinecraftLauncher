class VersionNotSupportedError(Exception):
    def __new__(cls, obj: object):
        return Exception(obj)
