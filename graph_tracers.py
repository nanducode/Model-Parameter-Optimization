import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from os import getcwd, listdir

# Initialize the figure
plt.style.use('seaborn-darkgrid')

# create a color palette
palette = plt.get_cmap('Set1')

tracers = {}
path = getcwd() + "/data"
for run in listdir(path):
    kh = run.split("_")[0]
    if run.startswith("1000") or run.startswith("10000") or run.startswith("30000"):
        if run.endswith("_10.csv"):
            tracers[kh] = pd.read_csv(path + "/" + run).iloc[:,0]


# multiple line plot
num=0
for kh, tracer in tracers.items():
    num+=1

    # Find the right spot on the plot
    plt.subplot(3,1, num)

    # plot every groups, but discreet
    for k, tracr in tracers.items():
        plt.plot(tracr, marker='', color='grey', linewidth=0.6, alpha=0.3)

    # Plot the lineplot
    plt.plot(tracer, marker='', color=palette(num), linewidth=2.4, alpha=0.9)
plt.show()


