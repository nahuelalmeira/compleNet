import igraph as ig
import os
import sys

from attacks import centralityUpdateAttack

L = int(sys.argv[1])
f = sys.argv[2]
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

dir_name = '../networks/Lattice'

seeds = range(min_seed, max_seed)

for seed in seeds:

    output_name = 'Lattice_L{}_f{}_{:05d}.txt'.format(L, f, seed)
    print(output_name)
    net_dir_name = os.path.join(dir_name, output_name[:-4])
    full_name = os.path.join(net_dir_name, output_name)

    G = ig.Graph().Read_Edgelist(full_name, directed=False)        

    centralityUpdateAttack(G, net_dir_name, output_name[:-4], centrality='betweenness', 
                            followGiant=giant, saveData=True, overwrite=overwrite)
    centralityUpdateAttack(G, net_dir_name, output_name[:-4], centrality='random', 
                            followGiant=giant, saveData=True, overwrite=overwrite)
    centralityUpdateAttack(G, net_dir_name, output_name[:-4], centrality='degree', 
                            followGiant=giant, saveData=True, overwrite=overwrite)