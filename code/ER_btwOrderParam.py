import os
import sys
import pickle
import bz2
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
        
        attack_dir_name = os.path.join(net_dir_name, network, attack)

        full_output_name  = os.path.join(attack_dir_name, 'btwOrderParam.txt')
        if not overwrite:
            if os.path.isfile(full_output_name):
                continue

        full_input_name  = os.path.join(attack_dir_name, 'btw_by_oi_arr.pickle.bz2')
        with bz2.BZ2File(full_input_name, 'r') as f:
            btw_by_oi_arr = pickle.load(f)
        #btw_by_oi_arr = np.loadtxt(full_input_name)

        spin_matrix = np.nan_to_num(btw_by_oi_arr, copy=True)
        np.nan_to_num(btw_by_oi_arr, copy=False)

        for i in range(len(spin_matrix)):
            if spin_matrix[i][0] == 0:
                spin_matrix[i] = [0.0 for elem in spin_matrix[i]]
            else:
                spin_matrix[i] = spin_matrix[i] / spin_matrix[i][0]

        btw_sum = np.nansum(btw_by_oi_arr, axis=0)
        spin_sum = np.nansum(spin_matrix, axis=0)

        btw_sum = np.append(btw_sum, np.repeat(np.NaN, (N-len(btw_sum))))
        spin_sum = np.append(spin_sum, np.repeat(np.NaN, (N-len(spin_sum))))

        np.savetxt(full_output_name, np.array([btw_sum, spin_sum]).T)
        