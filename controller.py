import pygame
import os
import sys
from model import *
from view import *


class MainController:
    def __init__(self):
        self.fileManager = FileManager()
        self.view = GameView()
        self.session = None
        self.iterator = None
        self.running = False

        # ===== MUSICA MENU (MENU + LOAD)
        self.menu_music_playing = False

    # =====================
    # MUSICA
    # =====================
    def _music_path(self, filename):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, "assets", "sounds", filename)

    def play_menu_music(self, volume=0.25):
        if self.menu_music_playing:
            return
        try:
            pygame.mixer.music.load(self._music_path("menu_music.mp3"))
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)  # loop infinito
            self.menu_music_playing = True
        except Exception as e:
            print("[Music] Menu music failed:", e)

    def fadeout_menu_music(self, ms=1200):
        """Fade-out morbido e poi stop automatico."""
        if not self.menu_music_playing:
            return
        try:
            pygame.mixer.music.fadeout(ms)  # dopo ms, si ferma da solo
        except Exception:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
        self.menu_music_playing = False

    # =====================
    # FILE DI GIOCO
    # =====================
    def parseScelteData(self, sceltaData):
        scelte = {}
        for key, data in sceltaData.items():
            scelte[key] = Scelta(
                key=key,
                text=data.get("text", ""),
                nextRight=data.get("nextRight", []),
                nextLeft=data.get("nextLeft", []),
                rightText=data.get("rightText", ""),
                leftText=data.get("leftText", ""),
                rightObjects=data.get("rightObjects", []),
                leftObjects=data.get("leftObjects", []),
            )
        return ScelteCollection(scelte)

    def parseCharactersData(self, charactersData):
        characters = []
        for char_id_str in charactersData:
            data = charactersData[char_id_str]
            characters.append(
                Character(
                    int(char_id_str),
                    data.get("nickname"),
                    data.get("abilities", []),
                )
            )
        return characters

    def readGameFile(self, fileName="storia.json"):
        scelteData, charactersData = self.fileManager.loadFile(fileName)
        self.session = GameSession(
            self.parseScelteData(scelteData),
            self.parseCharactersData(charactersData),
        )
        self.iterator = iter(self.session.scelteCollection)

    # =====================
    # MENU
    # =====================
    def showMainMenu(self):
        self.view.setScene("MENU")
        self.play_menu_music()  # 🎵 musica menu

        title = Text((300, 80), "BETA GAME", (255, 255, 0))

        btn_new = Button(
            (250, 200), (300, 60),
            "New Game",
            icon_path="assets/icons/play.png"
        )
        btn_load = Button(
            (250, 280), (300, 60),
            "Load Game",
            icon_path="assets\\icons\\flop disk.png",
            icon_size=65
        )
        btn_exit = Button(
            (250, 360), (300, 60),
            "Exit",
            icon_path="assets/icons/back.png",
            icon_size=65
        )

        self.view.linksToSubsystemObjects([title, btn_new, btn_load, btn_exit])

    def showLoadMenu(self):
        self.view.setScene("LOAD")
        self.play_menu_music()  # 🎵 continua anche nel load

        title = Text((310, 80), "LOAD GAME", (0, 200, 255))

        slot1 = Button((250, 200), (300, 60), "Slot 1",
                       icon_path="assets\\icons\\flop disk.png", icon_size=65)
        slot2 = Button((250, 270), (300, 60), "Slot 2",
                       icon_path="assets\\icons\\flop disk.png", icon_size=65)
        slot3 = Button((250, 340), (300, 60), "Slot 3",
                       icon_path="assets\\icons\\flop disk.png", icon_size=65)
        back = Button((250, 420), (300, 60), "Back",
                      icon_path="assets/icons/back.png", icon_size=65)

        self.view.linksToSubsystemObjects([title, slot1, slot2, slot3, back])

    # =====================
    # GIOCO
    # =====================
    def updateView(self):
        current = self.session.currentSceltaId
        scelta = self.session.scelteCollection.__getScelta__(current)
        player = self.session.getCurrentPlayer()

        objects = [
            Text((40, 10), f"Turno: {player.nickname} | Abilità: {player.abilities}", (200, 200, 0)),
            Text((50, 60), scelta.text),
        ]

        if scelta.leftText:
            objects.append(Button((50, 420), (300, 60), scelta.leftText))
        if scelta.rightText:
            objects.append(Button((450, 420), (300, 60), scelta.rightText))

        self.view.linksToSubsystemObjects(objects)

    def nextScelta(self, direction):
        self.iterator._position = self.session.currentSceltaId
        player = self.session.getCurrentPlayer()
        scelta = self.session.scelteCollection.__getScelta__(self.session.currentSceltaId)

        if direction == "left":
            if scelta.leftObjects:
                player.updateAbilities(scelta.leftObjects)
            next_s = self.iterator.getLeft(player.abilities)
        else:
            if scelta.rightObjects:
                player.updateAbilities(scelta.rightObjects)
            next_s = self.iterator.getRight(player.abilities)

        self.session.updateCurrentScelta(next_s.key)
        self.session.switchTurn()
        self.updateView()

    # =====================
    # EVENTI
    # =====================
    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                clicks = self.view.checkClick(event.pos)

                for msg in clicks:
                    if self.view.current_scene == "MENU":
                        if "New Game" in msg:
                            self.fadeout_menu_music(ms=1200)  # 🎵 fade-out morbido
                            self.readGameFile()
                            self.view.setScene("GAME")
                            self.updateView()

                        elif "Load Game" in msg:
                            self.showLoadMenu()

                        elif "Exit" in msg:
                            self.running = False

                    elif self.view.current_scene == "LOAD":
                        if "Slot" in msg:
                            print("Slot cliccato (non implementato)")
                        elif "Back" in msg:
                            self.showMainMenu()

                    elif self.view.current_scene == "GAME":
                        scelta = self.session.scelteCollection.__getScelta__(self.session.currentSceltaId)
                        if scelta.leftText and scelta.leftText in msg:
                            self.nextScelta("left")
                        elif scelta.rightText and scelta.rightText in msg:
                            self.nextScelta("right")

    # =====================
    # LOOP
    # =====================
    def gameLoop(self):
        self.view.initScreen()
        self.running = True
        self.showMainMenu()

        clock = pygame.time.Clock()
        while self.running:
            self.handleEvents()
            self.view.render()
            clock.tick(60)

        pygame.quit()
        sys.exit()
