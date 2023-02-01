import json
import sys

import pygame
import pandas as pd


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
    def __init__(self, screen, x_list, y_list, color=(100, 200, 200)):
        self.screen = screen
        self.color = color
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
        pygame.draw.aalines(surface=self.screen, color=self.color, closed=False,
                            points=self.points, blend=5)
        pygame.draw.circle(dot_surface, (255, 255, 255), self.end_point, 10, 0)


class Dots:
    pass

DISPLAY_SCALE = 1.25
DISPLAY_SIZE = (1920, 1080)
WINDOW_SIZE = (DISPLAY_SIZE[0] / DISPLAY_SCALE, DISPLAY_SIZE[1] / DISPLAY_SCALE)
FPS = 30  # 帧率

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
    # data_x.append(value['x'])
    # data_y.append(value['y'])
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
# window_surface = pygame.display.set_mode(pygame.FULLSCREEN)  # 设置窗口

grid_surface = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA, 32).convert_alpha()
vec_surface = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA, 32).convert_alpha()
dot_surface = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA, 32).convert_alpha()

grid = Grid(grid_surface, WINDOW_SIZE[0] / 2, WINDOW_SIZE[1] / 2, 0, WINDOW_SIZE[0], 0, WINDOW_SIZE[1])

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
    temp_vec = Vectors(vec_surface, data_x[frame_series], data_y[frame_series])
    temp_vec.draw()

    grid.draw_grid()
    window_surface.blit(grid_surface, (0, 0))
    window_surface.blit(vec_surface, (0, 0))
    window_surface.blit(dot_surface, (0, 0))
    pygame.display.update()
    clock.tick(FPS)
    frame_series += 1
    if frame_series >= frame_num:
        frame_series = 0
