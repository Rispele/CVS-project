import os
import queue


class CVSFileSystemAdapter:
    def __init__(self, rep):
        self._rep = rep
        pass

    def load_commit(self, object_hash):
        to_open = queue.Queue()
        to_open.put(('commit', f'.cvs\\objects\\{object_hash[:2]}\\{object_hash[2:]}', ''))
        while not to_open.empty():
            obj_type, path, to_write_path = to_open.get()
            content = self.read_file(path)
            if obj_type == 'commit':
                obj_hash = content.split('\n')[0].split(' ')[1]
                path = f'.cvs\\objects\\{obj_hash[:2]}\\{obj_hash[2:]}'
                to_open.put(('tree', path, ''))
                continue
            elif obj_type == 'tree':
                for record in content.split('\n'):
                    rec_type, obj_hash, name = record.split(' ')
                    path = f'.cvs\\objects\\{obj_hash[:2]}\\{obj_hash[2:]}'
                    to_open.put((rec_type, path, f'{to_write_path}\\{name}'))
            elif obj_type == 'blob':
                self.write(to_write_path, content)
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

    def read_file(self, path):
        path = self.get_full_path(path)
        with open(path) as f:
            content = f.read()
        return content

    def get_all_filepaths(self, path, exclude_cvs=True):
        for p in os.walk(self.get_full_path(path)):
            if ('.cvs' in p[0]) and exclude_cvs:
                continue

            p0 = p[0]
            if p0 == self._rep:
                for f in p[2]:
                    yield f'{self._rep}\\{f}'
            else:
                for f in p[2]:
                    yield f'{p0}\\{f}'

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
        if path == '':
            return self._rep
        return f'{path}'

    pass
