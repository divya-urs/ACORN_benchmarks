import sys
from routemap import *
from ir import *
from util import *
from datacenter.fattree import FatTree

def fattree_valleyfree_nv(k):
    print("(* fattree shortest-path reachability *)")
    ft = FatTree(k)
    nodes = ft.nodes
    edges = ft.edges
    src = ('l', k-1, (k//2)-1) 
    dest = ('l', 0, 0)

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

            policy[(node_index[u], node_index[v])] = \
                '''
                Some {r with length = r.length + 1}
                '''
            

    # nodes1 = [node_index[u] for u in nodes]
    edges1 = {}
    for u in nodes:
        edges1[node_index[u]] = []
        for v in edges[u]:
            edges1[node_index[u]].append(node_index[v])

    print("(* k = {} *)".format(k))
    print("(* dest:", node_index[dest], "*)")
    print("(* src:", node_index[src], "*)")
    print("(* single-src reachability *)")
    print()
    print("let src = ", node_index[src])
    print()

    # print("node_index")
    # for u in nodes:
    # 	print(u, ":", node_index[u])

    # Print NV code
    print("type bgpType = {comm: int; lp: int; length: int}")
    print("type attribute = option[bgpType]")
    # topology
    print("let nodes = {}".format(len(nodes)))
    print("let edges = {")
    for u in nodes:
        for v in edges[u]:
            if node_index[u] < node_index[v]:
                print("{} = {};".format(node_index[u], node_index[v]))
    print("}")

    trans = ''' 
let trans edge x =
    match x with
    | None -> None
    | Some r -> Some {r with length = r.length + 1}
    '''
    print(trans)

    merge_no_lp = '''
let merge u x y =
    match (x, y) with
    | (None, _) -> y
    | (_, None) -> x
    | (Some i, Some j) -> if i.length < j.length then x else y
    '''

    merge = '''
let merge u x y =
    match (x, y) with
    | (None, _) -> y
    | (_, None) -> x
    | (Some i, Some j) -> 
        if i.lp > j.lp then x
        else if j.lp > i.lp then y
        else if i.length < j.length then x else y
    '''

    print(merge)

    # init
    init = '''
let init node =
    match node with
    | {}n -> Some {{ comm = 0; lp = 100; length = 0;}}
    | _ -> None
    '''.format(node_index[dest])
    print(init)

    single_src_reach_property = '''
let reachable (u: tnode) (x: attribute) =
    match u with
    | src -> match x with
            | None -> false
            | Some _ -> true
    | _ -> true

let sol = solution {init = init; trans = trans; merge = merge}

assert foldNodes (fun u v acc -> acc && reachable u v) sol true
'''
    print(single_src_reach_property)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: fattree parameter")
        exit(1)
    
    k = int(sys.argv[1])
    fattree_valleyfree_nv(k)
    
