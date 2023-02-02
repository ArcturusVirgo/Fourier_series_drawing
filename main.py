import sys
import json
import math

import pygame
import svgpathtools
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d
from alive_progress import alive_bar
from win32api import GetSystemMetrics


class Svg2points:
    def __init__(self, filename, point_num, path_index=0, show=False):
        self.point_num = point_num
        self.file_name = filename
        self.path_index = path_index

        # 执行进程
        self.path = svgpathtools.svg2paths(f'./svg/{self.file_name}.svg')[0][path_index]
        self.data = self.get_points()
        self.save_points()
        if show:
            self.show()

    def get_points(self):
        data_x = []
        data_y = []
        total_length = self.path.length()  # 路径总长
        lengths = np.linspace(0, total_length, self.point_num)  # 划分路径
        print('正在获取点...')
        with alive_bar(self.point_num) as bar:
            for length in lengths:
                t = self.path.ilength(length)
                data_x.append(self.path.point(t).real)
                data_y.append(self.path.point(t).imag)
                bar()
        # 变换 + 去重 + 保存
        data = pd.DataFrame({
            't': np.linspace(0, 2 * np.pi, self.point_num),
            'x': data_x,
            'y': data_y
        })
        data['x'] = data['x'] - (data['x'].max() + data['x'].min()) / 2
        data['x'] = data['x'] / data['x'].max()
        data['y'] = -data['y'] + (data['y'].max() + data['y'].min()) / 2
        data['y'] = data['y'] / data['y'].max()
        return data

    def save_points(self):
        self.data.to_csv(f'./points/{self.file_name}.txt', header=False, index=False, sep=' ')

    def show(self):
        # 展示
        plt.scatter(self.data['x'], self.data['y'])
        plt.axis('equal')
        plt.show()


class CalCoeff:
    def __init__(self, svg_obj, point_num, vec_num=20, int_step=0.01):
        self.svg = svg_obj
        self.point_num = point_num
        self.vec_num = vec_num
        self.int_step = int_step
        self.t_cal = np.linspace(0, 2 * np.pi, self.point_num)
        self.x_cal = []
        self.y_cal = []

        # 执行
        self.data_json = self.cal()
        self.save_data()

    def cal(self):
        data_json = {}
        print('正在计算系数...')
        with alive_bar(self.point_num) as bar:
            for v in self.t_cal:
                temp_x = self.sum_fourier(v, self.svg.data['t'], self.svg.data['x'])
                temp_y = self.sum_fourier(v, self.svg.data['t'], self.svg.data['y'])
                self.x_cal.append(sum(temp_x))
                self.y_cal.append(sum(temp_y))
                data_json[v] = {'x': temp_x, 'y': temp_y}
                bar()
        return data_json

    def save_data(self):
        data_json = pd.DataFrame(self.data_json)
        data_json.to_json(f'./json/{self.svg.file_name}.json')

    def sum_fourier(self, x, data_x, data_y):
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
            N_ = int((b - a) / self.int_step)
            I_ff = fun(a, n_) + fun(b, n_)
            xx = np.linspace(a, b, N_)[:-1]
            I_ff += 2 * fun(xx, n_).sum()
            I_ff += 4 * fun(xx + self.int_step / 2, n_).sum()
            I_ff *= self.int_step / 6
            return I_ff

        a0 = int_Simpson(f_f, -1) / np.pi

        result = [a0 / 2]
        for n in range(1, self.vec_num):  # 这里代表叠加多少个波
            an = int_Simpson(f_cos, n) / np.pi
            bn = int_Simpson(f_sin, n) / np.pi
            result.append(an * np.cos(n * x) + bn * np.sin(n * x))
        return result


class Grid:
    def __init__(self, screen, x, y, left, right, top, bottom, step=50):
        self.x = x
        self.y = y
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
        self.screen = screen
        self.GRID_DEEP = (47, 60, 65)
        self.GRID = (15, 21, 24)
        self.BACKGROUND = (0, 0, 0)
        self.step = step

    def draw_grid(self):
        pygame.draw.rect(self.screen, self.BACKGROUND,
                         (self.left, self.top, self.right - self.left, self.bottom - self.top))
        for i in range(1, int((self.bottom - self.top) / self.step) + 1):
            if self.bottom > self.y + i * self.step > self.top:
                pygame.draw.line(self.screen, self.GRID, (self.left, self.y + i * self.step),
                                 (self.right - 1, self.y + i * self.step), width=2)
            if self.bottom > self.y - i * self.step > self.top:
                pygame.draw.line(self.screen, self.GRID, (self.left, self.y - i * self.step),
                                 (self.right - 1, self.y - i * self.step), width=2)
        for i in range(1, int((self.right - self.left) / self.step) + 1):
            if self.right > self.x + i * self.step > self.left:
                pygame.draw.line(self.screen, self.GRID, (self.x + i * self.step, self.top),
                                 (self.x + i * self.step, self.bottom - 1), width=2)
            if self.right > self.x - i * self.step > self.left:
                pygame.draw.line(self.screen, self.GRID, (self.x - i * self.step, self.top),
                                 (self.x - i * self.step, self.bottom - 1), width=2)
        # 画中心线
        pygame.draw.line(self.screen, self.GRID_DEEP, (self.left, self.y), (self.right - 1, self.y), width=2)
        pygame.draw.line(self.screen, self.GRID_DEEP, (self.x, self.top), (self.x, self.bottom - 1), width=2)


class Vectors:
    def __init__(self, window_size, screen, x_list, y_list, tracker_, color=(255, 255, 255)):
        self.window_size = window_size
        self.screen = screen
        self.color = color
        self.tracker = tracker_
        self.x_list = x_list
        self.y_list = y_list
        self.vec_num = len(self.x_list)
        self.points = self.get_points()
        self.end_point = self.points[-1]

    def get_points(self):
        x_temp = 0
        y_temp = 0
        temp = [(self.window_size[0] / 2, self.window_size[1] / 2)]

        for i in range(self.vec_num):
            x_temp += self.x_list[i]
            y_temp += self.y_list[i]
            temp.append((x_temp + self.window_size[0] / 2, y_temp + self.window_size[1] / 2))
        return temp

    def draw(self):
        for i in range(len(self.points) - 1):
            self.arrow(self.screen, self.color, self.color, self.points[i], self.points[i + 1])
        self.tracker.add(self.end_point)

    @staticmethod
    # https: // blog.csdn.net / weixin_51735114 / article / details / 128319565
    def arrow(screen, lcolor, tricolor, start, end):
        # trirad: 决定箭头三角形的大小，这里与原文作为参数传递不同，详见下方该值的初始化

        line_length = math.sqrt(math.pow(end[1] - start[1], 2) + math.pow(end[0] - start[0], 2))
        trirad = int(line_length * 1 / 10)  # 1/10数值可更换其他数值，trirad这里根据所绘箭头长度实现动态缩放其箭头三角的大小(且有上下限阈值)

        if trirad < 5:  # 增加下限阈值
            trirad = 8

        if trirad > 10:
            trirad = 10  # 增加上限阈值
        rad = math.pi / 160
        rowrad = 180  # 决定箭头三角形的顶角的大小，该值越大，顶角越小，也可自行修改数值

        # 使用aaline保证不会出现锯齿
        pygame.draw.aaline(screen, lcolor, start, end)
        rotation = (math.atan2(start[1] - end[1], end[0] - start[0])) + math.pi / 2

        # 使用终点坐标作为箭头三角形的顶点，而不是原文中继续向end终点方向延伸，下同
        pygame.draw.polygon(screen, tricolor, ((end[0],
                                                end[1]),
                                               (end[0] + trirad * math.sin(rotation - rowrad * rad),
                                                end[1] + trirad * math.cos(rotation - rowrad * rad)),
                                               (end[0] + trirad * math.sin(rotation + rowrad * rad),
                                                end[1] + trirad * math.cos(rotation + rowrad * rad))
                                               ))
        # 箭头三角形描边，消除pygame.draw.polygon绘制多边形边时出现的锯齿
        pygame.draw.aalines(screen, tricolor, True, ((end[0],
                                                      end[1]),
                                                     (end[0] + trirad * math.sin(rotation - rowrad * rad),
                                                      end[1] + trirad * math.cos(rotation - rowrad * rad)),
                                                     (end[0] + trirad * math.sin(rotation + rowrad * rad),
                                                      end[1] + trirad * math.cos(rotation + rowrad * rad))))


class Tracker:
    def __init__(self, screen, total_num, color=(249, 249, 87)):
        self.screen = screen
        self.color = color
        self.points = []
        self.total_num = total_num

    def add(self, point):
        self.points = [point] + self.points
        self.check()

    def check(self):
        if len(self.points) >= self.total_num:
            self.points.pop(-1)

    def draw(self, r=4, disappear=10):
        for i, point in enumerate(self.points):
            translucence_surface = pygame.Surface((2 * r, 2 * r))
            translucence_surface.fill((0, 0, 0))
            translucence_surface.set_colorkey((0, 0, 0))
            pygame.draw.circle(translucence_surface, self.color, (r, r), r)
            if i <= self.total_num * (disappear - 1) / disappear:
                translucence_surface.set_alpha(255)
            else:
                # translucence_surface.set_alpha(255 - int(i / self.total_num * 100))
                translucence_surface.set_alpha(
                    255 - int((disappear * i / self.total_num - (disappear - 1)) * 255))
            self.screen.blit(translucence_surface,
                             (point[0] - r, (point[1] + r)))


class Visualization:

    def __init__(self, t, coefficient=None, recalculate=True, filename=None, times=-1):
        self.window_size = (GetSystemMetrics(0), GetSystemMetrics(1))
        self.coeff = coefficient
        self.t = t
        self.times = times

        # 开始执行
        if recalculate:
            self.data = coefficient.data_json
        else:
            self.data = self.load_data(filename)
        self.t_draw, self.x_draw, self.y_draw, self.vector_num, self.frame_num = self.deal_data()
        self.run()

    def deal_data(self):
        t_draw = []
        x_draw = []
        y_draw = []
        for key, value in self.data.items():
            if type(key) == str:
                t_draw.append(eval(key))
            else:
                t_draw.append(key)
            x_draw.append(list(map(
                lambda x: (x * min(self.window_size) / 2.2), value['x'])))
            y_draw.append(list(map(
                lambda x: (-x * min(self.window_size) / 2.2), value['y'])))
        vector_num = len(x_draw[0])
        frame_num = len(y_draw)
        return t_draw, x_draw, y_draw, vector_num, frame_num

    def run(self):
        pygame.init()  # 初始化窗口
        pygame.display.set_caption('Fourier Series')  # 设置窗口标题
        clock = pygame.time.Clock()  # 添加管理时钟
        window_surface = pygame.display.set_mode(self.window_size, pygame.FULLSCREEN)  # 设置窗口
        FPS = int(self.frame_num / self.t)  # 帧率

        grid_surface = pygame.Surface(self.window_size, pygame.SRCALPHA, 32).convert_alpha()
        vec_surface = pygame.Surface(self.window_size, pygame.SRCALPHA, 32).convert_alpha()
        tracker_surface = pygame.Surface(self.window_size, pygame.SRCALPHA, 32).convert_alpha()

        grid = Grid(grid_surface, self.window_size[0] / 2, self.window_size[1] / 2, 0, self.window_size[0], 0,
                    self.window_size[1])
        tracker = Tracker(tracker_surface, self.frame_num)

        frame_series = 0
        times = 1
        is_running = True
        while is_running:
            # 获取事件并逐类响应
            for event in pygame.event.get():
                # 退出
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()
            vec_surface.fill((0, 0, 0, 0))
            tracker_surface.fill((0, 0, 0, 0))
            grid.draw_grid()
            temp_vec = Vectors(self.window_size, vec_surface, self.x_draw[frame_series], self.y_draw[frame_series],
                               tracker)
            temp_vec.draw()

            tracker.draw()

            window_surface.blit(grid_surface, (0, 0))
            window_surface.blit(vec_surface, (0, 0))
            window_surface.blit(tracker_surface, (0, 0))
            pygame.display.update()
            clock.tick(FPS)
            frame_series += 1
            if frame_series >= self.frame_num:
                frame_series = 0
                times += 1
            if times > self.times != -1:
                is_running = False

    @staticmethod
    def load_data(filename):
        json_file = open(f'./json/{filename}.json')
        data = json.load(json_file)
        json_file.close()
        return data


if __name__ == '__main__':
    svg = Svg2points('antlers', 200, 1)
    for vec in range(10, 30):
        coeff = CalCoeff(svg, 200, vec_num=vec)
        vis = Visualization(4, coeff, times=2)
