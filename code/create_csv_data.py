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
if 'Ran' in sys.argv:
    attacks.append('Ran')

dir_name = os.path.join('../networks', net_type)
#net_dir_name = os.path.join(dir_name, base_net_name, net_name)

for attack in attacks:
    print(attack)

    network_base = 'ER_N{}_p{}'.format(N, p)
    csv_file_name = os.path.join(dir_name, network_base, '{}_data.csv'.format(attack))
    if not overwrite:
        if os.path.isfile(csv_file_name):
            continue

    meank_values = []
    C_values = []
    Cws_values = []
    r_values = []
    l_values = []
    q_values = []

    for seed in range(max_seed):

        network = network_base + '_{:05d}'.format(seed)
        attack_dir_name = os.path.join(dir_name, network_base, network, attack)

        full_file_name  = os.path.join(attack_dir_name, 'general_data_' + network + '.txt')
        if not os.path.isfile(full_file_name):
            continue

        aux = np.loadtxt(full_file_name, dtype=float)
        n_data = len(aux)
        repeat =  np.repeat(np.NaN, (N-n_data))
        _meank_values = np.append(aux[:,0], repeat)
        _C_values     = np.append(aux[:,1], repeat)
        _Cws_values   = np.append(aux[:,2], repeat)
        _r_values     = np.append(aux[:,3], repeat)
        _l_values     = np.append(aux[:,4], repeat)
        _q_values     = np.append(aux[:,5], repeat)

        meank_values.append(_meank_values)
        C_values.append(_C_values)
        Cws_values.append(_Cws_values)
        r_values.append(_r_values)
        l_values.append(_l_values)
        q_values.append(_q_values)

    d = {
        't': np.arange(N)/N,  
        'meank': np.nanmean(meank_values, axis=0), 
        'C': np.nanmean(C_values, axis=0), 
        'Cws': np.nanmean(Cws_values, axis=0), 
        'r': np.nanmean(r_values, axis=0),
        'l': np.nanmean(l_values, axis=0),
        'q': np.nanmean(q_values, axis=0)
    }

    df = pd.DataFrame(data=d)
    df.to_csv(csv_file_name)