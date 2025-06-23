import pygame
import random
import sys
import math
import json

pygame.init()
pygame.mixer.init()

# Screen settings
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Space Invaders")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 100, 255)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)

# Game state
class GameState:
    def __init__(self):
        self.score = 0
        self.wave = 1
        self.lives = 3
        self.level = 1
        self.xp = 0
        self.coins = 0
        self.combo = 0
        self.max_combo = 0
        self.achievements = []
        self.weapon_type = 'laser'
        self.weapon_level = 1
        
game = GameState()

# Player
player_x = WIDTH // 2
player_y = HEIGHT - 80
player_speed = 6
invincible_timer = 0

# Bullets and weapons
bullets = []
missiles = []
laser_beam_active = False
laser_beam_timer = 0

# Enemies
aliens = []
mini_bosses = []
boss_active = False
boss_data = {'x': WIDTH//2, 'y': 100, 'health': 200, 'max_health': 200, 'pattern': 0}

# Environmental
obstacles = []
wormholes = []
particles = []
screen_shake = 0

# Power-ups and effects
powerups = []
bullet_time = False
bullet_time_timer = 0
magnetic_field = False
magnetic_timer = 0

# Timers
spawn_timers = {'alien': 0, 'powerup': 0, 'obstacle': 0, 'particle': 0}

# Audio (placeholder - would need actual sound files)
sounds = {'shoot': None, 'explosion': None, 'powerup': None, 'boss': None}

# Stars background
stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 4)] for _ in range(150)]

# Fonts
font_small = pygame.font.Font(None, 24)
font_medium = pygame.font.Font(None, 36)
font_large = pygame.font.Font(None, 48)
font_huge = pygame.font.Font(None, 72)

def create_particle(x, y, color, velocity):
    particles.append({'x': x, 'y': y, 'vx': velocity[0], 'vy': velocity[1], 'color': color, 'life': 30})

def screen_shake_effect(intensity):
    global screen_shake
    screen_shake = max(screen_shake, intensity)

def draw_enhanced_spaceship(x, y):
    # Enhanced ship design based on weapon type
    if game.weapon_type == 'laser':
        pygame.draw.polygon(screen, CYAN, [(x+20, y), (x+5, y+25), (x+35, y+25)])
        pygame.draw.polygon(screen, BLUE, [(x, y+20), (x+15, y+15), (x+15, y+25)])
        pygame.draw.polygon(screen, BLUE, [(x+25, y+15), (x+40, y+20), (x+25, y+25)])
    elif game.weapon_type == 'plasma':
        pygame.draw.polygon(screen, PURPLE, [(x+20, y), (x+5, y+25), (x+35, y+25)])
        pygame.draw.circle(screen, PINK, (x+20, y+12), 8)
    elif game.weapon_type == 'missile':
        pygame.draw.polygon(screen, ORANGE, [(x+20, y), (x+5, y+25), (x+35, y+25)])
        pygame.draw.rect(screen, RED, (x+15, y+5, 10, 15))
    
    # Invincibility effect
    if invincible_timer > 0 and invincible_timer % 10 < 5:
        pygame.draw.circle(screen, WHITE, (x+20, y+12), 25, 2)

def draw_alien(x, y, alien_type):
    if alien_type == 'basic':
        pygame.draw.ellipse(screen, GREEN, (x+5, y+10, 20, 10))
        pygame.draw.ellipse(screen, RED, (x+10, y, 10, 15))
        pygame.draw.circle(screen, YELLOW, (x+12, y+5), 2)
        pygame.draw.circle(screen, YELLOW, (x+18, y+5), 2)
    elif alien_type == 'fast':
        pygame.draw.polygon(screen, CYAN, [(x+15, y), (x+5, y+20), (x+25, y+20)])
    elif alien_type == 'armored':
        pygame.draw.rect(screen, (100, 100, 100), (x+5, y+5, 20, 15))
        pygame.draw.circle(screen, RED, (x+15, y+12), 3)
    elif alien_type == 'shooter':
        pygame.draw.ellipse(screen, PURPLE, (x+5, y+5, 20, 15))
        pygame.draw.rect(screen, ORANGE, (x+12, y+20, 6, 5))

def spawn_alien():
    alien_types = ['basic', 'fast', 'armored', 'shooter']
    weights = [40, 25, 20, 15]
    alien_type = random.choices(alien_types, weights=weights)[0]
    
    x = random.randint(30, WIDTH - 60)
    y = random.randint(30, 200)
    
    health = {'basic': 1, 'fast': 1, 'armored': 3, 'shooter': 2}[alien_type]
    speed = {'basic': 1, 'fast': 3, 'armored': 0.5, 'shooter': 1.5}[alien_type]
    
    aliens.append({
        'x': x, 'y': y, 'type': alien_type, 'health': health, 'max_health': health,
        'speed': speed, 'shoot_timer': 0, 'direction': random.choice([-1, 1])
    })

def spawn_powerup():
    powerup_types = ['rapid', 'shield', 'damage', 'freeze', 'life', 'weapon', 'bomb', 'magnet', 'time']
    x = random.randint(50, WIDTH - 70)
    y = random.randint(100, 300)
    powerup_type = random.choice(powerup_types)
    powerups.append({'x': x, 'y': y, 'type': powerup_type, 'timer': 600})

def draw_powerup(x, y, ptype):
    colors = {
        'rapid': (YELLOW, RED), 'shield': (CYAN, BLUE), 'damage': (PURPLE, RED),
        'freeze': (WHITE, CYAN), 'life': (GREEN, WHITE), 'weapon': (ORANGE, YELLOW),
        'bomb': (RED, ORANGE), 'magnet': (PINK, PURPLE), 'time': (BLUE, WHITE)
    }
    color1, color2 = colors.get(ptype, (WHITE, BLACK))
    pygame.draw.circle(screen, color1, (x+10, y+10), 10)
    pygame.draw.circle(screen, color2, (x+10, y+10), 6)

def create_obstacle():
    x = random.randint(100, WIDTH - 150)
    y = random.randint(200, 400)
    obstacles.append({'x': x, 'y': y, 'health': 5, 'max_health': 5})

def draw_obstacle(x, y, health, max_health):
    color_intensity = int(255 * (health / max_health))
    color = (color_intensity, color_intensity, color_intensity)
    pygame.draw.rect(screen, color, (x, y, 50, 30))

def update_particles():
    for particle in particles[:]:
        particle['x'] += particle['vx']
        particle['y'] += particle['vy']
        particle['life'] -= 1
        if particle['life'] <= 0:
            particles.remove(particle)

def draw_particles():
    for particle in particles:
        alpha = particle['life'] / 30.0
        size = max(1, int(alpha * 5))
        pygame.draw.circle(screen, particle['color'], (int(particle['x']), int(particle['y'])), size)

def draw_ui():
    # Main UI
    score_text = font_medium.render(f"Score: {game.score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    wave_text = font_medium.render(f"Wave: {game.wave}", True, WHITE)
    screen.blit(wave_text, (10, 50))
    
    lives_text = font_medium.render(f"Lives: {game.lives}", True, WHITE)
    screen.blit(lives_text, (10, 90))
    
    level_text = font_medium.render(f"Level: {game.level}", True, YELLOW)
    screen.blit(level_text, (10, 130))
    
    xp_text = font_small.render(f"XP: {game.xp}/100", True, CYAN)
    screen.blit(xp_text, (10, 170))
    
    coins_text = font_medium.render(f"Coins: {game.coins}", True, YELLOW)
    screen.blit(coins_text, (10, 190))
    
    weapon_text = font_small.render(f"Weapon: {game.weapon_type.upper()} Lv.{game.weapon_level}", True, ORANGE)
    screen.blit(weapon_text, (10, 220))
    
    if game.combo > 1:
        combo_text = font_medium.render(f"COMBO x{game.combo}!", True, YELLOW)
        screen.blit(combo_text, (WIDTH - 200, 10))

def draw_galaxy_background():
    for star in stars:
        star[1] += star[2] * 0.3
        if star[1] > HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, WIDTH)
        
        # Twinkling effect
        brightness = random.randint(100, 255)
        color = (brightness, brightness, brightness)
        pygame.draw.circle(screen, color, (int(star[0]), int(star[1])), star[2])

def handle_shooting():
    if game.weapon_type == 'laser':
        bullets.append({'x': player_x + 20, 'y': player_y, 'type': 'laser', 'damage': game.weapon_level})
        if game.weapon_level >= 2:
            bullets.append({'x': player_x + 10, 'y': player_y, 'type': 'laser', 'damage': game.weapon_level})
            bullets.append({'x': player_x + 30, 'y': player_y, 'type': 'laser', 'damage': game.weapon_level})
    
    elif game.weapon_type == 'plasma':
        bullets.append({'x': player_x + 20, 'y': player_y, 'type': 'plasma', 'damage': game.weapon_level * 2})
    
    elif game.weapon_type == 'missile':
        target = None
        min_dist = float('inf')
        for alien in aliens:
            dist = math.sqrt((alien['x'] - player_x)**2 + (alien['y'] - player_y)**2)
            if dist < min_dist:
                min_dist = dist
                target = alien
        
        missiles.append({
            'x': player_x + 20, 'y': player_y, 'target': target,
            'damage': game.weapon_level * 3, 'speed': 8
        })

def update_game_logic():
    global invincible_timer, screen_shake, bullet_time_timer, magnetic_timer
    
    # Update timers
    if invincible_timer > 0:
        invincible_timer -= 1
    if screen_shake > 0:
        screen_shake -= 1
    if bullet_time_timer > 0:
        bullet_time_timer -= 1
    else:
        global bullet_time
        bullet_time = False
    if magnetic_timer > 0:
        magnetic_timer -= 1
    else:
        global magnetic_field
        magnetic_field = False
    
    # Spawn entities
    spawn_timers['alien'] += 1
    if spawn_timers['alien'] >= (120 if not bullet_time else 240):
        spawn_alien()
        spawn_timers['alien'] = 0
    
    spawn_timers['powerup'] += 1
    if spawn_timers['powerup'] >= 600:
        spawn_powerup()
        spawn_timers['powerup'] = 0
    
    # Move bullets
    speed_multiplier = 0.5 if bullet_time else 1.0
    
    for bullet in bullets[:]:
        bullet['y'] -= 10 * speed_multiplier
        if bullet['y'] < 0:
            bullets.remove(bullet)
    
    # Move missiles with homing
    for missile in missiles[:]:
        if missile['target'] and missile['target'] in aliens:
            target = missile['target']
            dx = target['x'] - missile['x']
            dy = target['y'] - missile['y']
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                missile['x'] += (dx/dist) * missile['speed'] * speed_multiplier
                missile['y'] += (dy/dist) * missile['speed'] * speed_multiplier
        else:
            missile['y'] -= missile['speed'] * speed_multiplier
        
        if missile['y'] < 0 or missile['y'] > HEIGHT:
            missiles.remove(missile)
    
    # Move aliens
    for alien in aliens[:]:
        if alien['type'] == 'fast':
            alien['y'] += alien['speed'] * 2 * speed_multiplier
            alien['x'] += alien['direction'] * alien['speed'] * speed_multiplier
        elif alien['type'] == 'basic':
            alien['y'] += alien['speed'] * speed_multiplier
            alien['x'] += math.sin(alien['y'] * 0.01) * 2
        elif alien['type'] == 'armored':
            alien['y'] += alien['speed'] * speed_multiplier
        elif alien['type'] == 'shooter':
            alien['y'] += alien['speed'] * speed_multiplier
            alien['shoot_timer'] += 1
            if alien['shoot_timer'] >= 60:
                # Alien shoots at player
                alien['shoot_timer'] = 0
        
        if alien['y'] > HEIGHT:
            aliens.remove(alien)
    
    # Magnetic field effect
    if magnetic_field:
        for powerup in powerups:
            dx = player_x - powerup['x']
            dy = player_y - powerup['y']
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < 150 and dist > 0:
                powerup['x'] += (dx/dist) * 3
                powerup['y'] += (dy/dist) * 3

def check_collisions():
    global game, invincible_timer
    
    # Bullet-alien collisions
    for bullet in bullets[:]:
        for alien in aliens[:]:
            if (bullet['x'] > alien['x'] and bullet['x'] < alien['x'] + 30 and
                bullet['y'] > alien['y'] and bullet['y'] < alien['y'] + 25):
                bullets.remove(bullet)
                alien['health'] -= bullet['damage']
                
                create_particle(alien['x'] + 15, alien['y'] + 12, YELLOW, 
                              [random.randint(-3, 3), random.randint(-3, 3)])
                
                if alien['health'] <= 0:
                    aliens.remove(alien)
                    points = {'basic': 10, 'fast': 15, 'armored': 25, 'shooter': 20}[alien['type']]
                    game.score += points * (game.combo + 1)
                    game.combo += 1
                    game.xp += 5
                    game.coins += 1
                    
                    # Level up system
                    if game.xp >= 100:
                        game.level += 1
                        game.xp = 0
                        game.weapon_level = min(5, game.weapon_level + 1)
                    
                    screen_shake_effect(5)
                    create_particle(alien['x'] + 15, alien['y'] + 12, RED,
                                  [random.randint(-5, 5), random.randint(-5, 5)])
                break
    
    # Missile-alien collisions
    for missile in missiles[:]:
        for alien in aliens[:]:
            if (missile['x'] > alien['x'] and missile['x'] < alien['x'] + 30 and
                missile['y'] > alien['y'] and missile['y'] < alien['y'] + 25):
                missiles.remove(missile)
                alien['health'] -= missile['damage']
                
                if alien['health'] <= 0:
                    aliens.remove(alien)
                    game.score += 30
                    game.combo += 1
                    screen_shake_effect(8)
                break
    
    # Player-powerup collisions
    for powerup in powerups[:]:
        if (player_x < powerup['x'] + 20 and player_x + 40 > powerup['x'] and
            player_y < powerup['y'] + 20 and player_y + 25 > powerup['y']):
            powerups.remove(powerup)
            
            if powerup['type'] == 'weapon':
                weapons = ['laser', 'plasma', 'missile']
                game.weapon_type = random.choice(weapons)
            elif powerup['type'] == 'life':
                game.lives += 1
            elif powerup['type'] == 'time':
                global bullet_time, bullet_time_timer
                bullet_time = True
                bullet_time_timer = 300
            elif powerup['type'] == 'magnet':
                global magnetic_field, magnetic_timer
                magnetic_field = True
                magnetic_timer = 240
    
    # Player-alien collisions
    if invincible_timer <= 0:
        for alien in aliens[:]:
            if (player_x < alien['x'] + 30 and player_x + 40 > alien['x'] and
                player_y < alien['y'] + 25 and player_y + 25 > alien['y']):
                aliens.remove(alien)
                game.lives -= 1
                game.combo = 0
                invincible_timer = 120
                screen_shake_effect(15)
                
                if game.lives <= 0:
                    return False
    
    return True

def draw_game():
    # Apply screen shake
    shake_x = random.randint(-screen_shake, screen_shake) if screen_shake > 0 else 0
    shake_y = random.randint(-screen_shake, screen_shake) if screen_shake > 0 else 0
    
    # Background
    screen.fill(BLACK)
    draw_galaxy_background()
    
    # Bullet time effect
    if bullet_time:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(30)
        overlay.fill(BLUE)
        screen.blit(overlay, (0, 0))
    
    # Game entities
    draw_enhanced_spaceship(player_x + shake_x, player_y + shake_y)
    
    for alien in aliens:
        draw_alien(alien['x'] + shake_x, alien['y'] + shake_y, alien['type'])
    
    for bullet in bullets:
        color = PURPLE if bullet['type'] == 'plasma' else YELLOW
        pygame.draw.circle(screen, color, (int(bullet['x'] + shake_x), int(bullet['y'] + shake_y)), 3)
    
    for missile in missiles:
        pygame.draw.circle(screen, ORANGE, (int(missile['x'] + shake_x), int(missile['y'] + shake_y)), 5)
        # Missile trail
        create_particle(missile['x'], missile['y'], ORANGE, [0, 0])
    
    for powerup in powerups:
        draw_powerup(powerup['x'] + shake_x, powerup['y'] + shake_y, powerup['type'])
    
    draw_particles()
    update_particles()
    
    # Magnetic field visualization
    if magnetic_field:
        pygame.draw.circle(screen, CYAN, (player_x + 20, player_y + 12), 150, 2)
    
    draw_ui()

def main_menu():
    menu_active = True
    selected_option = 0
    options = ["START GAME", "UPGRADE SHOP", "ACHIEVEMENTS", "QUIT"]
    
    while menu_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if selected_option == 0:
                        return "start"
                    elif selected_option == 1:
                        return "shop"
                    elif selected_option == 2:
                        return "achievements"
                    elif selected_option == 3:
                        return "quit"
        
        screen.fill(BLACK)
        draw_galaxy_background()
        
        title = font_huge.render("ULTIMATE SPACE INVADERS", True, CYAN)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))
        
        for i, option in enumerate(options):
            color = YELLOW if i == selected_option else WHITE
            text = font_large.render(option, True, color)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, 300 + i * 60))
        
        pygame.display.flip()
        pygame.time.Clock().tick(60)

def main_game():
    global player_x, player_y, game
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "menu"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    handle_shooting()
                elif event.key == pygame.K_ESCAPE:
                    return "menu"
        
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - 40:
            player_x += player_speed
        if keys[pygame.K_UP] and player_y > HEIGHT // 2:
            player_y -= player_speed
        if keys[pygame.K_DOWN] and player_y < HEIGHT - 30:
            player_y += player_speed
        
        # Game logic
        update_game_logic()
        
        if not check_collisions():
            # Game over
            screen.fill(BLACK)
            game_over_text = font_huge.render("GAME OVER", True, RED)
            screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
            
            final_score = font_large.render(f"Final Score: {game.score}", True, WHITE)
            screen.blit(final_score, (WIDTH//2 - final_score.get_width()//2, HEIGHT//2 + 20))
            
            pygame.display.flip()
            pygame.time.wait(3000)
            return "menu"
        
        draw_game()
        pygame.display.flip()
        clock.tick(60)

def main():
    current_state = "menu"
    
    while current_state != "quit":
        if current_state == "menu":
            current_state = main_menu()
        elif current_state == "start":
            # Reset game state
            global game, player_x, player_y, aliens, bullets, missiles, powerups, particles
            game = GameState()
            player_x = WIDTH // 2
            player_y = HEIGHT - 80
            aliens.clear()
            bullets.clear()
            missiles.clear()
            powerups.clear()
            particles.clear()
            
            current_state = main_game()
        elif current_state == "shop":
            # Placeholder for upgrade shop
            current_state = "menu"
        elif current_state == "achievements":
            # Placeholder for achievements
            current_state = "menu"
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()