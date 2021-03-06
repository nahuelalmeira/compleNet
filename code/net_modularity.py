import igraph as ig
import os
import sys
import numpy as np

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

attacks = ['BtwU', 'DegU', 'Ran']

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
    net_file_name = net_name + '.txt'
    net_dir_name = os.path.join(dir_name, net_name)

    print(net_name)

    for attack in attacks:    
        
        attack_dir_name = os.path.join(net_dir_name, attack)
        output_file_name = 'q_values.txt'
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

        q_values = []
        Ngcc_values = []
        for oi in original_indices:
            communities = G.community_multilevel()
            q = communities.q
            q_values.append(q)

            idx = G.vs['original_index'].index(oi)
            G.vs[idx].delete()
            
            Ngcc = G.components(mode='WEAK').giant().vcount()
            Ngcc_values.append(Ngcc)
        q_values = np.append(np.array(q_values), np.repeat(np.NaN, N-len(q_values)))
        Ngcc_values = np.append(np.array(Ngcc_values), np.repeat(np.NaN, N-len(Ngcc_values)))
        np.savetxt(output_full_file_name, np.array([q_values, Ngcc_values]).T)
