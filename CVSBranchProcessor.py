import os
import CVSFileSystemAdapter


class CVSBranchProcessor:
    def __init__(self, rep):
        self._rep = rep
        self._files = CVSFileSystemAdapter.CVSFileSystemAdapter(rep)

    def get_branch_list(self):
        branches_path = self._files.get_all_filepaths(
            os.path.join('.cvs', 'refs', 'heads'),
            False)
        for path in branches_path:
            yield os.path.split(path)[-1]
        pass

    def get_head_branch(self):
        content = self._files.read_file(os.path.join('.cvs', 'HEAD'))
        head_type, head_pointer = content.split(': ')
        if head_type != 'ref':
            return None
        else:
            return head_pointer.split('/')[2]

    def get_head_commit(self):
        content = self._files.read_file(os.path.join('.cvs', 'HEAD'))
        head_type, head_pointer = content.split(': ')
        if head_type != 'ref':
            return head_pointer
        else:
            return None

    def get_branch_commit(self, branch):
        path = os.path.join('.cvs', 'refs', 'heads', branch)
        if not self._files.exist(path):
            return None

        return self._files.read_file(path)

    def set_branch_commit(self, branch, commit_hash):
        self._files.write(os.path.join('.cvs', 'refs', 'heads', branch), commit_hash)

        pass

    def set_head_to_commit(self, commit):
        self._files.write(os.path.join('.cvs', 'HEAD'), f'obj: {commit}')
        pass

    def set_head_to_branch(self, branch):
        self._files.write(os.path.join('.cvs', 'HEAD'), f'ref: refs/heads/{branch}')
        pass


