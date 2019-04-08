import igraph as ig
import numpy as np
import os
import sys

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
    N = L*L
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

    btw_base_file = os.path.join(data_dir, 'btw_data_' + net_name)

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

    ## Original indices in removal order
    oi_values = np.loadtxt(oi_file)

    ## Sample values for the fraction of nodes removed
    t_values = [0, 0.05, 0.1, 0.15, 0.2, 0.21, 0.215, 0.22, 0.225, 0.23]

    sample_i_values = [int(t*N0) for t in t_values]
    current_t = t_values[0]

    for i, oi in enumerate(oi_values):
        
        ## Compute giant component
        components = g.components(mode='WEAK')
        giant = components.giant()
        Ngcc = giant.vcount()

        ## Compute node betweenness
        betweenness = giant.betweenness()

        ## Save data
        if i in sample_i_values:
            l = sample_i_values.index(i)
            t = t_values[l]
            #print(t)
            btw_file = btw_base_file + '_t{:.6f}.txt'.format(t)
            if not overwrite:
                if os.path.isfile(btw_file):
                    break
            np.savetxt(btw_file, betweenness)

        ## Remove node
        idx = g.vs['original_index'].index(oi)
        g.vs[idx].delete()
    
    
