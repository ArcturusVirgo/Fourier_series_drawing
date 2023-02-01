import json
import math
import sys

import pygame
import pandas as pd

import time


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
    def __init__(self, screen, x_list, y_list, tracker_, color=(100, 200, 200)):
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
        temp = [(WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] / 2)]

        for i in range(self.vec_num):
            x_temp += self.x_list[i]
            y_temp += self.y_list[i]
            temp.append((x_temp + WINDOW_SIZE[0] / 2, y_temp + WINDOW_SIZE[1] / 2))
        return temp

    def draw(self):
        # pygame.draw.aalines(surface=self.screen, color=self.color, closed=False,
        #                     points=self.points, blend=5)
        for i in range(len(self.points) - 1):
            self.arrow(self.screen, self.color, self.color, self.points[i], self.points[i + 1], 2)
            # pygame.draw.circle(self.screen, (200, 200, 200), self.points[i], math.sqrt(
            #     (self.points[i + 1][0] - self.points[i][0]) ** 2 + (self.points[i + 1][1] - self.points[i][1]) ** 2),
            #                    width=1)
        self.tracker.add(self.end_point)

    @staticmethod
    # https: // blog.csdn.net / weixin_51735114 / article / details / 128319565
    def arrow(screen, lcolor, tricolor, start, end, width=2):
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
        pygame.draw.line(screen, lcolor, start, end, width=width)
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
    def __init__(self, screen, total_num, color=(23, 235, 6)):
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

    def draw(self, r=3):
        for i, point in enumerate(self.points):
            translucence_surface = pygame.Surface((2 * r, 2 * r))
            translucence_surface.fill(BLACK)
            translucence_surface.set_colorkey(BLACK)
            pygame.draw.circle(translucence_surface, self.color, (r, r), r)
            translucence_surface.set_alpha(255 - int(i / self.total_num * 200))
            self.screen.blit(translucence_surface,
                             (point[0] - r, (point[1] + r)))


BLACK = (0, 0, 0)
DISPLAY_SCALE = 1.25
DISPLAY_SIZE = (2560, 1400)
WINDOW_SIZE = (DISPLAY_SIZE[0] / DISPLAY_SCALE, DISPLAY_SIZE[1] / DISPLAY_SCALE)
FPS = 60  # 帧率

# 数据处理 ------------------------------------------
file_name = 'github'
json_file = open(f'./../2-cal_coefficients/result/json/{file_name}-python.json')
data = json.load(json_file)
json_file.close()

data_t = []
data_x = []
data_y = []
for key, value in data.items():
    data_t.append(eval(key))
    data_x.append(list(map(
        lambda x: (x * min(WINDOW_SIZE) / 2.2), value['x'])))
    data_y.append(list(map(
        lambda x: (-x * min(WINDOW_SIZE) / 2.2), value['y'])))
vector_num = len(data_x[0])
frame_num = len(data_x)

# pygame ------------------------------------------


pygame.init()  # 初始化窗口
pygame.display.set_caption('Fourier Series')  # 设置窗口标题
clock = pygame.time.Clock()  # 添加管理时钟
window_surface = pygame.display.set_mode(WINDOW_SIZE, pygame.FULLSCREEN)  # 设置窗口

grid_surface = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA, 32).convert_alpha()
vec_surface = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA, 32).convert_alpha()
tracker_surface = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA, 32).convert_alpha()

grid = Grid(grid_surface, WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] / 2, 0, WINDOW_SIZE[0], 0, WINDOW_SIZE[1])
tracker = Tracker(tracker_surface, frame_num)

frame_series = 0
while True:
    mouse_pos = pygame.mouse.get_pos()
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
    temp_vec = Vectors(vec_surface, data_x[frame_series], data_y[frame_series], tracker)
    temp_vec.draw()

    tracker.draw()

    window_surface.blit(grid_surface, (0, 0))
    window_surface.blit(vec_surface, (0, 0))
    window_surface.blit(tracker_surface, (0, 0))
    pygame.display.update()
    clock.tick(FPS)
    frame_series += 1
    if frame_series >= frame_num:
        frame_series = 0
