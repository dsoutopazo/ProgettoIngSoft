import pygame
import os
import sys
import json
from model import *
from view import *


class MainController:
    def __init__(self):
        self.fileManager = FileManager()
        self.view = GameView()
        self.session = None
        self.iterator = None
        self.running = False
        self.showing_endings_menu = False

        # ===== MENU MUSIC (MENU + LOAD)
        self.menu_music_playing = False

    # =====================
    # MUSIC
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
            pygame.mixer.music.play(-1)  # infinite loop
            self.menu_music_playing = True
        except Exception as e:
            print("[Music] Menu music failed:", e)

    def fadeout_menu_music(self, ms=1200):
        """Smooth fade-out and then automatic stop."""
        if not self.menu_music_playing:
            return
        try:
            pygame.mixer.music.fadeout(ms)  # after ms, it stops automatically
        except Exception:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
        self.menu_music_playing = False

    # =====================
    # GAME FILE
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
                level=data.get("level", 1),
                ending=data.get("ending", "NO"),
                endingTitle=data.get("endingTitle", ""),
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
    # ENDINGS
    # =====================
    def loadEndings(self):
        """Loads the endings.json file"""
        try:
            with open("endings.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            # If it doesn't exist, create initial structure
            return {"1": {"total": 9, "achieved": []}}

    def saveEndings(self, endings_data):
        """Saves the endings.json file"""
        with open("endings.json", "w", encoding="utf-8") as f:
            json.dump(endings_data, f, indent=4, ensure_ascii=False)

    def registerEnding(self, level, ending_title):
        """Registers an achieved ending"""
        if not ending_title:
            return
        endings = self.loadEndings()
        level_str = str(level)
        if level_str not in endings:
            endings[level_str] = {"total": 0, "achieved": []}
        if ending_title not in endings[level_str]["achieved"]:
            endings[level_str]["achieved"].append(ending_title)
            self.saveEndings(endings)

    def getAllEndingsForLevel(self, level):
        """Gets all endings for a level from storia.json, returns list of tuples (title, type)"""
        endings = []
        scelteData, _ = self.fileManager.loadFile("storia.json")
        for key, data in scelteData.items():
            if data.get("level") == level and data.get("ending") in ["WIN", "FAIL"]:
                endings.append((data.get("endingTitle", ""), data.get("ending", "FAIL")))
        return endings

    def showEndingsMenu(self):
        """Shows the endings menu"""
        self.showing_endings_menu = True
        endings_data = self.loadEndings()
        
        objects = []
        objects.append(Text((280, 30), "ACHIEVED ENDINGS", (255, 255, 0)))
        
        y_offset = 80
        # Sort levels by number
        sorted_levels = sorted(endings_data.keys(), key=lambda x: int(x))
        
        for level_str in sorted_levels:
            level = int(level_str)
            level_data = endings_data[level_str]
            all_endings = self.getAllEndingsForLevel(level)
            
            # Level title
            objects.append(Text((50, y_offset), f"Level {level}", (200, 200, 255)))
            y_offset += 35
            
            # Show all endings for this level
            for ending_title, ending_type in all_endings:
                if ending_title in level_data["achieved"]:
                    # Ending achieved - show with symbol based on type
                    if ending_type == "WIN":
                        symbol = "✓"
                        color = (100, 255, 100)  # Green
                    else:  # FAIL
                        symbol = "✗"
                        color = (255, 100, 100)  # Red
                    objects.append(Text((70, y_offset), f"{symbol} {ending_title}", color))
                else:
                    # Ending not achieved
                    objects.append(Text((70, y_offset), "??????", (150, 150, 150)))
                y_offset += 30
            
            y_offset += 10  # Space between levels
        
        # Close button
        btn_close = Button((350, 520), (100, 50), "Close")
        objects.append(btn_close)
        
        self.view.setScene("ENDINGS_MENU")
        self.view.linksToSubsystemObjects(objects)

    # =====================
    # MENU
    # =====================
    def showMainMenu(self):
        self.view.setScene("MENU")
        self.play_menu_music()  # 🎵 menu music

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
        btn_endings = Button(
            (250, 360), (300, 60),
            "Endings",
            icon_path=None
        )
        btn_exit = Button(
            (250, 440), (300, 60),
            "Exit",
            icon_path="assets/icons/back.png",
            icon_size=65
        )

        self.view.linksToSubsystemObjects([title, btn_new, btn_load, btn_endings, btn_exit])

    def showLoadMenu(self):
        self.view.setScene("LOAD")
        self.play_menu_music()  # 🎵 continues in load menu too

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
    # GAME
    # =====================
    def updateView(self):
        current = self.session.currentSceltaId
        scelta = self.session.scelteCollection.__getScelta__(current)
        player = self.session.getCurrentPlayer()

        # Format abilities as a pretty string
        abilities_str = ", ".join(player.abilities) if player.abilities else "(none)"
        objects = [
            Text((40, 10), f"Turn: {player.nickname}", (200, 200, 0)),
            Text((40, 40), f"Abilities: {abilities_str}", (150, 220, 150)),
            Text((50, 80), scelta.text, max_width=700),  # Text wraps to fit screen width
        ]

        if scelta.leftText:
            objects.append(Button((50, 420), (300, 60), scelta.leftText))
        if scelta.rightText:
            objects.append(Button((450, 420), (300, 60), scelta.rightText))
        
        # Endings button (bottom right corner)
        btn_endings_game = Button((610, 500), (170, 60), "Endings", icon_path=None)
        objects.append(btn_endings_game)

        self.view.linksToSubsystemObjects(objects)

    def nextScelta(self, direction):
        self.iterator._position = self.session.currentSceltaId
        player = self.session.getCurrentPlayer()
        scelta = self.session.scelteCollection.__getScelta__(self.session.currentSceltaId)

        try:
            if direction == "left":
                if scelta.leftObjects:
                    player.updateAbilities(scelta.leftObjects)
                next_s = self.iterator.getLeft(player.abilities)
            else:
                if scelta.rightObjects:
                    player.updateAbilities(scelta.rightObjects)
                next_s = self.iterator.getRight(player.abilities)
        except KeyError as e:
            # Handle EXIT - it's not a real node, just exit the game
            if str(e) == "EXIT":
                self.running = False
                return
            raise

        self.session.updateCurrentScelta(next_s.key)
        
        # Register ending if it's one
        if next_s.ending in ["WIN", "FAIL"] and next_s.endingTitle:
            self.registerEnding(next_s.level, next_s.endingTitle)
        
        self.session.switchTurn()
        self.updateView()

    # =====================
    # EVENTS
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
                            self.fadeout_menu_music(ms=1200)  # 🎵 smooth fade-out
                            self.readGameFile()
                            self.view.setScene("GAME")
                            self.updateView()

                        elif "Load Game" in msg:
                            self.showLoadMenu()

                        elif "Endings" in msg:
                            self.showEndingsMenu()

                        elif "Exit" in msg:
                            self.running = False

                    elif self.view.current_scene == "LOAD":
                        if "Slot" in msg:
                            print("Slot clicked (not implemented)")
                        elif "Back" in msg:
                            self.showMainMenu()

                    elif self.view.current_scene == "GAME":
                        scelta = self.session.scelteCollection.__getScelta__(self.session.currentSceltaId)
                        
                        # Check for Restart/Quit buttons first (they go to menu/exit, not game logic)
                        if scelta.leftText == "Restart" and "Restart" in msg:
                            self.showMainMenu()
                        elif scelta.rightText == "Quit" and "Quit" in msg:
                            self.running = False
                        elif scelta.leftText == "Play Again" and "Play Again" in msg:
                            self.showMainMenu()
                        elif scelta.rightText == "Exit" and "Exit" in msg:
                            self.running = False
                        # Check if endings button was clicked (but not from menu choices)
                        elif "Button 'Endings' clicked" in msg:
                            self.showEndingsMenu()
                        # Normal game choice buttons
                        elif scelta.leftText and scelta.leftText in msg:
                            self.nextScelta("left")
                        elif scelta.rightText and scelta.rightText in msg:
                            self.nextScelta("right")
                    
                    elif self.view.current_scene == "ENDINGS_MENU":
                        if "Close" in msg:
                            self.showing_endings_menu = False
                            # Return to previous scene (could be MENU or GAME)
                            if self.session and self.session.currentSceltaId:
                                self.view.setScene("GAME")
                                self.updateView()
                            else:
                                self.showMainMenu()

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
