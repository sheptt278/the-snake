"""Игра «Змейка» на pygame."""

from random import choice

import pygame as pg

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

OPPOSITE_DIRECTIONS = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT,
}

DIRECTIONS_BY_KEY = {
    pg.K_UP: UP,
    pg.K_DOWN: DOWN,
    pg.K_LEFT: LEFT,
    pg.K_RIGHT: RIGHT,
    pg.K_w: UP,
    pg.K_s: DOWN,
    pg.K_a: LEFT,
    pg.K_d: RIGHT,
}

BOARD_BACKGROUND_COLOR = (235, 235, 235)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

SPEED = 20
MIN_SPEED = 5
MAX_SPEED = 60
SPEED_STEP = 2

ALL_CELLS = {
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(GRID_WIDTH)
    for y in range(GRID_HEIGHT)
}

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
clock = pg.time.Clock()


class GameObject:
    """Базовый класс игровых объектов."""

    def __init__(self, body_color=None):
        """Инициализирует объект указанным цветом."""
        self.position = CENTER
        self.body_color = body_color

    def draw_cell(self, position, color=None):
        """Отрисовывает одну клетку игрового поля."""
        color = color or self.body_color
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)

        if color != BOARD_BACKGROUND_COLOR:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Требует реализации в дочернем классе."""
        raise NotImplementedError(
            f'Метод draw() не реализован в {type(self).__name__}.'
        )


class Apple(GameObject):
    """Яблоко на игровом поле."""

    def __init__(self, occupied_positions=(), body_color=APPLE_COLOR):
        """Создаёт яблоко в свободной клетке."""
        super().__init__(body_color)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions):
        """Размещает яблоко в свободной клетке."""
        free_cells = tuple(ALL_CELLS - set(occupied_positions))
        self.position = choice(free_cells)

    def draw(self):
        """Отрисовывает яблоко."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Змейка игрока."""

    def __init__(self, body_color=SNAKE_COLOR):
        """Создаёт змейку."""
        super().__init__(body_color)
        self.reset()

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def update_direction(self, new_direction):
        """Меняет направление без разворота на 180 градусов."""
        if new_direction != OPPOSITE_DIRECTIONS[self.direction]:
            self.direction = new_direction

    def move(self):
        """Перемещает змейку на одну клетку."""
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction
        self.positions.insert(0, (
            (head_x + direction_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + direction_y * GRID_SIZE) % SCREEN_HEIGHT,
        ))
        self.last = (
            self.positions.pop()
            if len(self.positions) > self.length
            else None
        )

    def reset(self):
        """Возвращает змейку в начальное состояние."""
        self.length = 1
        self.positions = [CENTER]
        self.direction = choice((UP, DOWN, LEFT, RIGHT))
        self.last = None

    def draw(self):
        """Рисует новую голову и очищает предыдущий хвост."""
        self.draw_cell(self.get_head_position())

        if self.last is not None:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR)


def handle_keys(snake, speed):
    """Обрабатывает события клавиатуры и возвращает скорость."""
    for event in pg.event.get():
        if event.type == pg.QUIT or (
            event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE
        ):
            pg.quit()
            raise SystemExit

        if event.type != pg.KEYDOWN:
            continue

        new_direction = DIRECTIONS_BY_KEY.get(event.key)
        if new_direction is not None:
            snake.update_direction(new_direction)
        elif event.key in (pg.K_PLUS, pg.K_EQUALS, pg.K_KP_PLUS):
            speed = min(MAX_SPEED, speed + SPEED_STEP)
        elif event.key in (pg.K_MINUS, pg.K_KP_MINUS):
            speed = max(MIN_SPEED, speed - SPEED_STEP)

    return speed


def update_caption(speed, max_length):
    """Обновляет заголовок игрового окна."""
    pg.display.set_caption(
        'Змейка | Стрелки/WASD — движение | ESC — выход | '
        '+/- — скорость | '
        f'Скорость: {speed} | Рекорд: {max_length}'
    )


def main():
    """Запускает игру."""
    pg.init()
    screen.fill(BOARD_BACKGROUND_COLOR)
    snake = Snake()
    apple = Apple(snake.positions)
    speed = SPEED
    max_length = snake.length

    while True:
        speed = handle_keys(snake, speed)
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            max_length = max(max_length, snake.length)
            apple.randomize_position(snake.positions)
        elif (
            snake.length > 3
            and snake.get_head_position() in snake.positions[2:]
        ):
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)

        snake.draw()
        apple.draw()
        update_caption(speed, max_length)
        pg.display.update()
        clock.tick(speed)


if __name__ == '__main__':
    main()
