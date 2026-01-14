import os
import math
import pygame

# Mixer: se fallisce (driver/audio) non deve crashare
try:
    pygame.mixer.init()
except Exception as e:
    print("[Audio] mixer init failed:", e)

# Volume globale effetti (hover/click). Lo modifica il controller.
SFX_VOLUME = 1.0

# ---- Font Settings
FONT_PATH_TITLE = "assets/fonts/OwreKynge.ttf"
FONT_PATH_BODY  = "assets/fonts/Alkhemikal.ttf" 

FONT_SIZE_TITLE = 70
FONT_SIZE_NORMAL = 32
FONT_SIZE_BUTTON = 26
FONT_SIZE_INFO = 22
FONT_SIZE_SMALL = 20

def get_font(size, is_title=False):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    f_path = FONT_PATH_TITLE if is_title else FONT_PATH_BODY
    
    font_full_path = os.path.join(base_dir, f_path)
    try:
        if os.path.exists(font_full_path):
            return pygame.font.Font(font_full_path, size)
    except Exception:
        pass
    return pygame.font.SysFont("Arial", size, bold=True)


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
        pygame.display.set_caption("The adventures of Lulucia")


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
    def __init__(self, position, content, color=(255, 255, 255), font_size=FONT_SIZE_NORMAL, is_title=False):
        super().__init__()
        self.position = list(position)
        self.content = content
        self.color = color
        pygame.font.init()
        self.font = get_font(font_size, is_title=is_title)

    def render(self, surface):
        text_surface = self.font.render(self.content, True, self.color)
        
        # Centrado automático se X é -1
        draw_x = self.position[0]
        if draw_x == -1:
            draw_x = (surface.get_width() - text_surface.get_width()) // 2
            
        surface.blit(text_surface, (draw_x, self.position[1]))

    def checkClick(self, pos):
        return []


# =====================
# MULTILINE TEXT (WRAP)
# =====================
class MultiLineText(RenderObject):
    def __init__(self, position, content, max_width, color=(255, 255, 255), font_size=FONT_SIZE_NORMAL):
        super().__init__()
        self.position = list(position)
        self.content = content
        self.max_width = max_width
        self.color = color
        pygame.font.init()
        self.font = get_font(font_size)
        self.lines = self._wrap_text()

    def _wrap_text(self):
        if not self.content:
            return [""]
        words = self.content.split(' ')
        lines = []
        current_line = []

        for word in words:
            # Se a palabra ten saltos de liña internos
            sub_words = word.split('\n')
            for i, sw in enumerate(sub_words):
                if i > 0:
                    lines.append(' '.join(current_line))
                    current_line = []
                
                test_line = ' '.join(current_line + [sw])
                w, _ = self.font.size(test_line)
                if w <= self.max_width:
                    current_line.append(sw)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [sw]
        
        lines.append(' '.join(current_line))
        return [l for l in lines if l or l == ""]

    def render(self, surface):
        y = self.position[1]
        for line in self.lines:
            text_surf = self.font.render(line, True, self.color)
            
            draw_x = self.position[0]
            if draw_x == -1:
                draw_x = (surface.get_width() - text_surf.get_width()) // 2
                
            surface.blit(text_surf, (draw_x, y))
            y += self.font.get_linesize() + 4

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
# BUTTON (ICONA + HOVER + CLICK + GLOW ANIMATO) + ACTION_ID
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
        hover_sound_path="assets/sounds/click.wav",
        click_sound_path="assets/sounds/click.wav",
        action_id=None,
        color=(200, 60, 60),
        hover_color=(235, 90, 90)
    ):
        super().__init__()
        self.position = position
        self.size = size
        self.rect = pygame.Rect(position[0], position[1], size[0], size[1])

        pygame.font.init()
        self.text = text
        self.font = get_font(FONT_SIZE_BUTTON)

        self.radius = radius
        self.action_id = action_id  
        self.color = color
        self.hover_color = hover_color

        # ---- Icona (path robusto: relativo al file view.py)
        self.icon = None
        self.icon_size = icon_size
        if icon_path:
            try:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                full_path = icon_path
                if not os.path.isabs(icon_path):
                    full_path = os.path.join(base_dir, icon_path)
                img = pygame.image.load(full_path).convert_alpha()
                self.icon = pygame.transform.smoothscale(img, (icon_size, icon_size))
            except Exception as e:
                print(f"[Button] Icon load failed ({icon_path}): {e}")

        # ---- Suoni
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

        # Prevent hover sound on first frame if mouse is already over the button
        self._hovered_last_frame = self._is_hovered()

        # ---- Glow animato
        self.glow_speed = 0.008  # prova 0.006–0.012

    def _is_hovered(self):
        mx, my = pygame.mouse.get_pos()
        return self.rect.collidepoint((mx, my))

    def render(self, surface):
        if not self.display:
            return
        hovered = self._is_hovered()

        # 🔊 hover sound (solo all’entrata)
        if hovered and not self._hovered_last_frame:
            if self.hover_sound:
                ch = self.hover_sound.play()
                if ch:
                    ch.set_volume(SFX_VOLUME)

        self._hovered_last_frame = hovered

        # ✨ glow animato
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

        # ---- Bottone
        bg = self.color if not hovered else self.hover_color
        border = (255, 255, 255)
        shadow = (0, 0, 0)

        shadow_rect = self.rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(surface, shadow, shadow_rect, border_radius=self.radius)

        pygame.draw.rect(surface, bg, self.rect, border_radius=self.radius)
        pygame.draw.rect(surface, border, self.rect, width=2, border_radius=self.radius)

        # ---- Contenuto (icona + testo centrati)
        gap = 10
        padding = 10
        available_w = self.rect.w - (padding * 2) - (self.icon_size + gap if self.icon else 0)
        
        # Wrap text if needed
        words = self.text.split(' ')
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            w, _ = self.font.size(test_line)
            if w <= available_w:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))
        
        # Calculate total height of text
        line_surfaces = [self.font.render(l, True, (255, 255, 255)) for l in lines]
        total_text_h = sum(s.get_height() for s in line_surfaces) + (len(lines)-1) * 2
        
        icon_w = self.icon_size if self.icon else 0
        # For layout calculation, we use the width of the widest line
        max_line_w = max(s.get_width() for s in line_surfaces) if line_surfaces else 0
        content_w = icon_w + (gap if self.icon and self.text else 0) + max_line_w

        start_x = self.rect.x + (self.rect.w - content_w) // 2
        center_y = self.rect.y + self.rect.h // 2

        if self.icon:
            icon_y = center_y - self.icon_size // 2
            surface.blit(self.icon, (start_x, icon_y))
            start_x += self.icon_size + (gap if self.text else 0)

        if self.text:
            current_y = center_y - total_text_h // 2
            for surf in line_surfaces:
                # Center line relative to the text block if needed, but here we just blit
                surface.blit(surf, (start_x, current_y))
                current_y += surf.get_height() + 2

    def checkClick(self, pos):
        if not self.display:
            return []
        if self.rect.collidepoint(pos):
            if self.click_sound:
                ch = self.click_sound.play()
                if ch:
                    ch.set_volume(SFX_VOLUME)

            # ✅ se c'è action_id, ritorna sempre quello (stabile)
            if self.action_id:
                return [f"ACTION:{self.action_id}"]

            return [f"Button '{self.text}' clicked"]
        return []


# =====================
# GAME VIEW (SFONDO MENU + LOAD)
# =====================
class GameView:
    def __init__(self):
        self.screen = Screen()
        self.root = RenderObject(zLayer=0)
        self.current_scene = "MENU"  # MENU | LOAD | GAME | EXIT_CONFIRM | SAVE_SLOTS
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
        # Mostramos o fondo do menú nestas escenas para manter a estética
        menu_scenes = ("MENU", "LOAD", "SAVE", "NAMING", "WARNING", "EXIT_CONFIRM", "INFO", "ENDINGS", "LEVEL_INTRO")
        if self.current_scene in menu_scenes and self.menu_bg:
            self.screen.screen.blit(self.menu_bg, (0, 0))

            overlay = pygame.Surface((self.screen.width, self.screen.height))
            overlay.set_alpha(100) # Un pouco máis escuro para lexibilidade
            overlay.fill((0, 0, 0))
            self.screen.screen.blit(overlay, (0, 0))
        else:
            self.screen.screen.fill((20, 20, 20)) # Fondo escuro para o xogo

        self.root.render(self.screen.screen)
        pygame.display.flip()

    def checkClick(self, pos):
        return self.root.checkClick(pos)
