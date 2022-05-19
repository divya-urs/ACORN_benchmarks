import sys
from routemap import *
from ir import *
from util import *
from datacenter.fattree import FatTree

OUTPUT_DIR='datacenter/external-access/'

def fattree_ext_acc(k, dest, local_pods):
    ft = FatTree(k)
    nodes = ft.nodes
    edges = ft.edges

    print('k = {}, {} nodes'.format(k, len(nodes)))

    ext_router = ('e')
    # connect external router to all core routers
    nodes.append(ext_router)
    edges[ext_router] = []
    for u in nodes:
        if u[0] == 'r': # core
            edges[u].append(ext_router)
            edges[ext_router].append(u)
    
    
    src = ('e')

    node_index = {}
    i = 0
    policy = {}

    # assign node ids
    for u in nodes:
        if u not in node_index:
            node_index[u] = i
            i += 1
        for v in edges[u]:
            if v not in node_index:
                node_index[v] = i
                i += 1

    cores = [u for u in nodes if u[0] == 'r']
    ToRs = [u for u in nodes if u[0] == 'l']
    core_ids = [node_index[u] for u in cores]
    local_ToRs = [u for u in nodes if u[0] == 'l' and u[1] in local_pods] # ToR nodes in local blocks
    local_ToRs_ids = [node_index[u] for u in local_ToRs]
    
    for u in nodes:
        for v in edges[u]:
            # valley-free policy.
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
                
            elif u[0] == 'r' and v[0] == 'e': # core -> external
                policy[(node_index[u], node_index[v])] = [
                    Routemap(
                        match_list = [Match('aspath', 
                            match_vals={'type':'has_any', 'params': local_ToRs_ids})],
                        action_list = [],
                        seq_num = 10,
                        result = 'deny'
                    ),
                    Routemap(
                        match_list = [], 
                        action_list = [prop_comm_action(), default_lp_action(), incr_pathlen_action(1)],
                        seq_num = 20,
                        result = 'permit'
                    )]
                
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
    
    # print("node_index")
    # for u in nodes:
    # 	print(u, ":", node_index[u])

    repr = IR(nodes=nodes1, edges=edges1, dest=node_index[dest], policy=policy, info={}, 
            property=Property('', {}), description='FatTree with parameter {} running isolation policy with regular expressions.'.format(k))
    return (repr, node_index)

def check_convergence(k):
    dest = ('l', 0, 0)
    local_pods = [0] # indices of local pods
    ir, _ = fattree_ext_acc(k, dest, local_pods)
    conv_prop = Property('convergence', {})
    ir.property = conv_prop
    f = OUTPUT_DIR + 'fattree_ext_acc_{}_convergence.in'.format(k)
    write_ir(ir, f)

def check_reachability(k):
    dest = ('l', 0, 0)
    src = ('l', k-1, (k//2)-1) 
    local_pods = [0] # indices of local pods

    ir, node_index = fattree_ext_acc(k, dest, local_pods)
    reach_single_prop = Property('reach-singlesrc', {'src': node_index[src]})
    ir.property = reach_single_prop
    f = OUTPUT_DIR + 'fattree_ext_acc_{}_reach.in'.format(k)
    write_ir(ir, f)

def check_isolation(k):
    src = ('e')
    local_pods = [0] # indices of local pods
    dest = ('l', 0, 0)
    ir, node_index = fattree_ext_acc(k, dest, local_pods)
    isolation_prop = Property('isolation', {'src': node_index[src]})
    ir.property = isolation_prop
    f = OUTPUT_DIR + 'fattree_ext_acc_{}_isolation.in'.format(k)
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
        print("Usage: fattree parameter, property")
        exit(1)

    k = int(sys.argv[1])
    prop = sys.argv[2]

    print("k", k)
    print("property", prop)

    if prop == 'reach-singlesrc':
        check_reachability(k)
    elif prop == 'isolation':
        check_isolation(k)
    elif prop == 'convergence':
        check_convergence(k)
    else:
        print("Invalid property")
        raise ValueError

