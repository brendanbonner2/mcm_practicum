# plot functions for the lifecycle management

from deepdiff.serialization import MODULE_NOT_FOUND_MSG
import numpy as np
import logging

log = logging.getLogger(__name__)

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.pyplot import figure

# For interactive history
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets

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

    print(model_diff)
    skew_data = []
    weight_data = []
    for x in model_diff['data']['weight']:
        if x:
            weight_data.append(x * 100)
        else:
            weight_data.append(0)

    for x in model_diff['data']['skew']:
        if x:
            skew_data.append(x)
        else:
            skew_data.append(0)



    # Example data
    y_pos = np.arange(len(weight_data))
    leeway = 0.05

    plt.rcParams["figure.figsize"] = (5,10)
    fig, axs = plt.subplots(1,2)
    axs[0].barh(y_pos, weight_data, align='center', fc="blue", alpha=0.5)
    axs[0].set_yticks(y_pos)
    axs[0].set_yticklabels(y_pos)
    axs[0].set_ylabel('Layers')
    axs[0].set_xlabel('Weight  %')
    axs[0].set_xlim([np.min(weight_data)-leeway, np.max(weight_data)+leeway])

    axs[1].barh(y_pos, skew_data, align='center', fc="orange", alpha=0.5)
    axs[1].set_yticks(y_pos)
    axs[1].set_yticklabels(y_pos)
    axs[1].set_ylabel('Layers')
    axs[1].set_xlabel('Skew Diff')
    axs[1].set_xlim([np.min(skew_data)-leeway, np.max(skew_data)+leeway])


    if len(model_diff['structure']) == 0:
        axs[0].set_title('Model : No structural changes')
    else:
        axs[0].set_title('Model : Structural changes found')

    plt.show()

def my_plot_func(self, value):
    disptime = value -1
    fig, axs = plt.subplots(2,8)
    layers = len(self.fig_full_weight[0])
    x = np.arange(0, layers)
    axs[0].grid(True)
    axs[1].grid(True)

    y_weight = self.fig_full_weight[disptime]
    y_skew = self.fig_full_skew[disptime]

    y = self.fig_full_weight[disptime]
    axs[0].set_ylim(0, self.fig_max_weight*1.1)
    axs[1].set_ylim(0, self.fig_max_skew*1.1)
    axs[0].set_title(self.fig_full_date[disptime])
    axs[1].bar(x, y_skew, color='red', alpha=0.4)
    axs[0].bar(x, y_weight, alpha=0.8)


def plot_interactive_history(self,sig):

    history = self.get_history(sig, full_data=True)

    full_weight = []
    full_skew = []
    full_date = []

    for m in history:

        date = m['timestamp']

        if m['data']:
            graph_data_weight = []
            graph_data_skew = []
            for k,v in m['data'].items():
                graph_data_weight.append(v['weight_std'])
                graph_data_skew.append(v['skew'])
        full_weight.append(graph_data_weight)
        full_skew.append(graph_data_skew)
        full_date.append(date)

    # put all values in class for printing
    self.fig_full_weight = full_weight
    self.fig_full_skew = full_skew
    self.fig_full_date = full_date

    fig_history_size = len(full_weight)
    self.fig_max_weight = np.max(full_weight)
    self.fig_max_skew = np.max(full_skew)
    print('History Size', fig_history_size)

    interact(self.my_plot_func, value = widgets.IntSlider(value=1, min=1, max=fig_history_size,step=1))
