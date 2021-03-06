""" Process all the hyperparameter output files in the given directory
and produce a ranking of different values based on per-layer results.

Files names look like this: hyperparam_search-<param_name>-<float value>-out

The average training error for each layer of each model is reported:

e.g Pre-training layer 0, epoch 49, cost  430.334141733

"""

import sys, re, os
import numpy as np
from collections import OrderedDict

# Extract the parameter name, value from each filename.
# Value can be in the last two parts of the match.groups() list, if it is in scientific notation.
def extract_model_name(regex,filename):
    match = regex.match(filename)
    if match is not None:
        if len(match.groups()) < 3:
            return match.groups()[0], match.groups()[1], None
        else:
            return match.groups()[0], match.groups()[1], match.groups()[2]

# Extract the layer and cost from a line
def extract_cost(line):
    first_split = line.split(",")
    layer_clause = first_split[0].split()
    cost_clause = first_split[2].split()
    layer = layer_clause[2]
    cost = cost_clause[1]
    return layer, float(cost)

# get the directory from sys.argv[1]
input_dir = sys.argv[1]

# read a list of all files in the directory that match model output files
os.chdir(input_dir)
model_files = os.listdir(".")

# compile a regex to extract the model from a given filename
# hyperparam_search-<param_name>-<float value>-out
param_keys = re.compile(".*?-([\w]+)-([\w\.]+)-?([\w]+)?-out")

# Store the results of the model search in this dictionary
### First level keys are layer id, values are dicts
### Second level keys are hyperparameter name, values are dicts
### Third level keys are hyperparameter values, values are costs
results = {}

results['0'] = {}
results['1'] = {}
results['2'] = {}
results['3'] = {}

results['0']['learning_rate'] = {}
results['0']['momentum'] = {}
results['0']['weight_decay'] = {}
results['0']['corruption'] = {}

results['1']['learning_rate'] = {}
results['1']['momentum'] = {}
results['1']['weight_decay'] = {}
results['1']['corruption'] = {}

results['2']['learning_rate'] = {}
results['2']['momentum'] = {}
results['2']['weight_decay'] = {}
results['2']['corruption'] = {}

results['3']['learning_rate'] = {}
results['3']['momentum'] = {}
results['3']['weight_decay'] = {}
results['3']['corruption'] = {}


print "...Processing files"

# for each file: 
for f in model_files:
        
    # read the file, populate these file entries in the three dicts
    hparam, value, exponent = extract_model_name(param_keys, f)
    if exponent is not None:
        value = value + "-" + exponent
    if hparam is None:
        continue
    
    infile = open(f, 'r')
    for line in infile:
        if not line.startswith("Pre-training"):
            continue
        layer, cost = extract_cost(line)
        if results[layer][hparam].has_key(value):
            results[layer][hparam][value].append(cost)
        else:
            results[layer][hparam][value] = [cost]       
    infile.close()
    
print "...Done"
    

print "...Finding the min for each layer, hyperparameter, value combination"
for layer in results.keys():
    for hparam in results[layer].keys():
        for value in results[layer][hparam].keys():
            val_list = results[layer][hparam][value]
            minval = min(val_list)
            results[layer][hparam][value] = minval

# At this point, find the top 5 scoring models in each of the dicts
# Also, compute some order statistics to qualify this list: max, min
print "...Sorting results by layer, hyperparameter"
for layer in results.keys():
    for hparam in results[layer].keys():
        d = results[layer][hparam]
        sorted_layer_results = sorted(d.items(), key=lambda t: t[1])
        sl_max = max(results[layer][hparam].values())
        sl_min = min(results[layer][hparam].values())
        print "Max, min, mean for layer " + layer + " and hyper-param " + hparam + ": " + str(sl_max) + " , " + str(sl_min) + " , " + str(np.mean(results[layer][hparam].values()))
        print "Top five archs for layer " + layer
        for value, score in sorted_layer_results:
            print value + ": " +  str(score)
        