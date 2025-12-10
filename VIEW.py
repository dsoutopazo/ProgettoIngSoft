import pygame


class Screen:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.screen = None

    def initScreen(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("BETA")


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


class Text(RenderObject):
    def __init__(self, position, content, color=(255,255,255)):
        super().__init__()
        self.position = position
        self.content = content
        self.color = color
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 24)

    def render(self, surface):
        text_surface = self.font.render(self.content, True, self.color)
        surface.blit(text_surface, self.position)

    def checkClick(self, pos):
        return []


class Image(RenderObject):
    def __init__(self, position, imageLink):
        super().__init__()
        self.position = position
        self.image = pygame.image.load(imageLink)

    def render(self, surface):
        surface.blit(self.image, self.position)

    def checkClick(self, pos):
        return []


class Button(RenderObject):
    def __init__(self, position, size, text="Button"):
        super().__init__()
        self.position = position
        self.size = size
        self.rect = pygame.Rect(position[0], position[1], size[0], size[1])
        pygame.font.init()
        self.text = text
        self.font = pygame.font.SysFont("Arial", 24)

    def render(self, surface):
        pygame.draw.rect(surface, (180, 50, 50), self.rect)
        label = self.font.render(self.text, True, (255,255,255))
        surface.blit(label, (self.position[0]+5, self.position[1]+5))

    def checkClick(self, pos):
        if self.rect.collidepoint(pos):
            return [f"Button '{self.text}' clicked"]
        return []


class GameView:
    def __init__(self):
        self.screen = Screen()
        self.root = RenderObject(zLayer=0)

    def initScreen(self):
        self.screen.initScreen()

    def linksToSubsystemObjects(self, objects):
        self.root.addChildren(objects)

    def render(self):
        self.screen.screen.fill((30, 30, 30))
        self.root.render(self.screen.screen)
        pygame.display.flip()

    def checkClick(self, pos):
        return self.root.checkClick(pos)


if __name__ == "__main__":
    game = GameView()
    game.initScreen()

    # Esempio oggetti GUI
    title = Text((50, 50), "BETA")
    button = Button((50, 150), (300, 60), "Premi qui per avviare il gioco")

    # Collegamento tramite facade
    game.linksToSubsystemObjects([title, button])

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                print(game.checkClick(event.pos))

        game.render()

    pygame.quit()
