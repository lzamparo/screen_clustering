"""
 This script pre-trains a stacked de-noising auto-encoder.  
 The SdA model is either recovered from a given pickle file, or is initialized.
 
 It is based on Stacked de-noising Autoencoder models from the Bengio lab.  
 See http://deeplearning.net/tutorial/SdA.html#sda  

 For the time being, timing information is retained from the original 

"""
import cPickle
import gzip
import os
import sys
import time

import numpy

import theano
import theano.tensor as T
from theano.tensor.shared_randomstreams import RandomStreams

from mlp.logistic_sgd import LogisticRegression
from mlp.hidden_layer import HiddenLayer
from dA.AutoEncoder import AutoEncoder
from SdA import SdA

from extract_datasets import extract_unlabeled_chunkrange
from load_shared import load_data_unlabeled
from tables import openFile

from datetime import datetime

from optparse import OptionParser
import os


def pretrain_SdA(pretraining_epochs=50, pretrain_lr=0.001, batch_size=10):
    """
    
    Pretrain an SdA model for the given number of training epochs.  The model is either initialized from scratch, or 
    is reconstructed from a previously pickled model.

    :type pretraining_epochs: int
    :param pretraining_epochs: number of epoch to do pretraining

    :type pretrain_lr: float
    :param pretrain_lr: learning rate to be used during pre-training

    :type batch_size: int
    :param batch_size: train in mini-batches of this size

    """
    
    current_dir = os.getcwd()    

    os.chdir(options.dir)
    today = datetime.today()
    day = str(today.date())
    hour = str(today.time())
    output_filename = "stacked_denoising_autoencoder_pretrain." + day + "." + hour
    output_file = open(output_filename,'w')
    os.chdir(current_dir)    
    print >> output_file, "Run on " + str(datetime.now())    
    
    # Get the training data sample from the input file
    data_set_file = openFile(str(options.inputfile), mode = 'r')
    datafiles = extract_unlabeled_chunkrange(data_set_file, num_files = 10)
    train_set_x = load_data_unlabeled(datafiles)
    data_set_file.close()

    # compute number of minibatches for training, validation and testing
    n_train_batches, n_features = train_set_x.get_value(borrow=True).shape
    n_train_batches /= batch_size
    
    # numpy random generator
    numpy_rng = numpy.random.RandomState(89677)
    print '... building the model'
    
    # TODO: If -r is present, load the model from that file and skip the initialization.
    # Also, check the restorefile for an indication of how many epochs were run.  Train on only the remaining epochs.    
    # construct the stacked denoising autoencoder class

    sda = SdA(numpy_rng=numpy_rng, n_ins=n_features,
              hidden_layers_sizes=[850, 400, 50],
              n_outs=3)

    #########################
    # PRETRAINING THE MODEL #
    #########################
    print '... getting the pretraining functions'
    pretraining_fns = sda.pretraining_functions(train_set_x=train_set_x,
                                                batch_size=batch_size)

    print '... pre-training the model'
    start_time = time.clock()
    ## Pre-train layer-wise
    corruption_levels = [float(options.corruption), float(options.corruption), float(options.corruption)]
    for i in xrange(sda.n_layers):
        # pickle the current model, along with the current epoch run
        # TODO: pickling code here.
        
        for epoch in xrange(pretraining_epochs):
            # go through the training set
            c = []
            for batch_index in xrange(n_train_batches):
                c.append(pretraining_fns[i](index=batch_index,
                         corruption=corruption_levels[i],
                         lr=pretrain_lr))
            print >> output_file, 'Pre-training layer %i, epoch %d, cost ' % (i, epoch),
            print >> output_file, numpy.mean(c)

    end_time = time.clock()

    print >> output_file, ('The pretraining code for file ' +
                          os.path.split(__file__)[1] +
                          ' ran for %.2fm' % ((end_time - start_time) / 60.))


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-d", "--dir", dest="dir", help="test output directory")
    parser.add_option("-s","--savefile",dest = "savefile", help = "Save the model to this pickle file")
    parser.add_option("-r","--restorefile",dest = "restorefile", help = "Restore the model from this pickle file")
    parser.add_option("-i", "--inputfile", dest="inputfile", help="the data (hdf5 file) prepended with an absolute path")
    parser.add_option("-c", "--corruption", dest="corruption", help="use this amount of corruption for the denoising AE")
    
    (options, args) = parser.parse_args()        
    
    pretrain_SdA()