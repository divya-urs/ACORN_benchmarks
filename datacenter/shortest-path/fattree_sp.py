import sys
from routemap import *
from ir import *
from util import *
from datacenter.fattree import FatTree

OUTPUT_DIR = 'datacenter/shortest-path/'

def fattree_sp(k):
    ft = FatTree(k)
    nodes = ft.nodes
    edges = ft.edges
    src = ('l', k-1, (k//2)-1) 
    dest = ('l', 0, 0)

    print('k = {}, {} nodes'.format(k, len(nodes)))

    node_index = {}
    i = 0
    policy = {}
    for u in nodes:
        if u not in node_index:
            node_index[u] = i
            i += 1
        for v in edges[u]:
            if v not in node_index:
                node_index[v] = i
                i += 1
            policy[(node_index[u], node_index[v])] = [
                    Routemap(
                        match_list = [], 
                        action_list = [prop_comm_action(), default_lp_action(), incr_pathlen_action(1)],
                        seq_num = 10,
                        result = 'permit')]

    nodes1 = [node_index[u] for u in nodes]
    edges1 = {}
    for u in nodes:
        edges1[node_index[u]] = []
        for v in edges[u]:
            edges1[node_index[u]].append(node_index[v])

    # print(policy)
    
    repr = IR(nodes=nodes1, edges=edges1, dest=node_index[dest], policy=policy, info={}, 
            property=Property('', {}), description='FatTree with parameter {} running shortest-path policy.'.format(k))     
    return (repr, node_index)

def check_convergence(k):
    ir, _ = fattree_sp(k)
    conv_prop = Property('convergence', {})
    ir.property = conv_prop
    f = OUTPUT_DIR + 'fattree_sp_{}_convergence.in'.format(k)
    write_ir(ir, f)

def check_reachability(k):
    src = ('l', k-1, (k//2)-1) 
    ir, node_index = fattree_sp(k)
    reach_single_prop = Property('reach-singlesrc', {'src': node_index[src]})
    ir.property = reach_single_prop
    f = OUTPUT_DIR + 'fattree_sp_{}_reach.in'.format(k)
    write_ir(ir, f)

def write_ir(ir, f, validate=False):
    ir.write(f)
    print("Written IR.")
    if validate:
        print("Validating IR...")
        ir_read = IR.read(f)
        try:
            assert(ir_read == ir)
            print("Written and validated IR to {}".format(f))
        except AssertionError:
            print("Assertion failed!")
            print(ir)
            print("-----")
            print(ir_read)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: fattree parameter, property ('reach-singlesrc' or 'convergence')")
        exit(1)

    k = int(sys.argv[1])
    prop = sys.argv[2]

    print("k", k)
    print("property", prop)

    if prop == 'reach-singlesrc':
        check_reachability(k)
    elif prop == 'convergence':
        check_convergence(k)
    else:
        print("Invalid property")
        raise ValueError