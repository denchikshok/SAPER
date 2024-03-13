import pygame
from grid import Grid
import os

os.environ['SDL_VIDEO_WINDOW_POS'] = '850, 100'  # положение окна относительно экрана

surface = pygame.display.set_mode((600, 600))
pygame.display.set_caption('Krestiki_Noliki')

import threading

pygame.init()


def create_thread(target):  # создает отдельный поток
    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()


import socket

HOST = 'localhost'
PORT = 65432

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

def show_winner(winner):
    font = pygame.font.Font(None, 36)
    text = font.render(f"Player {winner} wins!", True, (255, 0, 0))
    text_rect = text.get_rect(center=(300, 300))
    surface.blit(text, text_rect)
    pygame.display.flip()

def receive_data():
    global turn
    while True:
        data = sock.recv(1024).decode()
        data = data.split('-')
        if data[0] == 'X':
            # Обработка сообщения о победе
            show_winner(data[1])  # Показать сообщение о победе
            grid.game_over = True  # Установить флаг конца игры
        else:
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
winner_message_shown = False  # Переменная состояния для отображения сообщения о победе

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
RED = (255, 0, 0)


# Анимация для подсветки ячеек
def highlight_cell(cellX, cellY):
    pygame.draw.rect(surface, RED, (cellX * 200, cellY * 200, 200, 200), 4)


def show_message(surface, message):
    font = pygame.font.Font(None, 36)
    text = font.render(message, True, (255, 0, 0))
    text_rect = text.get_rect(center=(300, 300))

    # Определим размер рамки
    border_width = 50  # Увеличим ширину рамки
    border_rect = pygame.Rect(text_rect.left - border_width, text_rect.top - border_width,
                              text_rect.width + 2 * border_width, text_rect.height + 80)
    # Заливка фона белым цветом
    pygame.draw.rect(surface, (255, 255, 255), border_rect)

    # Рисуем рамку вокруг текста
    pygame.draw.rect(surface, (0, 0, 0), border_rect, 3)

    # Отображаем текст
    surface.blit(text, text_rect)

    # Добавляем текст "Нажмите Пробел для начала заново"
    font = pygame.font.Font(None, 24)
    restart_text = font.render("Нажмите Пробел, чтобы начать заново", True, (0, 0, 0))
    restart_rect = restart_text.get_rect(center=(300, 340))
    surface.blit(restart_text, restart_rect)

    pygame.display.flip()


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and not grid.game_over:
            if pygame.mouse.get_pressed()[0]:  # 0 означает что нажать можно только лкм
                if turn and not grid.game_over:
                    pos = pygame.mouse.get_pos()
                    cellX, cellY = pos[0] // 200, pos[1] // 200
                    grid.get_mouse(cellX, cellY, player)
                    if grid.game_over:
                        playing = 'False'
                        winner_message_shown = True  # Устанавливаем флаг отображения сообщения о победе
                    send_data = '{}-{}-{}-{}'.format(cellX, cellY, 'yourturn', playing).encode()
                    sock.send(send_data)
                    turn = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and grid.game_over:
                grid.clear_grid()
                grid.game_over = False
                playing = 'True'
                winner_message_shown = False  # Сбрасываем флаг отображения сообщения о победе
            elif event.key == pygame.K_ESCAPE:
                running = False

    # Отрисовка фона
    surface.fill((255, 255, 255))

    # Отрисовка сетки
    grid.draw(surface)

    # Подсветка ячеек при наведении мыши
    pos = pygame.mouse.get_pos()
    cellX, cellY = pos[0] // 200, pos[1] // 200
    highlight_cell(cellX, cellY)

    # Если игра окончена и сообщение о победе еще не было показано, покажем его
    if grid.game_over and not winner_message_shown:
        show_message(surface, "Игрок {} победил!".format(grid.get_winner()))
        winner_message_shown = True  # Устанавливаем флаг, что сообщение о победе было показано

    pygame.display.flip()
