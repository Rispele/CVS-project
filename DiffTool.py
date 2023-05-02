import difflib


# TODO Крч, это пока что заглушка, наверное нужно будет свой алгос сделать
#  у тебя дин прога только пройдет, так что замути эту парашу как будет
#  время


class DiffTool:
    def __init__(self):
        self._differ = difflib.Differ(linejunk=None, charjunk=None)

    def difference(self, from_str, to_str):
        return self._differ.compare(from_str, to_str)
