import os


class CVSFileSystemAdapter:
    def __init__(self, rep):
        self._rep = rep
        pass

    def read_file(self, path):
        path = self.get_full_path(path)
        with open(path) as f:
            content = f.read()
        return content

    def get_all_filepaths(self, path, exclude_cvs=True):
        for p in os.walk(self.get_full_path(path)):
            if ('.cvs' in p[0]) and exclude_cvs:
                continue

            p0 = p[0].replace('\\', '/')
            if p0 == self._rep:
                for f in p[2]:
                    yield f'{f}'
            else:
                p0 = p0[(p0.find('/') + 1):]
                for f in p[2]:
                    yield f'{p0}/{f}'

    def get_object_path(self, object_hash):
        for p in self.get_all_filepaths(f'.cvs/objects', exclude_cvs=False):
            parts = p.split('/')
            if object_hash in parts[-1]:
                return '/'.join(parts[1:]), f'{parts[-2]}{parts[-1]}'
        return None

    def exist(self, path):
        path = self.get_full_path(path)
        return os.path.exists(path)

    def is_file(self, path):
        return os.path.isfile(f'{self._rep}/{path}')

    def get_full_path(self, path):
        if path == '':
            return self._rep
        return f'{self._rep}/{path}'

    pass
