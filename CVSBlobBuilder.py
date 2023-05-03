import CVSHash
import os


class CVSBlobBuilder:
    def __init__(self, rep):
        self._rep = rep

    def build(self, content):
        h = CVSHash.get_cvs_hash(content)

        # blob file creation
        dir_path = f'{self._rep}/.cvs/objects/{h[:2]}'
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        with open(dir_path + f'/{h[2:]}', 'w') as f:
            f.truncate()
            f.write(content)

        return h
