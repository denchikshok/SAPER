import pygame
from grid import Grid

import os
os.environ['SDL_VIDEO_WINDOW_POS'] = '200, 100' #положение окна относительно экрана

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
connection_established = False
conn, addr = None, None

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP
sock.bind((HOST, PORT))
sock.listen(1)

def receive_data():
    global turn
    while True:
        data = conn.recv(1024).decode()
        data = data.split('-')
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


    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True  # перезапуск игры
                elif event.key == pygame.K_ESCAPE:
                    return False  # выход из игры

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and connection_established:
            if pygame.mouse.get_pressed()[0]: #0 означает что нажать можно только лкм
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


    surface.fill((255,255,255))

    grid.draw(surface)

    pos = pygame.mouse.get_pos()
    cellX, cellY = pos[0] // 200, pos[1] // 200
    highlight_cell(cellX, cellY)

    pygame.display.flip()