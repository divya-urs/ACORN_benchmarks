import sys
from routemap import *
from ir import *
from util import *  
from datacenter.fattree import FatTree

OUTPUT_DIR = 'datacenter/valley-free/'

def fattree_vf(k):
    ft = FatTree(k)
    nodes = ft.nodes
    edges = ft.edges
    src = ('l', k-1, (k//2)-1) 
    dest = ('l', 0, 0)

    print('FatTree k = {}, {} nodes'.format(k, len(nodes)))

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

            if u[0] == 'm' and v[0] == 'l': # aggr -> ToR
                policy[(node_index[u], node_index[v])] = [
                    Routemap(
                        match_list = [Match('comm', match_vals=[0])],
                        action_list = [set_comm_action(comm_val=1),
                                       default_lp_action(),
                                       incr_pathlen_action(1)],
                        seq_num = 10,
                        result = 'permit'
                    ),
                    Routemap(
                        match_list = [Match('comm', match_vals=[1])],
                        action_list = [set_comm_action(comm_val=2),
                                       default_lp_action(),
                                       incr_pathlen_action(1)],
                        seq_num = 20,
                        result = 'permit'
                    ),
                    Routemap(
                        match_list = [],
                        action_list = [set_comm_action(comm_val=3),
                                       default_lp_action(),
                                       incr_pathlen_action(1)],
                        seq_num = 30,
                        result = 'permit'
                    )
                ]

            elif u[0] == 'm' and v[0] == 'r': # aggr -> core
                policy[(node_index[u], node_index[v])] = [
                    Routemap(
                        match_list = [Match('comm', match_vals=[0])],
                        action_list = [set_comm_action(comm_val=1),
                                       default_lp_action(),
                                       incr_pathlen_action(1)],
                        seq_num = 10,
                        result = 'permit'
                    ),
                    Routemap(
                        match_list = [],
                        action_list = [],
                        seq_num = 20,
                        result = 'deny'
                    )    
                ]

            elif u[0] == 'l' and v[0] == 'm': # ToR -> aggr
                policy[(node_index[u], node_index[v])] = [
                    Routemap(
                        match_list = [Match('comm', match_vals=[0])],
                        action_list = [prop_comm_action(), default_lp_action(), incr_pathlen_action(1)],
                        seq_num = 10,
                        result = 'permit'
                    ),
                    Routemap(
                        match_list = [],
                        action_list = [],
                        seq_num = 20,
                        result = 'deny'
                    )
                ]
                
            else:
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
    
    repr = IR(nodes=nodes1, edges=edges1, dest=node_index[dest], policy=policy, info={}, 
            property=Property('', {}), description='FatTree with parameter {} running valley-free policy.'.format(k))
    return (repr, node_index)

def fattree_vf_buggy(k): # Aggr->ToR in destination pod drops routes if comm != 0
    ft = FatTree(k)
    nodes = ft.nodes
    edges = ft.edges
    src = ('l', k-1, (k//2)-1) 
    dest = ('l', 0, 0)

    print('FatTree k = {}, {} nodes'.format(k, len(nodes)))

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

            if u[0] == 'm' and v[0] == 'l': # aggr -> ToR
                if v[1] == k-1: # BUG: if src pod, use policy for ToR -> aggr (drop routes if comm != 0)
                    policy[(node_index[u], node_index[v])] = [
                        Routemap(
                        match_list = [Match('comm', match_vals=[0])],
                        action_list = [prop_comm_action(), default_lp_action(), incr_pathlen_action(1)],
                        seq_num = 10,
                        result = 'permit'
                    ),
                    Routemap(
                        match_list = [],
                        action_list = [],
                        seq_num = 20,
                        result = 'deny'
                    )
                    ]
                else:
                    policy[(node_index[u], node_index[v])] = [
                        Routemap(
                            match_list = [Match('comm', match_vals=[0])],
                            action_list = [set_comm_action(comm_val=1),
                                        default_lp_action(),
                                        incr_pathlen_action(1)],
                            seq_num = 10,
                            result = 'permit'
                        ),
                        Routemap(
                            match_list = [Match('comm', match_vals=[1])],
                            action_list = [set_comm_action(comm_val=2),
                                        default_lp_action(),
                                        incr_pathlen_action(1)],
                            seq_num = 20,
                            result = 'permit'
                        ),
                        Routemap(
                            match_list = [],
                            action_list = [set_comm_action(comm_val=3),
                                        default_lp_action(),
                                        incr_pathlen_action(1)],
                            seq_num = 30,
                            result = 'permit'
                        )
                    ]

            elif u[0] == 'm' and v[0] == 'r': # aggr -> core
                    policy[(node_index[u], node_index[v])] = [
                        Routemap(
                            match_list = [Match('comm', match_vals=[0])],
                            action_list = [set_comm_action(comm_val=1),
                                        default_lp_action(),
                                        incr_pathlen_action(1)],
                            seq_num = 10,
                            result = 'permit'
                        ),
                        Routemap(
                            match_list = [],
                            action_list = [],
                            seq_num = 20,
                            result = 'deny'
                        )    
                    ]

            elif u[0] == 'l' and v[0] == 'm': # ToR -> aggr
                policy[(node_index[u], node_index[v])] = [
                    Routemap(
                        match_list = [Match('comm', match_vals=[0])],
                        action_list = [prop_comm_action(), default_lp_action(), incr_pathlen_action(1)],
                        seq_num = 10,
                        result = 'permit'
                    ),
                    Routemap(
                        match_list = [],
                        action_list = [],
                        seq_num = 20,
                        result = 'deny'
                    )
                ]
                
            else:
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
    
    repr = IR(nodes=nodes1, edges=edges1, dest=node_index[dest], policy=policy, info={}, 
            property=Property('', {}), description='FatTree with parameter {} running buggy valley-free policy.'.format(k))
    return (repr, node_index)

def check_convergence(k):
    ir, _ = fattree_vf(k)
    conv_prop = Property('convergence', {})
    ir.property = conv_prop
    f = OUTPUT_DIR + 'fattree_vf_{}_convergence.in'.format(k)
    write_ir(ir, f)
    
def check_vf_property(k):
    src = ('l', k-1, (k//2)-1) 
    ir, node_index = fattree_vf(k)
    vf_prop = Property('valley-free', {'src': node_index[src]})
    ir.property = vf_prop
    f = OUTPUT_DIR + 'fattree_vf_{}_vf_prop.in'.format(k)
    write_ir(ir, f)
    
def check_reachability(k):
    src = ('l', k-1, (k//2)-1) 
    ir, node_index = fattree_vf(k)
    reach_single_prop = Property('reach-singlesrc', {'src': node_index[src]})
    ir.property = reach_single_prop
    f = OUTPUT_DIR + 'fattree_vf_{}_reach.in'.format(k)
    write_ir(ir, f)

def check_reachability_buggy(k):
    src = ('l', k-1, (k//2)-1) 
    ir, node_index = fattree_vf_buggy(k)
    reach_single_prop = Property('reach-singlesrc', {'src': node_index[src]})
    ir.property = reach_single_prop
    f = OUTPUT_DIR + 'fattree_vf_buggy_{}_reach.in'.format(k)
    write_ir(ir, f)

def write_ir(ir, f, validate=True):
    ir.write(f)
    print("Written IR.")
    if validate:
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
        print("Usage: fattree parameter, property ('reach-singlesrc', 'valley-free', 'reach-singlesrc-buggy', or 'convergence')")
        exit(1)

    k = int(sys.argv[1])
    prop = sys.argv[2]

    print("k", k)
    print("property", prop)

    if prop == 'reach-singlesrc':
        check_reachability(k)
    elif prop == 'valley-free':
        check_vf_property(k)
    elif prop == 'convergence':
        check_convergence(k)
    elif prop == 'reach-singlesrc-buggy':
        check_reachability_buggy(k)
    else:
        print("Invalid property")
        raise ValueError