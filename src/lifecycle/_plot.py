# plot functions for the lifecycle management

import numpy as np
import logging

log = logging.getLogger(__name__)

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.pyplot import figure

def plot_history(self, signature):

    local_history = self.get_history(signature)

    weights = []
    skews = []
    dates = []

    for x in local_history:
        dates.append(x['timestamp'])
        if x['data_diff']:
            weights.append(x['data_diff']['weight'] * 100)
            skews.append(x['data_diff']['skew'] * 100)
        else:
            weights.append(0)
            skews.append(0)

    plt_dates = mdates.date2num(dates)

    plt.rcParams["figure.figsize"] = (10,5)
    fig, ax = plt.subplots()
    ax2 = ax.twinx()
    ax.set_ylim([0,100])
    ax2.set_ylim([-200,200])

    ax.plot_date(plt_dates, weights, 'b-')
    ax2.plot_date(plt_dates, skews)
    xfmt = mdates.DateFormatter('%d-%m %H:%M')
    ax.xaxis.set_major_formatter(xfmt)

    ax.set_xlabel('Layers')
    
    ax.set_ylabel('Weight Change %')
    ax2.set_ylabel('Skew Change %')
    ax.set_title('Model Training')

    plt.show()

def plot_changes(self,sig1,sig2):
    model_diff = self.compare_models(sig1,sig2)

    data = []
    for x in model_diff['data']['skew']:
        if x:
            data.append(x * 100)
        else:
            data.append(0)



    # Example data
    y_pos = np.arange(len(data))

    plt.rcParams["figure.figsize"] = (5,10)
    fig, ax = plt.subplots()
    ax.barh(y_pos, data, align='center', fc="lightblue", alpha=0.9)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(y_pos)
    ax.set_ylabel('Layers')
    ax.set_xlabel('Deviation %')

    leeway = 0.05
    ax.set_xlim([np.min(data)-leeway, np.max(data)+leeway])


    if len(model_diff['structure']) == 0:
        ax.set_title('Model : No structural changes')
    else:
        ax.set_title('Model : Structural changes found')

    plt.show()