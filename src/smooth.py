import numpy as np
from numba import jit

@jit
def smoo(y, window):
    a = np.zeros(len(y))

    for i in range(len(y)):
        if a[i] == 0:
            win = y[i:i+window]
            average = win.sum()/ len(win)
            a[i:i+window] = average
        else:
            continue
    return a 