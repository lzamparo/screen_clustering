""" Process all the model training output files in the given directory
and produce a ranking of top 10 models based on per-layer results.

Files names look like this: stacked_denoising_autoencoder_800-900-300-50.2013-05-31.08:57:06.721435

The average training error for each layer of each model is reported:

e.g Pre-training layer 0, epoch 49, cost  430.334141733

Each layer transition is marked by the line: Pickling the model..."""

import sys, re, os
import numpy as np
from collections import OrderedDict

from pylab import savefig, figure, boxplot, xticks, xlabel, ylabel, title


# Extract the model name from each filename.
def extract_model_name(regex,filename):
    match = regex.match(filename)
    if match is not None:
        return match.groups()[0]

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
model_name = re.compile(".*?_([\d-]+)\.*")

# Store the results of the model search in this dictionary
### First level keys are layer id, values are dicts
### Second level keys are models, values are costs
results = OrderedDict()
results['0'] = {}
results['1'] = {}
results['2'] = {}
results['3'] = {}

print "...Processing files"

# for each file: 
for f in model_files:
    # if this file is a pkl or other file, ignore it
    if not f.startswith("stacked"):
        continue
    
    # read the file, populate this file's entry in the three dicts
    f_model = extract_model_name(model_name, f)
    if f_model is None:
        continue
    
    infile = open(f, 'r')
    for line in infile:
        if not line.startswith("Pre-training"):
            continue
        layer, cost = extract_cost(line)
        if results[layer].has_key(f_model):
            results[layer][f_model].append(cost)
        else:
            results[layer][f_model] = [cost]       
    infile.close()
    
print "...Done"
    

print "...Finding the min for each layer and model combination"
for layer in results.keys():
    for model in results[layer].keys():
        val_list = results[layer][model]
        minval = min(val_list)
        results[layer][model] = minval


# At this point, find the top 5 scoring models in each of the dicts
# Also, compute some order statistics to qualify this list: max, min

print "...Finding top 5 scoring results in each layer"
for layer in results.keys():
    d = results[layer]
    sorted_layer_results = sorted(d.items(), key=lambda t: t[1])
    sl_max = max(results[layer].values())
    sl_min = min(results[layer].values())
    print "Number of models: " + str(len(sorted_layer_results))
    print "Max, min, mean for layer " + layer + ": " + str(sl_max) + " , " + str(sl_min) + " , " + str(np.mean(results[layer].values()))
    print "Top five archs for layer " + layer
    for i in range(0,5):
        model, score = sorted_layer_results[i]
        print str(i) + ": " + model + " , " + str(score)
        