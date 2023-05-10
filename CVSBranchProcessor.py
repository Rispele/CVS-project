import os
import CVSFileSystemAdapter


class CVSBranchProcessor:
    def __init__(self, rep):
        self._rep = rep
        self._files = CVSFileSystemAdapter.CVSFileSystemAdapter(rep)

    def get_head_branch(self):
        content = self._files.read_file('.cvs/HEAD')
        head_type, head_pointer = content.split(': ')
        if head_type != 'ref':
            return None
        else:
            return head_pointer.split('/')[2]

    def get_head_commit(self):
        content = self._files.read_file('.cvs/HEAD')
        head_type, head_pointer = content.split(': ')
        if head_type != 'ref':
            return head_pointer
        else:
            return None

    def get_branch_commit(self, branch):
        path = f'.cvs/refs/heads/{branch}'
        if not self._files.exist(path):
            return None

        return self._files.read_file(path)

    def set_branch_commit(self, branch, commit_hash):
        path = f'{self._rep}/.cvs/refs/heads/{branch}'

        with open(path, 'w') as f:
            f.write(commit_hash)
        pass
