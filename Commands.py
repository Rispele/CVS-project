import abc
import os
import CVSBlobBuilder
import CVSBranchProcessor
import CVSIndex
import CVSTreeBuilder
import CVSFileSystemAdapter
from datetime import datetime


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

        os.mkdir(self._path + '\\.cvs')
        os.mkdir(self._path + '\\.cvs\\objects')
        os.mkdir(self._path + '\\.cvs\\refs')
        os.mkdir(self._path + '\\.cvs\\refs\\heads')
        os.mkdir(self._path + '\\.cvs\\refs\\tags')
        with open(self._path + '\\.cvs\\HEAD', 'w') as f:
            f.write('ref: refs/heads/master')
        with open(self._path + '\\.cvs\\LOG', 'w') as f:
            f.write('List of changed files and time when added/changed:\n')
        with open(self._path + '\\.cvs\\COMMITLOG', 'w') as f:
            f.write('Project commits:\n')
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
        if not self._files.is_file(self._path) and not self._files.is_dir(self._path):
            print(f'File or directory \'{self._path}\' does not exist')
        elif self._files.is_file(self._path):
            self._add_file(self._path)
            print(f'File \'{self._files.get_full_path(self._path)}\' was added')
        else:
            for p in self._files.get_all_filepaths(self._path):
                self._add_file(p)
            print(f'Directory \'{self._files.get_full_path(self._path)}\' and all files in it were added')

    def _add_file(self, path):
        content = self._files.read_file(path)

        h = self._blob_builder.build(content)

        # indexing and logging
        index = CVSIndex.CVSIndex(self._rep)
        d = index.read_index()
        if self._files.get_full_path(path) in d.keys() and not h == d[self._files.get_full_path(path)]:
            with open(self._rep + '\\.cvs\\LOG', 'a') as f:
                f.truncate()
                f.write(f'{datetime.now().strftime("%d/%m/%y %H:%M:%S")}: CHANGED -- {self._files.get_full_path(path)}'\
                        f' -- {d[self._files.get_full_path(path)]} -> {h}\n')
                d[self._files.get_full_path(path)] = h
                index.write_index(d)
        elif self._files.get_full_path(path) not in d.keys():
            d[self._files.get_full_path(path)] = h
            index.write_index(d)
            with open(self._rep + '\\.cvs\\LOG', 'a') as f:
                f.truncate()
                print(f'File \'{self._files.get_full_path(path)}\' was added')
                f.write(f'{datetime.now().strftime("%d/%m/%y %H:%M:%S")}: ADDED -- {self._files.get_full_path(path)}' \
                        f' -- {d[self._files.get_full_path(path)]}\n')
        else:
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
        changes = []
        tree, not_found = self._tree_builder.build()
        if len(not_found) != 0:
            print(f'Removed files: {list(not_found)}')
        for item in list(not_found):
            changes.append(f'File {item} was removed')

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

        with open(self._rep + '\\.cvs\\COMMITLOG', 'r') as f:
            text = f.read()

        with open(self._rep + '\\.cvs\\COMMITLOG', 'a') as f:
            f.truncate()
            f.write(f'Commit {h} -- {datetime.now().strftime("%d/%m/%y %H:%M:%S")} -- message: \'{self._message}\':\n')
            if parent is not None:
                previous_indexes = text[text.index(parent):]
            index = CVSIndex.CVSIndex(self._rep)
            d = index.read_index()
            for file in d.keys():
                if parent is not None and d[file] not in previous_indexes:
                    if file in previous_indexes:
                        print(f'{file} changed')
                        changes.append(f'File {file} changed')
                    else:
                        print(f'{file} added')
                        changes.append(f'File {file} added')
                if parent is None:
                    print(f'{file} added')
                    changes.append(f'File {file} added')
                f.write(f'{file} {d[file]}\n')
            for record in changes:
                f.write(f'-> {record}\n')
        print(f'Commit \'{h}\' has been deployed with message: \'{self._message}\'')
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
        self._index = CVSIndex.CVSIndex(rep)
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
                indexed = self._files.load_commit(commit_hash)
                self._branch_processor.set_head_to_branch(self._to)
        else:
            indexed = self._files.load_commit(commit_hash[1])
            self._branch_processor.set_head_to_commit(commit_hash[1])

        #reload index
        cur_index = self._index.read_index()
        for key, value in cur_index.items():
            if key in indexed.keys() and cur_index[key] == indexed[key]:
                continue
            os.remove(key)
        self._index.write_index(indexed)
        pass

    def _get_commit(self):
        fitting_objects = list(self._files.get_object_path(self._to))
        if len(fitting_objects) > 0:
            return fitting_objects[0]
        return None

    def _get_branch_commit(self):
        path = f'.cvs\\refs\\heads\\{self._to}'
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
        branch_path = f'.cvs\\refs\\heads\\{self._name}'
        branch = self._branch_processor.get_head_branch()
        commit = ''
        if branch is None:
            commit = self._branch_processor.get_head_commit()
        else:
            commit = self._branch_processor.get_branch_commit(branch)
        self._files.write(branch_path, commit)
        print(f'Branch {self._name} has been successfully built')
        pass

    def remove_branch(self):
        if self._branch_processor.get_head_branch() == self._name:
            commit = self._branch_processor.get_branch_commit(self._name)
            self._branch_processor.set_head_to_commit(commit)
        self._files.remove(f'.cvs/refs/heads/{self._name}')
        pass
    pass


class CreateTagCommand(CVSCommand):
    def __init__(self, rep, name, message=''):
        self._rep = rep
        self._name = name
        self._message = message
        self._files = CVSFileSystemAdapter.CVSFileSystemAdapter(rep)
        self._branch_processor = CVSBranchProcessor.CVSBranchProcessor(rep)
        pass

    def __call__(self, *args, **kwargs):
        self._do()
        pass

    def _do(self):
        tag_path = f'.cvs\\refs\\tags\\{self._name}'
        branch = self._branch_processor.get_head_branch()
        commit = ''
        if branch is None:
            commit = self._branch_processor.get_head_commit()
        else:
            commit = self._branch_processor.get_branch_commit(branch)

        self._files.write(tag_path, f'{commit}\n{self._message}')
        print(f'Tag {self._name} has been successfully added with message: \'{self._message}\'')
        pass
    pass
