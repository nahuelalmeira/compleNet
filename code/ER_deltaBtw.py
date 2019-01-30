import os
import sys
import pickle
import numpy as np
import igraph as ig

N = int(sys.argv[1])
p = sys.argv[2]
min_seed = int(sys.argv[3])
max_seed = int(sys.argv[4])

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
net_dir_name = '../networks/ER'

for seed in range(min_seed, max_seed):

    network = 'ER_N{}_p{}_{:05d}'.format(N, p, seed)
    print(network)
    network_file = network + '.txt'
    full_network_path = os.path.join(net_dir_name, network, network_file)

    for attack in attacks:    

        #G = ig.Graph().Read_Edgelist(full_network_path, directed=False)
        
        attack_dir_name = os.path.join(net_dir_name, network, attack)

        full_output_name  = os.path.join(attack_dir_name, 'deltaBtw.txt')
        if not overwrite:
            if os.path.isfile(full_output_name):
                continue

        full_input_name  = os.path.join(attack_dir_name, 'btw_by_oi_arr.txt')
        btw_by_oi_arr = np.loadtxt(full_input_name)

        delta2_btw = np.diff(btw_by_oi_arr)**2        
        delta2_btw_sum = np.nansum(delta2_btw, axis=0)
        delta2_btw_sum = np.append(delta2_btw_sum, np.repeat(np.NaN, (N-len(delta2_btw_sum))))
        
        np.savetxt(full_output_name, delta2_btw_sum)
        