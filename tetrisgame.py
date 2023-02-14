import pygame
from copy import deepcopy
from random import choice, randrange

WIDTH, HEIGHT = 15, 20
SQUARE = 32
GAME_RESOLUTION = WIDTH * SQUARE, HEIGHT * SQUARE
RESOLUTION = 750, 680
FPS = 60

pygame.init()
main_frame = pygame.display.set_mode(RESOLUTION)
game_label = pygame.Surface(GAME_RESOLUTION)
clock = pygame.time.Clock()
pygame.display.set_caption('Tetris Game')
icon = pygame.image.load('tetris.ico')
pygame.display.set_icon(icon)

grid = [pygame.Rect(x * SQUARE, y * SQUARE, SQUARE, SQUARE) for x in range(WIDTH) for y in range(HEIGHT)]

shapes_position = [[(-1, 0), (-2, 0), (0, 0), (1, 0)],
               [(0, -1), (-1, -1), (-1, 0), (0, 0)],
               [(-1, 0), (-1, 1), (0, 0), (0, -1)],
               [(0, 0), (-1, 0), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, -1)],
               [(0, 0), (0, -1), (0, 1), (1, -1)],
               [(0, 0), (0, -1), (0, 1), (-1, 0)]]

shapes = [[pygame.Rect(x + WIDTH // 2, y + 1, 1, 1) for x, y in fig_pos] for fig_pos in shapes_position]
shape_square = pygame.Rect(0, 0, SQUARE - 2, SQUARE - 2)
field = [[0 for i in range(WIDTH)] for j in range(HEIGHT)]

animation_count, animation_speed, animation_limit = 0, 60, 2000

main_background = pygame.image.load('images/main_img.jpg').convert()
game_background = pygame.image.load('images/img.jpg').convert()

main_font = pygame.font.SysFont('consolas', 65)
next_shape_font = pygame.font.SysFont('consolas', 30)
values_font = pygame.font.SysFont('consolas', 45)

title_tetris = main_font.render('TETRIS', True, pygame.Color('darkorange'))
title_next_shape = next_shape_font.render('Next Shape:', True, pygame.Color('green'))
title_score = values_font.render('score:', True, pygame.Color('green'))
title_record = values_font.render('record:', True, pygame.Color('purple'))

get_color = lambda: (randrange(30, 256), randrange(30, 256), randrange(30, 256))

shape, next_shape = deepcopy(choice(shapes)), deepcopy(choice(shapes))
color, next_color = get_color(), get_color()

score, lines = 0, 0
scores = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}


def check_border_limit():
    if shape[i].x < 0 or shape[i].x > WIDTH - 1:
        return False
    elif shape[i].y > HEIGHT - 1 or field[shape[i].y][shape[i].x]:
        return False
    return True


def get_record():
    try:
        with open('record') as record_file:
            return record_file.readline()
    except FileNotFoundError:
        with open('record', 'w') as record_file:
            record_file.write('0')


def set_record(record, score):
    rec = max(int(record), score)
    with open('record', 'w') as record_file:
        record_file.write(str(rec))


while True:
    record = get_record()
    dx, dy, rotate = 0, 0, False
    main_frame.blit(main_background, (0, 0))
    main_frame.blit(game_label, (20, 20))
    game_label.blit(game_background, (0, 0))

    for i in range(lines):
        pygame.time.wait(200)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                dx = -1
            elif event.key == pygame.K_RIGHT:
                dx = 1
            elif event.key == pygame.K_DOWN:
                dy = 1
            elif event.key == pygame.K_SPACE:
                animation_limit = 100
            elif event.key == pygame.K_UP:
                rotate = True

    shape_old = deepcopy(shape)
    for i in range(4):
        shape[i].x += dx
        shape[i].y += dy
        if not check_border_limit():
            shape = deepcopy(shape_old)
            break

    animation_count += animation_speed
    if animation_count > animation_limit:
        animation_count = 0
        shape_old = deepcopy(shape)
        for i in range(4):
            shape[i].y += 1
            if not check_border_limit():
                for i in range(4):
                    field[shape_old[i].y][shape_old[i].x] = color
                shape, color = next_shape, next_color
                next_shape, next_color = deepcopy(choice(shapes)), get_color()
                animation_limit = 2000
                break

    center = shape[0]
    shape_old = deepcopy(shape)
    if rotate:
        for i in range(4):
            x = shape[i].y - center.y
            y = shape[i].x - center.x
            shape[i].x = center.x - x
            shape[i].y = center.y + y
            if not check_border_limit():
                shape = deepcopy(shape_old)
                break

    line, lines = HEIGHT - 1, 0
    for row in range(HEIGHT - 1, -1, -1):
        count = 0
        for i in range(WIDTH):
            if field[row][i]:
                count += 1
            field[line][i] = field[row][i]
        if count < WIDTH:
            line -= 1
        else:
            animation_speed += 3
            lines += 1

    score += scores[lines]

    [pygame.draw.rect(game_label, (40, 40, 40), i_square, 1) for i_square in grid]

    for i in range(4):
        shape_square.x = shape[i].x * SQUARE
        shape_square.y = shape[i].y * SQUARE
        pygame.draw.rect(game_label, color, shape_square)

    for y, raw in enumerate(field):
        for x, col in enumerate(raw):
            if col:
                shape_square.x, shape_square.y = x * SQUARE, y * SQUARE
                pygame.draw.rect(game_label, col, shape_square)

    for i in range(4):
        shape_square.x = next_shape[i].x * SQUARE + 380
        shape_square.y = next_shape[i].y * SQUARE + 185
        pygame.draw.rect(main_frame, next_color, shape_square)

    main_frame.blit(title_tetris, (520, 10))
    main_frame.blit(title_next_shape, (530, 100))
    main_frame.blit(title_score, (550, 520))
    main_frame.blit(values_font.render(str(score), True, pygame.Color('white')), (580, 560))
    main_frame.blit(title_record, (550, 400))
    main_frame.blit(values_font.render(record, True, pygame.Color('gold')), (570, 450))

    for i in range(WIDTH):
        if field[0][i]:
            set_record(record, score)
            field = [[0 for i in range(WIDTH)] for i in range(HEIGHT)]
            animation_count, animation_speed, animation_limit = 0, 60, 2000
            score = 0
            for i_square in grid:
                pygame.draw.rect(game_label, get_color(), i_square)
                main_frame.blit(game_label, (20, 20))
                pygame.display.flip()
                clock.tick(200)

    pygame.display.flip()
    clock.tick(FPS)
