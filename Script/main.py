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
        left, right = self.horizontal_bounds()
        self.boy.x = max(left, min(right, self.boy.x))

    def horizontal_bounds(self):
        half_width = self.boy.FRAME_WIDTH * self.SCALE / 2
        return half_width, get_canvas_width() - half_width

    def expired(self):
        return (self.started_at is not None
                and get_time() - self.started_at >= self.DURATION)

    def update(self):
        now = get_time()
        elapsed = max(0.0, now - self.last_update)
        self.last_update = now
        speed = self.boy.RUN_SPEED * self.SPEED_MULTIPLIER
        left, right = self.horizontal_bounds()
        span = right - left
        # 왕복 거리를 펼쳐 계산하므로 긴 프레임에 벽을 여러 번 만나도 위치를 보존한다.
        phase = self.boy.x - left
        if self.boy.move_dir < 0:
            phase = 2 * span - phase
        phase = (phase + speed * elapsed) % (2 * span)
        if phase < span:
            self.boy.x = left + phase
            self.boy.move_dir = 1
        else:
            self.boy.x = right - (phase - span)
            self.boy.move_dir = -1
        self.boy.face_dir = self.boy.move_dir
        self.boy.frame = (self.boy.frame + self.boy.RUN_FPS * elapsed) % self.boy.RUN_FRAME_COUNT

    def draw(self):
        boy = self.boy
        row = 100 if boy.face_dir == 1 else 0
        boy.image.clip_draw(
            int(boy.frame) * boy.FRAME_WIDTH, row,
            boy.FRAME_WIDTH, boy.FRAME_HEIGHT, boy.x, boy.y,
            boy.FRAME_WIDTH * self.SCALE, boy.FRAME_HEIGHT * self.SCALE,
        )


class AutoRunBoy(Boy):
    """기존 Boy의 상태와 호출 규약을 유지하면서 자동 달리기를 연결한다."""

    def __init__(self):
        super().__init__()
        self.auto_run = AutoRunState(self)
        self.machine.add_states({
            'name': 'AUTO_RUN',
            'on_enter': self.auto_run.enter,
        })
        self.machine.add_transition('start_auto_run', 'IDLE', 'AUTO_RUN')
        self.machine.add_transition('start_run', 'AUTO_RUN', 'RUN')
        self.machine.add_transition(
            'tick', 'AUTO_RUN', 'IDLE', conditions=self.auto_run.expired,
        )
        self.machine.add_transition(
            'tick', 'AUTO_RUN', None, after=self.auto_run.update,
        )

    def handle_event(self, event):
        if (self.state == 'IDLE'
                and event.type == SDL_KEYDOWN and event.key == SDLK_a):
            self.start_auto_run()
            return
        if self.state == 'AUTO_RUN':
            if event.type == SDL_KEYDOWN and event.key in (SDLK_LEFT, SDLK_RIGHT):
                self._pressed_directions[:] = [event.key]
                self._set_run_direction()
                self.start_run()
            # 상하 키, a 재입력과 키 해제는 자동 달리기를 취소하지 않는다.
            return
        super().handle_event(event)

    def draw(self):
        if self.state == 'AUTO_RUN':
            self.auto_run.draw()
        else:
            super().draw()


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

    boy = AutoRunBoy()
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
            # 좌우 키 취소를 먼저 적용한 뒤 tick에서 5초 만료 여부를 검사한다.
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
