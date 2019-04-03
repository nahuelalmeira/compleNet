import igraph as ig
import numpy as np
import os
import sys
from collections import Counter
from attacks import betweennessUpdateAttack

net_type = sys.argv[1]
size = int(sys.argv[2])
param = sys.argv[3]
min_seed = int(sys.argv[4])
max_seed = int(sys.argv[5])

if 'overwrite' in sys.argv:
    overwrite = True
else:
    overwrite = False

dir_name = os.path.join('../networks', net_type)

seeds = range(min_seed, max_seed)

if net_type == 'ER':
    N = size
    p = param
    base_net_name = 'ER_N{}_p{}'.format(N, p)
elif net_type == 'BA':
    N = size
    m = param
    base_net_name = 'BA_N{}_m{}'.format(N, m)
elif net_type == 'Lattice':
    L = size
    p = param
    base_net_name = 'Lattice_L{}_f{}'.format(L, p)

for seed in seeds:

    net_name = base_net_name + '_{:05d}'.format(seed)
    print(net_name)

    net_dir_name = os.path.join(dir_name, base_net_name, net_name)
    
    input_name = net_name + '.txt'   
    full_input_name = os.path.join(net_dir_name, input_name)

    data_dir = os.path.join(net_dir_name, 'BtwU')

    oi_file = os.path.join(data_dir, 'oi_list_' + net_name + '.txt')
    if not os.path.isfile(oi_file):
        if overwrite:
            print("FILE " + oi_file + " NOT FOUND")
        continue

    components_file = os.path.join(data_dir, 'comp_data_' + net_name + '.txt')
    if not overwrite:
        if os.path.isfile(components_file):
            continue

    g = ig.Graph().Read_Edgelist(full_input_name, directed=False)        

    if not g.is_simple():
        print('Network "' + net_name + '" will be considered as simple.')
        g.simplify()
        
    if g.is_directed():
        print('Network "' + net_name + '" will be considered as undirected.')
        g.to_undirected()
        
    if not g.is_connected():
        print('Only giant component of network "' + net_name + '" will be considered.')
        components = g.components(mode='weak')
        g = components.giant()

    N0 = g.vcount()
    g.vs['original_index'] = range(N0)

    data = []

    oi_values = np.loadtxt(oi_file)
    for oi in oi_values:
        
        components = g.components(mode='WEAK')
        Ngcc = components.giant().vcount()
        comp_sizes = [len(c) for c in components]
        comp_sizes.remove(Ngcc)
        counter = Counter(comp_sizes)

        if comp_sizes:
            Nsec = np.max(comp_sizes)
            meanS = np.mean(comp_sizes)
            numerator = denominator = 0
            for size, n in counter.items():
                numerator += n*size*size
                denominator += n*size
            meanS2 = numerator / denominator
        else:
            Nsec = 0
            meanS = np.NaN
            meanS2 = np.NaN

        data.append([Ngcc, Nsec, meanS, meanS2])

        idx = g.vs['original_index'].index(oi)
        g.vs[idx].delete()
    
    np.savetxt(components_file, data, fmt='%d %d %f %f')
