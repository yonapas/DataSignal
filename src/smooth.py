import numpy as np

def running_mean(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

def movingaverage(interval, window_size):
    window = np.ones(int(window_size))/float(window_size)
    return np.convolve(interval, window, 'same')

def moving_average(x,y,step_size=10,bin_size=10):
    bin_centers  = np.arange(np.min(x),np.max(x)-0.5*step_size,step_size)+0.5*step_size
    bin_avg = np.zeros(len(bin_centers))

    for index in range(0,len(bin_centers)):
        bin_center = bin_centers[index]
        items_in_bin = y[(x>(bin_center-bin_size*0.5) ) & (x<(bin_center+bin_size*0.5))]
        bin_avg[index] = np.mean(items_in_bin)

    return bin_centers,bin_avg

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