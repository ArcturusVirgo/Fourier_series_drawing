import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import svgpathtools
from tqdm import tqdm

# 主要参数
point_num = 500
file_name = 'github.svg'
path_index = 0

# 放数据
data_x = []
data_y = []

# 创建路径对象
paths = svgpathtools.svg2paths('./svg/' + file_name)[0]
path = paths[path_index]

total_length = path.length()  # 路径总长
lengths = np.linspace(0, total_length, point_num)  # 划分路径
for length in tqdm(lengths):
    t = path.ilength(length)
    data_x.append(path.point(t).real)
    data_y.append(path.point(t).imag)

# 变换 + 去重 + 保存
data = pd.DataFrame({
    't': np.linspace(0, 2*np.pi, point_num),
    'x': data_x,
    'y': data_y
})
data['x'] = data['x'] - (data['x'].max() + data['x'].min()) / 2
data['x'] = data['x'] / data['x'].max()
data['y'] = -data['y'] + (data['y'].max() + data['y'].min()) / 2
data['y'] = data['y'] / data['y'].max()
data.to_csv(f'./result/{file_name.split(".")[0]}.txt', header=False, index=False, sep=' ')

# 展示
plt.scatter(data['x'], data['y'])
plt.axis('equal')
plt.show()
