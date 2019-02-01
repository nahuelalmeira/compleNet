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
    #G = ig.Graph().Read_Edgelist(full_network_path, directed=False)
    #print(G.summary())
    
    for attack in attacks: 

        btw_by_oi_list = []
        Ngcc_values = []
            
        attack_dir_name = os.path.join(net_dir_name, network, attack)
        btw_dir         = os.path.join(attack_dir_name, 'btw_values')
        oi_dir          = os.path.join(attack_dir_name, 'original_indices_values')
        comp_sizes_dir  = os.path.join(attack_dir_name, 'componentSizes')
        
        old_full_file_name  = os.path.join(attack_dir_name, 'btw_by_oi_arr.txt')
        if os.path.isfile(old_full_file_name):
            os.remove(old_full_file_name)
        full_file_name  = os.path.join(attack_dir_name, 'btw_by_oi_arr.pickle.bz2')
        if not overwrite:
            if os.path.isfile(full_file_name):
                continue
        
        btw_files = sorted(os.listdir(btw_dir))
        oi_files = sorted(os.listdir(oi_dir))
        comp_sizes_files = sorted(os.listdir(comp_sizes_dir))
        
        for btw_file, oi_file, comp_sizes_file in zip(btw_files, oi_files, comp_sizes_files):
            
            try:
                assert(btw_file.split('.')[0][-6:] == oi_file.split('.')[0][-6:])
                assert(oi_file.split('.')[0][-6:]  == comp_sizes_file.split('.')[0][-6:])
            except:
                print(btw_file.split('.')[0][-6:], oi_file.split('.')[0][-6:], 
                      comp_sizes_file.split('.')[0][-6:])
                
            full_btw_file_path = os.path.join(btw_dir, btw_file)
            with open(full_btw_file_path, 'rb') as f:
                btw_values = pickle.load(f)
                
            full_oi_file_path = os.path.join(oi_dir, oi_file)
            with open(full_oi_file_path, 'rb') as f:
                oi_values = pickle.load(f)
                
            full_comp_sizes_file_path = os.path.join(comp_sizes_dir, comp_sizes_file)    
            comp_sizes = np.loadtxt(full_comp_sizes_file_path, dtype=int)
            try:
                Ngcc = comp_sizes[0][0]
            except:
                Ngcc = comp_sizes[0]
            
            Ngcc_values.append(Ngcc)
            
            btw_dict = dict(zip(range(N), [np.NaN]*N))
            for oi, btw in zip(oi_values, btw_values):
                if Ngcc <= 2:
                    btw_dict[oi] = np.NaN
                else:
                    if giant:
                        btw_dict[oi] = 2* btw / ((Ngcc-1)*(Ngcc-2))
                    else:
                        btw_dict[oi] = 2* btw / ((N-1)*(N-2))

            btw_by_oi = list(zip(*sorted(btw_dict.items(), key=lambda x: x [0])))[1]

            btw_by_oi_list.append(btw_by_oi)
        
        Ngcc_values = np.array(Ngcc_values + [1]*(N-len(Ngcc_values)))
        btw_by_oi_arr = np.array(btw_by_oi_list).T
        
        with bz2.BZ2File(full_file_name, 'w') as f:
            pickle.dump(btw_by_oi_arr, f)
        #np.savetxt(full_file_name, btw_by_oi_arr)
        np.savetxt(os.path.join(attack_dir_name, 'Ngcc_values.txt'), Ngcc_values, fmt='%d')