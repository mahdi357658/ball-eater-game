"""
بازی «خوردن توپ‌ها»
------------------------------------------------
- بازیکن یک «مار» است که سرش دنبال موس حرکت می‌کند و بدنه‌اش مسیر قبلی سر را دنبال می‌کند.
- سه نوع توپ روی صفحه ظاهر می‌شود:
    1) توپ ساده (رنگ سفید/خاکستری)  -> ۲ امتیاز و کمی بزرگ‌تر شدن بازیکن
    2) توپ طلایی (رنگ زرد)          -> ۱۰ امتیاز و بزرگ‌تر شدن بیشتر
    3) بمب (رنگ قرمز با علامت)      -> منفی ۳۰ امتیاز و کوچک شدن بازیکن
- بازی ۲۰ مرحله دارد. هر مرحله یک «امتیاز هدف» دارد که باید به آن برسید تا به مرحله بعد بروید.
- هر مرحله نسبت به مرحله قبل کمی سخت‌تر می‌شود: سرعت توپ‌ها بیشتر، تعداد توپ‌ها بیشتر و تعداد بمب‌ها بیشتر می‌شود.

نحوه اجرا:
    pip install pygame
    python ball_game.py

کنترل:
    - حرکت موس  = حرکت بازیکن
    - کلیک/Enter در صفحه شروع و صفحه پایان = ادامه/شروع دوباره
    - Esc = خروج
"""

import pygame
import random
import sys
import math

# ---------------------------------------------------------------------------
# تنظیمات کلی
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 900, 650
FPS = 60
TOTAL_LEVELS = 20

WHITE = (240, 240, 240)
BLACK = (15, 15, 20)
GRAY = (120, 120, 130)
YELLOW = (255, 210, 40)
RED = (220, 60, 60)
DARK_RED = (120, 20, 20)
GREEN = (80, 200, 120)
BLUE = (60, 140, 230)
BG_COLOR = (22, 24, 33)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("خوردن توپ‌ها - بازی مار موسی")
clock = pygame.time.Clock()

# فونت (اگر فونت فارسی روی سیستم نصب نباشد، اعداد و حروف انگلیسی درست نمایش داده می‌شوند)
FONT_BIG = pygame.font.SysFont("arial", 54, bold=True)
FONT_MED = pygame.font.SysFont("arial", 30, bold=True)
FONT_SMALL = pygame.font.SysFont("arial", 22)


# ---------------------------------------------------------------------------
# تعریف مراحل: هر مرحله یک دیکشنری با تنظیمات مخصوص خودش دارد
# ---------------------------------------------------------------------------
def build_levels():
    levels = []
    for lvl in range(1, TOTAL_LEVELS + 1):
        target_score = 60 + (lvl - 1) * 45          # امتیاز لازم برای رد شدن از مرحله - هر مرحله بیشتر
        ball_speed = 1.4 + (lvl - 1) * 0.22          # سرعت توپ‌ها هر مرحله کمی بیشتر
        spawn_interval = max(0.35, 1.15 - (lvl - 1) * 0.045)  # هر چه مرحله بالاتر، توپ‌ها سریع‌تر ظاهر می‌شوند
        max_balls = min(9 + lvl, 26)                 # تعداد توپ همزمان روی صفحه
        bomb_chance = min(0.12 + (lvl - 1) * 0.015, 0.38)     # احتمال ظاهر شدن بمب هر مرحله بیشتر می‌شود
        gold_chance = 0.18                             # احتمال توپ طلایی نسبتا ثابت
        levels.append({
            "level": lvl,
            "target_score": target_score,
            "ball_speed": ball_speed,
            "spawn_interval": spawn_interval,
            "max_balls": max_balls,
            "bomb_chance": bomb_chance,
            "gold_chance": gold_chance,
        })
    return levels


LEVELS = build_levels()

# ---------------------------------------------------------------------------
# انواع توپ‌ها
# ---------------------------------------------------------------------------
BALL_TYPES = {
    "simple": {"color": WHITE, "value": 2, "radius": 11, "grow": 1},
    "gold": {"color": YELLOW, "value": 10, "radius": 15, "grow": 4},
    "bomb": {"color": RED, "value": -30, "radius": 16, "grow": -6},
}


class Ball:
    """یک توپ که روی صفحه حرکت می‌کند."""

    def __init__(self, kind, speed_mult):
        self.kind = kind
        info = BALL_TYPES[kind]
        self.radius = info["radius"]
        self.color = info["color"]
        self.value = info["value"]
        self.grow = info["grow"]

        # موقعیت شروع تصادفی در لبه‌های صفحه
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            self.x = random.uniform(0, WIDTH)
            self.y = -self.radius
        elif side == "bottom":
            self.x = random.uniform(0, WIDTH)
            self.y = HEIGHT + self.radius
        elif side == "left":
            self.x = -self.radius
            self.y = random.uniform(0, HEIGHT)
        else:
            self.x = WIDTH + self.radius
            self.y = random.uniform(0, HEIGHT)

        # سرعت به سمت یک نقطه تصادفی داخل صفحه (حرکت اریب و متنوع)
        target_x = random.uniform(WIDTH * 0.15, WIDTH * 0.85)
        target_y = random.uniform(HEIGHT * 0.15, HEIGHT * 0.85)
        dx, dy = target_x - self.x, target_y - self.y
        dist = math.hypot(dx, dy) or 1
        base_speed = random.uniform(0.6, 1.3) * speed_mult
        self.vx = dx / dist * base_speed
        self.vy = dy / dist * base_speed

    def update(self):
        self.x += self.vx
        self.y += self.vy
        # اگر از صفحه خارج شد، از سمت دیگر برگردانش (حلقه‌ای/wrap)
        margin = self.radius + 5
        if self.x < -margin:
            self.x = WIDTH + margin
        elif self.x > WIDTH + margin:
            self.x = -margin
        if self.y < -margin:
            self.y = HEIGHT + margin
        elif self.y > HEIGHT + margin:
            self.y = -margin

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)
        if self.kind == "bomb":
            # یک ضربدر روی بمب می‌کشیم تا واضح باشد خطرناک است
            r = self.radius
            pygame.draw.line(surf, DARK_RED, (self.x - r * 0.5, self.y - r * 0.5),
                              (self.x + r * 0.5, self.y + r * 0.5), 3)
            pygame.draw.line(surf, DARK_RED, (self.x - r * 0.5, self.y + r * 0.5),
                              (self.x + r * 0.5, self.y - r * 0.5), 3)
        elif self.kind == "gold":
            pygame.draw.circle(surf, (255, 245, 200), (int(self.x), int(self.y)), self.radius, 2)


class Player:
    """
    بازیکن حالا به شکل «مار» است.
    سر مار دنبال موس حرکت می‌کند و بدنه‌ی مار مسیر قبلی سر را دنبال می‌کند.
    هر توپ که خورده شود به تعداد بندهای مار اضافه/کم می‌شود.
    """

    HEAD_RADIUS = 15
    BODY_RADIUS = 12
    MIN_LENGTH = 4
    MAX_LENGTH = 70
    SEGMENT_GAP = 5   # هر چند فریم یک بند جدید از مسیر برداشته شود (فاصله بین بندها)

    def __init__(self):
        start_x, start_y = WIDTH // 2, HEIGHT // 2
        self.x, self.y = start_x, start_y          # موقعیت سر مار (برای برخورد استفاده می‌شود)
        self.radius = self.HEAD_RADIUS               # شعاع سر - برای برخورد با توپ‌ها
        self.length = self.MIN_LENGTH + 3            # تعداد بندهای مار
        # مسیر طی‌شده‌ی سر مار را ذخیره می‌کنیم تا بدنه از روی آن رسم شود
        self.trail = [(start_x, start_y)] * (self.MAX_LENGTH * self.SEGMENT_GAP + 5)

    def update(self, target_pos):
        # حرکت نرم سر مار دنبال موس (کمی تاخیر طبیعی برای حس بهتر)
        tx, ty = target_pos
        self.x += (tx - self.x) * 0.35
        self.y += (ty - self.y) * 0.35

        self.trail.append((self.x, self.y))
        max_needed = self.MAX_LENGTH * self.SEGMENT_GAP + 5
        if len(self.trail) > max_needed:
            self.trail = self.trail[-max_needed:]

    def grow(self, amount):
        # amount مثبت = اضافه شدن بند، amount منفی (بمب) = کم شدن بند
        self.length += amount
        self.length = max(self.MIN_LENGTH, min(self.MAX_LENGTH, self.length))

    def draw(self, surf):
        # بدنه را از دم به سمت سر رسم می‌کنیم تا سر همیشه روی بدنه دیده شود
        segments = []
        for i in range(int(self.length)):
            idx = -(1 + i * self.SEGMENT_GAP)
            if -idx <= len(self.trail):
                pos = self.trail[idx]
            else:
                pos = self.trail[0]
            segments.append(pos)

        n = len(segments)
        for i in range(n - 1, -1, -1):
            pos = segments[i]
            # هر چه به سمت دم برویم بندها کمی کوچک‌تر و کمی تیره‌تر می‌شوند
            t = i / max(1, n - 1)
            radius = self.BODY_RADIUS * (1 - 0.35 * t)
            shade = 1 - 0.4 * t
            color = (int(GREEN[0] * shade), int(GREEN[1] * shade), int(GREEN[2] * shade))
            pygame.draw.circle(surf, color, (int(pos[0]), int(pos[1])), int(radius))

        # سر مار (رنگ متفاوت و کمی بزرگ‌تر) + دو چشم کوچک برای حس زنده بودن
        hx, hy = self.x, self.y
        pygame.draw.circle(surf, (40, 160, 90), (int(hx), int(hy)), self.HEAD_RADIUS)
        pygame.draw.circle(surf, WHITE, (int(hx), int(hy)), self.HEAD_RADIUS, 2)

        eye_offset = self.HEAD_RADIUS * 0.4
        for ex, ey in [(-eye_offset, -eye_offset * 0.6), (eye_offset, -eye_offset * 0.6)]:
            pygame.draw.circle(surf, WHITE, (int(hx + ex), int(hy + ey)), 3)
            pygame.draw.circle(surf, BLACK, (int(hx + ex), int(hy + ey)), 1)


# ---------------------------------------------------------------------------
# توابع کمکی برای رسم متن
# ---------------------------------------------------------------------------
def draw_text_center(surf, text, font, color, cx, cy):
    img = font.render(text, True, color)
    rect = img.get_rect(center=(cx, cy))
    surf.blit(img, rect)


def draw_text(surf, text, font, color, x, y):
    img = font.render(text, True, color)
    surf.blit(img, (x, y))


# ---------------------------------------------------------------------------
# صفحه‌ی شروع
# ---------------------------------------------------------------------------
def start_screen():
    while True:
        screen.fill(BG_COLOR)
        draw_text_center(screen, "Ball Eater Game - 20 Levels", FONT_BIG, WHITE, WIDTH // 2, HEIGHT // 2 - 100)
        draw_text_center(screen, "Move the mouse to control your snake", FONT_MED, GRAY, WIDTH // 2, HEIGHT // 2 - 30)
        draw_text_center(screen, "White ball = +2   |   Gold ball = +10   |   Bomb = -30", FONT_MED, YELLOW, WIDTH // 2, HEIGHT // 2 + 20)
        draw_text_center(screen, "Click or press ENTER to start", FONT_MED, GREEN, WIDTH // 2, HEIGHT // 2 + 100)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_RETURN:
                    return
            if event.type == pygame.MOUSEBUTTONDOWN:
                return

        pygame.display.flip()
        clock.tick(FPS)


# ---------------------------------------------------------------------------
# صفحه‌ی پایان بازی (باخت یا برد کامل)
# ---------------------------------------------------------------------------
def end_screen(win, score, level_reached):
    while True:
        screen.fill(BG_COLOR)
        if win:
            draw_text_center(screen, "You finished all 20 levels!", FONT_BIG, GREEN, WIDTH // 2, HEIGHT // 2 - 80)
        else:
            draw_text_center(screen, "Game Over", FONT_BIG, RED, WIDTH // 2, HEIGHT // 2 - 80)
            draw_text_center(screen, f"You reached level {level_reached}", FONT_MED, WHITE, WIDTH // 2, HEIGHT // 2 - 20)

        draw_text_center(screen, f"Final Score: {score}", FONT_MED, YELLOW, WIDTH // 2, HEIGHT // 2 + 30)
        draw_text_center(screen, "Click or press ENTER to play again, ESC to quit", FONT_SMALL, GRAY, WIDTH // 2, HEIGHT // 2 + 100)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_RETURN:
                    return
            if event.type == pygame.MOUSEBUTTONDOWN:
                return

        pygame.display.flip()
        clock.tick(FPS)


# ---------------------------------------------------------------------------
# صفحه‌ی «مرحله بعد» بین دو مرحله
# ---------------------------------------------------------------------------
def level_up_screen(level, score):
    timer = 0
    while timer < FPS * 1.4:  # حدود ۱.۴ ثانیه نمایش داده می‌شود
        screen.fill(BG_COLOR)
        draw_text_center(screen, f"Level {level} Complete!", FONT_BIG, GREEN, WIDTH // 2, HEIGHT // 2 - 40)
        draw_text_center(screen, f"Score: {score}", FONT_MED, YELLOW, WIDTH // 2, HEIGHT // 2 + 30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.flip()
        clock.tick(FPS)
        timer += 1


# ---------------------------------------------------------------------------
# اجرای یک مرحله؛ خروجی: "win" اگر به هدف رسید، "dead" اگر امتیاز منفی شد بیش از حد مجاز
# ---------------------------------------------------------------------------
def run_level(level_info, player, total_score_start):
    balls = []
    spawn_timer = 0.0
    level_score = 0  # امتیازی که فقط در همین مرحله جمع شده

    while True:
        dt = clock.tick(FPS) / 1000.0
        spawn_timer += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        # اضافه کردن توپ جدید طبق فاصله زمانی مرحله
        if spawn_timer >= level_info["spawn_interval"] and len(balls) < level_info["max_balls"]:
            spawn_timer = 0.0
            r = random.random()
            if r < level_info["bomb_chance"]:
                kind = "bomb"
            elif r < level_info["bomb_chance"] + level_info["gold_chance"]:
                kind = "gold"
            else:
                kind = "simple"
            balls.append(Ball(kind, level_info["ball_speed"]))

        # به‌روزرسانی بازیکن با موقعیت موس
        mouse_pos = pygame.mouse.get_pos()
        player.update(mouse_pos)

        # به‌روزرسانی توپ‌ها و بررسی برخورد
        eaten = []
        for ball in balls:
            ball.update()
            dist = math.hypot(ball.x - player.x, ball.y - player.y)
            if dist < player.radius + ball.radius * 0.6:
                eaten.append(ball)
                level_score += ball.value
                player.grow(ball.grow)

        for ball in eaten:
            balls.remove(ball)

        total_score_now = total_score_start + level_score

        # ---------------- رسم صحنه ----------------
        screen.fill(BG_COLOR)

        for ball in balls:
            ball.draw(screen)

        player.draw(screen)

        # اطلاعات بالای صفحه (HUD)
        draw_text(screen, f"Level: {level_info['level']} / {TOTAL_LEVELS}", FONT_SMALL, WHITE, 15, 12)
        draw_text(screen, f"Score: {total_score_now}", FONT_SMALL, YELLOW, 15, 38)
        draw_text(screen, f"Target: {level_info['target_score']}", FONT_SMALL, GREEN, 15, 64)

        # نوار پیشرفت مرحله
        progress = max(0.0, min(1.0, level_score / level_info["target_score"]))
        bar_w = 260
        pygame.draw.rect(screen, GRAY, (WIDTH - bar_w - 20, 20, bar_w, 18), 2)
        pygame.draw.rect(screen, GREEN, (WIDTH - bar_w - 20, 20, int(bar_w * progress), 18))

        pygame.display.flip()

        # ---------------- بررسی پایان مرحله ----------------
        if level_score >= level_info["target_score"]:
            return "win", level_score
        if total_score_now < -50:
            # اگر امتیاز کلی خیلی منفی شد بازی تمام می‌شود
            return "dead", level_score


# ---------------------------------------------------------------------------
# حلقه اصلی بازی
# ---------------------------------------------------------------------------
def main():
    pygame.mouse.set_visible(True)
    while True:
        start_screen()

        player = Player()
        total_score = 0
        current_level_index = 0
        game_over = False

        while current_level_index < TOTAL_LEVELS:
            level_info = LEVELS[current_level_index]
            result, level_score = run_level(level_info, player, total_score)
            total_score += level_score

            if result == "dead":
                game_over = True
                break

            current_level_index += 1
            if current_level_index < TOTAL_LEVELS:
                level_up_screen(level_info["level"], total_score)

        if game_over:
            end_screen(False, total_score, level_info["level"])
        else:
            end_screen(True, total_score, TOTAL_LEVELS)


if __name__ == "__main__":
    main()
