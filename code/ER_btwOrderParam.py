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

if giant:
    attacks = ['BtwGU', 'DegGU', 'RanG']
else:
    attacks = ['BtwU', 'DegU', 'Ran']
net_dir_name = '../networks/ER'

for seed in range(min_seed, max_seed):

    network = 'ER_N{}_p{}_{:05d}'.format(N, p, seed)
    print(network)
    network_file = network + '.txt'
    full_network_path = os.path.join(net_dir_name, network, network_file)

    for attack in attacks:    
        
        attack_dir_name = os.path.join(net_dir_name, network, attack)

        full_output_name = os.path.join(attack_dir_name, 'orderParams.txt')
        if not overwrite:
            if os.path.isfile(full_output_name):
                continue

        full_input_name  = os.path.join(attack_dir_name, 'btwMatrix.pickle.bz2')
        with bz2.BZ2File(full_input_name, 'r') as f:
            btw_matrix = pickle.load(f)

        spin_data = []
       
        for mode in range(5):

            spin_matrix = np.nan_to_num(btw_matrix, copy=True)

            if mode == 0:
                # s_i^t = b_i^t
                for t in range(len(btw_matrix)):
                    for i in range(len(btw_matrix[0])):
                        spin_matrix[t][i] = btw_matrix[t][i]

            if False:
                if mode == 0:
                    # s_i^t = b_i^t
                    for t, row in enumerate(spin_matrix):
                        for i, b_i_t in enumerate(row):
                            spin_matrix[t][i] = b_i_t

            if mode == 1:
                # s_i^t = b_i^t / b_i^0
                for t in range(len(btw_matrix)):
                    for i in range(len(btw_matrix[0])):
                        b_i_t = btw_matrix[t][i]
                        b_i_0 = btw_matrix[0][i]
                        if b_i_0 != 0:
                            spin_matrix[t][i] = b_i_t / b_i_0
                        else:
                            spin_matrix[t][i] = 0.0

            if False:
                if mode == 1:
                    # s_i^t = b_i^t / b_i^0
                    for t, row in enumerate(spin_matrix):
                        for i, b_i_t in enumerate(row):
                            b_i_0 = spin_matrix[0][i]
                            if b_i_0 != 0:
                                spin_matrix[t][i] = b_i_t / b_i_0
                            else:
                                spin_matrix[t][i] = 0.0

            if mode == 2:
                # s_i^t = b_i^{t+1} / b_i^t
                for t, row in enumerate(btw_matrix):
                    if t == len(btw_matrix):
                        spin_matrix[t] = [0.0 for elem in btw_matrix[t]]
                        break
                    for i, b_t in enumerate(row):
                        if b_t != 0:
                            spin_matrix[t][i] = btw_matrix[t+1][i] / b_t

            if mode == 3:
                # s_i^t = ln( (b_i^t + 1) / (<b^t> + 1) )
                for t, row in enumerate(btw_matrix):
                    mean_b_t = np.mean(row)
                    for i, b_t in enumerate(row):
                        spin_matrix[t][i] = np.log((b_t + 1) / (mean_b_t + 1))

            if mode == 4:
                # s_i^t = tanh(b_i^t / <b^t>)
                for t, row in enumerate(btw_matrix):
                    mean_b_t = np.mean(row)
                    for i, b_t in enumerate(row):
                        if mean_b_t > 0:
                            spin_matrix[t][i] = np.tanh(b_t / mean_b_t)
                        else:
                            spin_matrix[t][i] = 0

            spin_sum = np.sum(spin_matrix, axis=1)
            spin_sum = np.append(spin_sum, np.repeat(np.NaN, (N-len(spin_sum))))
            spin_data.append(spin_sum)

        spin_data = np.array(spin_data)
        output = spin_data.T
        np.savetxt(full_output_name, output)
        