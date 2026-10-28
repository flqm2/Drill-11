from math import pi

from pico2d import (
    SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE,
    get_canvas_width, get_time, load_image,
)
from transitions import Machine


class Boy:
    IDLE_FRAME_COUNT = 8
    IDLE_FPS = 8
    IDLE_TIMEOUT = 5.0
    RUN_FRAME_COUNT = 8
    RUN_FPS = 12
    RUN_SPEED = 200.0
    FRAME_WIDTH = 100
    FRAME_HEIGHT = 100

    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0.0
        self.face_dir = 1
        self.move_dir = 0
        self._pressed_directions = []
        self.image = load_image('animation_sheet.png')
        self.machine = Machine(
            model=self,
            states=[
                {'name': 'IDLE', 'on_enter': '_enter_idle'},
                {'name': 'SLEEP', 'on_enter': '_enter_sleep'},
                {'name': 'RUN', 'on_enter': '_enter_run'},
            ],
            initial='IDLE',
            auto_transitions=False,
            transitions=[
                {
                    'trigger': 'tick',
                    'source': 'IDLE',
                    'dest': 'SLEEP',
                    'conditions': '_idle_timed_out',
                },
                {
                    'trigger': 'tick',
                    'source': 'IDLE',
                    'dest': None,
                    'after': '_animate_idle',
                },
                {'trigger': 'tick', 'source': 'SLEEP', 'dest': None},
                {'trigger': 'wake', 'source': 'SLEEP', 'dest': 'IDLE'},
                {
                    'trigger': 'tick',
                    'source': 'RUN',
                    'dest': None,
                    'after': '_update_run',
                },
                {'trigger': 'start_run', 'source': ['IDLE', 'SLEEP'], 'dest': 'RUN'},
                {'trigger': 'stop_run', 'source': 'RUN', 'dest': 'IDLE'},
            ],
        )
        # initial 지정만으로는 on_enter가 호출되지 않으므로 처음에도 초기화한다.
        self._enter_idle()

    def update(self):
        # 현재 상태에 따라 대기 시간 검사 또는 달리기·애니메이션을 갱신한다.
        self.tick()

    def handle_event(self, event):
        if event.type not in (SDL_KEYDOWN, SDL_KEYUP):
            return

        if (
            self.state == 'SLEEP'
            and event.type == SDL_KEYDOWN
            and event.key == SDLK_SPACE
        ):
            self.wake()
            return

        if event.key not in (SDLK_LEFT, SDLK_RIGHT):
            return

        if event.type == SDL_KEYDOWN:
            if event.key in self._pressed_directions:
                return
            self._pressed_directions.append(event.key)
            self._set_run_direction()
            if self.state in ('IDLE', 'SLEEP'):
                self.start_run()
        elif event.key in self._pressed_directions:
            self._pressed_directions.remove(event.key)
            if self._pressed_directions:
                self._set_run_direction()
            elif self.state == 'RUN':
                self.stop_run()

    def _set_run_direction(self):
        # 상태는 RUN 하나만 사용하고, 마지막으로 누른 키로 방향을 정한다.
        key = self._pressed_directions[-1]
        self.move_dir = 1 if key == SDLK_RIGHT else -1
        self.face_dir = self.move_dir

    def _enter_idle(self):
        now = get_time()
        self.idle_started_at = now
        self._last_update_time = now
        self.frame = 0.0
        self.move_dir = 0
        self._pressed_directions.clear()

    def _idle_timed_out(self):
        return get_time() - self.idle_started_at >= self.IDLE_TIMEOUT

    def _enter_sleep(self):
        self.frame = 0.0

    def _enter_run(self):
        self._last_update_time = get_time()
        self.frame = 0.0

    def _update_run(self):
        now = get_time()
        elapsed = max(0.0, now - self._last_update_time)
        self._last_update_time = now

        self.x += self.move_dir * self.RUN_SPEED * elapsed
        # 이미지 중심뿐 아니라 100px 프레임 전체가 화면 안에 남도록 제한한다.
        half_width = self.FRAME_WIDTH / 2
        self.x = max(half_width, min(get_canvas_width() - half_width, self.x))
        self.frame = (self.frame + self.RUN_FPS * elapsed) % self.RUN_FRAME_COUNT

    def _animate_idle(self):
        now = get_time()
        elapsed = max(0.0, now - self._last_update_time)
        self._last_update_time = now

        # 위치는 그대로 두고 대기 자세 8장만 초당 8프레임으로 순환한다.
        self.frame = (self.frame + self.IDLE_FPS * elapsed) % self.IDLE_FRAME_COUNT

    def draw(self):
        row = 300 if self.face_dir == 1 else 200
        if self.state == 'SLEEP':
            # 기존 IDLE 첫 자세를 눕혀 잠든 모습을 표현한다.
            self.image.clip_composite_draw(
                0, row, 100, 100, pi / 2, '', self.x, self.y - 25, 100, 100
            )
            return

        if self.state == 'RUN':
            row = 100 if self.face_dir == 1 else 0
        frame = int(self.frame)
        self.image.clip_draw(
            frame * self.FRAME_WIDTH, row,
            self.FRAME_WIDTH, self.FRAME_HEIGHT, self.x, self.y,
        )

