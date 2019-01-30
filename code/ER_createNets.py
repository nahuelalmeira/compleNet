import os
import sys
import pickle
import pathlib
import numpy as np
import igraph as ig

N = int(sys.argv[1])
str_p = sys.argv[2]
p = float(str_p)
min_seed = int(sys.argv[3])
max_seed = int(sys.argv[4])

if 'overwrite' in sys.argv:
    overwrite = True
else:
    overwrite = False

seeds = range(min_seed, max_seed)

dir_name = '../networks/ER'

for seed in seeds:
   
    output_name = 'ER_N{}_p{}_{:05d}.txt'.format(N, str_p, seed) 
    net_dir_name = os.path.join(dir_name, output_name[:-4])
    pathlib.Path(net_dir_name).mkdir(parents=True, exist_ok=True)
    full_name = os.path.join(net_dir_name, output_name)

    if not overwrite:
        if os.path.isfile(full_name):
            continue

    print(output_name)
    G = ig.Graph().Erdos_Renyi(N, p)
    G.write_edgelist(full_name) 