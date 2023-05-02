import os.path


class CVSIndex:
    def __init__(self, rep):
        self._rep = rep

    def read_index(self):
        if os.path.exists(f'{self._rep}/.cvs/index'):
            with open(self._rep + '/.cvs/index', 'r') as f:
                index = f.read()
        else:
            index = ''

        d = {}
        for l in index.split('\n'):
            parts = l.split(' ')
            if len(parts) > 1:
                d[parts[0]] = parts[1]

        return d

    def write_index(self, d):
        with open(self._rep + '/.cvs/index', 'w') as f:
            f.truncate()
            for key, value in d.items():
                f.write(f'{key} {value}\n')