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

seeds = range(min_seed, max_seed)

if giant:
    attacks = ['BtwGU', 'DegGU', 'RanG']
else:
    attacks = ['BtwU', 'DegU', 'Ran']
net_dir_name = '../networks/ER'

for seed in seeds:

    network = 'ER_N{}_p{}_{:05d}'.format(N, p, seed)
    print(network)
    network_file = network + '.txt'
    full_network_path = os.path.join(net_dir_name, network, network_file)
    
    for attack in attacks: 
           
        attack_dir_name = os.path.join(net_dir_name, network, attack)
        btw_dir         = os.path.join(attack_dir_name, 'btw_values')

        full_file_name  = os.path.join(attack_dir_name, 'btwDistData.txt')
        if not overwrite:
            if os.path.isfile(full_file_name):
                continue
        
        btwDistData = []

        btw_files = sorted(os.listdir(btw_dir))       
        for btw_file in btw_files:

            full_btw_file_path = os.path.join(btw_dir, btw_file)
            with open(full_btw_file_path, 'rb') as f:
                btw_values = pickle.load(f)
            
            mean = np.mean(btw_values)
            std = np.std(btw_values)
            CV = std / mean
            data = [mean, std, CV]
            btwDistData.append(data)

        btwDistData += [[0.0, 0.0, np.NaN]]*(N-len(btwDistData))

        assert(len(btwDistData) == N)
        np.savetxt(full_file_name, btwDistData)
