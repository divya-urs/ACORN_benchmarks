import sys
import os
import networkx as nx
from routemap import *
from ir import *
from util import *

OUTPUT_DIR='wan/topologyZoo/'

p2p = "peer_peer"
cust2prov = "cust_prov"
prov2cust = "prov_cust"

def generate_ir(file):
    g = nx.read_gml(file)
    dest = g.graph['dest']

    nodes = list(g.nodes)
    edges = {u: list(g.neighbors(u)) for u in nodes}

    print("dest", dest)
    # print("nodes", nodes)
    # print("edges", edges)

    business_rel = {}
    for e in g.edges():
        u, v = e
        rel = g[u][v]['business_rel']
        # print(e, rel)
        if rel == prov2cust:
            business_rel[(u, v)] = prov2cust
            business_rel[(v, u)] = cust2prov
        elif rel == cust2prov:
            business_rel[(u, v)] = cust2prov
            business_rel[(v, u)] = prov2cust
        elif rel == p2p:
            business_rel[(u, v)] = p2p
            business_rel[(v, u)] = p2p
        else:
            raise ValueError("Invalid business relationship")

    # print("business_rel")
    # for e, rel in business_rel.items():
    #     print(e, rel)
    
    # Cust: comm = 0
    # Peer: comm = 1
    # Prov: comm = 2
    policy = {}
    for u in nodes:
        for v in edges[u]:
            if business_rel[(u, v)] == prov2cust: # u: prov, v: cust
                policy[(u, v)] = [
                    Routemap(
                        match_list = [],
                        action_list = [set_comm_action(comm_val=2), 
                                        set_lp_action(lp_val=100),
                                        incr_pathlen_action(1)],
                        seq_num = 10,
                        result = 'permit')]

            elif business_rel[(u, v)] == cust2prov: # u: cust, v: prov
                policy[(u, v)] = [
                    Routemap(
                        match_list = [Match('comm', match_vals=[0])],
                        action_list = [set_comm_action(comm_val=0),
                                        set_lp_action(lp_val=300),
                                        incr_pathlen_action(1)],
                        seq_num = 10,
                        result = 'permit'
                    ),
                    Routemap(
                        match_list = [],
                        action_list = [],
                        seq_num = 20,
                        result = 'deny'
                    )]
                
            elif business_rel[(u, v)] == p2p: # u: peer, v: peer
                policy[(u, v)] = [
                    Routemap(
                        match_list = [Match('comm', match_vals=[0])],
                        action_list = [set_comm_action(comm_val=1),
                                        set_lp_action(lp_val=200),
                                        incr_pathlen_action(1)],
                        seq_num = 10,
                        result = 'permit'
                    ),
                    Routemap(
                        match_list = [],
                        action_list = [],
                        seq_num = 20,
                        result = 'deny'
                    )]
            else:
                raise ValueError("Invalid business relationship")


    name = os.path.basename(file).replace('_annotated.gml', '')
    print("Topology: {} nodes, {} edges".format(len(nodes), len(policy.keys())))
    return IR(nodes=nodes, edges=edges, dest=dest, policy=policy, info={'business_rel': business_rel}, 
            property=None, description="Topology Zoo network {}, with policy based on Gao-Rexford conditions.".format(name))


def check_convergence(file):
    ir = generate_ir(file)
    ir.property = Property('convergence', {})
    name = os.path.basename(file)
    f = OUTPUT_DIR + '{}_convergence.in'.format(name.replace('_annotated.gml', ''))
    write_ir(ir, f)

def check_no_transit(file):
    ir = generate_ir(file)
    ir.property = Property('no-transit', {})
    name = os.path.basename(file)
    f = OUTPUT_DIR + '{}_no-transit.in'.format(name.replace('_annotated.gml', ''))
    write_ir(ir, f)

def check_reachability_allsrc(file):
    ir = generate_ir(file)
    ir.property = Property('reach-allsrc', {})
    name = os.path.basename(file)
    f = OUTPUT_DIR + '{}_reach-allsrc.in'.format(name.replace('_annotated.gml', ''))
    write_ir(ir, f)

def write_ir(ir, f, validate=True):
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
        print("Usage: file (annotated topology), property")
        exit(1)

    file = sys.argv[1]
    prop = sys.argv[2]

    print("file", file)
    print("property", prop)

    if prop == 'reach-allsrc':
        check_reachability_allsrc(file)

    elif prop == 'no-transit':
        check_no_transit(file)

    elif prop == 'convergence':
        check_convergence(file)
    else:
        raise ValueError("Invalid property")
