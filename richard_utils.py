

class RichardUtils:
    @staticmethod
    def set_property(dictionary: dict, path: list, value) -> None:
        for location in path[:-1]:
            dictionary = dictionary.setdefault(location, {})
        dictionary[path[-1]] = value

    @staticmethod
    def access_property(dictionary: dict, path: list):
        pointer = dictionary

        for location in path:
            if location in pointer:
                pointer = pointer[location]
            else:
                raise Exception("Incorrect path: {path}".format(path=path))
        return pointer

    @staticmethod
    def check_target_exists(dictionary: dict, path: list) -> bool:
        pointer = dictionary
        for location in path:
            if location not in pointer:
                return False
        return True
