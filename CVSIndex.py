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
            if len(line) >= 40:
                index_dict[line[:-41]] = line[-40:]
        return index_dict

    def write_index(self, d):
        with open(self._rep + '\\.cvs\\index', 'w') as f:
            f.truncate()
            for key, value in d.items():
                f.write(f'{key} {value}\n')
