import os
import sys
import pickle
import pathlib
import numpy as np
import igraph as ig

L = int(sys.argv[1])
str_f = sys.argv[2]
f = float(str_f)
min_seed = int(sys.argv[3])
max_seed = int(sys.argv[4])

if 'overwrite' in sys.argv:
    overwrite = True
else:
    overwrite = False

seeds = range(min_seed, max_seed)

dir_name = '../networks/Lattice'

for seed in seeds:
   
    output_name = 'Lattice_L{}_f{}_{:05d}.txt'.format(L, str_f, seed) 
    net_dir_name = os.path.join(dir_name, output_name[:-4])
    pathlib.Path(net_dir_name).mkdir(parents=True, exist_ok=True)
    full_name = os.path.join(net_dir_name, output_name)

    if not overwrite:
        if os.path.isfile(full_name):
            continue

    print(output_name)
    G = ig.Graph().Lattice([L, L], nei=1, circular=False)
    M = G.ecount()
    edges_to_remove = np.random.choice(G.es(), int(f*M), replace=False)
    indices_to_remove = [e.index for e in edges_to_remove]
    G.delete_edges(indices_to_remove)
    G.write_edgelist(full_name) 