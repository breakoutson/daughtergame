import pygame
import sys
import os
import math
import random

# --- 1. 초기화 및 환경 설정 ---
pygame.init()
WIDTH, HEIGHT = 1000, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🏠 마법의 공주님 집 🏠")
clock = pygame.time.Clock()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE_DIR, "assets")

def load_img(path, scale=None):
    full_path = os.path.join(ASSETS, path)
    if not os.path.exists(full_path):
        surf = pygame.Surface((50, 50), pygame.SRCALPHA)
        surf.fill((255, 0, 255, 128))
        return surf
    img = pygame.image.load(full_path).convert_alpha()
    if scale:
        w, h = img.get_size()
        img = pygame.transform.smoothscale(img, (int(w * scale), int(h * scale)))
    return img

class Player:
    def __init__(self):
        self.pos = [WIDTH // 2, HEIGHT // 2 + 100]
        self.speed = 5
        self.direction = "front"
        self.frame = 0
        self.walking = False
        self.outfit = {"dress": None, "acc": None, "wings": None, "shoes": None}
        
        # 스케일 조정 (0.8 정도로 캐릭터와 배경 비율 맞춤)
        self.scale = 0.8
        # 슬라이싱된 프레임 로드
        self.frames = {
            "front": [load_img(f"player_sheet_frames/front_{i}.png", self.scale) for i in range(4)],
            "back": [load_img(f"player_sheet_frames/back_{i}.png", self.scale) for i in range(4)],
            "left": [load_img(f"player_sheet_frames/left_{i}.png", self.scale) for i in range(4)],
            "right": [load_img(f"player_sheet_frames/right_{i}.png", self.scale) for i in range(4)],
        }

    def update(self, keys):
        dx, dy = 0, 0
        moved = False
        
        # 대각선 이동 시에도 방향 하나가 고정되도록 로직 개선 (좌우 우선)
        if keys[pygame.K_LEFT]:
            dx = -self.speed
            self.direction = "left"
            moved = True
        elif keys[pygame.K_RIGHT]:
            dx = self.speed
            self.direction = "right"
            moved = True
        
        if keys[pygame.K_UP]:
            dy = -self.speed
            if dx == 0: self.direction = "back"
            moved = True
        elif keys[pygame.K_DOWN]:
            dy = self.speed
            if dx == 0: self.direction = "front"
            moved = True

        if moved:
            self.pos[0] += dx
            self.pos[1] += dy
            self.frame = (self.frame + 0.15) % 4
            self.walking = True
        else:
            self.frame = 0
            self.walking = False

        # 화면 경계 제한
        self.pos[0] = max(50, min(WIDTH-50, self.pos[0]))
        self.pos[1] = max(150, min(HEIGHT-50, self.pos[1]))

    def draw(self, surf, center_pos=None):
        draw_pos = center_pos if center_pos else self.pos
        sprite = self.frames[self.direction][int(self.frame)]
        rect = sprite.get_rect(center=draw_pos)
        
        # 걷기 반동 효과
        bounce = math.sin(self.frame * math.pi) * 3 if self.walking else 0
        
        # 1. 날개 (캐릭터 뒤)
        if self.outfit["wings"]:
            w = self.outfit["wings"]
            surf.blit(w, w.get_rect(center=(draw_pos[0], draw_pos[1] - 5)))
        
        # 2. 캐릭터 본체
        surf.blit(sprite, rect)
        
        # 3. 옷 & 액세서리 (좌표 정밀 보정)
        if self.outfit["dress"]: 
            d = self.outfit["dress"]
            surf.blit(d, d.get_rect(center=(draw_pos[0], draw_pos[1] + 25 + bounce)))
        if self.outfit["acc"]: 
            a = self.outfit["acc"]
            surf.blit(a, a.get_rect(center=(draw_pos[0], draw_pos[1] - 65 + bounce)))
        if self.outfit["shoes"]: 
            s = self.outfit["shoes"]
            surf.blit(s, s.get_rect(center=(draw_pos[0], draw_pos[1] + 115)))

class Dog:
    def __init__(self):
        self.scale = 0.5
        self.frames = {
            "front": [load_img(f"dog_sheet_frames/front_{i}.png", self.scale) for i in range(4)],
            "back": [load_img(f"dog_sheet_frames/back_{i}.png", self.scale) for i in range(4)],
            "left": [load_img(f"dog_sheet_frames/left_{i}.png", self.scale) for i in range(4)],
            "right": [load_img(f"dog_sheet_frames/right_{i}.png", self.scale) for i in range(4)],
        }
        self.pos = [random.randint(200, 800), random.randint(350, 600)]
        self.direction = "front"
        self.frame = 0
        self.state = "idle" # idle, walk, sleep
        self.timer = 0
        self.target = list(self.pos)

    def update(self):
        self.timer += 1
        if self.timer % 180 == 0:
            self.state = random.choice(["idle", "idle", "walk", "sleep"])
            if self.state == "walk":
                self.target = [random.randint(200, 800), random.randint(350, 600)]
        
        if self.state == "walk":
            dx = self.target[0] - self.pos[0]
            dy = self.target[1] - self.pos[1]
            if abs(dx) > 5 or abs(dy) > 5:
                if abs(dx) > abs(dy): self.direction = "right" if dx > 0 else "left"
                else: self.direction = "front" if dy > 0 else "back"

                self.pos[0] += dx / 60
                self.pos[1] += dy / 60
                self.frame = (self.frame + 0.1) % 4
            else:
                self.state = "idle"
                self.frame = 0
        elif self.state == "sleep":
            self.direction = "back"
            self.frame = 0
        else:
            self.frame = 0

    def draw(self, surf):
        sprite = self.frames[self.direction][int(self.frame)]
        surf.blit(sprite, sprite.get_rect(center=self.pos))

class GameEngine:
    def __init__(self):
        self.player = Player()
        self.dog = Dog()
        self.current_room = "living" # living, wardrobe, bedroom, kitchen, bathroom
        self.bg = {
            "living": load_img("rooms/living.png"),
            "wardrobe": load_img("rooms/wardrobe.png"),
            "bedroom": load_img("rooms/bedroom.png"),
            "kitchen": load_img("rooms/kitchen.png"),
            "bathroom": load_img("rooms/bathroom.png")
        }
        
        # 옷 아이템
        sc = 0.35
        self.items = {
            "pink": load_img("pink_dress.png", sc),
            "yellow": load_img("yellow_dress.png", sc),
            "crown": load_img("crown.png", 0.18),
            "wings": load_img("wings.png", 0.6)
        }
        self.font = pygame.font.SysFont("arial", 22, bold=True)
        self.close_btn_rect = pygame.Rect(WIDTH - 150, 30, 120, 50)

    def draw_close_button(self):
        pygame.draw.rect(screen, (255, 100, 100), self.close_btn_rect, border_radius=10)
        label = self.font.render("<- EXIT", True, (255, 255, 255))
        screen.blit(label, (WIDTH - 130, 42))

    def run(self):
        while True:
            screen.fill((0, 0, 0))
            keys = pygame.key.get_pressed()
            mx, my = pygame.mouse.get_pos()
            mouse_clicked = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_clicked = True

            # 룸에 따른 로직 분기
            if self.current_room == "living":
                # 거실: 캐릭터 이동 가능
                self.player.update(keys)
                self.dog.update()
                
                # 배경 그리기
                bg_surf = pygame.transform.scale(self.bg["living"], (WIDTH, HEIGHT))
                screen.blit(bg_surf, (0, 0))
                
                # 방 이동 가이드
                screen.blit(self.font.render("Dress Room ->", True, (0, 0, 0)), (850, 400))
                screen.blit(self.font.render("<- Kitchen", True, (0, 0, 0)), (20, 400))
                screen.blit(self.font.render("Bedroom ^", True, (0, 0, 0)), (450, 150))
                screen.blit(self.font.render("Bathroom (L)", True, (0,0,0)), (50, 550))

                # 이동 감지
                px, py = self.player.pos
                if px > 950: self.current_room = "wardrobe"
                elif px < 50: self.current_room = "kitchen"
                elif py < 200: self.current_room = "bedroom"
                elif px < 100 and py > 500: self.current_room = "bathroom"

                self.player.draw(screen)
                self.dog.draw(screen)

            else:
                # 다른 방: 캐릭터는 중앙에 고정 (정적인 뷰)
                bg_surf = pygame.transform.scale(self.bg[self.current_room], (WIDTH, HEIGHT))
                screen.blit(bg_surf, (0, 0))
                
                # 캐릭터 고정 표시 (거울 앞에 있는 느낌)
                self.player.direction = "front"
                self.player.walking = False
                self.player.draw(screen, center_pos=(WIDTH//2, HEIGHT//2 + 50))
                
                # 나가기 버튼
                self.draw_close_button()
                if mouse_clicked and self.close_btn_rect.collidepoint(mx, my):
                    self.current_room = "living"
                    self.player.pos = [WIDTH // 2, HEIGHT // 2 + 100]

                # 옷방 코디 기능
                if self.current_room == "wardrobe":
                    menu = pygame.Surface((WIDTH, 140), pygame.SRCALPHA)
                    menu.fill((255, 255, 255, 180))
                    screen.blit(menu, (0, 610))
                    
                    # 아이콘 그리기 및 클릭 감지
                    icons = [
                        (self.items["pink"], (150, 630), "dress"),
                        (self.items["yellow"], (350, 630), "dress"),
                        (self.items["crown"], (580, 640), "acc"),
                        (self.items["wings"], (840, 630), "wings")
                    ]
                    
                    for img, pos, cat in icons:
                        i_rect = pygame.transform.scale(img, (80, 80)).get_rect(topleft=pos)
                        screen.blit(pygame.transform.scale(img, (80, 80)), pos)
                        if mouse_clicked and i_rect.collidepoint(mx, my):
                            if cat == "dress": self.player.outfit["dress"] = img
                            elif cat == "acc": self.player.outfit["acc"] = img
                            elif cat == "wings": self.player.outfit["wings"] = img

            # 공통 라벨
            label = self.font.render(f"📍 Location: {self.current_room.upper()}", True, (50, 50, 50))
            screen.blit(label, (20, 20))

            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    GameEngine().run()
