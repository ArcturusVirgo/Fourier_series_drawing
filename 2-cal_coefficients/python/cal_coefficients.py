import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from tqdm import tqdm


def sum_fourier(x, data_x, data_y, N=100, int_step=0.0005):
    # 常用的插值算法 ["linear", "cubic", "quadratic", "nearest"]
    # 二次插值
    f = interp1d(data_x, data_y, kind='quadratic')

    def f_f(x_, placeholder):
        return f(x_)

    def f_sin(x_, n_):
        return f(x_) * np.sin(n_ * x_)

    def f_cos(x_, n_):
        return f(x_) * np.cos(n_ * x_)

    def int_Simpson(fun, n_, a=0, b=2 * np.pi):
        N_ = int((b - a) / int_step)
        I_ff = fun(a, n_) + fun(b, n_)
        xx = np.linspace(a, b, N_)[:-1]
        I_ff += 2 * fun(xx, n_).sum()
        I_ff += 4 * fun(xx + int_step / 2, n_).sum()
        I_ff *= int_step / 6
        return I_ff

    a0 = int_Simpson(f_f, -1) / np.pi

    result = [a0 / 2]
    for n in range(1, N):  # 这里代表叠加多少个波
        an = int_Simpson(f_cos, n) / np.pi
        bn = int_Simpson(f_sin, n) / np.pi
        result.append(an * np.cos(n * x) + bn * np.sin(n * x))
    return result


# 导入初始数据
file_name = 'github.svg'
data = pd.read_csv(f'../../1-get_points/result/{file_name.split(".")[0]}.txt', sep='\s+', names=['t', 'x', 'y'])

t_cal = np.linspace(0, 2 * np.pi, 500)
x_cal = []
y_cal = []
data_json = {}
for v in tqdm(t_cal):
    temp_x = sum_fourier(v, data['t'], data['x'])
    temp_y = sum_fourier(v, data['t'], data['y'])
    x_cal.append(sum(temp_x))
    y_cal.append(sum(temp_y))
    data_json[v] = {'x': temp_x, 'y': temp_y}

# 存储
data_txt = pd.DataFrame({
    't': t_cal,
    'x': x_cal,
    'y': y_cal
})
data.to_csv(f'./../result/txt/{file_name.split(".")[0]}-python.txt', header=False, index=False, sep=' ')

data_json = pd.DataFrame(data_json)
data_json.to_json(f'./../result/json/{file_name.split(".")[0]}-python.json')

# 展示
plt.plot(data['x'], data['y'])
plt.plot(x_cal, y_cal)
plt.axis('equal')
plt.show()
