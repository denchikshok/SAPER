import pygame
from grid import Grid

import os
os.environ['SDL_VIDEO_WINDOW_POS'] = '850, 100' #положение окна относительно экрана

surface = pygame.display.set_mode((600, 600))
pygame.display.set_caption('Krestiki_Noliki')

import threading

def create_thread(target): #создает отдельный поток
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()

import socket

HOST = 'localhost'
PORT = 65432

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

def receive_data():
    global turn
    while True:
        data = sock.recv(1024).decode()
        data = data.split('-')
        x, y = int(data[0]), int(data[1])
        if data[2] == 'yourturn':
            turn = True
        if data[3] == 'False':
            grid.game_over = True
        if grid.get_cell_value(x, y) == 0:
            grid.set_cell_value(x, y, 'X')
        print(data)

create_thread(receive_data)

grid = Grid()

running = True
player = 'O'
turn = False
playing = 'True'

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
RED = (255, 0, 0)

# Загрузка фонового изображения
#background_image = pygame.image.load("background.jpg").convert()

# Анимация для подсветки ячеек
def highlight_cell(cellX, cellY):
    pygame.draw.rect(surface, RED, (cellX * 200, cellY * 200, 200, 200), 4)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and not grid.game_over:
            if pygame.mouse.get_pressed()[0]: #0 означает что нажать можно только лкм
                if turn and not grid.game_over:
                    pos = pygame.mouse.get_pos()
                    cellX, cellY = pos[0] // 200, pos[1] // 200
                    grid.get_mouse(cellX, cellY, player)
                    if grid.game_over:
                        playing = 'False'
                    send_data = '{}-{}-{}-{}'.format(cellX, cellY, 'yourturn', playing).encode()
                    sock.send(send_data)
                    turn = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and grid.game_over:
                grid.clear_grid()
                grid.game_over = False
                playing = 'True'
            elif event.key == pygame.K_ESCAPE:
                running = False

    # Отрисовка фона
    surface.fill((255,255,255))

    # Отрисовка сетки
    grid.draw(surface)

    # Подсветка ячеек при наведении мыши
    pos = pygame.mouse.get_pos()
    cellX, cellY = pos[0] // 200, pos[1] // 200
    highlight_cell(cellX, cellY)

    pygame.display.flip()
