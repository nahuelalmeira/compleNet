import os
import sys
import pickle
import bz2
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

    output_file = buildFileName(output_dir, net_name, centrality, followGiant)
    if not overwrite:
        if os.path.isfile(output_file):
            print('File "' + output_file + '"\talready exist.')
            return None
    
    btw_file_name = output_dir + '/btwMatrix.pickle.bz2'
    deg_file_name = output_dir + '/degMatrix.pickle.bz2'
    component_sizes_file_name = output_dir + '/componentSizes.pickle.bz2'

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
    
    sorted_btw = np.zeros((N0,N0))
    sorted_deg = np.zeros((N0,N0), dtype=int)
    sizes_arrs = []

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
            btw_values = gcc.betweenness(directed=False, nobigint=False)
            deg_values = gcc.degree()                
        else:
            original_indices_values = g.vs['original_index']
            btw_values = g.betweenness(directed=False, nobigint=False)
            deg_values = g.degree()

        for i in range(len(original_indices_values)):
            oi = original_indices_values[i]
            sorted_btw[j][oi] = btw_values[i]
            sorted_deg[j][oi] = deg_values[i]

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
        
        comp_sizes = [len(c) for c in components]
        counter = Counter(comp_sizes)
        sizes_arr = np.array(sorted([(s, ns) for s, ns in counter.items()], 
                                    key=lambda x: x[0], reverse=True), dtype=int)        
        sizes_arrs.append(sizes_arr)
        
        ## Remove node
        idx = g.vs()['original_index'].index(original_idx)
        g.vs[idx].delete()     

        j += 1

    ## Save data in .pickle.bz2 files
    with bz2.BZ2File(component_sizes_file_name, 'w') as f:
        pickle.dump(sizes_arrs, f)
    with bz2.BZ2File(btw_file_name, 'w') as f:
        pickle.dump(sorted_btw, f)
    with bz2.BZ2File(deg_file_name, 'w') as f:
        pickle.dump(sorted_deg, f)

    steps = len(original_indices)
    data_to_file = list(zip(range(steps), original_indices, s_gcc_values))
    np.savetxt(output_file, data_to_file, fmt='%d %d %f')
    return original_indices

def centralityUpdateAttackFast(graph, data_dir, net_name, 
                           centrality='random', 
                           followGiant=False, saveData=True, 
                           overwrite=False):
    
    if centrality not in ['degree', 'random']:
        print('ERROR: centrality "', centrality, '" is not supported')
        return
    
    attackPrefix = buildAttackPrefix(centrality, followGiant)
    
    ## Create output directories if they don't exist
    output_dir = data_dir + '/' + attackPrefix
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    output_file = buildFileName(output_dir, net_name, centrality, followGiant)
    if not overwrite:
        if os.path.isfile(output_file):
            print('File "' + output_file + '"\talready exist.')
            return None
    
    component_sizes_file_name = output_dir + '/componentSizes.pickle.bz2'

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
    
    sizes_arrs = []

    j = 0
    while True:
        
        n = g.vcount()
        
        ## Compute components
        components = g.components(mode='weak')
        gcc = components.giant()
        n_gcc = gcc.vcount()

        if n_gcc < 2:
            break

        ## Identify node to be removed
        if centrality == 'degree':
            deg_values = g.degree()                
            #idx = max(enumerate(deg_values), key=lambda x: x[1])[0]
            idx = np.argmax(deg_values)
        elif centrality == 'random':
            idx = np.random.randint(n) 
        else:
            print('ERROR')
            return None

        ## Add index to list
        original_idx = g.vs[idx]['original_index']
        original_indices.append(original_idx)

        ## Add relative size of giant component to list
        s_gcc_values.append(n_gcc/N0)
        
        comp_sizes = [len(c) for c in components]
        counter = Counter(comp_sizes)
        sizes_arr = np.array(sorted([(s, ns) for s, ns in counter.items()], 
                                    key=lambda x: x[0], reverse=True), dtype=int)        
        sizes_arrs.append(sizes_arr)
        
        ## Remove node
        idx = g.vs()['original_index'].index(original_idx)
        g.vs[idx].delete()     

        j += 1

    ## Save data in .pickle.bz2 files
    with bz2.BZ2File(component_sizes_file_name, 'w') as f:
        pickle.dump(sizes_arrs, f)

    steps = len(original_indices)
    data_to_file = list(zip(range(steps), original_indices, s_gcc_values))
    np.savetxt(output_file, data_to_file, fmt='%d %d %f')
    return original_indices


def betweennessUpdateAttack(graph, data_dir, net_name, overwrite=False, ignore_existing=True):
        
    ## Create output directories if they don't exist
    output_dir = os.path.join(data_dir, 'BtwU') 
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    output = "oi_list_" + net_name + ".txt"
    output_file = os.path.join(output_dir, output)
    if overwrite:
        if os.path.isfile(output_file):
            print('Removing file "' + output_file)
            os.remove(output_file)

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

    j = 0

    if os.path.isfile(output_file):   
        if ignore_existing:
            print('Ignoring file "' + output_file)
            return None
        else:
            oi_values = np.loadtxt(output_file)
            for oi in oi_values:
                idx = g.vs['original_index'].index(oi)
                g.vs[idx].delete()
                original_indices.append(oi)
                j += 1
    
    with open(output_file, 'a+') as f:
    
        while j < N0:

            ## Compute betweenness
            btw_values = g.betweenness(directed=False, nobigint=False)

            ## Identify node to be removed
            idx = max(enumerate(btw_values), key=lambda x: x[1])[0]

            ## Add index to list
            original_idx = g.vs[idx]['original_index']
            original_indices.append(original_idx)

            ## Remove node
            idx = g.vs()['original_index'].index(original_idx)
            g.vs[idx].delete()     

            j += 1
            
            f.write('{}\n'.format(original_idx))
            f.flush()

    return original_indices

def updateAttack(graph, data_dir, net_name, centrality='degree', overwrite=False, ignore_existing=True):
        
    ## Create output directories if they don't exist
    if centrality == 'betweenness':
        output_dir = os.path.join(data_dir, 'BtwU')
    elif centrality == 'degree':
        output_dir = os.path.join(data_dir, 'DegU')
    elif centrality == 'random':
        import random
        output_dir = os.path.join(data_dir, 'Ran')
    else:
        print('ERROR: Centrality not supported')
        return None
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    output = "oi_list_" + net_name + ".txt"
    output_file = os.path.join(output_dir, output)
    if overwrite:
        if os.path.isfile(output_file):
            print('Removing file "' + output_file)
            os.remove(output_file)

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

    j = 0

    if os.path.isfile(output_file):   
        if ignore_existing:
            print('Ignoring file "' + output_file)
            return None
        else:
            oi_values = np.loadtxt(output_file, dtype='int')
            #for oi in oi_values:
            #    idx = g.vs['original_index'].index(oi)
            #    g.vs[idx].delete()
            #    original_indices.append(oi)
            #    j += 1
            g.delete_vertices(oi_values)
            j += len(oi_values)
    
    with open(output_file, 'a+') as f:
    
        while j < N0:

            ## Identify node to be removed
            if centrality == 'betweenness':
                c_values = g.betweenness(directed=False, nobigint=False)
                idx = max(enumerate(c_values), key=lambda x: x[1])[0]
            elif centrality == 'degree':
                c_values = g.degree()
                idx = max(enumerate(c_values), key=lambda x: x[1])[0]
            elif centrality == 'random':
                idx = int(random.random()*(N0-j))
            
            ## Add index to list
            original_idx = g.vs[idx]['original_index']
            original_indices.append(original_idx)

            ## Remove node
            idx = g.vs()['original_index'].index(original_idx)
            g.vs[idx].delete()     

            j += 1
            
            f.write('{}\n'.format(original_idx))
            f.flush()

    return original_indices

def nonUpdateAttack(graph, data_dir, net_name, centrality='degree', overwrite=False, ignore_existing=True):
        
    ## Create output directories if they don't exist
    if centrality == 'betweenness':
        output_dir = os.path.join(data_dir, 'Btw')
    elif centrality == 'degree':
        output_dir = os.path.join(data_dir, 'Deg')
    elif centrality == 'random':
        output_dir = os.path.join(data_dir, 'Ran')
    else:
        print('ERROR: Centrality not supported')
        return None
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    output = "oi_list_" + net_name + ".txt"
    output_file = os.path.join(output_dir, output)
    if overwrite:
        if os.path.isfile(output_file):
            print('Removing file "' + output_file)
            os.remove(output_file)
    else:
        if os.path.isfile(output_file):
            return

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
    n = g.vcount()
    g.vs['original_index'] = range(n)

    if centrality == 'random':
        oi_arr = np.array(range(n))
        np.random.shuffle(oi_arr)
        original_indices = oi_arr
    else:
        ## Compute centrality
        if centrality == 'betweenness':
            c_values = g.betweenness(directed=False, nobigint=False)
        elif centrality == 'degree':
            c_values = g.degree()

        ## List with the node original indices in removal order
        original_indices = list(zip(*sorted(zip(g.vs['original_index'], c_values), 
                            key=lambda x: x[1], reverse=True)))[0]

    np.savetxt(output_file, original_indices, fmt='%d')
    return original_indices

def OldcentralityUpdateAttack(graph, data_dir, net_name, 
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
            btw_values = gcc.betweenness(directed=False, nobigint=False)
            deg_values = gcc.degree()                
        else:
            original_indices_values = g.vs['original_index']
            btw_values = g.betweenness(directed=False, nobigint=False)
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
                old_original_indices_file_name = original_indices_file_base_name + str(j).zfill(6) + '.pickle.bz2'
                if os.path.isfile(old_original_indices_file_name):
                    os.remove(old_original_indices_file_name)
                original_indices_file_name = original_indices_file_base_name + str(j).zfill(6) + '.pickle'
                with open(original_indices_file_name, 'wb') as f:
                #with bz2.BZ2File(original_indices_file_name, 'w') as f:
                    pickle.dump(original_indices_values, f)

                old_btw_file_name = btw_file_base_name + str(j).zfill(6) + '.pickle.bz2'
                if os.path.isfile(old_btw_file_name):
                    os.remove(old_btw_file_name)
                btw_file_name = btw_file_base_name + str(j).zfill(6) + '.pickle'
                with open(btw_file_name, 'wb') as f:
                #with bz2.BZ2File(btw_file_name, 'w') as f:
                    pickle.dump(btw_values, f)

                old_deg_file_name = deg_file_base_name + str(j).zfill(6) + '.pickle.bz2'
                if os.path.isfile(old_deg_file_name):
                    os.remove(old_deg_file_name)
                deg_file_name = deg_file_base_name + str(j).zfill(6) + '.pickle'
                with open(deg_file_name, 'wb') as f:
                #with bz2.BZ2File(deg_file_name, 'w') as f:
                    pickle.dump(deg_values, f)

            #components_file_name = components_file_base_name + str(j).zfill(6) + '.pickle'
            #with open(components_file_name, 'wb') as f:
            #    pickle.dump(components, f)   

            old_component_sizes_file_name = component_sizes_file_base_name + str(j).zfill(6) + '.pickle.bz2'
            if os.path.isfile(old_component_sizes_file_name):
                    os.remove(old_component_sizes_file_name)
            component_sizes_file_name = component_sizes_file_base_name + str(j).zfill(6) + '.txt'
            comp_sizes = [len(c) for c in components]
            counter = Counter(comp_sizes)
            sizes_arr = np.array(sorted([(s, ns) for s, ns in counter.items()], 
                                        key=lambda x: x[0], reverse=True), dtype=int)
            np.savetxt(component_sizes_file_name, sizes_arr, fmt='%d\t%d', header='s\tns')
            #with bz2.BZ2File(component_sizes_file_name, 'w') as f:
            #        pickle.dump(sizes_arr, f)
            

        ## Remove node
        idx = g.vs()['original_index'].index(original_idx)
        g.vs[idx].delete()     

        j += 1
    

    steps = len(original_indices)
    data_to_file = list(zip(range(steps), original_indices, s_gcc_values))
    np.savetxt(output_file, data_to_file, fmt='%d %d %f')
    return original_indices