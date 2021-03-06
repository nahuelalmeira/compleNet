import os
import sys
import pickle
import bz2
import numpy as np
import igraph as ig
from collections import Counter

def counterToList(counter):

    try:
        counter[0][0]
    except:
        return [counter[0]]

    lst = []
    for s, ns in counter:
        lst += [s]*ns
    return sorted(lst, reverse=True)

def normalizedAvgSize(comp_sizes):
    if len(comp_sizes) < 2:
        return np.NaN

    counter = Counter(comp_sizes[1:])
    
    numerator = denominator = 0
    for size, n in counter.items():
        numerator += n*size*size
        denominator += n*size
    
    return numerator/denominator


def avgSize(comp_sizes):
    if len(comp_sizes) < 2:
        return np.NaN

    counter = Counter(comp_sizes[1:])
    
    numerator = denominator = 0
    for size, n in counter.items():
        numerator += n*size*size
        denominator += n*size
    
    return numerator
    
def binderCumulant(comp_sizes):
    if len(comp_sizes) < 2:
        return np.NaN
    
    counter = Counter(comp_sizes[1:])
    
    s_forth = s_second = norm = 0
    for size, n in counter.items():
        s_forth += n*np.power(size, 5)
        s_second += n*np.power(size, 3)
        norm += n*size
    
    return 1 - norm*s_forth/(3*s_second*s_second)

def binderCumulant2(comp_sizes):
    if len(comp_sizes) < 2:
        return np.NaN
    
    comp_sizes = np.array(comp_sizes[1:])
    s_forth = np.mean(comp_sizes**4)
    s_second = np.mean(comp_sizes**2)
    
    return 1 - s_forth/(3*s_second*s_second)

def binderCumulant3(comp_sizes):
    if len(comp_sizes) < 2:
        return np.NaN
    
    comp_sizes = np.array(comp_sizes[1:])
    s_second = np.mean(comp_sizes**2)
    s_third = np.mean(comp_sizes**3)
    
    return s_second*s_second / s_third

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

if 'fast' in sys.argv:
    fast = True
else:
    fast = False

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

if giant:
    if fast:
        attacks = ['DegGU', 'RanG']
    else:
        attacks = ['BtwGU', 'DegGU', 'RanG']
else:
    if fast:
        attacks = ['DegU', 'Ran']
    else:
        attacks = ['BtwU', 'DegU', 'Ran']

for seed in seeds:

    network = base_net_name + '_{:05d}'.format(seed)
    print(network)
    network_file = network + '.txt'
    full_network_path = os.path.join(net_dir_name, network, network_file)
    
    for attack in attacks: 

        meanS_values = []
        meanS2_values = []
        binder_values = []
        binder2_values = []
        binder3_values = []
        Ngcc_values = []
        Nsec_values = []
            
        attack_dir_name = os.path.join(net_dir_name, network, attack)
        comp_sizes_file  = os.path.join(attack_dir_name, 'componentSizes.pickle.bz2')
        with bz2.BZ2File(comp_sizes_file, 'r') as f:
            comp_sizes_values = pickle.load(f)
        
        full_file_name  = os.path.join(attack_dir_name, 'finiteClusters.txt')
        if not overwrite:
            if os.path.isfile(full_file_name):
                continue

        for comp_sizes in comp_sizes_values:
            
            comp_sizes_lst = counterToList(comp_sizes)
            Ngcc = comp_sizes_lst[0]
            if len(comp_sizes_lst) > 1:
                Nsec = comp_sizes_lst[1]
            else:
                Nsec = 0

            Ngcc_values.append(Ngcc)
            Nsec_values.append(Nsec)

            meanS = normalizedAvgSize(comp_sizes_lst)
            meanS2 = avgSize(comp_sizes_lst)
            binder = binderCumulant(comp_sizes_lst)
            binder2 = binderCumulant2(comp_sizes_lst)
            binder3 = binderCumulant3(comp_sizes_lst)

            meanS_values.append(meanS)
            meanS2_values.append(meanS2)
            binder_values.append(binder)
            binder2_values.append(binder2)
            binder3_values.append(binder3)

        Ngcc_values = np.array(Ngcc_values + [1]*(N-len(Ngcc_values)), dtype=int)
        Nsec_values = np.array(Nsec_values + [1]*(N-len(Nsec_values)), dtype=int)
        meanS_values = np.array(meanS_values + [np.NaN]*(N-len(meanS_values)))
        meanS2_values = np.array(meanS2_values + [np.NaN]*(N-len(meanS2_values)))
        binder_values = np.array(binder_values + [np.NaN]*(N-len(binder_values)))
        binder2_values = np.array(binder2_values + [np.NaN]*(N-len(binder2_values)))
        binder3_values = np.array(binder3_values + [np.NaN]*(N-len(binder3_values)))

        header = 'meanS meanS2 binder binder2 binder3'
        finiteClusterMeassures = np.array([meanS_values, meanS2_values, binder_values, binder2_values, binder3_values]).T
        np.savetxt(full_file_name, finiteClusterMeassures, header=header)
        np.savetxt(os.path.join(attack_dir_name, 'Ngcc_values.txt'), 
                   np.array([Ngcc_values, Nsec_values], dtype=int).T, fmt='%d %d', header='Ngcc Nsec')
