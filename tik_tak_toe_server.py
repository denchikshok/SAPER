import pygame
from grid import Grid

import os

os.environ['SDL_VIDEO_WINDOW_POS'] = '200, 100'  # положение окна относительно экрана

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
connection_established = False
conn, addr = None, None

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP
sock.bind((HOST, PORT))
sock.listen(1)


def receive_data():
    global turn
    while True:
        data = conn.recv(1024).decode()
        data = data.split('-')
        if data[0] == 'winner':
            # Обработка сообщения о победе
            print(data[1])  # Вывод сообщения о победе
            conn.send(data.encode())  # Отправка сообщения о победителе
            # Здесь можно дать клиентам время на прочтение сообщения
            # и выполнение дополнительных действий перед закрытием соединения
        elif data[0] == 'quit':
            # Если получено сообщение о завершении игры от клиента
            break
        else:
            x, y = int(data[0]), int(data[1])
            if data[2] == 'yourturn':
                turn = True
            if data[3] == 'False':
                grid.game_over = True
            if grid.get_cell_value(x, y) == 0:
                grid.set_cell_value(x, y, 'O')
            print(data)




def waiting_for_connection():
    global connection_established, conn, addr
    conn, addr = sock.accept()  # ждет соединение, яв-ся методом блокировки основного потока
    print('client is connected')
    connection_established = True
    receive_data()


create_thread(waiting_for_connection)

grid = Grid()

running = True
player = 'X'
turn = True
playing = 'True'

RED = (255, 0, 0)


def highlight_cell(cellX, cellY):
    pygame.draw.rect(surface, RED, (cellX * 200, cellY * 200, 200, 200), 4)


def show_message(surface, message):
    font = pygame.font.Font(None, 36)
    text = font.render(message, True, (255, 0, 0))
    text_rect = text.get_rect(center=(300, 300))

    # Определим размер рамки
    border_width = 57  # Увеличим ширину рамки
    border_rect = pygame.Rect(text_rect.left - border_width, text_rect.top - border_width,
                              text_rect.width + 2 * border_width, text_rect.height + 80)
    # Заливка фона белым цветом
    pygame.draw.rect(surface, (255, 255, 255), border_rect)

    # Рисуем рамку вокруг текста
    pygame.draw.rect(surface, (0, 0, 0), border_rect, 3)

    # Отображаем текст
    surface.blit(text, (text_rect.left, text_rect.top - 40))

    # Добавляем текст "Нажмите Пробел для начала заново"
    font = pygame.font.Font(None, 24)
    restart_text = font.render("Нажмите Пробел, чтобы начать заново", True, (0, 0, 0))
    restart_rect = restart_text.get_rect(center=(300, 340))
    surface.blit(restart_text, (restart_rect.left, restart_rect.top - 40))  # Поднимаем текст на 40 пикселей)

    pygame.display.flip()


def check_game_status(surface, grid):
    if grid.game_over:
        if grid.get_winner() == 'X':
            winner_message = "Игрок X выиграл!"
        elif grid.get_winner() == 'O':
            winner_message = "Игрок O выиграл!"
        else:
            winner_message = "Ничья!"

        return show_message(surface, winner_message)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and connection_established:
            if pygame.mouse.get_pressed()[0]:  # 0 означает что нажать можно только лкм
                if turn and not grid.game_over:
                    pos = pygame.mouse.get_pos()
                    cellX, cellY = pos[0] // 200, pos[1] // 200
                    grid.get_mouse(cellX, cellY, player)
                    if grid.game_over:
                        playing = 'False'
                    send_data = '{}-{}-{}-{}'.format(cellX, cellY, 'yourturn', playing).encode()
                    conn.send(send_data)
                    turn = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and grid.game_over:
                grid.clear_grid()
                grid.game_over = False
                playing = 'True'
            elif event.key == pygame.K_ESCAPE:
                running = False

    surface.fill((255, 255, 255))

    grid.draw(surface)

    pos = pygame.mouse.get_pos()
    cellX, cellY = pos[0] // 200, pos[1] // 200
    highlight_cell(cellX, cellY)

    winner = grid.get_winner()
    if winner:
        send_data = f'winner-{winner}'.encode()
        conn.send(send_data)  # Отправка сообщения о победителе

    if check_game_status(surface, grid):
        grid.clear_grid()
        grid.game_over = False

    pygame.display.flip()
