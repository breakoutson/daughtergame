import pygame
import os

pygame.init()

# Let's inspect the player_v6 front image
img_path = "assets/player_v6/front.png"
if not os.path.exists(img_path):
    print("File not found.")
    exit()

img = pygame.image.load(img_path)
print(f"Original image size: {img.get_width()}x{img.get_height()}")

# Find bounding box
rect = img.get_bounding_rect()
print(f"Bounding rect: {rect}")

