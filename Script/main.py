from pico2d import *

from boy import Boy #boy 모듈 이름 , Boy 클래스 이름
from grass import Grass # grass 모듈 이름 , Grass 클래스 이름

class AutoRunState:
    """자동 달리기의 진입, 갱신, 표시와 종료를 담당하는 개별 상태."""

    DURATION = 5.0
    SPEED_MULTIPLIER = 2.0
    SCALE = 1.5

    def __init__(self, boy):
        self.boy = boy
        self.started_at = None
        self.last_update = None

    def enter(self):
        now = get_time()
        self.started_at = now
        self.last_update = now
        self.boy.move_dir = 1
        self.boy.face_dir = 1
        self.boy.frame = 0.0
        self.boy._pressed_directions.clear()

    def expired(self):
        return (self.started_at is not None
                and get_time() - self.started_at >= self.DURATION)

    def update(self):
        now = get_time()
        elapsed = max(0.0, now - self.last_update)
        self.last_update = now
        speed = self.boy.RUN_SPEED * self.SPEED_MULTIPLIER
        self.boy.x += self.boy.move_dir * speed * elapsed
        self.boy.frame = (self.boy.frame + self.boy.RUN_FPS * elapsed) % self.boy.RUN_FRAME_COUNT

    def draw(self):
        boy = self.boy
        row = 100 if boy.face_dir == 1 else 0
        boy.image.clip_draw(
            int(boy.frame) * boy.FRAME_WIDTH, row,
            boy.FRAME_WIDTH, boy.FRAME_HEIGHT, boy.x, boy.y,
            boy.FRAME_WIDTH * self.SCALE, boy.FRAME_HEIGHT * self.SCALE,
        )


def handle_events():
    global running

    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        else:
            boy.handle_event(event)


def reset_world():
    global world
    global boy

    world = []

    grass = Grass()
    world.append(grass)

    boy = Boy()
    world.append(boy)



def update_world():
    for o in world:
        o.update()
    pass


def render_world():
    clear_canvas()
    for o in world:
        o.draw()
    update_canvas()


def main():
    global running
    running = True
    open_canvas()
    try:
        reset_world()
        while running:
            handle_events()
            if not running:
                break
            update_world()
            render_world()
            delay(0.01)
    finally:
        close_canvas()


if __name__ == '__main__':
    main()
