from pprint import pprint

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d
from alive_progress import alive_bar

# 常用的插值算法 ["linear", "cubic", "quadratic", "nearest"]

data = pd.read_csv('./points/github.txt', sep='\s+', names=['t', 'x', 'y'])
# data['x'] += 1
# data['y'] += 1




# f_fourier(1, 50)
x = []
y = []
with alive_bar(total=200, force_tty=True) as bar:
    for t in np.linspace(0, 2 * np.pi, 200):
        v = f_fourier(t, 50)
        x.append(v[0])
        y.append(v[1])
        bar()
plt.plot(x, y)
plt.plot(data['x'], data['y'])
plt.axis('equal')
plt.show()
