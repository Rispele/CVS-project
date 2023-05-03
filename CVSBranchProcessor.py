import os


class CVSBranchProcessor:
    def __init__(self, rep):
        self._rep = rep

    def get_head_branch(self):
        path = f'{self._rep}/.cvs/HEAD'
        with open(path) as f:
            content = f.read()
        head_type, head_pointer = content.split(': ')
        if head_type != 'ref':
            return None
        else:
            return head_pointer.split('/')[2]

    def get_head_commit(self):
        path = f'{self._rep}/.cvs/HEAD'
        with open(path) as f:
            content = f.read()
        head_type, head_pointer = content.split(': ')
        if head_type != 'ref':
            return head_pointer
        else:
            return None

    def get_branch_commit(self, branch):
        path = f'{self._rep}/.cvs/refs/heads/{branch}'
        if not os.path.exists(path):
            return None

        with open(path) as f:
            return f.read()
        pass

    def set_branch_commit(self, branch, commit_hash):
        path = f'{self._rep}/.cvs/refs/heads/{branch}'

        with open(path, 'w') as f:
            f.write(commit_hash)
        pass
