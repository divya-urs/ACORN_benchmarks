import sys
from routemap import *
from ir import *
from util import *
from datacenter.fattree import FatTree

def fattree_valleyfree_nv(k):
    print("(* fattree valley-free reachability *)")
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

            if u[0] == 'm' and v[0] == 'l': # aggr -> ToR
                policy[(node_index[u], node_index[v])] = \
                '''Some {r with comm = (update_comm r.comm); length = r.length + 1}
                '''
                
            #     '''(match r.comm with
            # | 0 -> Some {r with comm = 1; length = r.length + 1}
            # | 1 -> Some {r with comm = 2; length = r.length + 1}
            # | _ -> Some {r with comm = 3; length = r.length + 1})
            # '''

            elif u[0] == 'm' and v[0] == 'r': # aggr -> core
                policy[(node_index[u], node_index[v])] = \
                    '''if (r.comm = 0) then Some {r with comm = 1; length = r.length + 1} else None
                    '''
                # policy[(node_index[u], node_index[v])] = '''(match r.comm with
            # | 0 -> Some {r with comm = 1; length = r.length + 1}
            # | _ -> None)
            # ''' NOTE: much slower (more than 10 times) if match is used instead of if-then-else
           
            elif u[0] == 'l' and v[0] == 'm': # ToR -> aggr
                policy[(node_index[u], node_index[v])] = \
                    '''if (r.comm = 0) then Some {r with length = r.length + 1} else None
                    '''
            #     '''(match r.comm with
            # | 0 -> Some {r with length = r.length + 1}
            # | _ -> None)
            # '''

            # else: default
            

    # nodes1 = [node_index[u] for u in nodes]
    edges1 = {}
    for u in nodes:
        edges1[node_index[u]] = []
        for v in edges[u]:
            edges1[node_index[u]].append(node_index[v])

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

    update_comm = '''
let update_comm c =
    match c with
    | 0 -> 1
    | 1 -> 2
    | _ -> 3
'''

    print(update_comm)

    trans_pre = ''' 
let trans edge x =
    match x with
    | None -> None
    | Some r -> 
        (match edge with'''
    print(trans_pre)
    # trans function
    for edge, pol in policy.items():
        # print(edge, stmts)
        print("\t| {}n~{}n -> {}".format(edge[0], edge[1], pol))
    
    # print default action
    print("\t| _ -> Some {r with length = r.length + 1}")

    print("\t)")

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
    
