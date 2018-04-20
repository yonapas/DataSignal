from __future__ import print_function
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
from matplotlib import gridspec
import smooth

class Graph():

    """docstring for G"""
    def __init__(self):
        self.x = None
        self.y = None
        self.label = None
        self.key = None

    def onpick(self, event):
        self.x = event.mouseevent.xdata
        self.y = event.mouseevent.ydata
        self.label = event.mouseevent.inaxes._label
        plt.close()
        # self.update(event.mouseevent.inaxes._label)

    def get_xy(self):
        if self.x :
            return self.label, self.x
        if self.key:
            return "reset", self.key


    def press(self, event):
        # print('press', event.key)
        self.key = event.key
        plt.close()
        # self.update("reset")



def set_plot(x,y, xf, yf, dt, N, sta, nevent, fc, low=None, high=None, time=None):
    """
    the function get time and frequency parametrs and make graphes. 
    params:
    x - time [s]
    y - acceleration [g]
    xf - frequncy
    yf - amplitude
    dt - delta time
    N - x length 
    sta - station name
    nevent - event name (data)
    fc - pradictible corner frequncy
    low (optional) - low frequncy filter
    high (optional) - high frequncy filter
    time (optional) - cut time

    return:
    press key or pick point
    """
    mpl.rcParams["lines.linewidth"] = 0.4

    yy = 2.0/N * np.abs(yf[0:N//2])
    smoo_y = smooth.smoo(yy, 101)
    # define fig size:

    fig = plt.figure(figsize=(8, 6)) 
    ax1 = plt.subplot2grid((2, 2), (0, 0), colspan=2)
    ax2 =  plt.subplot2grid((2, 2), (1, 0), colspan=1)

    # set title and label axis:
    fig.suptitle('{0} {1} ,dt:{2}'.format(sta, nevent, dt), fontsize=20)
    ax1.set_title("press Esc for reset signal", fontsize=12)
    ax1.set_ylabel("ACC [g]")
    ax1.set_xlabel("time [sec]")

    # set name for any canvas:
    ax1._label = "Time"
    ax2._label = "Frequency"

    # show low\high filter if exist:
    if low or high:
        ax2.text(0.95, 0.01, 'highpass = {0} lowpass = {1}'.format(high, low),
        verticalalignment='bottom', horizontalalignment='right',
        transform=ax2.transAxes,
        color='red', fontsize=10)
    if time:
        ax1.text(0.95, 0.01, 'cut time = {0}'.format(time),
        verticalalignment='bottom', horizontalalignment='right',
        transform=ax1.transAxes,
        color='red', fontsize=10)

    # init the press\pick option
    graph = Graph()

    # set x y axis
    ax1.plot(x, y, 'k', picker=7)
    ax2.loglog(xf, 2.0/N * np.abs(yf[0:N//2]), "k", picker=2)
    ax2.loglog(xf, smoo_y)
    ax2.axvline(x=fc, color='red')

    fig.canvas.mpl_connect('pick_event', graph.onpick)
    fig.canvas.mpl_connect('key_press_event', graph.press)

    # flot fig in maximum resoulotion
    manager = plt.get_current_fig_manager()
    manager.resize(*manager.window.maxsize())

    plt.show()
    # plt.close()
    try :
        x, y = graph.get_xy()
        return x, y
    except:
        return None, None
