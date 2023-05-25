import CVSHash
import os


class CVSBlobBuilder:
    def __init__(self, rep):
        self._rep = rep

    def build(self, content):
        obj_hash = CVSHash.get_cvs_hash(content)

        # blob file creation
        dir_path = os.path.join(self._rep, '.cvs', 'objects', obj_hash[:2])
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        with open(os.path.join(dir_path, obj_hash[2:]), 'w') as f:
            f.truncate()
            f.write(content)

        return obj_hash
