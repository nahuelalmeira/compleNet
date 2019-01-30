import os
import sys
import pickle
import igraph as ig
import numpy as np
from collections import Counter


def buildAttackPrefix(centrality, followGiant, update=True):
    """ (str, bool, bool) -> str
    Returns a string with a prefix corresponding to the 
    attack to be performed.
    
    >>> buildAttackPrefix('degree', True, True)
    'DegGU'
    >>> buildAttackPrefix('random', False, True)
    'Ran'
    >>> buildAttackPrefix('betweenness', True, False)
    'BtwG'
    """
    
    if centrality == 'degree':
        prefix = 'Deg'
    elif centrality == 'betweenness':
        prefix = 'Btw'
    elif centrality == 'random':
        prefix = 'Ran'
        
    if followGiant:
        prefix += 'G'

    if update and (centrality is not 'random'):
        prefix += 'U'
        
    return prefix

def buildFileName(output_dir, net_name, centrality, followGiant, update=True):
    """ (str, str, str, bool, bool) -> str
    
    Builds the file name according to centrality and followGiant
    parameteres.
    
    >>> buildFileName('../data', 'powergrid', 'betweenness', True, True)
    '../data/BtwGU_powergrid.txt'
    >>> buildFileName('../data', 'euroroad', 'random', False, True)
    '../data/Ran_euroroad.txt'
    >>> buildFileName('../data', 'internet', 'degree', False, False)
    '../data/Deg_internet.txt'
    """
    
    prefix = buildAttackPrefix(centrality, followGiant, update)
    file_name = output_dir + '/' + prefix + '_' + net_name + '.txt'

    return file_name

def centralityUpdateAttack(graph, data_dir, net_name, 
                           centrality='betweenness', 
                           followGiant=False, saveData=True, 
                           overwrite=False):
    """ (iGraph.Graph(), str, str, str, bool, bool) -> list 
    
    Performs a node attack based on 'centrality' restricted or not to
    the giant component.
    
    Centralities allowed: 'betweenness', 'degree', 'random'.
    
    >>> data_dir = '../data'
    >>> net_name = 'net_test'
    >>> g = ig.Graph()

    >>> g.add_vertices(16)
    >>> edge_list = [(0,1),(0,2),(0,3),(0,4),(0,7),(0,8),\
                     (1,3),(1,4),(1,5),(1,6),(2,7),(2,8),\
                     (2,10),(7,9),(10,11),(11,12),(13,14),\
                     (14,15)]
    >>> g.add_edges(edge_list)
    >>> centralityUpdateAttack(g, data_dir, net_name,\
                               centrality='degree',\
                               followGiant=False, overwrite=True)
    Only giant component of network "net_test" will be considered.
    [0, 1, 2, 11, 7]
    >>> centralityUpdateAttack(g, data_dir, net_name,\
                               centrality='degree',\
                               followGiant=True, overwrite=True)
    Only giant component of network "net_test" will be considered.
    [0, 2, 1, 11, 7]
                                    
    """
    
    if centrality not in ['degree', 'betweenness', 'random']:
        print('ERROR: centrality "', centrality, '" is not supported')
        return
    
    attackPrefix = buildAttackPrefix(centrality, followGiant)
    
    ## Create output directories if they don't exist
    output_dir = data_dir + '/' + attackPrefix
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
        #print('Creating dir ', output_dir)

    output_file = buildFileName(output_dir, net_name, centrality, followGiant)
    #print(output_file)
    if not overwrite:
        if os.path.isfile(output_file):
            print('File "' + output_file + '"\talready exist.')
            return None
    
    if saveData:
        for data in ['original_indices_values', 'btw_values', 'deg_values',
                     #'components',
                     'componentSizes']:
            if not os.path.exists(output_dir + '/' + data):
                os.mkdir(output_dir + '/' + data)
                #print('Creating dir ', output_dir + '/' + data)
    

    
    original_indices_file_base_name = output_dir + '/original_indices_values/oiValues'
    btw_file_base_name = output_dir + '/btw_values/btwValues'
    deg_file_base_name = output_dir + '/deg_values/degValues'
    #components_file_base_name = output_dir + '/components/components'
    component_sizes_file_base_name = output_dir + '/componentSizes/componentSizes'
    ## Create a copy of graph so as not to modify the original
    g = graph.copy()
    
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
        
    ## Save original index as a vertex property
    N0 = g.vcount()
    n = N0
    g.vs['original_index'] = range(n)
    
    ## List with the node original indices in removal order
    original_indices = []

    ## Relative sizes of the giant component
    s_gcc_values = []
    
    j = 0
    while True:
        
        n = g.vcount()
        
        ## Compute components
        components = g.components(mode='weak')
        gcc = components.giant()
        n_gcc = gcc.vcount()

        if n_gcc < 2:
            break

        ## Compute centrality measures
        if followGiant:
            original_indices_values = gcc.vs['original_index']
            btw_values = gcc.betweenness(directed=False)
            deg_values = gcc.degree()                
        else:
            original_indices_values = g.vs['original_index']
            btw_values = g.betweenness(directed=False)
            deg_values = g.degree()             
            
        ## Identify node to be removed
        if centrality == 'betweenness':
            idx = max(enumerate(btw_values), key=lambda x: x[1])[0]
        elif centrality == 'degree':
            idx = max(enumerate(deg_values), key=lambda x: x[1])[0]
        elif centrality == 'random':
            if followGiant:
                idx = np.random.randint(n_gcc) 
            else:
                idx = np.random.randint(n) 

        ## Add index to list
        if followGiant:
            original_idx = gcc.vs[idx]['original_index']
        else:
            original_idx = g.vs[idx]['original_index']
        original_indices.append(original_idx)

        ## Add relative size of giant component to list
        s_gcc_values.append(n_gcc/N0)
        
        if saveData:
            ## Save data in .pickle files
            if saveData != 'components':
                original_indices_file_name = original_indices_file_base_name + str(j).zfill(6) + '.pickle'
                with open(original_indices_file_name, 'wb') as f:
                    pickle.dump(original_indices_values, f)
                btw_file_name = btw_file_base_name + str(j).zfill(6) + '.pickle'
                with open(btw_file_name, 'wb') as f:
                    pickle.dump(btw_values, f)
                deg_file_name = deg_file_base_name + str(j).zfill(6) + '.pickle'
                with open(deg_file_name, 'wb') as f:
                    pickle.dump(deg_values, f)
            #components_file_name = components_file_base_name + str(j).zfill(6) + '.pickle'
            #with open(components_file_name, 'wb') as f:
            #    pickle.dump(components, f)   
            component_sizes_file_name = component_sizes_file_base_name + str(j).zfill(6) + '.txt'
            comp_sizes = [len(c) for c in components]
            counter = Counter(comp_sizes)
            sizes_arr = np.array(sorted([(s, ns) for s, ns in counter.items()], 
                                        key=lambda x: x[0], reverse=True))
            np.savetxt(component_sizes_file_name, sizes_arr, fmt='%d\t%d', header='s\tns')
            

        ## Remove node
        idx = g.vs()['original_index'].index(original_idx)
        g.vs[idx].delete()     

        j += 1
    
    steps = len(original_indices)
    data_to_file = list(zip(range(steps), original_indices, s_gcc_values))
    np.savetxt(output_file, data_to_file, fmt='%d %d %f')
    return original_indices
