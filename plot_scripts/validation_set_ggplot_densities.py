# coding: utf-8
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pylab as pylab
import matplotlib.pyplot as plt

from scipy.stats import gaussian_kde
import husl

#################### Plotting functions to make the subplots pretty ####################  
def husl_gen():
    '''Generate random set of HUSL colors, one dark, one light'''
    hue = np.random.randint(0, 360)
    saturation, lightness = np.random.randint(0, 100, 2)
    husl_dark = husl.husl_to_hex(hue, saturation, lightness/3)
    husl_light = husl.husl_to_hex(hue, saturation, lightness)
    return husl_dark, husl_light

def rstyle(ax): 
    '''Styles x,y axes to appear like ggplot2
    Must be called after all plot and axis manipulation operations have been 
    carried out (needs to know final tick spacing)
    '''
    #Set the style of the major and minor grid lines, filled blocks
    ax.grid(True, 'major', color='w', linestyle='-', linewidth=1.4)
    ax.grid(True, 'minor', color='0.99', linestyle='-', linewidth=0.7)
    ax.patch.set_facecolor('0.90')
    ax.set_axisbelow(True)
    
    #Set minor tick spacing to 1/2 of the major ticks
    ax.xaxis.set_minor_locator((pylab.MultipleLocator((plt.xticks()[0][1]
                                -plt.xticks()[0][0]) / 2.0 )))
    ax.yaxis.set_minor_locator((pylab.MultipleLocator((plt.yticks()[0][1]
                                -plt.yticks()[0][0]) / 2.0 )))
    
    #Remove axis border
    for child in ax.get_children():
        if isinstance(child, matplotlib.spines.Spine):
            child.set_alpha(0)
       
    #Restyle the tick lines
    for line in ax.get_xticklines() + ax.get_yticklines():
        line.set_markersize(5)
        line.set_color("gray")
        line.set_markeredgewidth(1.4)
    
    #Remove the minor tick lines    
    for line in (ax.xaxis.get_ticklines(minor=True) + 
                 ax.yaxis.get_ticklines(minor=True)):
        line.set_markersize(0)
    
    #Only show bottom left ticks, pointing out of axis
    plt.rcParams['xtick.direction'] = 'out'
    plt.rcParams['ytick.direction'] = 'out'
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

def rfill_between(ax, x_range, dist, label, **kwargs):
    '''Create a distribution fill with default parameters to resemble ggplot2
    kwargs can be passed to change other parameters
    '''
    husl_dark_hex, husl_light_hex = husl_gen()
    defaults = {'color': husl_dark_hex,
                'facecolor': husl_light_hex,
                'linewidth' : 2.0, 
                'alpha': 0.2}
                
    for x,y in defaults.iteritems():
        kwargs.setdefault(x, y)
    
    ax.plot(x_range, dist, label=label,  antialiased=True)       
    return ax.fill_between(x_range, dist, **kwargs)

def make_x_axis(vals,granularity=500):
    ''' Take an Series of a DataFrame, return an appropriately scaled x-axis sampled at granularity points for plotting '''
    return np.linspace(vals.min(), vals.max(), granularity)

def make_kde(vals):
    ''' Return a scipy.stats.gaussian_kde object, but shrink the default bandwidth '''
    gkde = gaussian_kde(vals)
    gkde.silverman_factor()
    return gkde


#################### The script part to generate the plots, and find the limits ####################

from tables import *
from extract_datasets import extract_labeled_chunkrange    
import pickle as pkl

# AreaShape feature names for both Cells and Nuclei; choose one for reduction
# I removed EulerNumber,Orientation from either Nuclei or Cells thresholds; they're uninformative
cells_areashape_names = ["Cells_AreaShape_Area","Cells_AreaShape_Eccentricity","Cells_AreaShape_Solidity","Cells_AreaShape_Extent","Cells_AreaShape_Perimeter","Cells_AreaShape_FormFactor","Cells_AreaShape_MajorAxisLength","Cells_AreaShape_MinorAxisLength"]
nuclei_areashape_names = ["Nuclei_AreaShape_Area","Nuclei_AreaShape_Eccentricity","Nuclei_AreaShape_Solidity","Nuclei_AreaShape_Extent","Nuclei_AreaShape_Perimeter","Nuclei_AreaShape_FormFactor","Nuclei_AreaShape_MajorAxisLength","Nuclei_AreaShape_MinorAxisLength"]

# Grab the headers for the AreaShape features
header_file = open('/data/sm_rep1_screen/Object_Headers_trimmed.txt')
headers = header_file.readlines()
headers = [item.strip() for item in headers]
positions = [headers.index(name) for name in cells_areashape_names]
labeled_shape_data_headers = [headers[pos] for pos in positions]
header_file.close()

# Grab the validation data and labels, select only those positions we want
data_file = openFile('/data/sm_rep1_screen/sample.h5','r')
nodes = data_file.listNodes('/recarrays')
data,labels = extract_labeled_chunkrange(data_file,11)
labels = labels[:,0]
label_names = {0.: 'WT', 1.: "Focus", 2.: "Non-round nucleus", 3.: "Bizarro"}
label_str = [label_names[val] for val in labels]
shape_data = data[:,positions]
data_file.close()

# Form & concatenate the label DF with the data DF
labels_pd = pd.DataFrame({'labels': label_str})
data = pd.DataFrame(shape_data, columns=labeled_shape_data_headers)
labeled_data = pd.concat([labels_pd,data],axis=1)

# Go through the features, calculate the thresholds
thresholds = {}
for feature in labeled_shape_data_headers:
    wt_mean = labeled_data[feature].where(labeled_data['labels'] == 'WT').mean()
    wt_std = labeled_data[feature].where(labeled_data['labels'] == 'WT').std()
    lower,upper = wt_mean - 2*wt_std, wt_mean + 2*wt_std
    thresholds[feature] = (lower,upper)

# Pickle the thresholds, along with their column positions
filename = labeled_shape_data_headers[0].split('_')[0] + "_" + "thresholds.pkl"
pkl.dump((zip(positions,labeled_shape_data_headers),thresholds), open(filename,'wb'))


####################  Plot the data and thresholds ####################

# We only care about these labels
labels_used = ["WT", "Focus", "Non-round nucleus"]

# Try a faceted density plot for each feature
fig = plt.figure()
for n,key in enumerate(thresholds.keys()):
    lower,upper = thresholds[key]
    sp = fig.add_subplot(4,2,n+1)
    x_vals = make_x_axis(labeled_data[labeled_data['labels'] == "WT"][key])
    # plot all labels worth of densities, as well as the thresholds
    for label in labels_used:
        data = labeled_data[labeled_data['labels'] == label][key]
        kde = make_kde(data)
        rfill_between(sp, x_vals, kde(x_vals),label)
    sp.set_title(key)
    sp.axvline(lower,ls='--',color='k')
    sp.axvline(upper,ls='--',color='k')
    rstyle(sp)

# Put a legend below current axis
sp.legend(loc='upper center', bbox_to_anchor=(-0.25, -0.15),
          fancybox=True, shadow=True, ncol=4)

# Put a title on the main figure
fig.suptitle("Area and Shape Parameter Density Plots by Label (with 2 x std WT dashed)",fontsize=20)
fig.subplots_adjust(hspace=0.35)
plt.show()     
