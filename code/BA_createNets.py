import os
import sys
import pickle
import pathlib
import numpy as np
import igraph as ig

N = int(sys.argv[1])
m = int(sys.argv[2])
min_seed = int(sys.argv[3])
max_seed = int(sys.argv[4])

if 'overwrite' in sys.argv:
    overwrite = True
else:
    overwrite = False

seeds = range(min_seed, max_seed)

dir_name = '../networks/BA'

for seed in seeds:
   
    output_name = 'BA_N{}_m{}_{:05d}.txt'.format(N, m, seed) 
    net_dir_name = os.path.join(dir_name, output_name[:-4])
    pathlib.Path(net_dir_name).mkdir(parents=True, exist_ok=True)
    full_name = os.path.join(net_dir_name, output_name)

    if not overwrite:
        if os.path.isfile(full_name):
            continue

    print(output_name)
    G = ig.Graph().Barabasi(N, m)
    G.write_edgelist(full_name) 