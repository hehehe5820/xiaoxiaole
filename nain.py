import pygame
import random
import os

pygame.init()
BLOCK_SIZE = 60
BOARD_W = 8
BOARD_H = 8
SCREEN_WIDTH = BLOCK_SIZE * BOARD_W + 220
SCREEN_HEIGHT = BLOCK_SIZE * BOARD_H
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption

TYPE_COUNT = 5
NORMAL = 0
LV2 = 2
LV3 = 3

img_list = []
asset_path = "assets"
image_names = [
    "strawberry.png",
    "blueberry.png",
    "raspberry.png",
    "cranberry.png",
    "plum.png"
]

for name in image_names:
    full_path = os.path.join(asset_path, name)
    img = pygame.image.load(full_path).convert_alpha()
    img = pygame.transform.scale(img, (BLOCK_SIZE - 8, BLOCK_SIZE - 8))
    img_list.append(img)

img_lv2 = pygame.image.load(os.path.join(asset_path, "fruit_lv2.png")).convert_alpha()
img_lv2 = pygame.transform.scale(img_lv2, (BLOCK_SIZE - 8, BLOCK_SIZE - 8))

img_lv3 = pygame.image.load(os.path.join(asset_path, "fruit_lv3.png")).convert_alpha()
img_lv3 = pygame.transform.scale(img_lv3, (BLOCK_SIZE - 8, BLOCK_SIZE - 8))

COLOR_LV2 = (255, 220, 60)
COLOR_LV3 = (80, 255, 255)
font = pygame.font.SysFont(None, 36)
clock = pygame.time.Clock()

level = 1
difficulty = 1.0 
board = []
selected = None
is_swapping = False
score = 0
MIN_TARGET = 500
MAX_TARGET = 600
target_score = MIN_TARGET

def create_board():
    global board
    board = []
    for y in range(BOARD_H):
        row = []
        for x in range(BOARD_W):
            t = random.randint(0, TYPE_COUNT - 1)
            row.append({"type": t, "level": NORMAL})
        board.append(row)
    while find_matches():
        for y in range(BOARD_H):
            for x in range(BOARD_W):
                board[y][x]["type"] = random.randint(0, TYPE_COUNT - 1)

def find_matches():
    matches = set()
    for y in range(BOARD_H):
        x = 0
        while x < BOARD_W - 2:
            cell = board[y][x]
            if cell["level"] != NORMAL:
                x += 1
                continue
            cnt = 1
            while x+cnt < BOARD_W and board[y][x+cnt]["type"] == cell["type"] and board[y][x+cnt]["level"] == NORMAL:
                cnt += 1
            if cnt >= 3:
                for i in range(cnt):
                    matches.add((x+i, y))
            x += cnt
    for x in range(BOARD_W):
        y = 0
        while y < BOARD_H - 2:
            cell = board[y][x]
            if cell["level"] != NORMAL:
                y += 1
                continue
            cnt = 1
            while y+cnt < BOARD_H and board[y+cnt][x]["type"] == cell["type"] and board[y+cnt][x]["level"] == NORMAL:
                cnt += 1
            if cnt >= 3:
                for i in range(cnt):
                    matches.add((x, y+i))
            y += cnt
    return list(matches)

def process_match(matches):
    global score
    if not matches:
        return False
    match_count = len(matches)
    score += match_count * 2

    cx, cy = matches[len(matches)//2]
    if match_count >= 5:
        board[cy][cx]["level"] = LV3
    elif match_count == 4:
        board[cy][cx]["level"] = LV2

    for (x,y) in matches:
        if board[y][x]["level"] == NORMAL:
            board[y][x] = None
    return True

def drop_blocks():
    for x in range(BOARD_W):
        empty = 0
        for y in range(BOARD_H-1, -1, -1):
            if board[y][x] is None:
                empty += 1
            else:
                if empty > 0:
                    board[y+empty][x] = board[y][x]
                    board[y][x] = None
        for y in range(empty):
            rand_type = random.randint(0, TYPE_COUNT-1)
            board[y][x] = {"type": rand_type, "level": NORMAL}

def swap(pos_a, pos_b):
    x1,y1 = pos_a
    x2,y2 = pos_b
    board[y1][x1], board[y2][x2] = board[y2][x2], board[y1][x1]

def is_adjacent(p1,p2):
    x1,y1 = p1
    x2,y2 = p2
    dx = abs(x1-x2)
    dy = abs(y1-y2)
    return (dx == 1 and dy == 0) or (dx == 0 and dy ==1)

def special_clear(p1, p2):
    global score
    cell1 = board[p1[1]][p1[0]]
    cell2 = board[p2[1]][p2[0]]
    lv1 = cell1["level"]
    lv2 = cell2["level"]
    x1,y1 = p1
    x2,y2 = p2
    horizontal = (y1 == y2)

    if (lv1 == LV2 and lv2 == LV3) or (lv1 == LV3 and lv2 == LV2):
        score +=15
        if horizontal:
            start_y = max(0, y1 -1)
            end_y = min(BOARD_H, start_y + 4)
            for ry in range(start_y, end_y):
                for rx in range(BOARD_W):
                    board[ry][rx] = None
        else:
            start_x = max(0, x1 -1)
            end_x = min(BOARD_W, start_x + 4)
            for rx in range(start_x, end_x):
                for ry in range(BOARD_H):
                    board[ry][rx] = None
        return True

    if lv1 == LV2 or lv2 == LV2:
        score +=5
        if horizontal:
            for x in range(BOARD_W):
                board[y1][x] = None
        else:
            for y in range(BOARD_H):
                board[y][x1] = None
        return True

    if lv1 == LV3 or lv2 == LV3:
        score +=10
        cx, cy = x1, y1
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                nx = cx + dx
                ny = cy + dy
                if 0 <= nx < BOARD_W and 0 <= ny < BOARD_H:
                    board[ny][nx] = None
        return True
    return False

def draw_board():
    for y in range(BOARD_H):
        for x in range(BOARD_W):
            cell = board[y][x]
            rect = pygame.Rect(x*BLOCK_SIZE, y*BLOCK_SIZE, BLOCK_SIZE-2, BLOCK_SIZE-2)
            if cell is None:
                pygame.draw.rect(screen,(30,30,40), rect)
                continue
            t = cell["type"]
            lvl = cell["level"]

            # 特效底色
            if lvl == LV2:
                pygame.draw.rect(screen, COLOR_LV2, rect, border_radius=8)
            elif lvl == LV3:
                pygame.draw.rect(screen, COLOR_LV3, rect, border_radius=8)
            else:
                pygame.draw.rect(screen, (240,240,240), rect, border_radius=8)
            pygame.draw.rect(screen,(255,255,255), rect,2, border_radius=8)

            if lvl == LV2:
                screen.blit(img_lv2, (x*BLOCK_SIZE +4, y*BLOCK_SIZE +4))
            elif lvl == LV3:
                screen.blit(img_lv3, (x*BLOCK_SIZE +4, y*BLOCK_SIZE +4))
            else:
                screen.blit(img_list[t], (x*BLOCK_SIZE +4, y*BLOCK_SIZE +4))
    if selected is not None:
        sx,sy = selected
        rect = pygame.Rect(sx*BLOCK_SIZE, sy*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(screen, (255,255,255), rect,4)

def draw_ui():
    off_x = BLOCK_SIZE * BOARD_W +10
    screen.blit(font.render(f"关卡:{level}",True,(255,255,255)),(off_x,20))
    screen.blit(font.render(f"难度:{difficulty:.3f}",True,(255,255,255)),(off_x,60))
    screen.blit(font.render(f"分数:{score}",True,(255,255)),(off_x,100))
    screen.blit(font.render(f"目标:{target_score}",True,(255,255)),(off_x,140))

def next_level():
    global level, difficulty, target_score, score
    level += 1
    difficulty += 0.001
    target_score = min(target_score + 20, MAX_TARGET)
    score = 0
    create_board()

create_board()
running = True
while running:
    screen.fill((20,20,40))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and not is_swapping:
            mx, my = pygame.mouse.get_pos()
            bx = mx // BLOCK_SIZE
            by = my // BLOCK_SIZE
            if 0 <= bx < BOARD_W and 0 <= by < BOARD_H:
                pos = (bx, by)
                if selected is None:
                    selected = pos
                else:
                    if selected == pos:
                        selected = None
                    else:
                        if is_adjacent(selected, pos):
                            swap(selected, pos)
                            c1 = board[pos[1]][pos[0]]
                            c2 = board[selected[1]][selected[0]]
                            special_trigger = False
                            if c1["level"] != NORMAL or c2["level"] != NORMAL:
                                special_trigger = special_clear(selected, pos)
                            matches = find_matches()
                            if not matches and not special_trigger:
                                swap(selected, pos)
                            else:
                                is_swapping = True
                        selected = None
    if is_swapping:
        matched = True
        while matched:
            matched = process_match(find_matches())
            drop_blocks()
        is_swapping = False
        if score >= target_score:
            next_level()

    draw_board()
    draw_ui()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()