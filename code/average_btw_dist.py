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
    N = L*L
    p = param
    base_net_name = 'Lattice_L{}_f{}'.format(L, p)


## Sample values for the fraction of nodes removed
t_values = [0, 0.025, 0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.21, 0.215, 0.22, 0.225, 0.23,
                0.24, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5]

for t in t_values:
    print(t)
    norm_betweenness_values = np.array([], dtype=float)

    base_net_dir_name = os.path.join(dir_name, base_net_name)
    output_base_name = os.path.join(base_net_dir_name, 'btw_data_' + base_net_name)
    
    output_name = output_base_name + '_t{:.6f}.txt'.format(t)
    if not overwrite:
        if os.path.isfile(output_name):
            continue
    with open(output_name, 'w') as f:
        for seed in seeds:

            net_name = base_net_name + '_{:05d}'.format(seed)

            net_dir_name = os.path.join(base_net_dir_name, net_name)
            data_dir = os.path.join(net_dir_name, 'BtwU')

            btw_base_file = os.path.join(data_dir, 'btw_data_' + net_name)
            btw_file = btw_base_file + '_t{:.6f}.txt'.format(t)
            if not os.path.isfile(btw_file):
                continue
            
            betweenness = np.loadtxt(btw_file, dtype=float)
            Ngcc = len(betweenness)

            print(net_name, Ngcc)
            norm_betweenness = 2 * betweenness / ( (Ngcc-1) * (Ngcc-2) )
            #norm_betweenness_values = np.concatenate((norm_betweenness_values, norm_betweenness))
            for norm_btw_value in norm_betweenness:
                f.write('{}\n'.format(norm_btw_value))# + '\n')
                f.flush()
    #np.savetxt(output_name, norm_betweenness_values)
    
    
