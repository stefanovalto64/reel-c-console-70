# reel_c_console.py
# Console Reel C - Anni '70
# Giochi: Tennis, Calcio, Pelota, Squash
# Comandi: P1 (destra) = ↑/↓ | P2 (sinistra) = S/X
# Squash: punto a chi ha colpito per ultimo (regole reali adattate)
import pygame
import os
import numpy as np
import random
import time
import sys

# Inizializzazione Pygame
os.environ["SDL_VIDEO_CENTERED"] = "1"
pygame.init()
pygame.mixer.init(frequency=44100, size=8, channels=1)

# Dimensioni base
BASE_WIDTH, BASE_HEIGHT = 640, 480
WIDTH, HEIGHT = BASE_WIDTH, BASE_HEIGHT
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("REEL C - Console Anni '70 by Geppetto 64")

# Colori
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Font
FONT_SIZE = 24
font = pygame.font.Font(None, FONT_SIZE)
SCORE_FONT_SIZE = 76
victory_font = pygame.font.Font(None, 100)
score_font = pygame.font.Font(None, SCORE_FONT_SIZE)
goal_font = pygame.font.Font(None, 140)  # Font grande per "GOL!"

# Fattore di scala
SPEED_SCALE = 1.0

# Superficie per effetto CRT (scanlines)
SCANLINE_SURFACE = None

def update_speed_scale():
    """Aggiorna il fattore di scala in base all'altezza."""
    global SPEED_SCALE
    SPEED_SCALE = HEIGHT / BASE_HEIGHT

def apply_resolution(mode: int):
    """Aggiorna risoluzione e ridisegna la finestra."""
    global WIDTH, HEIGHT, SCREEN
    flags = 0
    if mode == 1:
        WIDTH, HEIGHT = BASE_WIDTH, BASE_HEIGHT
    elif mode == 2:
        WIDTH = int(BASE_WIDTH * 1.6)
        HEIGHT = int(BASE_HEIGHT * 1.6)
    elif mode == 3:
        WIDTH = 1632
        HEIGHT = 920
    elif mode == 4:
        display_info = pygame.display.get_desktop_sizes()
        if display_info:
            max_w, max_h = display_info[0]
        else:
            info = pygame.display.Info()
            max_w, max_h = info.current_w, info.current_h
        WIDTH = int(max_w * 0.98)
        HEIGHT = int(max_h * 0.98)
    else:
        WIDTH, HEIGHT = BASE_WIDTH, BASE_HEIGHT
    SCREEN = pygame.display.set_mode((WIDTH, HEIGHT), flags)
    pygame.display.set_caption(f"REEL C - Console Anni '70 ({WIDTH}x{HEIGHT})")
    update_speed_scale()
    create_scanlines()

def show_resolution_menu():
    """Menu iniziale per scegliere risoluzione."""
    selecting = True
    while selecting:
        SCREEN.fill(BLACK)
        title = font.render("Seleziona Risoluzione", True, WHITE)
        hint = font.render("F1 = Base (640x480)  |  F2 = +60%  |  F3 = 1632x920  |  F4 = 98% Fullscreen", True, YELLOW)
        cur = font.render(f"Attuale: {WIDTH}x{HEIGHT}", True, GREEN)
        cont = font.render("INVIO per continuare  |  ESC per uscire", True, WHITE)
        SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, 140))
        SCREEN.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 190))
        SCREEN.blit(cur, (WIDTH // 2 - cur.get_width() // 2, 230))
        SCREEN.blit(cont, (WIDTH // 2 - cont.get_width() // 2, 280))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    selecting = False
                elif event.key == pygame.K_F1:
                    apply_resolution(1)
                elif event.key == pygame.K_F2:
                    apply_resolution(2)
                elif event.key == pygame.K_F3:
                    apply_resolution(3)
                elif event.key == pygame.K_F4:
                    apply_resolution(4)
    return True

def draw_scoreboard(score_p1, score_p2):
    """Punteggio con etichette VERDE/BIANCO."""
    s1 = score_font.render(str(score_p1), True, WHITE)
    s2 = score_font.render(str(score_p2), True, WHITE)
    colon = score_font.render(":", True, WHITE)
    padding = 20
    total_width = s1.get_width() + padding + colon.get_width() + padding + s2.get_width()
    start_x = WIDTH // 2 - total_width // 2
    label_left = font.render("VERDE", True, GREEN)
    label_right = font.render("BIANCO", True, WHITE)
    left_x = start_x
    colon_x = left_x + s1.get_width() + padding
    right_x = colon_x + colon.get_width() + padding
    SCREEN.blit(label_left, (left_x + (s1.get_width() - label_left.get_width()) // 2, 4))
    SCREEN.blit(label_right, (right_x + (s2.get_width() - label_right.get_width()) // 2, 4))
    y_score = 28
    SCREEN.blit(s1, (left_x, y_score))
    SCREEN.blit(colon, (colon_x, y_score))
    SCREEN.blit(s2, (right_x, y_score))

def draw_single_scoreboard(label_text, score_value, best_value):
    """Punteggio singolo con BEST."""
    label = font.render(label_text, True, WHITE)
    score_surface = score_font.render(str(score_value), True, WHITE)
    best_surface = font.render(f"BEST: {best_value}", True, YELLOW)
    # Calcolo livello: ogni 10 punti, max 10
    livello = min(10, score_value // 10 + 1)
    livello_surface = font.render(f"Livello={livello}", True, WHITE)
    score_x = WIDTH // 2 - score_surface.get_width() // 2
    label_x = WIDTH // 2 - label.get_width() // 2
    SCREEN.blit(label, (label_x, 4))
    SCREEN.blit(score_surface, (score_x, 4 + label.get_height() + 4))
    # BEST in alto a destra
    best_y = 8
    SCREEN.blit(best_surface, (WIDTH - best_surface.get_width() - 10, best_y))
    # Livello subito sotto BEST
    SCREEN.blit(livello_surface, (WIDTH - livello_surface.get_width() - 10, best_y + best_surface.get_height() + 2))

# ================== SUONI ==================
PADDLE_HIT_SOUND = None
WALL_BOUNCE_SOUND = None
POINT_SCORE_SOUND = None
GOAL_SOUND = None
VICTORY_JINGLE = None

def init_sounds():
    global PADDLE_HIT_SOUND, WALL_BOUNCE_SOUND, POINT_SCORE_SOUND, GOAL_SOUND, VICTORY_JINGLE
    sample_rate = 44100
    # Racchetta - acuto
    t = np.linspace(0, 0.06, int(sample_rate * 0.06), False)
    wave = np.sin(2 * np.pi * 523 * t)
    sound_array = (wave * 127 + 128).astype(np.uint8)
    PADDLE_HIT_SOUND = pygame.mixer.Sound(sound_array)
    # Muro - medio
    t = np.linspace(0, 0.08, int(sample_rate * 0.08), False)
    wave = np.sin(2 * np.pi * 392 * t)
    sound_array = (wave * 127 + 128).astype(np.uint8)
    WALL_BOUNCE_SOUND = pygame.mixer.Sound(sound_array)
    # Punto normale - grave
    t = np.linspace(0, 0.15, int(sample_rate * 0.15), False)
    wave = np.sin(2 * np.pi * 220 * t)
    sound_array = (wave * 127 + 128).astype(np.uint8)
    POINT_SCORE_SOUND = pygame.mixer.Sound(sound_array)
    # Goal! - festoso
    frequencies = [659, 784, 1047, 1318]
    durations = [0.1, 0.1, 0.1, 0.3]
    full_wave = []
    for freq, dur in zip(frequencies, durations):
        t = np.linspace(0, dur, int(sample_rate * dur), False)
        wave = np.sin(2 * np.pi * freq * t)
        full_wave.append(wave)
    combined = np.concatenate(full_wave)
    sound_array = ((combined * 127 + 128).astype(np.uint8))
    GOAL_SOUND = pygame.mixer.Sound(sound_array)
    # Jingle vittoria
    frequencies_v = [523, 659, 784, 1047]
    durations_v = [0.15, 0.15, 0.15, 0.3]
    full_wave_v = []
    for freq, dur in zip(frequencies_v, durations_v):
        t = np.linspace(0, dur, int(sample_rate * dur), False)
        wave = np.sin(2 * np.pi * freq * t)
        full_wave_v.append(wave)
    combined_v = np.concatenate(full_wave_v)
    sound_array_v = ((combined_v * 127 + 128).astype(np.uint8))
    VICTORY_JINGLE = pygame.mixer.Sound(sound_array_v)

def play_paddle_hit():
    if PADDLE_HIT_SOUND:
        PADDLE_HIT_SOUND.play()

def play_wall_bounce():
    if WALL_BOUNCE_SOUND:
        WALL_BOUNCE_SOUND.play()

def play_point_score():
    if POINT_SCORE_SOUND:
        POINT_SCORE_SOUND.play()

def play_goal_sound():
    if GOAL_SOUND:
        GOAL_SOUND.play()

def play_victory_jingle():
    if VICTORY_JINGLE:
        VICTORY_JINGLE.play()

# ================== CRT EFFECT ==================
def create_scanlines():
    global SCANLINE_SURFACE
    SCANLINE_SURFACE = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for y in range(0, HEIGHT, 2):
        if y % 4 == 0:
            pygame.draw.line(SCANLINE_SURFACE, (0, 0, 0, 128), (0, y), (WIDTH, y))

def apply_crt_effect(surface):
    if SCANLINE_SURFACE is not None:
        surface.blit(SCANLINE_SURFACE, (0, 0))

# ================== CLASSE BASE GIOCO ==================
class Game:
    def __init__(self):
        self.running = True
        self.score_p1 = 0
        self.score_p2 = 0
        self.clock = pygame.time.Clock()
        self.fps = 30

    def reset(self):
        pass

    def draw(self):
        pass

    def update(self):
        pass

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def run(self):
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            apply_crt_effect(SCREEN)
            pygame.display.flip()
            self.clock.tick(self.fps)

# ================== TENNIS ==================
class Tennis(Game):
    def __init__(self):
        super().__init__()
        self.paddle_width = int(8 * SPEED_SCALE)
        self.paddle_height = int(66 * SPEED_SCALE)
        self.speed = max(1, int(round(7 * SPEED_SCALE)))
        self.paddle1_y = HEIGHT // 2 - self.paddle_height // 2
        self.paddle2_y = HEIGHT // 2 - self.paddle_height // 2
        self.total_points = 0
        self.waiting_start = True
        self.starter = None
        self.show_starter_msg = False
        self.starter_msg_time = 0
        self.ball_waiting = False
        self.level = 1
        self.paused = False
        self.show_level_msg = False
        self.level_msg_time = 0
        self.wins_p1 = 0
        self.wins_p2 = 0
        self.match_winner = None
        self.match_over = False
        self.reset()

    def reset(self):
        base_speed = 5 * SPEED_SCALE
        speed_multiplier = 1.0 + 0.15 * (self.level - 1)
        mag = base_speed * speed_multiplier
        self.ball_x = WIDTH // 2
        self.ball_y = HEIGHT // 2
        if self.ball_waiting:
            self.ball_speed_x = 0
            self.ball_speed_y = 0
        else:
            self.ball_speed_x = random.choice([-mag, mag])
            self.ball_speed_y = random.choice([-mag, mag])

    def draw_dashed_rect(self):
        for x in range(0, WIDTH, 20):
            pygame.draw.line(SCREEN, WHITE, (x, 0), (x + 10, 0), 2)
            pygame.draw.line(SCREEN, WHITE, (x, HEIGHT), (x + 10, HEIGHT), 2)
        for y in range(0, HEIGHT, 20):
            pygame.draw.line(SCREEN, WHITE, (0, y), (0, y + 10), 2)
            pygame.draw.line(SCREEN, WHITE, (WIDTH, y), (WIDTH, y + 10), 2)

    def draw(self):
        SCREEN.fill(BLACK)
        self.draw_dashed_rect()
        for y in range(0, HEIGHT, 20):
            pygame.draw.rect(SCREEN, WHITE, (WIDTH // 2 - 2, y, 4, 10))
        pygame.draw.rect(SCREEN, GREEN, (10, self.paddle1_y, self.paddle_width, self.paddle_height))
        pygame.draw.rect(SCREEN, WHITE, (WIDTH - 20 - self.paddle_width, self.paddle2_y, self.paddle_width, self.paddle_height))
        pygame.draw.circle(SCREEN, WHITE, (int(self.ball_x), int(self.ball_y)), 6)
        draw_scoreboard(self.score_p1, self.score_p2)
        livello_text = font.render(f"Livello: {self.level}", True, YELLOW)
        SCREEN.blit(livello_text, (WIDTH - livello_text.get_width() - 20, 10))
        
        # Mostra vittorie dei livelli
        wins_text = font.render(f"Vittorie - Verde: {self.wins_p1}  Bianco: {self.wins_p2}", True, WHITE)
        SCREEN.blit(wins_text, (10, 10))
        
        # Scritta del livello al centro per 3 secondi
        if self.show_level_msg and time.time() - self.level_msg_time < 3:
            level_font = pygame.font.Font(None, int(10 * 2.83))  # 10mm ≈ 28.3 pixel
            level_msg = level_font.render(f"{self.level} LIVELLO", True, WHITE)
            SCREEN.blit(level_msg, (WIDTH // 2 - level_msg.get_width() // 2, HEIGHT // 2 - level_msg.get_height() // 2))
        
        # Scritta vittoria match
        if self.match_over and self.match_winner:
            win_font = pygame.font.Font(None, int(20 * 2.83))  # 20mm ≈ 56.6 pixel
            winner_name = "VERDE" if self.match_winner == 'p1' else "BIANCO"
            winner_color = GREEN if self.match_winner == 'p1' else WHITE
            win_msg = win_font.render(f"HA VINTO IL GIOCATORE {winner_name}", True, winner_color)
            SCREEN.blit(win_msg, (WIDTH // 2 - win_msg.get_width() // 2, HEIGHT // 2 - win_msg.get_height() // 2))
            
        if self.waiting_start:
            msg = font.render("Premere G per iniziare", True, YELLOW)
            SCREEN.blit(msg, (WIDTH // 2 - msg.get_width() // 2, 90))
            pause_msg = font.render("Premere P per pausa gioco e ripremere P per continuare", True, ORANGE)
            SCREEN.blit(pause_msg, (WIDTH // 2 - pause_msg.get_width() // 2, 120))
            if self.show_starter_msg and self.starter:
                starter_col = GREEN if self.starter == 'p1' else WHITE
                starter_txt = "VERDE" if self.starter == 'p1' else "BIANCO"
                starter_msg = font.render(f"Inizia il giocatore: {starter_txt}", True, starter_col)
                SCREEN.blit(starter_msg, (WIDTH // 2 - starter_msg.get_width() // 2, 150))
        elif self.ball_waiting and self.show_starter_msg and self.starter:
            if time.time() - self.starter_msg_time < 3:
                starter_col = GREEN if self.starter == 'p1' else WHITE
                starter_txt = "VERDE" if self.starter == 'p1' else "BIANCO"
                starter_msg = font.render(f"Inizia il giocatore: {starter_txt}", True, starter_col)
                SCREEN.blit(starter_msg, (WIDTH // 2 - starter_msg.get_width() // 2, 90))
                pause_msg = font.render("Premere P per pausa gioco e ripremere P per continuare", True, ORANGE)
                SCREEN.blit(pause_msg, (WIDTH // 2 - pause_msg.get_width() // 2, 120))
            else:
                self.show_starter_msg = False
                self.ball_waiting = False
                base_speed = 5 * SPEED_SCALE
                speed_multiplier = 1.0 + 0.15 * (self.level - 1)
                mag = base_speed * speed_multiplier
                self.ball_speed_x = random.choice([-mag, mag])
                self.ball_speed_y = random.choice([-mag, mag])

    def update(self):
        if self.waiting_start or self.ball_waiting or self.paused:
            return
        self.ball_x += self.ball_speed_x
        self.ball_y += self.ball_speed_y
        if self.ball_y <= 0 or self.ball_y >= HEIGHT:
            self.ball_speed_y *= -1
            play_wall_bounce()
        if (self.ball_x <= 20 and self.paddle1_y <= self.ball_y <= self.paddle1_y + self.paddle_height):
            self.ball_speed_x *= -1.1
            play_paddle_hit()
        if (self.ball_x >= WIDTH - 20 and self.paddle2_y <= self.ball_y <= self.paddle2_y + self.paddle_height):
            self.ball_speed_x *= -1.1
            play_paddle_hit()
        if self.ball_x < 0:
            self.score_p2 += 1
            self.total_points += 1
            play_point_score()
            # Controllo se il giocatore 2 ha raggiunto 7 punti
            if self.score_p2 >= 7:
                self.wins_p2 += 1
                self.level += 1
                self.score_p1 = 0
                self.score_p2 = 0
                self.show_level_msg = True
                self.level_msg_time = time.time()
                # Controllo vittoria match
                if self.wins_p2 >= 3:
                    self.match_winner = 'p2'
                    self.match_over = True
            self.reset()
        if self.ball_x > WIDTH:
            self.score_p1 += 1
            self.total_points += 1
            play_point_score()
            # Controllo se il giocatore 1 ha raggiunto 7 punti
            if self.score_p1 >= 7:
                self.wins_p1 += 1
                self.level += 1
                self.score_p1 = 0
                self.score_p2 = 0
                self.show_level_msg = True
                self.level_msg_time = time.time()
                # Controllo vittoria match
                if self.wins_p1 >= 3:
                    self.match_winner = 'p1'
                    self.match_over = True
            self.reset()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_s] and self.paddle1_y > 0:
            self.paddle1_y -= self.speed
        if keys[pygame.K_x] and self.paddle1_y < HEIGHT - self.paddle_height:
            self.paddle1_y += self.speed
        if keys[pygame.K_UP] and self.paddle2_y > 0:
            self.paddle2_y -= self.speed
        if keys[pygame.K_DOWN] and self.paddle2_y < HEIGHT - self.paddle_height:
            self.paddle2_y += self.speed

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_p and not self.waiting_start:
                    self.paused = not self.paused
                if self.waiting_start and event.key == pygame.K_g:
                    self.starter = random.choice(['p1', 'p2'])
                    self.show_starter_msg = True
                    self.starter_msg_time = time.time()
                    self.ball_waiting = True
                    self.ball_speed_x = 0
                    self.ball_speed_y = 0
                    self.waiting_start = False

# ================== CALCIO ==================
class Soccer(Game):
    def __init__(self):
        super().__init__()
        self.player_width = int(10 * SPEED_SCALE)
        self.player_height = int(30 * SPEED_SCALE)
        self.speed = int(6 * SPEED_SCALE)
        self.goal_width = int(160 * SPEED_SCALE)
        self.player1_y = HEIGHT // 2 - self.player_height // 2
        self.player2_y = HEIGHT // 2 - self.player_height // 2
        self.last_hitter = None
        self.ball_speed_multiplier = 1.0
        self.game_over = False
        self.winner = None
        self.victory_time = 0
        self.victory_played = False
        self.waiting_start = True
        self.goal_mode = False
        self.goal_timer = 0
        self.starter = None
        self.show_starter_msg = False
        self.starter_msg_time = 0
        self.ball_waiting = False
        self.paused = False
        self.reset()

    def reset(self):
        base = 4 * SPEED_SCALE
        mag = base * self.ball_speed_multiplier
        self.ball_x = WIDTH // 2
        self.ball_y = HEIGHT // 2
        if self.ball_waiting:
            self.ball_speed_x = 0
            self.ball_speed_y = 0
        else:
            self.ball_speed_x = random.choice([-mag, mag])
            self.ball_speed_y = random.choice([-mag, mag])
        self.last_hitter = None

    def draw_soccer_field(self):
        line_width = 4

        # Bordo esterno
        pygame.draw.rect(SCREEN, WHITE, (0, 0, WIDTH, HEIGHT), line_width)

        # Linea di metà campo
        pygame.draw.line(SCREEN, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), line_width)

        # Cerchio di centrocampo e punto centrale
        center_radius = int(HEIGHT * 0.15)
        pygame.draw.circle(SCREEN, WHITE, (WIDTH // 2, HEIGHT // 2), center_radius, line_width)
        pygame.draw.circle(SCREEN, WHITE, (WIDTH // 2, HEIGHT // 2), int(line_width * 1.5))

        # Aree di rigore
        penalty_area_width = int(WIDTH * 0.125)
        penalty_area_height = int(HEIGHT * 0.45)
        # Area sinistra
        left_penalty_area = pygame.Rect(0, (HEIGHT - penalty_area_height) / 2, penalty_area_width, penalty_area_height)
        pygame.draw.rect(SCREEN, WHITE, left_penalty_area, line_width)
        # Area destra
        right_penalty_area = pygame.Rect(WIDTH - penalty_area_width, (HEIGHT - penalty_area_height) / 2, penalty_area_width, penalty_area_height)
        pygame.draw.rect(SCREEN, WHITE, right_penalty_area, line_width)

        # Punto del calcio di rigore
        penalty_spot_left_x = int(WIDTH * 0.1)
        penalty_spot_right_x = int(WIDTH * 0.9)
        pygame.draw.circle(SCREEN, WHITE, (penalty_spot_left_x, HEIGHT // 2), int(line_width * 1.5))
        pygame.draw.circle(SCREEN, WHITE, (penalty_spot_right_x, HEIGHT // 2), int(line_width * 1.5))

        # Arco dell'area di rigore
        arc_radius = int(HEIGHT * 0.1)
        # Arco sinistro
        arc_rect_left = pygame.Rect(penalty_spot_left_x - arc_radius, HEIGHT / 2 - arc_radius, arc_radius * 2, arc_radius * 2)
        pygame.draw.arc(SCREEN, WHITE, arc_rect_left, -np.pi / 2.8, np.pi / 2.8, line_width)
        # Arco destro
        arc_rect_right = pygame.Rect(penalty_spot_right_x - arc_radius, HEIGHT / 2 - arc_radius, arc_radius * 2, arc_radius * 2)
        pygame.draw.arc(SCREEN, WHITE, arc_rect_right, np.pi - np.pi / 2.8, np.pi + np.pi / 2.8, line_width)

        # Archi d'angolo
        corner_radius = int(WIDTH * 0.05)
        # Angolo in alto a sinistra
        pygame.draw.arc(SCREEN, WHITE, pygame.Rect(-corner_radius, -corner_radius, corner_radius*2, corner_radius*2), 0, np.pi/2, line_width)
        # Angolo in alto a destra
        pygame.draw.arc(SCREEN, WHITE, pygame.Rect(WIDTH-corner_radius, -corner_radius, corner_radius*2, corner_radius*2), np.pi/2, np.pi, line_width)
        # Angolo in basso a sinistra
        pygame.draw.arc(SCREEN, WHITE, pygame.Rect(-corner_radius, HEIGHT-corner_radius, corner_radius*2, corner_radius*2), 3*np.pi/2, 2*np.pi, line_width)
        # Angolo in basso a destra
        pygame.draw.arc(SCREEN, WHITE, pygame.Rect(WIDTH-corner_radius, HEIGHT-corner_radius, corner_radius*2, corner_radius*2), np.pi, 3*np.pi/2, line_width)

    def draw(self):
        SCREEN.fill(BLACK)
        self.draw_soccer_field()

        # Porte (già presenti nel gioco)
        pygame.draw.rect(SCREEN, GREEN, (0, HEIGHT//2 - self.goal_width//2, 20, self.goal_width), 2)
        pygame.draw.rect(SCREEN, WHITE, (WIDTH - 20, HEIGHT//2 - self.goal_width//2, 20, self.goal_width), 2)

        # Giocatori
        pygame.draw.rect(SCREEN, GREEN, (30, self.player1_y, self.player_width, self.player_height))
        pygame.draw.rect(SCREEN, WHITE, (WIDTH - 30 - self.player_width, self.player2_y, self.player_width, self.player_height))

        # Palla
        pygame.draw.circle(SCREEN, WHITE, (int(self.ball_x), int(self.ball_y)), 12)

        # Punteggio
        draw_scoreboard(self.score_p1, self.score_p2)

        # Livello
        level = int(self.ball_speed_multiplier / 1.05) + 1
        level_text = font.render(f"LIV: {level}", True, YELLOW)
        SCREEN.blit(level_text, (WIDTH - 100, 10))

        # Messaggio di attesa
        if self.waiting_start:
            msg = font.render("Premere G per iniziare gioco", True, YELLOW)
            SCREEN.blit(msg, (WIDTH // 2 - msg.get_width() // 2, 90))
            pause_msg = font.render("Premere P per pausa gioco e ripremere P per continuare", True, ORANGE)
            SCREEN.blit(pause_msg, (WIDTH // 2 - pause_msg.get_width() // 2, 120))
            if self.show_starter_msg and self.starter:
                starter_col = GREEN if self.starter == 'p1' else WHITE
                starter_txt = "VERDE" if self.starter == 'p1' else "BIANCO"
                starter_msg = font.render(f"Inizia il giocatore: {starter_txt}", True, starter_col)
                SCREEN.blit(starter_msg, (WIDTH // 2 - starter_msg.get_width() // 2, 150))
        elif self.ball_waiting and self.show_starter_msg and self.starter:
            if time.time() - self.starter_msg_time < 5:
                starter_col = GREEN if self.starter == 'p1' else WHITE
                starter_txt = "VERDE" if self.starter == 'p1' else "BIANCO"
                starter_msg = font.render(f"Inizia il giocatore: {starter_txt}", True, starter_col)
                SCREEN.blit(starter_msg, (WIDTH // 2 - starter_msg.get_width() // 2, 90))
                pause_msg = font.render("Premere P per pausa gioco e ripremere P per continuare", True, ORANGE)
                SCREEN.blit(pause_msg, (WIDTH // 2 - pause_msg.get_width() // 2, 120))
            else:
                self.show_starter_msg = False
                self.ball_waiting = False
                base = 4 * SPEED_SCALE
                mag = base * self.ball_speed_multiplier
                if self.starter == 'p1':
                    self.ball_speed_x = -abs(mag)
                else:
                    self.ball_speed_x = abs(mag)
                self.ball_speed_y = random.choice([-mag, mag])

        # Effetto "GOL!" con messaggio personalizzato
        if self.goal_mode:
            goal_text = goal_font.render("GOAL!", True, YELLOW)
            goal_rect = goal_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            SCREEN.blit(goal_text, goal_rect)

            # Scritta sotto: chi ha segnato
            if self.last_hitter == 'p1':
                player_text = font.render("Il giocatore VERDE ha segnato!", True, GREEN)
            else:
                player_text = font.render("Il giocatore BIANCO ha segnato!", True, WHITE)
            player_rect = player_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
            SCREEN.blit(player_text, player_rect)

        # Schermata vittoria
        if self.game_over and self.winner:
            win_text = font.render(f"VITTORIA: {self.winner}", True, GREEN if self.winner == "VERDE" else WHITE)
            cont_text = font.render("ESC per uscire", True, WHITE)
            SCREEN.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2 - 40))
            SCREEN.blit(cont_text, (WIDTH//2 - cont_text.get_width()//2, HEIGHT//2 + 10))

    def update(self):
        if self.game_over or self.waiting_start or self.ball_waiting or self.goal_mode or self.paused:
            if self.goal_mode:
                self.goal_timer -= 1
                if self.goal_timer <= 0:
                    self.goal_mode = False
                    self.reset()
            return

        self.ball_x += self.ball_speed_x
        self.ball_y += self.ball_speed_y

        if self.ball_y <= 0 or self.ball_y >= HEIGHT:
            self.ball_speed_y *= -1
            play_wall_bounce()

        p1_rect = pygame.Rect(10, self.player1_y, self.player_width, self.player_height)
        p2_rect = pygame.Rect(WIDTH - 30 - self.player_width, self.player2_y, self.player_width, self.player_height)
        ball_rect = pygame.Rect(self.ball_x - 12, self.ball_y - 12, 24, 24)

        if ball_rect.colliderect(p1_rect):
            self.ball_speed_x *= -1.1
            self.last_hitter = 'p1'
            play_paddle_hit()
        if ball_rect.colliderect(p2_rect):
            self.ball_speed_x *= -1.1
            self.last_hitter = 'p2'
            play_paddle_hit()

        # Goal
        if (self.ball_x < 20 and HEIGHT//2 - self.goal_width//2 < self.ball_y < HEIGHT//2 + self.goal_width//2):
            self.score_p2 += 5
            self.ball_speed_multiplier *= 1.05
            play_goal_sound()
            self.goal_mode = True
            self.goal_timer = int(1.6 * self.fps)
            return
        if (self.ball_x > WIDTH - 20 and HEIGHT//2 - self.goal_width//2 < self.ball_y < HEIGHT//2 + self.goal_width//2):
            self.score_p1 += 5
            self.ball_speed_multiplier *= 1.05
            play_goal_sound()
            self.goal_mode = True
            self.goal_timer = int(1.6 * self.fps)
            return

        # Punto per errore
        if self.ball_x > WIDTH:
            if self.last_hitter == 'p1':
                self.score_p1 += 1
                play_point_score()
                self.ball_speed_multiplier *= 1.00
                self.reset()
            return
        if self.ball_x < 0:
            if self.last_hitter == 'p2':
                self.score_p2 += 1
                play_point_score()
                self.ball_speed_multiplier *= 1.00
                self.reset()
            return

        # Vittoria
        if self.score_p1 >= 100:
            self.game_over = True
            self.winner = "VERDE"
            if not self.victory_played:
                play_victory_jingle()
                self.victory_played = True
        elif self.score_p2 >= 100:
            self.game_over = True
            self.winner = "BIANCO"
            if not self.victory_played:
                play_victory_jingle()
                self.victory_played = True

        # Movimenti
        keys = pygame.key.get_pressed()
        if keys[pygame.K_s] and self.player1_y > 0:
            self.player1_y -= self.speed
        if keys[pygame.K_x] and self.player1_y < HEIGHT - self.player_height:
            self.player1_y += self.speed
        if keys[pygame.K_UP] and self.player2_y > 0:
            self.player2_y -= self.speed
        if keys[pygame.K_DOWN] and self.player2_y < HEIGHT - self.player_height:
            self.player2_y += self.speed

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_p and not self.waiting_start:
                    self.paused = not self.paused
                if self.waiting_start and event.key == pygame.K_g:
                    self.starter = random.choice(['p1', 'p2'])
                    self.show_starter_msg = True
                    self.starter_msg_time = time.time()
                    self.ball_waiting = True
                    self.ball_speed_x = 0
                    self.ball_speed_y = 0
                    self.waiting_start = False

# ================== PELOTA ==================
class Pelota(Game):
    def __init__(self):
        super().__init__()
        self.base_speed = 5 * SPEED_SCALE
        self.ball_x = WIDTH // 2
        self.ball_y = HEIGHT // 2
        self.ball_speed_x = -self.base_speed
        self.ball_speed_y = random.choice([-self.base_speed, self.base_speed])
        self.paddle_width = int(10 * SPEED_SCALE)
        self.paddle_height = int(66 * SPEED_SCALE)
        self.speed = int(7 * SPEED_SCALE)
        self.paddle_y = HEIGHT // 2 - self.paddle_height // 2
        self.level = 1
        self.max_level = 6
        self.current_score = 0
        self.best_score = 0
        self.hits = 0
        self.waiting_start = True
        self.paused = False
        self.apply_speed_from_level(preserve_direction=False)

    def update_multiplier(self):
        self.level = max(1, min(self.level, self.max_level))
        return 1.0 + 0.2 * (self.level - 1)

    def apply_speed_from_level(self, preserve_direction=True):
        mag = self.base_speed * self.update_multiplier()
        if preserve_direction:
            sx = -1 if self.ball_speed_x < 0 else 1
            sy = -1 if self.ball_speed_y < 0 else 1
            self.ball_speed_x = sx * mag
            self.ball_speed_y = sy * mag
        else:
            self.ball_speed_x = -mag
            self.ball_speed_y = random.choice([-mag, mag])

    def reset(self):
        self.ball_x = WIDTH // 2
        self.ball_y = HEIGHT // 2
        self.apply_speed_from_level(preserve_direction=False)
        self.hits = 0

    def draw_dashed_rect(self):
        for x in range(0, WIDTH, 20):
            pygame.draw.line(SCREEN, WHITE, (x, 0), (x + 10, 0), 2)
            pygame.draw.line(SCREEN, WHITE, (x, HEIGHT), (x + 10, HEIGHT), 2)
        for y in range(0, HEIGHT, 20):
            pygame.draw.line(SCREEN, WHITE, (0, y), (0, y + 10), 2)
            pygame.draw.line(SCREEN, WHITE, (WIDTH, y), (WIDTH, y + 10), 2)

    def draw_brick_wall(self):
        """Disegna un muro di mattoni sul lato sinistro"""
        brick_width = 20
        brick_height = 12
        wall_width = 40
        
        # Disegna i mattoni riga per riga
        for row in range(0, HEIGHT, brick_height):
            # Alterna l'offset dei mattoni per creare il pattern tipico
            offset = (brick_width // 2) if (row // brick_height) % 2 == 1 else 0
            
            # Disegna i mattoni in questa riga
            x = -offset
            while x < wall_width:
                # Solo disegna mattoni che sono visibili
                if x + brick_width > 0 and x < wall_width:
                    # Limita le dimensioni del mattone ai bordi
                    start_x = max(0, x)
                    end_x = min(wall_width, x + brick_width)
                    actual_width = end_x - start_x
                    
                    if actual_width > 0:
                        # Disegna il mattone
                        pygame.draw.rect(SCREEN, WHITE, 
                                       (start_x, row, actual_width, brick_height), 2)
                x += brick_width

    def draw(self):
        SCREEN.fill(BLACK)
        self.draw_dashed_rect()
        self.draw_brick_wall()  # Disegna il muro di mattoni invece del rettangolo semplice
        pygame.draw.rect(SCREEN, WHITE, (WIDTH - 30 - self.paddle_width, self.paddle_y, self.paddle_width, self.paddle_height))
        pygame.draw.circle(SCREEN, WHITE, (int(self.ball_x), int(self.ball_y)), 10)
        draw_single_scoreboard("BIANCO", self.current_score, self.best_score)
        hud_text = font.render(f"HITS: {self.hits}   VEL: {self.update_multiplier():.2f}x   LIV: {self.level}", True, GREEN)
        SCREEN.blit(hud_text, (10, HEIGHT - 28))
        if self.waiting_start:
            msg = font.render("Premere G per iniziare gioco", True, YELLOW)
            SCREEN.blit(msg, (WIDTH // 2 - msg.get_width() // 2, 90))
            pause_msg = font.render("Premere P per pausa gioco e ripremere P per continuare", True, ORANGE)
            SCREEN.blit(pause_msg, (WIDTH // 2 - pause_msg.get_width() // 2, 120))

    def update(self):
        if self.waiting_start or self.paused:
            return
        self.ball_x += self.ball_speed_x
        self.ball_y += self.ball_speed_y
        if self.ball_y <= 0 or self.ball_y >= HEIGHT:
            self.ball_speed_y *= -1
            play_wall_bounce()
        if self.ball_x <= 40:
            self.apply_speed_from_level(preserve_direction=True)
            self.ball_speed_x = abs(self.ball_speed_x)
            play_wall_bounce()
        if (self.ball_x >= WIDTH - 50 - self.paddle_width and
            self.paddle_y <= self.ball_y <= self.paddle_y + self.paddle_height):
            self.apply_speed_from_level(preserve_direction=True)
            self.ball_speed_x = -abs(self.ball_speed_x)
            self.hits += 1
            self.current_score += 1
            if self.current_score > self.best_score:
                self.best_score = self.current_score
            if self.current_score % 10 == 0 and self.level < self.max_level:
                self.level += 1
                self.apply_speed_from_level(preserve_direction=True)
            play_paddle_hit()
        if self.ball_x > WIDTH:
            self.current_score = 0
            self.hits = 0
            self.level = 1
            play_point_score()
            self.reset()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and self.paddle_y > 0:
            self.paddle_y -= self.speed
        if keys[pygame.K_DOWN] and self.paddle_y < HEIGHT - self.paddle_height:
            self.paddle_y += self.speed

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_p and not self.waiting_start:
                    self.paused = not self.paused
                if self.waiting_start and event.key == pygame.K_g:
                    self.waiting_start = False

# ================== SQUASH ==================
class Squash(Game):
    def __init__(self):
        super().__init__()
        self.paddle_width = int(10 * SPEED_SCALE)
        self.paddle_height = int(66 * SPEED_SCALE)
        self.speed = int(7 * SPEED_SCALE)
        self.paddle_green_y = HEIGHT // 2 - self.paddle_height // 2
        self.paddle_white_y = HEIGHT // 2 - self.paddle_height // 2
        self.ball_x = WIDTH // 2
        self.ball_y = HEIGHT // 2
        self.last_hitter = None
        self.game_over = False
        self.winner = None
        self.victory_time = 0
        self.victory_played = False
        self.ball_speed_multiplier = 1.0
        self.waiting_start = True
        self.starter = random.choice(["BIANCO", "VERDE"])
        self.paused = False
        self.reset()

    def reset(self):
        base = 5 * SPEED_SCALE
        mag = base * self.ball_speed_multiplier
        self.ball_x = 30 + self.paddle_width + 10
        self.ball_speed_x = mag
        self.ball_y = HEIGHT // 2
        self.ball_speed_y = random.choice([-mag, mag])
        self.last_hitter = None

    def draw_dashed_rect(self):
        for x in range(0, WIDTH, 20):
            pygame.draw.line(SCREEN, WHITE, (x, 0), (x + 10, 0), 2)
            pygame.draw.line(SCREEN, WHITE, (x, HEIGHT), (x + 10, HEIGHT), 2)
        for y in range(0, HEIGHT, 20):
            pygame.draw.line(SCREEN, WHITE, (0, y), (0, y + 10), 2)
            pygame.draw.line(SCREEN, WHITE, (WIDTH, y), (WIDTH, y + 10), 2)

    def draw(self):
        SCREEN.fill(BLACK)
        self.draw_dashed_rect()
        pygame.draw.line(SCREEN, WHITE, (0, 0), (WIDTH, 0), 2)
        pygame.draw.line(SCREEN, WHITE, (0, HEIGHT), (WIDTH, HEIGHT), 2)
        pygame.draw.line(SCREEN, WHITE, (0, 0), (0, HEIGHT), 2)
        pygame.draw.line(SCREEN, WHITE, (WIDTH, 0), (WIDTH, HEIGHT), 2)
        pygame.draw.rect(SCREEN, GREEN, (WIDTH - 52 - self.paddle_width, self.paddle_green_y, self.paddle_width, self.paddle_height))
        pygame.draw.rect(SCREEN, WHITE, (WIDTH - 28 - self.paddle_width, self.paddle_white_y, self.paddle_width, self.paddle_height))
        if not self.game_over and not self.waiting_start:
            pygame.draw.circle(SCREEN, WHITE, (int(self.ball_x), int(self.ball_y)), 10)
        draw_scoreboard(self.score_p1, self.score_p2)
        max_score = max(self.score_p1, self.score_p2)
        level = max(1, (max_score // 10) + 1)
        level_text = font.render(f"LIV: {level}", True, YELLOW)
        SCREEN.blit(level_text, (WIDTH - 100, 10))
        if not self.waiting_start:
            tocca = 'VERDE' if self.last_hitter == 'p1' else 'BIANCO' if self.last_hitter == 'p2' else self.starter
            tocca_col = GREEN if tocca == 'VERDE' else WHITE
            tocca_msg = font.render(f"Tocca al giocatore: {tocca}", True, tocca_col)
            SCREEN.blit(tocca_msg, (WIDTH // 2 - tocca_msg.get_width() // 2, 28 + score_font.get_height() + 20))
        if self.waiting_start:
            msg = font.render("Premere G per iniziare gioco", True, YELLOW)
            SCREEN.blit(msg, (WIDTH // 2 - msg.get_width() // 2, 90))
            pause_msg = font.render("Premere P per pausa gioco e ripremere P per continuare", True, ORANGE)
            SCREEN.blit(pause_msg, (WIDTH // 2 - pause_msg.get_width() // 2, 120))
            starter_msg = font.render(f"Il giocatore che inizia è: {self.starter}", True, GREEN if self.starter=="VERDE" else WHITE)
            SCREEN.blit(starter_msg, (WIDTH // 2 - starter_msg.get_width() // 2, 150))
        elif self.paused:
            pause_text = font.render("GIOCO IN PAUSA", True, WHITE)
            SCREEN.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 20))
            resume_text = font.render("Premere P per riprendere", True, ORANGE)
            SCREEN.blit(resume_text, (WIDTH // 2 - resume_text.get_width() // 2, HEIGHT // 2 + 20))
        if self.game_over and self.winner:
            elapsed = time.time() - self.victory_time
            pulse_scale = 1 + 0.2 * np.sin(elapsed * 8)
            color = GREEN if self.winner == "VERDE" else WHITE
            blink = int(elapsed * 5) % 2 == 0
            win_text = victory_font.render("VITTORIA:", True, color if blink else YELLOW)
            player_text = victory_font.render(f"{self.winner}", True, color)
            win_text = pygame.transform.rotozoom(win_text, 0, pulse_scale)
            player_text = pygame.transform.rotozoom(player_text, 0, pulse_scale)
            SCREEN.blit(win_text, win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))
            SCREEN.blit(player_text, player_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))
            cont_text = font.render("ESC per uscire", True, WHITE)
            SCREEN.blit(cont_text, (WIDTH // 2 - cont_text.get_width() // 2, HEIGHT // 2 + 100))

    def update(self):
        if self.game_over or self.waiting_start or self.paused:
            return
        self.ball_x += self.ball_speed_x
        self.ball_y += self.ball_speed_y
        if self.ball_y <= 0 or self.ball_y >= HEIGHT:
            self.ball_speed_y *= -1
            play_wall_bounce()
        if self.ball_x <= 0:
            self.ball_speed_x *= -1
            play_wall_bounce()
        if self.ball_x > WIDTH:
            if self.last_hitter == 'p1':
                self.score_p2 += 1
            elif self.last_hitter == 'p2':
                self.score_p1 += 1
            play_point_score()
            self.ball_speed_multiplier *= 1.15
            self.reset()
            if self.score_p1 >= 100:
                self.game_over = True
                self.winner = "BIANCO"
                if not self.victory_played:
                    play_victory_jingle()
                    self.victory_played = True
            elif self.score_p2 >= 100:
                self.game_over = True
                self.winner = "VERDE"
                if not self.victory_played:
                    play_victory_jingle()
                    self.victory_played = True
            return
        green_paddle_rect = pygame.Rect(WIDTH - 50 - self.paddle_width, self.paddle_green_y, self.paddle_width, self.paddle_height)
        white_paddle_rect = pygame.Rect(WIDTH - 30 - self.paddle_width, self.paddle_white_y, self.paddle_width, self.paddle_height)
        ball_rect = pygame.Rect(self.ball_x - 10, self.ball_y - 10, 20, 20)
        def calculate_angle_bounce(paddle_rect):
            hit_pos = (self.ball_y - paddle_rect.centery) / (paddle_rect.height / 2)
            speed_mag = abs(self.ball_speed_x)
            return hit_pos * speed_mag * 1.5
        if ball_rect.colliderect(white_paddle_rect) and self.ball_speed_x > 0:
            if self.last_hitter == 'p1':
                self.score_p2 += 1
                play_point_score()
                self.ball_speed_multiplier *= 1.15
                self.reset()
                if self.score_p2 >= 100:
                    self.game_over = True
                    self.winner = "VERDE"
                    if not self.victory_played:
                        play_victory_jingle()
                        self.victory_played = True
                return
            self.ball_speed_x *= -1.1
            self.ball_speed_y = calculate_angle_bounce(white_paddle_rect)
            self.ball_x = white_paddle_rect.left - 10
            play_paddle_hit()
            self.last_hitter = 'p1'
        if ball_rect.colliderect(green_paddle_rect) and self.ball_speed_x > 0:
            if self.last_hitter == 'p2':
                self.score_p1 += 1
                play_point_score()
                self.ball_speed_multiplier *= 1.15
                self.reset()
                if self.score_p1 >= 100:
                    self.game_over = True
                    self.winner = "BIANCO"
                    if not self.victory_played:
                        play_victory_jingle()
                        self.victory_played = True
                return
            self.ball_speed_x *= -1.1
            self.ball_speed_y = calculate_angle_bounce(green_paddle_rect)
            self.ball_x = green_paddle_rect.left - 10
            play_paddle_hit()
            self.last_hitter = 'p2'
        keys = pygame.key.get_pressed()
        if keys[pygame.K_s] and self.paddle_green_y > 0:
            self.paddle_green_y -= self.speed
        if keys[pygame.K_x] and self.paddle_green_y < HEIGHT - self.paddle_height:
            self.paddle_green_y += self.speed
        if keys[pygame.K_UP] and self.paddle_white_y > 0:
            self.paddle_white_y -= self.speed
        if keys[pygame.K_DOWN] and self.paddle_white_y < HEIGHT - self.paddle_height:
            self.paddle_white_y += self.speed

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_p and not self.waiting_start:
                    self.paused = not self.paused
                if self.waiting_start and event.key == pygame.K_g:
                    self.waiting_start = False

# ================== BOOT & MENU ==================
def boot_sequence():
    SCREEN.fill(BLACK)
    title = font.render("REEL C", True, GREEN)
    version = font.render("1978", True, GREEN)
    loading = font.render("LOADING...", True, GREEN)
    SCREEN.blit(title, (WIDTH // 2 - 60, HEIGHT // 2 - 60))
    SCREEN.blit(version, (WIDTH // 2 - 40, HEIGHT // 2 - 30))
    SCREEN.blit(loading, (WIDTH // 2 - 70, HEIGHT // 2 + 10))
    pygame.display.flip()
    play_point_score()
    time.sleep(1)
    for _ in range(5):
        SCREEN.fill(BLACK)
        SCREEN.blit(title, (WIDTH // 2 - 60, HEIGHT // 2 - 60))
        SCREEN.blit(version, (WIDTH // 2 - 40, HEIGHT // 2 - 30))
        SCREEN.blit(loading, (WIDTH // 2 - 70, HEIGHT // 2 + 10))
        pygame.display.flip()
        time.sleep(0.5)
        SCREEN.fill(BLACK)
        pygame.display.flip()
        time.sleep(0.5)
    SCREEN.fill(BLACK)
    ready = font.render("READY TO PLAY", True, GREEN)
    SCREEN.blit(ready, (WIDTH // 2 - 100, HEIGHT // 2))
    pygame.display.flip()
    play_paddle_hit()
    time.sleep(1)

def show_menu():
    running = True
    while running:
        SCREEN.fill(BLACK)
        title = font.render("REEL C - CONSOLE 1978", True, WHITE)
        options = [
            "1. TENNIS",
            "2. CALCIO",
            "3. PELOTA",
            "4. SQUASH",
            "ESC - Uscita"
        ]
        SCREEN.blit(title, (WIDTH // 2 - 140, 80))
        for i, text in enumerate(options):
            color = GREEN if i == 0 else WHITE
            txt = font.render(text, True, color)
            SCREEN.blit(txt, (WIDTH // 2 - 100, 130 + i * 40))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_1:
                    return Tennis()
                elif event.key == pygame.K_2:
                    return Soccer()
                elif event.key == pygame.K_3:
                    return Pelota()
                elif event.key == pygame.K_4:
                    return Squash()

# ================== MAIN ==================
def main():
    init_sounds()
    boot_sequence()
    create_scanlines()
    while True:
        if not show_resolution_menu():
            break
        game = show_menu()
        if game is None:
            break
        game.run()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
