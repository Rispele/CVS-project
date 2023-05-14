import os
import queue


class CVSFileSystemAdapter:
    def __init__(self, rep):
        self._rep = rep

        pass

    def load_commit(self, object_hash):
        to_open = queue.Queue()
        to_open.put(('commit', object_hash, ''))
        indexed = {}
        while not to_open.empty():
            obj_type, obj_hash, to_write_path = to_open.get()
            content = self.read_file(f'.cvs\\objects\\{obj_hash[:2]}\\{obj_hash[2:]}')
            if obj_type == 'commit':
                obj_hash = content.split('\n')[0].split(' ')[1]
                to_open.put(('tree', obj_hash, ''))
                continue
            elif obj_type == 'tree':
                for record in content.split('\n'):
                    rec_type, obj_hash, name = record.split(' ')
                    to_open.put((rec_type, obj_hash, os.path.join(to_write_path, name)))
            elif obj_type == 'blob':
                self.write(to_write_path, content)
                indexed[self.get_full_path(to_write_path)] = obj_hash
        return indexed
        pass

    def write(self, path, content):
        path = self.get_full_path(path)
        with open(path, 'w') as f:
            f.write(content)
        pass

    def mkdir(self, dir_path):
        parts = dir_path.split('\\')
        for i in range(1, parts):
            dir = '\\'.join(parts[:i])
            if not self.exist(dir):
                os.mkdir(dir)
        pass

    def remove(self, path):
        os.remove(os.path.join(self._rep, path))
        pass

    def read_file(self, path):
        path = self.get_full_path(path)

        with open(path, errors='ignore') as f:
            content = f.read()
        return content

    def get_all_filepaths(self, path, exclude_cvs=True):
        for p in os.walk(self.get_full_path(path)):
            if ('.cvs' in p[0]) and exclude_cvs:
                continue

            p0 = p[0]
            if p0 == self._rep:
                for f in p[2]:
                    yield f
            else:
                p0 = p0[(p0.index('\\') + 1):]
                for f in p[2]:
                    yield os.path.join(p0, f)

    def get_object_path(self, object_hash):
        for p in self.get_all_filepaths(f'.cvs\\objects', exclude_cvs=False):
            parts = p.split('\\')
            if object_hash in parts[-1]:
                yield p, f'{parts[-2]}{parts[-1]}'
        return None

    def exist(self, path):
        path = self.get_full_path(path)
        return os.path.exists(path)

    def is_file(self, path):
        return os.path.isfile(f'{self._rep}\\{path}')

    def is_dir(self, path):
        return os.path.isdir(f'{self._rep}\\{path}')

    def get_full_path(self, path):
        return os.path.join(self._rep, path)

    pass
