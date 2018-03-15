import matplotlib.pyplot as plt
# import plotly.plotly as py
import numpy as np
# Learn about API authentication here: https://plot.ly/python/getting-started
# Find your api_key here: https://plot.ly/settings/api

Fs = 150.0;  # sampling rate
Ts = 1.0/Fs; # sampling interval
t = np.arange(0,4,Ts) # time vector

ff1 = 5;   # frequency of the signal
ff2 = 30
ff3 = 47
ff4 = 16
ff5 = 10
y = np.sin(2*np.pi*ff1*t) + 4*np.sin(2*np.pi*ff2*t) +13*np.sin(2*np.pi*ff3*t) + 7*np.sin(2*np.pi*ff3*t) +22*np.sin(2*np.pi*ff5*t) 

n = len(y) # length of the signal
k = np.arange(n)
T = n/Fs
frq = k/T # two sides frequency range
frq = frq[range(n/2)] # one side frequency range

Y = np.fft.fft(y)*2/n # fft computing and normalization
Y = Y[range(n/2)]

fig, ax = plt.subplots(2, 1)
ax[0].plot(t,y)
ax[0].set_xlabel('Time')
ax[0].set_ylabel('Amplitude')
ax[1].plot(frq,abs(Y),'r') # plotting the spectrum
ax[1].set_xlabel('Freq (Hz)')
ax[1].set_ylabel('|Y(freq)|')

plt.show()
#plot_url = py.plot_mpl(fig, filename='mpl-basic-fft')