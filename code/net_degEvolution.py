import os
import sys
import pickle
import bz2
import numpy as np
import igraph as ig

net_type = sys.argv[1]
size = int(sys.argv[2])
param = sys.argv[3]
min_seed = int(sys.argv[4])
max_seed = int(sys.argv[5])

if 'giant' in sys.argv:
    giant = True
else:
    giant = False

if 'overwrite' in sys.argv:
    overwrite = True
else:
    overwrite = False

if giant:
    attacks = ['BtwGU', 'DegGU', 'RanG']
else:
    attacks = ['BtwU', 'DegU', 'Ran']
dir_name = os.path.join('../networks', net_type)

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

for seed in range(min_seed, max_seed):

    net_name = base_net_name + '_{:05d}'.format(seed)
    net_file_name = net_name + '.txt'
    net_dir_name = os.path.join(dir_name, net_name)

    print(net_name)

    for attack in attacks:    
        
        attack_dir_name = os.path.join(net_dir_name, attack)
        output_file_name = 'deg_values.txt'
        output_full_file_name = os.path.join(attack_dir_name, output_file_name)

        if not overwrite:
            if os.path.isfile(output_full_file_name):
                continue
    
        full_net_file_name = os.path.join(net_dir_name, net_file_name)
        G = ig.Graph().Read_Edgelist(full_net_file_name, directed=False) 

        if not G.is_connected():
            #print('Only giant component of network "' + net_name + '" will be considered.')
            components = G.components(mode='weak')
            G = components.giant()
        N0 = G.vcount()
        oi_file_name = attack + '_' + net_name + '.txt'
        full_oi_file_name = os.path.join(attack_dir_name, oi_file_name)
        original_indices = np.loadtxt(full_oi_file_name, usecols=1, dtype=int)
        G.vs['original_index'] = range(N0)

        mean_deg_values = []
        std_deg_values = []
        for oi in original_indices:

            components = G.components(mode='weak')
            gcc = components.giant()

            degSeq = gcc.degree()
            mean_deg = np.mean(degSeq)
            std_deg = np.std(degSeq)
            mean_deg_values.append(mean_deg)
            std_deg_values.append(std_deg)

            idx = G.vs['original_index'].index(oi)
            G.vs[idx].delete()
            
        mean_deg_values = np.append(np.array(mean_deg_values), np.repeat(np.NaN, N-len(mean_deg_values)))
        std_deg_values = np.append(np.array(std_deg_values), np.repeat(np.NaN, N-len(std_deg_values)))

        np.savetxt(output_full_file_name, np.array([mean_deg_values, std_deg_values]).T)
