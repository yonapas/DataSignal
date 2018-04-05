from __future__ import print_function
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl



class Graph():

    """docstring for G"""
    def __init__(self):
        self.x = None
        self.y = None
        self.label = None

    def onpick(self, event):
        self.x = event.mouseevent.xdata
        self.y = event.mouseevent.ydata
        self.label = event.mouseevent.inaxes._label
        plt.close()

    def get_xy(self):
        return self.label, self.x


def set_plot(x,y, xf, yf, dt, N, sta, nevent, fc, low=None, high=None, time=None):
    mpl.rcParams["lines.linewidth"] = 0.4

    fig, (ax1, ax2) = plt.subplots(2, 1)

    ax1.set_title('{0} {1} ,dt:{2}'.format(sta, nevent, dt))
    ax1.set_ylabel("ACC [g]")
    ax1.set_xlabel("time [sec]")
    ax1._label = "Time"
    ax2._label = "Frequency"
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

    graph = Graph()
    ax1.plot(x, y, 'k', picker=7)
    ax2.loglog(xf, 2.0/N * np.abs(yf[0:N//2]), "k", picker=2)
    ax2.axvline(x=fc, color='red')

    fig.canvas.mpl_connect('pick_event', graph.onpick)
    manager = plt.get_current_fig_manager()
    manager.resize(*manager.window.maxsize())

    plt.show()
    plt.close()
    x, y = graph.get_xy()
    return x, y
