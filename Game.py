import pygame
import random

# Changeable variables
screenLen = 1500
screenHight = 900
speed = 2.5
goonCount = 10
EnemyProxy = 200
playerHealth = 100
goonHealth = 25
attackRadius = 75
attackPower = 5
goonAttackRadius = 50
goonAttackPower = 5
goonAttackBuffer = 500  # in milliseconds
sprintSpeed = 5
sprintDuration = 4000  # in milliseconds
sprintRecoveryRate = 750  # in milliseconds

# Brute-specific variables
bruteCount = 5
bruteHealth = 150
bruteAttackRadius = 75
bruteAttackPower = 10
bruteAttackBuffer = 1000  # in milliseconds

# Upgrade-specific customizable variables
attackPowerUpgrade = 10  # Increment for attack power
attackRadiusUpgrade = 100  # Increase for attack radius
maxHealthUpgrade = 20  # Increment for max health
restoreHealthUpgrade = playerHealth  # Full health restoration value

# Boss-specific variables
bossHealth = 500
bossAttackPower = 20
bossAttackBuffer = 800  # in milliseconds
bossAttackRadius = 100

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = screenLen
SCREEN_HEIGHT = screenHight

# Load assets and scale them proportionally
background_image = pygame.image.load('medieval_background.png')
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

knight_image = pygame.image.load('knight.png')
knight_width, knight_height = knight_image.get_size()
knight_image = pygame.transform.scale(knight_image, (knight_width // 4, knight_height // 4))

# Get the updated dimensions of the knight
knight_width, knight_height = knight_image.get_size()

# Knight's initial position
knight_x = SCREEN_WIDTH // 2
knight_y = SCREEN_HEIGHT // 2

# Knight's speed
KNIGHT_SPEED = speed

# Knight's health
knight_health = playerHealth

# Load goon image and scale it
goon_image = pygame.image.load('goon.png')
new_goon_height = knight_height
aspect_ratio = goon_image.get_width() / goon_image.get_height()
new_goon_width = int(new_goon_height * aspect_ratio)
goon_image = pygame.transform.scale(goon_image, (new_goon_width, new_goon_height))
goon_width, goon_height = goon_image.get_size()

# Load brute image and scale it
brute_image = pygame.image.load('brute.png')
new_brute_height = knight_height  # Same height as knight
aspect_ratio = brute_image.get_width() / brute_image.get_height()
new_brute_width = int(new_brute_height * aspect_ratio)
brute_image = pygame.transform.scale(brute_image, (new_brute_width, new_brute_height))
brute_width, brute_height = brute_image.get_size()

# Load boss image and scale it
boss_image = pygame.image.load('boss.png')
new_boss_height = knight_height * 1.5  # Boss is larger than the knight
aspect_ratio = boss_image.get_width() / boss_image.get_height()
new_boss_width = int(new_boss_height * aspect_ratio)
boss_image = pygame.transform.scale(boss_image, (new_boss_width, new_boss_height))
boss_width, boss_height = boss_image.get_size()

# Function to draw health bar
def draw_health_bar(screen, x, y, health, max_health, width=50, height=5):
    health_ratio = health / max_health
    pygame.draw.rect(screen, (255, 0, 0), (x, y, width, height))  # Red background
    pygame.draw.rect(screen, (0, 255, 0), (x, y, width * health_ratio, height))  # Green foreground

# Function to draw sprint bar
def draw_sprint_bar(screen, x, y, sprint_time, max_sprint_time, width=200, height=20):
    sprint_ratio = sprint_time / max_sprint_time
    pygame.draw.rect(screen, (255, 255, 255), (x, y, width, height))  # White background
    pygame.draw.rect(screen, (0, 0, 255), (x, y, width * sprint_ratio, height))  # Blue foreground

# Function to check if all goons are defeated
def all_goons_defeated(goons):
    return all(goon[2] <= 0 for goon in goons)

# Create screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Medieval Game - Levels with Upgrades")

# Clock to control the frame rate
clock = pygame.time.Clock()

# Font for health display
font = pygame.font.Font(None, 36)

# Game Variables
level = 1  # Start at level 1
goons = []  # List for goons
brutes = []  # List for brutes
boss = None  # Initialize boss for Level 3

def initialize_level(level):
    global goons, brutes, boss
    goons = []
    brutes = []
    boss = None  # Initialize boss for Level 3

    if level == 1:  # Level 1: Only goons
        for _ in range(goonCount):
            goon_x = random.randint(0, SCREEN_WIDTH - goon_width)
            goon_y = random.randint(0, SCREEN_HEIGHT - goon_height)
            goons.append([goon_x, goon_y, goonHealth, pygame.time.get_ticks()])
    elif level == 2:  # Level 2: Goons and brutes
        for _ in range(goonCount):
            goon_x = random.randint(0, SCREEN_WIDTH - goon_width)
            goon_y = random.randint(0, SCREEN_HEIGHT - goon_height)
            goons.append([goon_x, goon_y, goonHealth, pygame.time.get_ticks()])
        for _ in range(bruteCount):
            brute_x = random.randint(0, SCREEN_WIDTH - brute_width)
            brute_y = random.randint(0, SCREEN_HEIGHT - brute_height)
            brutes.append([brute_x, brute_y, bruteHealth, pygame.time.get_ticks()])
    elif level == 3:  # Level 3: Spawn the boss
        boss_x = SCREEN_WIDTH // 2 - new_boss_width // 2
        boss_y = SCREEN_HEIGHT // 4  # Boss starts near the top of the screen
        boss = [boss_x, boss_y, bossHealth, pygame.time.get_ticks()]  # Position, health, and last attack time

def upgrade_screen(choices):
    global knight_health, playerHealth, attackPower, attackRadius

    # Create a basic upgrade screen
    upgrade_running = True
    screen.fill((0, 0, 0))  # Black background
    font = pygame.font.Font(None, 36)
    title = font.render(f"Choose {choices} upgrades", True, (255, 255, 255))
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

    # Available upgrades
    upgrades = [
        ("Increase Attack Power", "A"),
        ("Increase Attack Radius", "R"),
        ("Max Health Upgrade", "H"),
        ("Restore Health", "F")
    ]

    upgrade_buttons = []
    for i, (upgrade_text, key) in enumerate(upgrades):
        text = font.render(f"{key}: {upgrade_text}", True, (255, 255, 255))
        button_x = SCREEN_WIDTH // 2 - text.get_width() // 2
        button_y = 200 + i * 50
        screen.blit(text, (button_x, button_y))
        upgrade_buttons.append((upgrade_text, key, button_x, button_y, text))

    pygame.display.flip()

    # Handle upgrade selection
    selected_upgrades = []
    while upgrade_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                for upgrade_text, key, _, _, _ in upgrade_buttons:
                    if event.unicode.upper() == key and upgrade_text not in selected_upgrades:
                        selected_upgrades.append(upgrade_text)

                        # Apply the upgrade
                        if upgrade_text == "Increase Attack Power":
                            attackPower += attackPowerUpgrade
                        elif upgrade_text == "Increase Attack Radius":
                            attackRadius += attackRadiusUpgrade
                        elif upgrade_text == "Max Health Upgrade":
                            playerHealth += maxHealthUpgrade
                            knight_health = playerHealth
                        elif upgrade_text == "Restore Health":
                            knight_health = restoreHealthUpgrade

                        # Break if enough upgrades have been selected
                        if len(selected_upgrades) == choices:
                            upgrade_running = False

        # Redraw the screen to show selected upgrades
        screen.fill((0, 0, 0))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        for i, (upgrade_text, key, button_x, button_y, text) in enumerate(upgrade_buttons):
            if upgrade_text in selected_upgrades:
                pygame.draw.rect(screen, (0, 255, 0), (button_x - 5, button_y - 5, text.get_width() + 10, text.get_height() + 10))
            screen.blit(text, (button_x, button_y))
        pygame.display.flip()

def reset_game():
    global knight_health, level, goons, brutes, boss, sprint_time_left
    # Reset all game variables
    knight_health = playerHealth
    level = 1
    sprint_time_left = sprintDuration
    initialize_level(level)
    main_game_loop()  # Restart the main game loop

def show_reset_button():
    # Display a reset button after death
    screen.fill((0, 0, 0))  # Black background
    font = pygame.font.Font(None, 60)
    title = font.render("Game Over!", True, (255, 0, 0))
    reset_button_text = font.render("Reset Game", True, (255, 255, 255))

    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 300))
    button_x = SCREEN_WIDTH // 2 - reset_button_text.get_width() // 2
    button_y = 400
    screen.blit(reset_button_text, (button_x, button_y))

    pygame.display.flip()

    # Wait for the player to click the reset button
    reset_clicked = False
    while not reset_clicked:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                # Check if the click is within the button area
                if button_x <= mouse_x <= button_x + reset_button_text.get_width() and \
                   button_y <= mouse_y <= button_y + reset_button_text.get_height():
                    reset_clicked = True

    reset_game()

def main_game_loop():
    global knight_x, knight_y, knight_health, level, sprint_time_left, goons, brutes, boss 
    running = True
    sprinting = False
    sprint_time_left = sprintDuration
    last_sprint_update = pygame.time.get_ticks()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and knight_health > 0:
                # Knight attacks goons within attack radius
                for goon in goons:
                    goon_x, goon_y, goon_health, _ = goon
                    distance_to_knight = ((knight_x - goon_x) ** 2 + (knight_y - goon_y) ** 2) ** 0.5
                    if distance_to_knight <= attackRadius:
                        goon[2] -= attackPower  # Reduce goon health by attack power

                # Knight attacks brutes within attack radius
                for brute in brutes:
                    brute_x, brute_y, brute_health, _ = brute
                    distance_to_knight = ((knight_x - brute_x) ** 2 + (knight_y - brute_y) ** 2) ** 0.5
                    if distance_to_knight <= attackRadius:
                        brute[2] -= attackPower  # Reduce brute health by attack power

                # Knight attacks the boss within attack radius
                if level == 3 and boss and boss[2] > 0:
                    boss_x, boss_y, boss_health, _ = boss
                    distance_to_knight = ((knight_x - boss_x) ** 2 + (knight_y - boss_y) ** 2) ** 0.5
                    if distance_to_knight <= attackRadius:
                        boss[2] -= attackPower  # Reduce boss health by attack power

        if knight_health <= 0:
            running = False
            show_reset_button()
        # Get keys pressed
        keys = pygame.key.get_pressed()

        if knight_health > 0:  # Only allow movement if knight is alive
            sprinting = keys[pygame.K_LSHIFT] and sprint_time_left > 0

            # Move knight with boundary checks
            current_speed = sprintSpeed if sprinting else KNIGHT_SPEED
            if keys[pygame.K_w] and knight_y > 0: knight_y -= current_speed
            if keys[pygame.K_s] and knight_y < SCREEN_HEIGHT - knight_height: knight_y += current_speed
            if keys[pygame.K_a] and knight_x > 0: knight_x -= current_speed
            if keys[pygame.K_d] and knight_x < SCREEN_WIDTH - knight_width: knight_x += current_speed

            # Update sprint time
            current_time = pygame.time.get_ticks()
            if sprinting:
                sprint_time_left -= current_time - last_sprint_update
                sprint_time_left = max(0, sprint_time_left)
            else:
                sprint_time_left += sprintRecoveryRate * (current_time - last_sprint_update) / 1000
                sprint_time_left = min(sprintDuration, sprint_time_left)
            last_sprint_update = current_time

        # Move and attack logic for goons
        for goon in goons:
            goon_x, goon_y, goon_health, last_attack_time = goon
            if goon_health > 0:
                distance_to_knight = ((knight_x - goon_x) ** 2 + (knight_y - goon_y) ** 2) ** 0.5

                # Move the goon toward the knight
                if distance_to_knight <= EnemyProxy:
                    if goon_x < knight_x: goon[0] += 1
                    elif goon_x > knight_x: goon[0] -= 1
                    if goon_y < knight_y: goon[1] += 1
                    elif goon_y > knight_y: goon[1] -= 1

                # Goons attack the knight
                if distance_to_knight <= goonAttackRadius and pygame.time.get_ticks() - last_attack_time >= goonAttackBuffer:
                    knight_health -= goonAttackPower
                    goon[3] = pygame.time.get_ticks()

        # Move and attack logic for brutes
        for brute in brutes:
            brute_x, brute_y, brute_health, last_attack_time = brute
            if brute_health > 0:
                distance_to_knight = ((knight_x - brute_x) ** 2 + (knight_y - brute_y) ** 2) ** 0.5

                # Move the brute toward the knight
                if distance_to_knight <= EnemyProxy:
                    if brute_x < knight_x: brute[0] += 1
                    elif brute_x > knight_x: brute[0] -= 1
                    if brute_y < knight_y: brute[1] += 1
                    elif brute_y > knight_y: brute[1] -= 1

                # Brutes attack the knight
                if distance_to_knight <= bruteAttackRadius and pygame.time.get_ticks() - last_attack_time >= bruteAttackBuffer:
                    knight_health -= bruteAttackPower
                    brute[3] = pygame.time.get_ticks()

        # Handle boss logic in Level 3
        if level == 3 and boss and boss[2] > 0:
            boss_x, boss_y, boss_health, last_attack_time = boss
            distance_to_knight = ((knight_x - boss_x) ** 2 + (knight_y - boss_y) ** 2) ** 0.5

            # Boss moves toward the knight
            if boss_x < knight_x: boss[0] += 1
            elif boss_x > knight_x: boss[0] -= 1
            if boss_y < knight_y: boss[1] += 1
            elif boss_y > knight_y: boss[1] -= 1

            # Boss attacks the knight
            if distance_to_knight <= bossAttackRadius and pygame.time.get_ticks() - last_attack_time >= bossAttackBuffer:
                knight_health -= bossAttackPower
                boss[3] = pygame.time.get_ticks()

        # Check level transitions
        if level == 1 and all_goons_defeated(goons):
            upgrade_screen(choices=1)
            level = 2
            initialize_level(level)
        elif level == 2 and all_goons_defeated(goons) and all(brute[2] <= 0 for brute in brutes):
            upgrade_screen(choices=2)
            level = 3
            initialize_level(level)

        # Draw everything
        screen.blit(background_image, (0, 0))
        screen.blit(knight_image, (knight_x, knight_y))

        for goon_x, goon_y, goon_health, _ in goons:
            if goon_health > 0:
                screen.blit(goon_image, (goon_x, goon_y))
                draw_health_bar(screen, goon_x, goon_y - 10, goon_health, goonHealth)

        for brute_x, brute_y, brute_health, _ in brutes:
            if brute_health > 0:
                screen.blit(brute_image, (brute_x, brute_y))
                draw_health_bar(screen, brute_x, brute_y - 10, brute_health, bruteHealth)

        if level == 3 and boss and boss[2] > 0:
            boss_x, boss_y, boss_health, _ = boss
            screen.blit(boss_image, (boss_x, boss_y))
            draw_health_bar(screen, boss_x, boss_y - 10, boss_health, bossHealth)

        draw_health_bar(screen, 10, 10, knight_health, playerHealth, width=200, height=20)
        draw_sprint_bar(screen, 10, 40, sprint_time_left, sprintDuration, width=200, height=20)

        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

    # Quit pygame
    pygame.quit()

# Start the game
initialize_level(level)
main_game_loop()
