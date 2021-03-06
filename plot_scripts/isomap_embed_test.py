from sklearn import metrics
from sklearn.mixture import GMM
from sklearn.preprocessing import scale
from sklearn.manifold import Isomap

import logging, os
from optparse import OptionParser
import sys
from time import time

import numpy as np
import pandas as pd
from tables import *
from extract_datasets import extract_labeled_chunkrange

# Display progress logs on stdout
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

# parse commandline arguments
op = OptionParser()
op.add_option("--h5file",
              dest="inputfile", help="Read data input from this hdf5 file.")
op.add_option("--output",
              dest="outputfile", help="Write matrix to .npy output file.")
op.add_option("--size",
              dest="size", type="int", help="Extract the first size chunks of the data set and labels.")
op.add_option("--high",
              dest="high", type="int", help="Start at high dimensions.")
op.add_option("--low",
              dest="low", type="int", help="End at low dimensions.")
op.add_option("--step",
              dest="step", type="int", help="Go from high to low by step sizes")
op.add_option("--iters",
              dest="iters", type="int", help="Do this many iterations of k-means clustering")

(opts, args) = op.parse_args()


np.random.seed(0)

###############################################################################
# Load a training set from the given .h5 file
datafile = openFile(opts.inputfile, mode = "r", title = "Data is stored here")

# Extract some of the dataset from the datafile
X, labels = extract_labeled_chunkrange(datafile, opts.size)

# Remove the first four indexing features introduced by CP
X = X[:,5:-1]

true_k =  np.unique(labels[:,0]).shape[0]

# done, close h5 files
datafile.close()

###############################################################################

# Build the output arrays
cells = opts.high / opts.step
isomap_gmm_results = np.zeros((cells,opts.iters))

D = scale(X)

n_samples, n_features = D.shape
# chosen by hyperparam search in a separate test.
n_neighbors = 10

# For the specified number of principal components, do the clustering
dimension_list = range(opts.low, opts.high + 1, opts.step)
data_files = []
for i in dimension_list:
    index = (i / opts.step) - 1 
    isomap = Isomap(n_neighbors, n_components=i)
    X_iso = isomap.fit_transform(D)
     
    for j in range(0,opts.iters,1): 
        gaussmix = GMM(n_components=true_k, covariance_type='tied', n_init=10, n_iter=1000)
        gaussmix.fit(X_iso)
        gaussmix_labels = gaussmix.predict(X_iso)
        homog = metrics.homogeneity_score(labels[:,0], gaussmix_labels)
        print "Homogeneity: %0.3f" % homog
        test_result = {"Model": 'Isomap', "Dimension": i, "Homogeneity": homog, "Trial": j}
        index = pd.Index([0], name='rows')
        data_files.append(pd.DataFrame(data=test_result,index=index))
        
print "...Done"
print "...rbinding DataFrames"
master_df = data_files[0]
for i in xrange(1,len(data_files)):
    master_df = master_df.append(data_files[i])
print "...Done"    
outfilename = opts.outputfile+".csv"
master_df.to_csv(path_or_buf=outfilename,index=False)