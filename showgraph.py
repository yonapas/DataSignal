from __future__ import print_function
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.text import Text
from matplotlib.image import AxesImage
from matplotlib import backend_bases
import numpy as np

class Graph():
    """docstring for G"""
    def __init__(self):
        self.x = None
        self.y = None


    def onpick(self, event):
        self.x = event.mouseevent.xdata
        self.y = event.mouseevent.ydata
        plt.close()


    def get_xy(self):
        return self.x ,self.y

def set_plot(x,y, xf, yf, dt, N,sta, nevent, low=None, high=None):
    fig, (ax1, ax2) = plt.subplots(2, 1)

    ax1.set_title('{0} {1} ,dt:{2}'.format(sta, nevent, dt))
    ax1.set_ylabel("ACC [g]")
    ax1.set_xlabel("time [sec]")
    if low or high:
        ax2.text(0.95, 0.01, 'highpass {0} lowpass = {1}'.format(high, low),
        verticalalignment='bottom', horizontalalignment='right',
        transform=ax2.transAxes,
        color='red', fontsize=10)

    graph = Graph()
    line1 = ax1.plot(x, y, 'k', picker=2)
    line2 = ax2.loglog(xf, 2.0/N * np.abs(yf[0:N//2]), picker=2)

    fig.canvas.mpl_connect('pick_event',graph.onpick)

    plt.show()
    plt.close()
    x, y = graph.get_xy()
    return x
