import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('../计算傅立叶系数/fortan/res-100.txt', sep='\s+', names=['x', 'y'])
df2 = pd.read_csv('../get_points/points.txt', sep='\s+', names=['x', 'y'])
print(df['y'].name)
plt.plot(df2['x'], df2['y'])
plt.plot(df['x'], df['y'])
plt.axis('equal')
plt.show()