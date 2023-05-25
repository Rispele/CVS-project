import os

import CVSBlobBuilder
import CVSIndex


class CVSTreeBuilder:
    def __init__(self, rep):
        self._rep = rep

        index = CVSIndex.CVSIndex(rep)
        self._index = index.read_index()
        self._indexed = set(self._index.keys())
        self._not_found = set(self._index.keys())
        self._blob_builder = CVSBlobBuilder.CVSBlobBuilder(rep)

    def build(self):
        return self._build(self._rep)[0], self._not_found

    def _build(self, path):
        tree = []
        for single_path in os.listdir(path):
            if '.cvs' in single_path:
                continue

            to_open_path = os.path.join(path, single_path)
            if os.path.isfile(to_open_path):
                if to_open_path in self._indexed:
                    self._not_found.remove(to_open_path)
                    tree.append(
                        f'blob {self._index[to_open_path]} {single_path}')
            else:
                obj_hash, is_empty = self._build(to_open_path)
                if is_empty:
                    continue
                tree.append(f'tree {obj_hash} {single_path}')

        if len(tree) == 0:
            return '', True

        content = ''
        for index_record in tree:
            content += index_record + '\n'
        if len(content) > 0:
            content = content[0:-1]

        return self._blob_builder.build(content), False
