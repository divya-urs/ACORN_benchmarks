from collections import defaultdict


class FatTree:
    '''
    A generic parameterized fattree
    '''

    def __init__(self, k):
        self.k = k
        self._nblocks = k
        self._block_width = k//2
        self._leaves_per_block = k//2
        self._roots_per_mid_node = k//2
        nblocks = self._nblocks
        block_width = self._block_width
        leaves_per_block = self._leaves_per_block
        roots_per_mid_node = self._roots_per_mid_node

        roots = [
            ('r', mid_node, root_index)
            for mid_node in range(block_width)
            for root_index in range(roots_per_mid_node)
        ]
        mid_nodes = [
            ('m', block, node)
            for block in range(nblocks)
            for node in range(block_width)
        ]
        leaves = [
            ('l', block, node)
            for block in range(nblocks)
            for node in range(leaves_per_block)
        ]

        self.nodes = roots + mid_nodes + leaves
        self.edges = defaultdict(list)
        for m in mid_nodes:
            for r in self.get_roots(m):
                self.edges[r].append(m)
                self.edges[m].append(r)

        for c in leaves:
            _, block, _ = c
            for node in range(block_width):
                m = self.get_mid_node(block, node)
                self.edges[c].append(m)
                self.edges[m].append(c)

    def get_mid_node(self, block, index_in_block):
        return ('m', block, index_in_block)

    def get_roots(self, mid_node):
        _, _, index_in_block = mid_node
        return [
            ('r', index_in_block, ri)
            for ri in range(self._roots_per_mid_node)
        ]

    def get_leaves(self, block):
        return [
            ('l', block, li)
            for li in range(self._leaves_per_block)
        ]

    def num_blocks(self):
        return self._nblocks

    def block_width(self):
        return self._block_width






