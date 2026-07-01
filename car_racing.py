import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# --- CONSTANTS ---
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 700
FPS = 60

# Colors (RGB)
COLOR_ROAD = (50, 50, 50)
COLOR_GRASS = (34, 139, 34)
COLOR_LINE = (240, 240, 240)
COLOR_TEXT = (255, 255, 255)
COLOR_OVERLAY = (0, 0, 0, 180)  # Transparent black for game over

# Road Boundaries
ROAD_LEFT = 60
ROAD_RIGHT = SCREEN_WIDTH - 60

# --- CLASSES ---

class PlayerCar:
    def __init__(self):
        self.width = 45
        self.height = 80
        self.x = (SCREEN_WIDTH // 2) - (self.width // 2)
        self.y = SCREEN_HEIGHT - 130
        
        # Physics vectors for smooth movement
        self.velocity_x = 0.0
        self.acceleration = 0.8
        self.friction = 0.85
        self.max_speed = 8.0
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x -= self.acceleration
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x += self.acceleration

    def update(self):
        # Apply physics friction
        self.velocity_x *= self.friction
        
        # Cap maximum speed
        if self.velocity_x > self.max_speed:
            self.velocity_x = self.max_speed
        elif self.velocity_x < -self.max_speed:
            self.velocity_x = -self.max_speed

        # Update horizontal position
        self.x += self.velocity_x
        
        # Keep within road boundaries safely
        if self.x < ROAD_LEFT:
            self.x = ROAD_LEFT
            self.velocity_x = 0
        elif self.x > ROAD_RIGHT - self.width:
            self.x = ROAD_RIGHT - self.width
            self.velocity_x = 0

        # Sync hitbox rect with exact float position
        self.rect.x = int(self.x)

    def draw(self, surface):
        # Base Body (Sleek Dark Gray / Cyan Accent Sports Car)
        pygame.draw.rect(surface, (0, 180, 216), self.rect, border_radius=6)
        
        # Cabin / Windshield
        cabin_rect = pygame.Rect(self.rect.x + 6, self.rect.y + 25, self.width - 12, 30)
        pygame.draw.rect(surface, (30, 41, 59), cabin_rect, border_radius=4)
        
        # Glass Highlights
        glass_rect = pygame.Rect(self.rect.x + 9, self.rect.y + 28, self.width - 18, 12)
        pygame.draw.rect(surface, (173, 232, 244), glass_rect, border_radius=2)

        # Headlights
        pygame.draw.circle(surface, (255, 255, 200), (self.rect.x + 8, self.rect.y + 4), 4)
        pygame.draw.circle(surface, (255, 255, 200), (self.rect.x + self.width - 8, self.rect.y + 4), 4)

        # Wheels (4 corner blocks)
        wheel_w, wheel_h = 6, 14
        pygame.draw.rect(surface, (10, 10, 10), (self.rect.x - 4, self.rect.y + 10, wheel_w, wheel_h), border_radius=2)
        pygame.draw.rect(surface, (10, 10, 10), (self.rect.x + self.width, self.rect.y + 10, wheel_w, wheel_h), border_radius=2)
        pygame.draw.rect(surface, (10, 10, 10), (self.rect.x - 4, self.rect.y + self.height - 24, wheel_w, wheel_h), border_radius=2)
        pygame.draw.rect(surface, (10, 10, 10), (self.rect.x + self.width, self.rect.y + self.height - 24, wheel_w, wheel_h), border_radius=2)


class EnemyCar:
    def __init__(self, base_speed):
        # 3 Archetypes Configuration: (Color, Width, Height, Speed Modifier)
        types = [
            ((220, 53, 69), 40, 75, 2.5),    # Red Sports Car: Fast, Narrow
            ((0, 123, 255), 52, 95, -1.5),   # Blue Delivery Truck: Heavy, Slow
            ((255, 193, 7), 44, 80, 0.0)     # Yellow Sedan: Standard Profile
        ]
        
        color, width, height, speed_mod = random.choice(types)
        
        self.color = color
        self.width = width
        self.height = height
        self.speed = max(3.5, base_speed + speed_mod) # Guarantee it always rolls down
        
        # Safely constrain spawn inside lanes
        self.x = random.randint(ROAD_LEFT + 5, ROAD_RIGHT - self.width - 5)
        self.y = random.randint(-400, -100) # Stagger spawn entry heights
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        self.y += self.speed
        self.rect.y = int(self.y)

    def draw(self, surface):
        # Main Chassis
        pygame.draw.rect(surface, self.color, self.rect, border_radius=5)
        
        # Windshield outline profile
        windshield_y = self.rect.y + (self.height // 3)
        pygame.draw.rect(surface, (40, 40, 40), (self.rect.x + 5, windshield_y, self.width - 10, 18), border_radius=3)
        
        # Tail lights
        pygame.draw.rect(surface, (180, 0, 0), (self.rect.x + 4, self.rect.y + self.height - 6, 8, 4))
        pygame.draw.rect(surface, (180, 0, 0), (self.rect.x + self.width - 12, self.rect.y + self.height - 6, 8, 4))


class BackgroundEnvironment:
    def __init__(self):
        self.line_height = 40
        self.line_gap = 30
        self.scroll_speed = 5.0
        # Initialize an array of track line offsets spanning past window sizes
        self.line_positions = [y for y in range(-self.line_height, SCREEN_HEIGHT, self.line_height + self.line_gap)]

    def update(self, game_speed):
        # Scroll background dynamically linked to general difficulty curve speed
        self.scroll_speed = game_speed
        for i in range(len(self.line_positions)):
            self.line_positions[i] += self.scroll_speed
            if self.line_positions[i] > SCREEN_HEIGHT:
                self.line_positions[i] = -self.line_height

    def draw(self, surface):
        # Draw Side Grass Curbs
        pygame.draw.rect(surface, COLOR_GRASS, (0, 0, ROAD_LEFT, SCREEN_HEIGHT))
        pygame.draw.rect(surface, COLOR_GRASS, (ROAD_RIGHT, 0, ROAD_LEFT, SCREEN_HEIGHT))
        
        # Draw Lane markings (Two-lane dotted separation dividers)
        lane_width = (ROAD_RIGHT - ROAD_LEFT) // 3
        for y_pos in self.line_positions:
            pygame.draw.rect(surface, COLOR_LINE, (ROAD_LEFT + lane_width, y_pos, 6, self.line_height))
            pygame.draw.rect(surface, COLOR_LINE, (ROAD_LEFT + (lane_width * 2), y_pos, 6, self.line_height))


# --- GAME ENGINE CONTROLLER ---

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Neon Highway - Infinite Outrun")
        self.clock = pygame.time.Clock()
        
        # Font settings
        self.font_ui = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_title = pygame.font.SysFont("Arial", 46, bold=True)
        self.font_subtitle = pygame.font.SysFont("Arial", 24)
        
        self.reset_game()

    def reset_game(self):
        self.player = PlayerCar()
        self.environment = BackgroundEnvironment()
        self.enemies = []
        
        self.score = 0
        self.level = 1
        self.base_enemy_speed = 5.0
        self.spawn_timer = 0
        self.spawn_cooldown = 70  # Frame intervals between enemy entries
        
        self.is_game_over = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if self.is_game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

    def update(self):
        if self.is_game_over:
            return

        # Core Game Progress Tracking
        self.score += 1
        
        # Level Scaling Difficulty Mechanics
        new_level = (self.score // 500) + 1
        if new_level != self.level:
            self.level = new_level
            self.base_enemy_speed += 0.8
            self.spawn_cooldown = max(35, self.spawn_cooldown - 6) # Accelerate spawning frequency

        # Update environment & player inputs
        self.environment.update(self.base_enemy_speed)
        self.player.handle_input()
        self.player.update()

        # Handle Enemy Spawning cycles
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_cooldown:
            self.spawn_timer = 0
            if len(self.enemies) < 8: # Maximum entity clamp on-screen to avoid blocking completely
                self.enemies.append(EnemyCar(self.base_enemy_speed))

        # Update enemies positions & process cleanup
        for enemy in self.enemies[:]:
            enemy.update()
            
            # Bounding box collision checker
            if self.player.rect.colliderect(enemy.rect):
                self.is_game_over = True
                
            # Pop off obsolete objects out of display boundaries
            if enemy.y > SCREEN_HEIGHT:
                self.enemies.remove(enemy)

    def draw_ui(self):
        # Render top header dashboard stats tracking
        score_text = self.font_ui.render(f"SCORE: {self.score}", True, COLOR_TEXT)
        level_text = self.font_ui.render(f"LEVEL: {self.level}", True, COLOR_TEXT)
        
        self.screen.blit(score_text, (20, 15))
        self.screen.blit(level_text, (SCREEN_WIDTH - 130, 15))

    def draw_game_over_screen(self):
        # Overlay tint layout surface conversion
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(COLOR_OVERLAY)
        self.screen.blit(overlay, (0, 0))

        # Text layouts configurations
        text_go = self.font_title.render("GAME OVER", True, (255, 75, 75))
        text_sc = self.font_subtitle.render(f"Final Score: {self.score}", True, COLOR_TEXT)
        text_hint = self.font_subtitle.render("Press 'R' to Restart or 'Q' to Quit", True, (200, 200, 200))

        # Center texts positioning loops
        self.screen.blit(text_go, (SCREEN_WIDTH // 2 - text_go.get_width() // 2, SCREEN_HEIGHT // 2 - 80))
        self.screen.blit(text_sc, (SCREEN_WIDTH // 2 - text_sc.get_width() // 2, SCREEN_HEIGHT // 2 - 10))
        self.screen.blit(text_hint, (SCREEN_WIDTH // 2 - text_hint.get_width() // 2, SCREEN_HEIGHT // 2 + 40))

    def run(self):
        while True:
            # Main ticking timeline controller loop
            self.handle_events()
            self.update()
            
            # Screen rendering pipelines resets
            self.screen.fill(COLOR_ROAD)
            
            # Drawing assets layers hierarchy 
            self.environment.draw(self.screen)
            
            for enemy in self.enemies:
                enemy.draw(self.screen)
                
            self.player.draw(self.screen)
            self.draw_ui()
            
            if self.is_game_over:
                self.draw_game_over_screen()

            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()