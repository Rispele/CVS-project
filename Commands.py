import abc
import os
import CVSIndex
import hashlib


class CVSCommand(abc.ABC):
    @abc.abstractmethod
    def __init__(self):
        self._type = ''

    @abc.abstractmethod
    def do(self):
        raise NotImplementedError

    pass


class InitCommand(CVSCommand):
    def __init__(self, path):
        self._type = 'init'
        self._path = path

    def do(self):
        if os.path.exists(self._path + '/.cvs'):
            print('Already exist')
            return

        os.mkdir(self._path + '/.cvs')
        os.mkdir(self._path + '/.cvs/objects')
        print('Initialized')
        pass

    pass


class AddCommand(CVSCommand):
    def __init__(self, rep, path):
        self._path = path
        self._rep = rep

    def do(self):
        path = f'{self._rep}/{self._path}'
        if os.path.isfile(path):
            self._add_file(path)
        else:
            for p in os.walk(path):
                if '.cvs' in p[0]:
                    continue

                p0 = p[0].replace('\\', '/')
                for f in p[2]:
                    self._add_file(f'{p0}/{f}')

    def _add_file(self, path):
        content = self._read_file(path)
        h = hashlib.sha1(content.encode("utf-8")).hexdigest()

        # blob file creation
        dir_path = f'{self._rep}/.cvs/objects/{h[:2]}'
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        with open(dir_path + f'/{h[2:]}', 'w') as f:
            f.truncate()
            f.write(content)

        index = CVSIndex.CVSIndex(self._rep)
        d = index.read_index()
        d[path] = h
        index.write_index(d)

    @staticmethod
    def _read_file(file_path):
        if os.path.exists(file_path):
            with open(file_path) as f:
                return f.read()
        else:
            raise Exception

    pass

