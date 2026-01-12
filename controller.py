import pygame
import os
import sys
from model import *
from view import *
import view  # per modificare view.SFX_VOLUME


class MainController:
    def __init__(self):
        self.fileManager = FileManager()
        self.view = GameView()
        self.session = None
        self.iterator = None
        self.running = False

        # ===== MUSICA MENU (MENU + LOAD)
        self.menu_music_playing = False

        # ===== VOLUME (4 livelli)
        self.volume_levels = [
            ("Mute", 0.0),
            ("Low", 0.25),
            ("Medium", 0.5),
            ("High", 1.0),
        ]
        self.volume_index = 3
        self.menu_music_base = 0.25  # volume musica = master * base
        self.apply_volume()

    # =====================
    # PATH MUSICA
    # =====================
    def _music_path(self, filename):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, "assets", "sounds", filename)

    # =====================
    # VOLUME
    # =====================
    def current_volume_label(self):
        return self.volume_levels[self.volume_index][0]

    def current_master_volume(self):
        return self.volume_levels[self.volume_index][1]

    def apply_volume(self):
        master = self.current_master_volume()
        view.SFX_VOLUME = master
        try:
            pygame.mixer.music.set_volume(master * self.menu_music_base)
        except Exception:
            pass

    def cycle_volume(self):
        self.volume_index = (self.volume_index + 1) % len(self.volume_levels)
        self.apply_volume()
        self.refresh_scene()

    def make_volume_button(self):
        return Button(
            (20, 530), (220, 50),
            self.current_volume_label(),
            icon_path="assets/icons/volume.png",
            icon_size=36,
            action_id="VOLUME"
        )

    def refresh_scene(self):
        if self.view.current_scene == "MENU":
            self.showMainMenu()
        elif self.view.current_scene == "LOAD":
            self.showLoadMenu()
        elif self.view.current_scene == "GAME":
            self.updateView()
        elif self.view.current_scene == "EXIT_CONFIRM":
            self.showExitConfirm()
        elif self.view.current_scene == "SAVE_SLOTS":
            self.showSaveSlots()
        elif self.view.current_scene == "INFO":
            self.showInfoMenu()

    # =====================
    # MUSICA
    # =====================
    def play_menu_music(self):
        if self.menu_music_playing:
            return
        try:
            pygame.mixer.music.load(self._music_path("menu_music.mp3"))
            self.apply_volume()
            pygame.mixer.music.play(-1)
            self.menu_music_playing = True
        except Exception as e:
            print("[Music] Menu music failed:", e)

    def fadeout_menu_music(self, ms=1200):
        if not self.menu_music_playing:
            return
        try:
            pygame.mixer.music.fadeout(ms)
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
        self.play_menu_music()

        title = Text((300, 80), "BETA GAME", (255, 255, 0))

        btn_new = Button((250, 200), (300, 60), "New Game", icon_path="assets/icons/play.png")
        btn_load = Button((250, 280), (300, 60), "Load Game", icon_path="assets\\icons\\flop disk.png", icon_size=65)
        btn_exit = Button((250, 360), (300, 60), "Exit", icon_path="assets/icons/back.png", icon_size=65)

        self.view.linksToSubsystemObjects([title, btn_new, btn_load, btn_exit, self.make_volume_button()])

    def showLoadMenu(self):
        self.view.setScene("LOAD")
        self.play_menu_music()

        title = Text((310, 80), "LOAD GAME", (0, 200, 255))

        slot1 = Button((250, 200), (300, 60), "Slot 1", icon_path="assets\\icons\\flop disk.png", icon_size=65)
        slot2 = Button((250, 270), (300, 60), "Slot 2", icon_path="assets\\icons\\flop disk.png", icon_size=65)
        slot3 = Button((250, 340), (300, 60), "Slot 3", icon_path="assets\\icons\\flop disk.png", icon_size=65)
        back  = Button((250, 420), (300, 60), "Back", icon_path="assets/icons/back.png", icon_size=65)

        self.view.linksToSubsystemObjects([title, slot1, slot2, slot3, back, self.make_volume_button()])

    # =====================
    # EXIT FLOW
    # =====================
    def showExitConfirm(self):
        self.view.setScene("EXIT_CONFIRM")

        title = Text((160, 180), "Vuoi chiudere senza salvare?", (255, 255, 255))

        btn_yes = Button((250, 260), (300, 60), "Si", action_id="EXIT_YES")
        btn_no  = Button((250, 340), (300, 60), "No", action_id="EXIT_NO")
        btn_back = Button((250, 420), (300, 60), "Back", action_id="EXIT_BACK")

        self.view.linksToSubsystemObjects([title, btn_yes, btn_no, btn_back, self.make_volume_button()])

    def showSaveSlots(self):
        self.view.setScene("SAVE_SLOTS")

        title = Text((190, 120), "Scegli uno slot per salvare", (255, 255, 255))

        slot1 = Button((250, 200), (300, 60), "Slot 1", action_id="SAVE_SLOT_1")
        slot2 = Button((250, 270), (300, 60), "Slot 2", action_id="SAVE_SLOT_2")
        slot3 = Button((250, 340), (300, 60), "Slot 3", action_id="SAVE_SLOT_3")
        back = Button((250, 420), (300, 60), "Back", action_id="SAVE_BACK")

        self.view.linksToSubsystemObjects([title, slot1, slot2, slot3, back, self.make_volume_button()])

    # =====================
    # INFO MENU (P1 + P2) + bottone in alto a destra
    # =====================
    def _get_players_list(self):
        # prova a trovare la lista dei personaggi nella session
        for attr in ("characters", "players", "characterList", "charactersList"):
            if hasattr(self.session, attr):
                val = getattr(self.session, attr)
                if isinstance(val, list):
                    return val
        # fallback: prova dentro self.session.characters se è un dict ecc.
        return None

    def showInfoMenu(self):
        self.view.setScene("INFO")

        # recupero P1/P2 in modo robusto
        players = self._get_players_list()
        p1 = None
        p2 = None

        if isinstance(players, list) and len(players) >= 2:
            p1, p2 = players[0], players[1]
        else:
            # fallback: almeno current player come P1
            try:
                p1 = self.session.getCurrentPlayer()
            except Exception:
                p1 = None
            p2 = None

        p1_name = getattr(p1, "nickname", "P1")
        p1_abilities = getattr(p1, "abilities", [])

        if p2 is not None:
            p2_name = getattr(p2, "nickname", "P2")
            p2_abilities = getattr(p2, "abilities", [])
        else:
            p2_name = "P2"
            p2_abilities = ["(not available)"]

        current_id = getattr(self.session, "currentSceltaId", None)

        total_nodes = None
        try:
            total_nodes = len(self.session.scelteCollection.scelte)
        except Exception:
            try:
                total_nodes = len(self.session.scelteCollection._scelte)
            except Exception:
                total_nodes = None

        title = Text((300, 60), "INFO MENU", (255, 255, 255))

        t1 = Text((120, 150), f"P1: {p1_name}", (255, 255, 255))
        t2 = Text((120, 190), f"P1 abilities/items: {p1_abilities}", (255, 255, 255))

        t3 = Text((120, 260), f"P2: {p2_name}", (255, 255, 255))
        t4 = Text((120, 300), f"P2 abilities/items: {p2_abilities}", (255, 255, 255))

        if current_id is not None and total_nodes is not None:
            t5 = Text((120, 380), f"Progress: node {current_id} / {total_nodes}", (255, 255, 255))
        elif current_id is not None:
            t5 = Text((120, 380), f"Progress: current node = {current_id}", (255, 255, 255))
        else:
            t5 = Text((120, 380), "Progress: not available", (255, 255, 255))

        back = Button((250, 460), (300, 60), "Back", action_id="INFO_BACK")

        self.view.linksToSubsystemObjects([title, t1, t2, t3, t4, t5, back, self.make_volume_button()])

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

        # ✅ Bottone INFO (solo icona) in alto a destra
        # 800 - 36 - 10 = 754
        objects.append(
            Button(
                (754, 10), (36, 36),
                text="",
                icon_path="assets/icons/info.png",
                icon_size=35,
                action_id="INFO_MENU",
            )
        )

        # ✅ Bottone Exit in-game: piccolo in basso a destra
        objects.append(
            Button(
                (750, 550), (36, 36),
                text="",
                icon_path="assets/icons/quit.png",
                icon_size=35,
                action_id="EXIT_GAME",
            )
        )

        objects.append(self.make_volume_button())
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

            # tasto I per aprire/chiudere info
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_i and self.view.current_scene == "GAME":
                    self.showInfoMenu()
                elif event.key == pygame.K_i and self.view.current_scene == "INFO":
                    self.view.setScene("GAME")
                    self.updateView()

            if event.type == pygame.MOUSEBUTTONDOWN:
                clicks = self.view.checkClick(event.pos)

                for msg in clicks:
                    # ✅ ACTIONS
                    if msg.startswith("ACTION:"):
                        action = msg.split("ACTION:")[1]

                        if action == "VOLUME":
                            self.cycle_volume()
                            continue

                        if action == "INFO_MENU":
                            self.showInfoMenu()
                            continue

                        if action == "INFO_BACK":
                            self.view.setScene("GAME")
                            self.updateView()
                            continue

                        if action == "EXIT_GAME":
                            self.showExitConfirm()
                            continue

                        if action == "EXIT_YES":
                            self.running = False
                            continue

                        if action == "EXIT_NO":
                            self.showSaveSlots()
                            continue

                        if action == "EXIT_BACK":
                            self.view.setScene("GAME")
                            self.updateView()
                            continue

                        if action in ("SAVE_SLOT_1", "SAVE_SLOT_2", "SAVE_SLOT_3"):
                            print("Salvataggio su:", action)  # TODO: salvataggio vero
                            self.running = False
                            continue

                        if action == "SAVE_BACK":
                            self.view.setScene("GAME")
                            self.updateView()
                            continue

                    # ✅ Logica classica per MENU/LOAD/GAME (testo)
                    if self.view.current_scene == "MENU":
                        if "New Game" in msg:
                            self.fadeout_menu_music(ms=1200)
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
