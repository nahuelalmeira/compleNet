import igraph as ig
import os
import sys

from attacks import centralityUpdateAttack, centralityUpdateAttackFast

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

dir_name = os.path.join('../networks', net_type)

seeds = range(min_seed, max_seed)

if net_type == 'ER':
    N = size
    p = param
    base_output_name = 'ER_N{}_p{}'.format(N, p)
elif net_type == 'BA':
    N = size
    m = param
    base_output_name = 'BA_N{}_m{}'.format(N, m)
elif net_type == 'Lattice':
    L = size
    p = param
    base_output_name = 'Lattice_L{}_f{}'.format(L, p)

for seed in seeds:

    output_name = base_output_name + '_{:05d}.txt'.format(seed)

    print(output_name)
    net_dir_name = os.path.join(dir_name, base_output_name, output_name[:-4])
    full_name = os.path.join(net_dir_name, output_name)

    G = ig.Graph().Read_Edgelist(full_name, directed=False)        

    if fast:
        #centralityUpdateAttackFast(G, net_dir_name, output_name[:-4], centrality='random', 
        #                        followGiant=giant, saveData=True, overwrite=overwrite)
        centralityUpdateAttackFast(G, net_dir_name, output_name[:-4], centrality='degree', 
                                followGiant=giant, saveData=True, overwrite=overwrite)
    else:
        centralityUpdateAttack(G, net_dir_name, output_name[:-4], centrality='betweenness', 
                                followGiant=giant, saveData=True, overwrite=overwrite)
        centralityUpdateAttack(G, net_dir_name, output_name[:-4], centrality='random', 
                                followGiant=giant, saveData=True, overwrite=overwrite)
        centralityUpdateAttack(G, net_dir_name, output_name[:-4], centrality='degree', 
                                followGiant=giant, saveData=True, overwrite=overwrite)