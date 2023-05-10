import abc
import os
import CVSBlobBuilder
import CVSBranchProcessor
import CVSIndex
import CVSTreeBuilder
import CVSFileSystemAdapter


class CVSCommand(abc.ABC):
    @abc.abstractmethod
    def __init__(self):
        self._type = ''

    @abc.abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def _do(self):
        raise NotImplementedError

    pass


class InitCommand(CVSCommand):
    def __init__(self, path):
        self._type = 'init'
        self._path = path

    def __call__(self, *args, **kwargs):
        self._do()

    def _do(self):
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
        self._files = CVSFileSystemAdapter.CVSFileSystemAdapter(rep)
        self._blob_builder = CVSBlobBuilder.CVSBlobBuilder(rep)

    def __call__(self, *args, **kwargs):
        self._do()

    def _do(self):
        if self._files.is_file(self._path):
            self._add_file(self._files.get_full_path(self._path))
        else:
            for p in self._files.get_all_filepaths(self._path):
                self._add_file(p)

    def _add_file(self, path):
        content = self._files.read_file(path)

        h = self._blob_builder.build(content)

        # indexing
        index = CVSIndex.CVSIndex(self._rep)
        d = index.read_index()
        d[self._files.get_full_path(path)] = h
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

    def __call__(self, *args, **kwargs):
        self._do()

    def _do(self):
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
        if branch is None:
            self._branch_processor.set_head_to_commit(h)
            pass
        self._branch_processor.set_branch_commit(branch, h)
        pass

    pass


class CheckoutCommand(CVSCommand):

    def __init__(self, rep, to):
        self._rep = rep
        self._to = to
        self._files = CVSFileSystemAdapter.CVSFileSystemAdapter(rep)
        self._branch_processor = CVSBranchProcessor.CVSBranchProcessor(rep)
        pass

    def __call__(self, *args, **kwargs):
        self._do()

    def _do(self):
        commit_hash = self._get_commit()
        if commit_hash is None:
            commit_hash = self._get_branch_commit()
            if commit_hash is None:
                raise Exception(f'Unable to find {commit_hash}')
            else:
                self._branch_processor \
                    .set_head_to_commit(commit_hash)
                self._files.load_commit(commit_hash)
                self._branch_processor.set_head_to_branch(self._to)
        else:
            self._branch_processor\
                .set_head_to_commit(commit_hash[1])
            self._files.load_commit(commit_hash[1])
            self._branch_processor.set_head_to_commit(commit_hash[1])
        pass

    def _get_commit(self):
        fitting_objects = list(self._files.get_object_path(self._to))
        if len(fitting_objects) > 0:
            return fitting_objects[0]
        return None

    def _get_branch_commit(self):
        path = f'.cvs/refs/heads/{self._to}'
        if not self._files.exist(path):
            return None

        return self._files.read_file(path)

    pass


class BranchCommand(CVSCommand):

    def __init__(self, rep, name):
        self._rep = rep
        self._name = name
        self._files = CVSFileSystemAdapter.CVSFileSystemAdapter(rep)
        self._branch_processor = CVSBranchProcessor.CVSBranchProcessor(rep)
        pass

    def __call__(self, *args, **kwargs):
        self._do()
        pass

    def _do(self):
        branch_path = f'.cvs/refs/heads/{self._name}'
        branch = self._branch_processor.get_head_branch()
        commit = ''
        if branch is None:
            commit = self._branch_processor.get_head_commit()
        else:
            commit = self._branch_processor.get_branch_commit(branch)
        self._files.write(branch_path, commit)
        pass