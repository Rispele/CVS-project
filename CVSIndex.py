import os.path


class CVSIndex:
    def __init__(self, rep):
        self._rep = rep

    def read_index(self):
        if os.path.exists(f'{self._rep}\\.cvs\\index'):
            with open(self._rep + '\\.cvs\\index', 'r') as f:
                index = f.read()
        else:
            index = ''

        index_dict = {}
        for line in index.split('\n'):
            parts = line.split(' ')
            if len(parts) > 1:
                index_dict[parts[0].replace("_", " ")] = parts[1]

        return index_dict

    def write_index(self, d):
        with open(self._rep + '\\.cvs\\index', 'w') as f:
            f.truncate()
            for key, value in d.items():
                f.write(f'{key.replace(" ", "_")} {value}\n')
