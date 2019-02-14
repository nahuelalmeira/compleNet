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

net_dir_name = os.path.join('../networks', net_type)

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

for seed in range(min_seed, max_seed):

    network = base_net_name + '_{:05d}'.format(seed)
    print(network)
    network_file = network + '.txt'
    full_network_path = os.path.join(net_dir_name, network, network_file)
    G = ig.Graph().Read_Edgelist(full_network_path, directed=False)
    gcc = G.components(mode='WEAK').giant()
    Ngcc0 = gcc.vcount()

    for attack in attacks:    
        
        attack_dir_name = os.path.join(net_dir_name, network, attack)

        full_output_name  = os.path.join(attack_dir_name, 'deltaBtw.txt')
        if not overwrite:
            if os.path.isfile(full_output_name):
                continue
        

        full_input_name  = os.path.join(attack_dir_name, 'btwMatrix.pickle.bz2')
        with bz2.BZ2File(full_input_name, 'r') as f:
            btwMatrix = pickle.load(f)
        
        if False:
            ### Normalize
            for i, row in enumerate(btwMatrix):
                n = Ngcc0 - i
                if n > 2:
                    btwMatrix[i] = 2*row / ((n-1)*(n-2))
                else:
                    btwMatrix[i] = 0.0*row

        ## Compute distribution parameters
        mean_values = np.mean(btwMatrix, axis=1)
        std_values = np.std(btwMatrix, axis=1)
        sum_values = np.sum(btwMatrix, axis=1)

        mean_values = np.append(mean_values, np.repeat(np.NaN, (N-len(mean_values))))
        std_values = np.append(std_values, np.repeat(np.NaN, (N-len(std_values))))
        sum_values = np.append(sum_values, np.repeat(np.NaN, (N-len(sum_values))))
        output  = os.path.join(attack_dir_name, 'btwDistParameters.txt')
        np.savetxt(output, np.array([mean_values, std_values, sum_values]).T)

        ## Compute susceptibility (sqared differences)
        btwMatrix = btwMatrix.T
        delta2_btw = np.diff(btwMatrix)**2        
        delta2_btw_sum = np.nansum(delta2_btw, axis=0)
        delta2_btw_sum = np.append(delta2_btw_sum, np.repeat(np.NaN, (N-len(delta2_btw_sum))))
        
        np.savetxt(full_output_name, delta2_btw_sum)
        