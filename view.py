import os
import math
import pygame

# Mixer: se fallisce (driver/audio) non deve crashare
try:
    pygame.mixer.init()
except Exception as e:
    print("[Audio] mixer init failed:", e)


# =====================
# SCREEN
# =====================
class Screen:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.screen = None

    def initScreen(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("BETA GAME")


# =====================
# RENDER OBJECT
# =====================
class RenderObject:
    def __init__(self, zLayer=0, display=True):
        self.zLayer = zLayer
        self.display = display
        self.children = []

    def addChildren(self, children_list):
        self.children.extend(children_list)

    def render(self, surface):
        for child in self.children:
            child.render(surface)

    def checkClick(self, pos):
        results = []
        for child in self.children:
            results.extend(child.checkClick(pos))
        return results


# =====================
# TEXT
# =====================
class Text(RenderObject):
    def __init__(self, position, content, color=(255, 255, 255), max_width=None):
        super().__init__()
        self.position = position
        self.content = content
        self.color = color
        self.max_width = max_width  # Maximum width in pixels for text wrapping
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 26, bold=True)

    def _wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width, returning list of lines"""
        if not max_width:
            return [text]
        
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            # Test if adding this word would exceed max_width
            test_line = ' '.join(current_line + [word])
            test_surface = font.render(test_line, True, self.color)
            
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                # Current line is full, start a new line
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Word itself is too long, add it anyway (or could break it)
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]

    def render(self, surface):
        if self.max_width:
            # Render with word wrapping
            lines = self._wrap_text(self.content, self.font, self.max_width)
            y_offset = 0
            for line in lines:
                if line:  # Skip empty lines
                    text_surface = self.font.render(line, True, self.color)
                    surface.blit(text_surface, (self.position[0], self.position[1] + y_offset))
                    y_offset += text_surface.get_height() + 2  # Small spacing between lines
        else:
            # Render without wrapping (original behavior)
            text_surface = self.font.render(self.content, True, self.color)
            surface.blit(text_surface, self.position)

    def checkClick(self, pos):
        return []


# =====================
# IMAGE
# =====================
class Image(RenderObject):
    def __init__(self, position, imageLink):
        super().__init__()
        self.position = position
        self.image = pygame.image.load(imageLink).convert_alpha()

    def render(self, surface):
        surface.blit(self.image, self.position)

    def checkClick(self, pos):
        return []


# =====================
# BUTTON (ICONA + HOVER + CLICK + GLOW ANIMATO)
# =====================
class Button(RenderObject):
    def __init__(
        self,
        position,
        size,
        text="Button",
        icon_path=None,
        icon_size=28,
        radius=14,
        hover_sound_path="assets/sounds/hover.wav",
        click_sound_path="assets/sounds/click.wav",
    ):
        super().__init__()
        self.position = position
        self.size = size
        self.rect = pygame.Rect(position[0], position[1], size[0], size[1])

        pygame.font.init()
        self.text = text
        self.font = pygame.font.SysFont("Arial", 24, bold=True)

        self.radius = radius

        # ---- Icon
        self.icon = None
        self.icon_size = icon_size
        if icon_path:
            try:
                img = pygame.image.load(icon_path).convert_alpha()
                self.icon = pygame.transform.smoothscale(img, (icon_size, icon_size))
            except Exception as e:
                print(f"[Button] Icon load failed ({icon_path}): {e}")

        # ---- Sounds
        self.hover_sound = None
        self.click_sound = None

        try:
            self.hover_sound = pygame.mixer.Sound(hover_sound_path)
        except Exception as e:
            print(f"[Button] Hover sound load failed: {e}")

        try:
            self.click_sound = pygame.mixer.Sound(click_sound_path)
        except Exception as e:
            print(f"[Button] Click sound load failed: {e}")

        self._hovered_last_frame = False

        # ---- Animated glow
        self.glow_speed = 0.008

    def _is_hovered(self):
        mx, my = pygame.mouse.get_pos()
        return self.rect.collidepoint((mx, my))

    def render(self, surface):
        hovered = self._is_hovered()

        # 🔊 hover sound (only on entry)
        if hovered and not self._hovered_last_frame:
            if self.hover_sound:
                self.hover_sound.play()

        self._hovered_last_frame = hovered

        # ✨ animated glow
        if hovered:
            t = pygame.time.get_ticks()
            pulse01 = (math.sin(t * self.glow_speed) + 1.0) / 2.0

            glow_intensity = int(110 + pulse01 * 90)
            glow_color = (255, glow_intensity, glow_intensity)

            for i in range(3):
                expand = 6 + i * 5 + int(pulse01 * 4)
                glow_rect = self.rect.inflate(expand, expand)
                pygame.draw.rect(
                    surface,
                    glow_color,
                    glow_rect,
                    width=2,
                    border_radius=self.radius,
                )

        # ---- Button
        bg = (200, 60, 60) if not hovered else (235, 90, 90)
        border = (255, 255, 255)
        shadow = (0, 0, 0)

        shadow_rect = self.rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(surface, shadow, shadow_rect, border_radius=self.radius)

        pygame.draw.rect(surface, bg, self.rect, border_radius=self.radius)
        pygame.draw.rect(surface, border, self.rect, width=2, border_radius=self.radius)

        # ---- Text + icon
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_w, text_h = text_surf.get_size()

        gap = 10
        icon_w = self.icon_size if self.icon else 0
        content_w = icon_w + (gap if self.icon else 0) + text_w

        start_x = self.rect.x + (self.rect.w - content_w) // 2
        center_y = self.rect.y + self.rect.h // 2

        if self.icon:
            icon_y = center_y - self.icon_size // 2
            surface.blit(self.icon, (start_x, icon_y))
            start_x += self.icon_size + gap

        text_y = center_y - text_h // 2
        surface.blit(text_surf, (start_x, text_y))

    def checkClick(self, pos):
        if self.rect.collidepoint(pos):
            if self.click_sound:
                self.click_sound.play()
            return [f"Button '{self.text}' clicked"]
        return []


# =====================
# GAME VIEW (MENU + LOAD BACKGROUND)
# =====================
class GameView:
    def __init__(self):
        self.screen = Screen()
        self.root = RenderObject(zLayer=0)
        self.current_scene = "MENU"
        self.menu_bg = None

    def initScreen(self):
        self.screen.initScreen()
        self._load_menu_background()

    def _load_menu_background(self):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            bg_path = os.path.join(base_dir, "assets", "backgrounds", "menu_bg.png")

            img = pygame.image.load(bg_path).convert()
            self.menu_bg = pygame.transform.scale(
                img, (self.screen.width, self.screen.height)
            )
        except Exception as e:
            print("[GameView] Menu background load failed:", e)
            self.menu_bg = None

    def setScene(self, scene_name):
        self.current_scene = scene_name
        self.root.children = []

    def linksToSubsystemObjects(self, objects):
        self.root.children = []
        self.root.addChildren(objects)

    def render(self):
        if self.current_scene in ("MENU", "LOAD") and self.menu_bg:
            self.screen.screen.blit(self.menu_bg, (0, 0))

            overlay = pygame.Surface((self.screen.width, self.screen.height))
            overlay.set_alpha(80)
            overlay.fill((0, 0, 0))
            self.screen.screen.blit(overlay, (0, 0))
        elif self.current_scene == "ENDINGS_MENU":
            # Dark semi-transparent background for endings menu
            self.screen.screen.fill((20, 20, 30))
            # Draw central panel
            panel_rect = pygame.Rect(40, 20, 720, 560)
            pygame.draw.rect(self.screen.screen, (40, 40, 50), panel_rect)
            pygame.draw.rect(self.screen.screen, (100, 100, 150), panel_rect, width=3)
        else:
            self.screen.screen.fill((30, 30, 30))

        self.root.render(self.screen.screen)
        pygame.display.flip()

    def checkClick(self, pos):
        return self.root.checkClick(pos)
