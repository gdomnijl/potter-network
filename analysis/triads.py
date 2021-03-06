import csv
from sets import Set
import json

IN_PATH = './relations.csv'
OUT_PATH = './relations.json'

def read_edges():
    edges = {}
    with open(IN_PATH, 'r') as f:
        next(f)
        reader = csv.reader(f)
        for row in reader:
            source = row[0]
            target = row[1]
            label = row[2]

            # because undirected graph is assumed
            key = (source,target)
            flip_key = (target,source)
            edges[key] = label
            edges[flip_key] = label
    # endwith
    return edges

def _get_triad_type(labels):
    ally = 0
    enemy = 0
    for l in labels:
        if l == '+': ally += 1
        else: enemy += 1

    if ally == 3:
        return 'T3'
    elif ally == 1 and enemy == 2:
        return 'T1'
    elif ally == 2 and enemy == 1:
        return 'T2'
    else:
        return 'T0'


def _get_neighbors(edges):
    neighbors = {}
    for key in edges:
        s = key[0]
        t = key[1]

        if not s in neighbors:
            neighbors[s] = Set([t])
        else:
            neighbors[s].add(t)

        if not t in neighbors:
            neighbors[t] = Set([s])
        else:
            neighbors[t].add(s)

    return neighbors

def _prune_triads(triads):
    edges = []
    for edge in triads:
        edges.append(edge)
    for edge in edges:
        s = edge[0]
        t = edge[1]
        if (t,s) in triads:
            del triads[edge]

def get_triads(edges):
    neighbors = _get_neighbors(edges)
    triads = {}
    triad_counts = {}
    for key in edges:
        s = key[0]
        s_neighbors = neighbors[s]

        for n1 in s_neighbors:
            for n2 in s_neighbors:
                if n1 == n2: continue
                if not (n1,n2) in edges: continue

                l1 = edges[(n1,n2)]
                l2 = edges[(s,n1)]
                l3 = edges[(s,n2)]

                triangle = sorted([s,n1,n2])
                t = _get_triad_type([l1,l2,l3])

                if not tuple(triangle) in triad_counts:
                    triad_counts[tuple(triangle)] = t
                
                if not (n1,n2) in triads:
                    triads[(n1,n2)] = Set([t])
                else:
                    triads[(n1,n2)].add(t)

                if not (s,n1) in triads:
                    triads[(s,n1)] = Set([t])
                else:
                    triads[(s,n1)].add(t)

                if not (s,n2) in triads:
                    triads[(s,n2)] = Set([t])
                else:
                    triads[(s,n2)].add(t)
        _prune_triads(triads)
    return (triads, triad_counts)

def write_triads(triads,edges):
    j = []
    seen = Set([])
    for edge in triads:
        s = edge[0]
        t = edge[1]
        seen.add((s,t))
        l = edges[(s,t)]
        tr = list(triads[(s,t)])
        j.append({
            'source': s,
            'target': t,
            'type': l,
            'triads': tr
        })
    for edge in edges:
        s = edge[0]
        t = edge[1]
        if s == '64':
            print s,t
        if (s,t) in seen or (t,s) in seen:
            continue
        seen.add((s,t))
        j.append({
            'source': s,
            'target': t,
            'type': edges[(s,t)],
            'triads': []
        })

    with open(OUT_PATH, 'w') as f:
        json.dump(j,f)

def print_stats(triad_counts):
    T3 = 0
    T1 = 0
    T2 = 0
    T0 = 0
    for triangle in triad_counts:
        t = triad_counts[triangle]
        if t == 'T3':
            T3 += 1
        elif t == 'T2':
            T2 += 1
        elif t == 'T1':
            T1 += 1
        else:
            T0 += 1
    print "T3: " + str(T3)
    print "T1: " + str(T1)
    print "T2: " + str(T2)
    print "T0: " + str(T0)


if __name__=='__main__':
    edges = read_edges()
    (triads,triad_counts) = get_triads(edges)
    write_triads(triads,edges)
    print_stats(triad_counts)
