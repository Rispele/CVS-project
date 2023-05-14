import os

import CVSBlobBuilder
import CVSIndex


class CVSTreeBuilder:
    def __init__(self, rep):
        self._rep = rep

        ind = CVSIndex.CVSIndex(rep)
        self._index = ind.read_index()
        self._indexed = set(self._index.keys())
        self._not_found = set(self._index.keys())
        self._blob_builder = CVSBlobBuilder.CVSBlobBuilder(rep)

    def build(self):
        return self._build(self._rep)[0], self._not_found

    def _build(self, path):
        tree = []
        for p in os.listdir(path):
            if '.cvs' in p:
                continue

            to_open_path = f'{path}\\{p}'
            if os.path.isfile(to_open_path):
                if to_open_path in self._indexed:
                    self._not_found.remove(to_open_path)
                    tree.append(f'blob {self._index[to_open_path]} {p}')
            else:
                h, is_empty = self._build(to_open_path)
                if is_empty:
                    continue
                tree.append(f'tree {h} {p}')

        if len(tree) == 0:
            return '', True

        content = ''
        for rec in tree:
            content += rec + '\n'
        if len(content) > 0:
            content = content[0:-1]

        return self._blob_builder.build(content), False





