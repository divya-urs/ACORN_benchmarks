import json
from routemap import *

class IR(object):
    def __init__(self, nodes, edges, dest, policy, property, info = {},  description = ''):
        self.description = description
        self.nodes = nodes # list of nodes
        self.edges = edges # adjacency list
        self.dest = dest # destination
        self.property = property # property
        self.policy = policy # edge -> list of routemaps
        self.info = info # additional information
    
    def __repr__(self):
        s = 'description: {}\n'.format(self.description)
        # s += 'Topology (#nodes, #edges): ({}, {})\n'.format(len(self.nodes), len(self.policy.keys()))
        s += 'nodes: {}\n'.format(self.nodes)
        s += 'edges: {}\n'.format(self.edges)
        s += 'destination: {}\n'.format(self.dest)
        s += 'property: {}\n'.format(self.property)
        s += 'policy: {}\n'.format(self.policy)
        s += 'info: {}\n'.format(self.info)
        return s

    def __eq__(self, other):
        return (set(self.nodes) == set(other.nodes)) and (self.edges == other.edges) and \
            (self.dest == other.dest)  and (self.property == other.property) and \
            (self.policy == other.policy) and (self.info == other.info)

    @classmethod
    def read(cls, input_file):
        f = open(input_file, 'r')
        d = json.load(f)
        f.close()

        def make_tuple(s): # convert string "(1, 2)" to tuple (1, 2)
            s = s[1:-1] # remove parentheses
            try:
                toks = [t.strip() for t in s.split(',')]
                assert(len(toks) == 2)
            except AssertionError:
                toks = [t.strip() for t in s.split("'")]
                toks = [toks[1], toks[3]]
                
            if toks[0].isnumeric() and toks[1].isnumeric():
                return tuple(int(x) for x in toks)
            else:
                return tuple(x.replace("'", '').strip() for x in toks)

        if type(d['nodes']) == int:
            nodes = list(range(d['nodes']))
        else:
            nodes = d['nodes']

        if type(d['nodes']) == int:
            edges = {int(k) : v for k, v in d['adjacency_list'].items()}
        else:
            edges = d['adjacency_list']

        pol = {make_tuple(e): [Routemap.read(r) for r in d['policy'][e]]
                for e in d['policy'].keys()}
        
        if 'business_rel' in d['info']:
            d['info']['business_rel'] = {make_tuple(e): d['info']['business_rel'][e] for 
                                            e in d['info']['business_rel'].keys()}
        prop = Property.read(d['property'])

        return cls(description=d['description'], nodes=nodes, edges=edges,
        dest=d['dest'], policy=pol, property=prop, info=d['info'])

    # def write(self, output_file):
    def write(self, output_file):
        d = {}
        d['description'] = self.description
        if str not in [type(x) for x in self.nodes]:
            d['nodes'] = len(self.nodes)
        else:
            d['nodes'] = self.nodes
        d['adjacency_list'] = self.edges
        d['dest'] = self.dest
        d['property'] = self.property.write()
       
        d['info'] = {}
        if 'business_rel' in self.info:
            d['info']['business_rel'] = {str(e): self.info['business_rel'][e] 
                    for e in self.info['business_rel'].keys()}
        else:
             d['info'] = self.info

        d['policy'] = {str(e): [rmap.write() for rmap in self.policy[e]]
                for e in self.policy.keys()}

        with open(output_file, 'w+') as f:
            json.dump(d, f, indent=4)




        
        
