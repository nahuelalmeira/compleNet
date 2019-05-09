import os
import sys
import igraph as ig
import numpy as np
import pandas as pd

net_type = sys.argv[1]
size = int(sys.argv[2])
param = sys.argv[3]
max_seed = int(sys.argv[4])

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

if 'overwrite' in sys.argv:
    overwrite = True
else:
    overwrite = False

attacks = []
if 'BtwU' in sys.argv:
    attacks.append('BtwU')
if 'DegU' in sys.argv:
    attacks.append('DegU')
if 'Btw' in sys.argv:
    attacks.append('Btw')
if 'Deg' in sys.argv:
    attacks.append('Deg')
if 'Ran' in sys.argv:
    attacks.append('Ran')

dir_name = os.path.join('../networks', net_type)
#net_dir_name = os.path.join(dir_name, base_net_name, net_name)

for attack in attacks:
    print(attack)
    
    network_base = 'ER_N{}_p{}'.format(N, p)
    csv_file_name = os.path.join(dir_name, network_base, '{}.csv'.format(attack))
    if not overwrite:
        if os.path.isfile(csv_file_name):
            continue

    Ngcc_values = []
    Nsec_values = []
    meanS2_values = []
    #N0_values = []
    #Sgcc_values = []
    #meanS_values = []

    for seed in range(max_seed):
        
        network = network_base + '_{:05d}'.format(seed)
        attack_dir_name = os.path.join(dir_name, network_base, network, attack)
        
        full_file_name  = os.path.join(attack_dir_name, 'comp_data_' + network + '.txt')
        if not os.path.isfile(full_file_name):
            continue

        aux = np.loadtxt(full_file_name, dtype=float)
        _Ngcc_values = np.append(aux[:,0], np.repeat(1, (N-len(aux[:,0]))))
        _Nsec_values = np.append(aux[:,1], np.repeat(1, (N-len(aux[:,1]))))
        _meanS2_values = np.append(aux[:,3], np.repeat(1, (N-len(aux[:,3])))) 
        #_meanS_values = np.append(aux[:,2], np.repeat(1, (N-len(aux[:,2])))) 
        #_Sgcc_values = _Ngcc_values / np.arange(N, 0, -1)
    
        Ngcc_values.append(_Ngcc_values)
        Nsec_values.append(_Nsec_values)
        meanS2_values.append(_meanS2_values)
        #Sgcc_values.append(_Sgcc_values)
        #meanS_values.append(_meanS_values)
        #N0_values.append(_Ngcc_values[0])

    #N0[N] = np.mean(N0_values)  
    Ngcc_values = np.array(Ngcc_values)  
    d = {'t': np.arange(N)/N,  
         'Sgcc': np.mean(Ngcc_values, axis=0)/N, 
         'varSgcc': np.var(Ngcc_values, axis=0)/N,
         'Nsec': np.mean(Nsec_values, axis=0),
         'meanS2': np.nanmean(meanS2_values, axis=0),
         'binder': 1 - np.mean(Ngcc_values**4, axis=0) / (3*(np.mean(Ngcc_values**2, axis=0))**2)

         #'SgccV2': np.mean(Sgcc_values, axis=0), 
         #'varSgcc': np.var(Sgcc_values, axis=0)*np.arange(N, 0, -1),
         #'varSgccV3': np.var(Ngcc_values, axis=0)/np.mean(Ngcc_values, axis=0), 
         #'meanS': np.mean(meanS_values, axis=0),
        }

    df = pd.DataFrame(data=d)
    df.to_csv(csv_file_name)
