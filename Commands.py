import abc
import os

import CVSBlobBuilder
import CVSBranchProcessor
import CVSIndex
import CVSHash
import CVSTreeBuilder


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
        os.mkdir(self._path + '/.cvs/refs')
        os.mkdir(self._path + '/.cvs/refs/heads')
        with open(self._path + '/.cvs/HEAD', 'w') as f:
            f.write('ref: refs/heads/master')
        print('Initialized')
        pass

    pass


class AddCommand(CVSCommand):
    def __init__(self, rep, path=''):
        self._path = path
        self._rep = rep

    def do(self):
        if self._path == '':
            path = f'{self._rep}'
        else:
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
        # h = CVSHash.get_cvs_hash(content)

        # blob file creation
        blob_builder = CVSBlobBuilder.CVSBlobBuilder(self._rep)
        h = blob_builder.build(content)
        # dir_path = f'{self._rep}/.cvs/objects/{h[:2]}'
        # if not os.path.exists(dir_path):
        #     os.mkdir(dir_path)
        # with open(dir_path + f'/{h[2:]}', 'w') as f:
        #     f.truncate()
        #     f.write(content)

        # indexing
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


class CommitCommand(CVSCommand):
    def __init__(self, rep, message):
        self._rep = rep
        self._message = message
        self._tree_builder = CVSTreeBuilder.CVSTreeBuilder(rep)
        self._blob_builder = CVSBlobBuilder.CVSBlobBuilder(rep)
        self._branch_processor = CVSBranchProcessor.CVSBranchProcessor(rep)

    def do(self):
        tree, not_found = self._tree_builder.build()
        if len(not_found) != 0:
            print(f'Unable to find files: {list(not_found)}')
            return

        branch = self._branch_processor.get_head_branch()
        if branch is None:
            parent = self._branch_processor.get_head_commit()
        else:
            parent = self._branch_processor.get_branch_commit(branch)

        commit = f'tree {tree}\n' \
                 f'parent {parent}\n' \
                 f'\n' \
                 f'{self._message}'
        h = self._blob_builder.build(commit)
        self._branch_processor.set_branch_commit(branch, h)
        pass

    pass
