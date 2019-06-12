import igraph as ig
import numpy as np
import os
import sys

net_type = sys.argv[1]
size = int(sys.argv[2])
param = sys.argv[3]
str_f = sys.argv[4]
attack = sys.argv[5]
max_seed = int(sys.argv[6])

if 'overwrite' in sys.argv:
    overwrite = True
else:
    overwrite = False

dir_name = os.path.join('../networks', net_type)

seeds = range(max_seed)

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
    p = param
    base_net_name = 'Lattice_L{}_f{}'.format(L, p)

base_net_dir_name = os.path.join(dir_name, base_net_name)
seed_file = os.path.join(base_net_dir_name, 'comp_sizes_{}_f{}_seeds.txt'.format(attack, str_f))
if os.path.isfile(seed_file):
    if overwrite:
        os.remove(seed_file)
        past_seeds = []
    else:
        print('Passt seeds will be considered')
        past_seeds = np.loadtxt(seed_file, dtype=int)
else:
    past_seeds = np.array([])

components_file = os.path.join(base_net_dir_name, 'comp_sizes_{}_f{}.txt'.format(attack, str_f))
if os.path.isfile(components_file):
    if overwrite:
        os.remove(components_file)

new_seeds = []
for seed in seeds:

    if seed in past_seeds:
        continue

    net_name = base_net_name + '_{:05d}'.format(seed)
    print(net_name)

    net_dir_name = os.path.join(base_net_dir_name, net_name)
    
    input_name = net_name + '.txt'   
    full_input_name = os.path.join(net_dir_name, input_name)

    data_dir = os.path.join(net_dir_name, attack)

    oi_file = os.path.join(data_dir, 'oi_list_' + net_name + '.txt')
    if not os.path.isfile(oi_file):
        if overwrite:
            print("FILE " + oi_file + " NOT FOUND")
        continue
    oi_values = np.loadtxt(oi_file, dtype=int)
    new_seeds.append(seed)

    g = ig.Graph().Read_Edgelist(full_input_name, directed=False)        

    if not g.is_simple():
        print('Network "' + net_name + '" will be considered as simple.')
        g.simplify()
        
    if g.is_directed():
        print('Network "' + net_name + '" will be considered as undirected.')
        g.to_undirected()
        
    if not g.is_connected():
        print('Only giant component of network "' + net_name + '" will be considered.')
        components = g.components(mode='weak')
        g = components.giant()

    N0 = g.vcount()
    g.vs['original_index'] = range(N0)
    
    f = float(str_f)
    #for i in range(int(f*N)):
    #    oi = oi_values[i]
    #    idx = g.vs['original_index'].index(oi)
    #    g.vs[idx].delete()
    oi_values = oi_values[:int(f*N)]
    g.delete_vertices(oi_values)

    components = g.components(mode='WEAK')
    Ngcc = components.giant().vcount()
    comp_sizes = [len(c) for c in components]
    comp_sizes.remove(Ngcc)
    with open(components_file, 'a') as c_file:
        for c_size in comp_sizes:
            c_file.write('{:d}\n'.format(c_size))

new_seeds = np.array(new_seeds, dtype=int)
all_seeds = np.sort(np.concatenate((past_seeds, new_seeds)))
np.savetxt(seed_file, all_seeds, fmt='%d')