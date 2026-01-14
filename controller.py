import pygame
import os
import sys
from model import *
from view import *
import view 


class MainController:
    def __init__(self):
        self.fileManager = FileManager()
        self.view = GameView()
        self.session = None
        self.iterator = None
        self.running = False
        self.is_saved = True 
        self.save_data = self.fileManager.loadSaves()
        self.selected_slot = None
        self.temp_name = ""

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
        self.menu_music_base = 0.25  
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

    def make_volume_button(self, position=(250, 440), size=(300, 60)):
        return Button(
            position, size,
            f"Volume: {self.current_volume_label()}",
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
                turn=data.get("turn", 0),
                is_end=data.get("is_end", False),
                level=data.get("level", 1)
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
                    image_path=data.get("image")
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

        title = Text((-1, 80), "The Adventures of Lulucia", (255, 255, 0), font_size=FONT_SIZE_TITLE, is_title=True)

        btn_new = Button((250, 220), (300, 60), "New Game", icon_path="assets/icons/play.png")
        btn_load = Button((250, 300), (300, 60), "Load Game", icon_path="assets\\icons\\flop disk.png", icon_size=65)
        btn_vol = self.make_volume_button(position=(250, 380))
        btn_exit = Button((250, 460), (300, 60), "Exit", icon_path="assets/icons/back.png", icon_size=65)

        self.view.linksToSubsystemObjects([title, btn_new, btn_load, btn_vol, btn_exit])

    def showLoadMenu(self):
        self.view.setScene("LOAD")
        self.play_menu_music()
        self.save_data = self.fileManager.loadSaves()
        
        title = Text((-1, 50), "Load Game", is_title=True)
        objects = [title]
        positions = [(250, 180), (250, 260), (250, 340)]
        
        for i in range(1, 4):
            slot_key = str(i)
            name = self.save_data.get(slot_key, {}).get("name", "Empty Slot")
            btn = Button(positions[i-1], (300, 60), f"Slot {i}: {name}", action_id=f"LOAD_SLOT_{i}")
            objects.append(btn)
            
        # Botón de volta dinámico: ao menú principal se estamos fóra, ou ao INFO MENU se estamos dentro
        back_action = "GO_MAIN_MENU" if self.view.current_scene == "MENU" else "INFO_MENU"
        objects.append(Button((250, 420), (300, 60), "Back", action_id=back_action))
        self.view.linksToSubsystemObjects(objects)

    def showSaveSlots(self):
        self.view.setScene("SAVE")
        self.save_data = self.fileManager.loadSaves()
        
        title = Text((-1, 50), "Select a Save Slot", is_title=True)
        objects = [title]
        positions = [(250, 180), (250, 260), (250, 340)]
        
        for i in range(1, 4):
            slot_key = str(i)
            name = self.save_data.get(slot_key, {}).get("name", "Empty Slot")
            btn = Button(positions[i-1], (300, 60), f"Slot {i}: {name}", action_id=f"SAVE_SLOT_{i}")
            objects.append(btn)
            
        objects.append(Button((250, 420), (300, 60), "Back", action_id="INFO_MENU"))
        self.view.linksToSubsystemObjects(objects)

    def showNamingScreen(self):
        self.view.setScene("NAMING")
        title = Text((-1, 100), "Enter a name for your save:", is_title=True)
        name_display = Text((-1, 200), f"> {self.temp_name} <", (0, 255, 0))
        hint = Text((-1, 300), "Use letters/numbers and press ENTER to confirm", font_size=FONT_SIZE_SMALL)
        btn_back = Button((250, 400), (300, 60), "Cancel", action_id="SAVE_BACK")
        self.view.linksToSubsystemObjects([title, name_display, hint, btn_back])

    def showOverwriteWarning(self, slot):
        self.view.setScene("WARNING")
        self.selected_slot = slot
        existing_name = self.save_data.get(str(slot), {}).get("name", "Unknown")
        
        title = Text((-1, 100), "WARNING!", (255, 0, 0), is_title=True)
        msg = Text((-1, 180), f"Slot {slot} contains: '{existing_name}'", font_size=FONT_SIZE_NORMAL)
        msg2 = Text((-1, 220), "Overwriting this will delete it forever.", font_size=FONT_SIZE_NORMAL)
        msg3 = Text((-1, 260), "Do you want to proceed?", font_size=FONT_SIZE_NORMAL)
        
        btn_yes = Button((100, 350), (280, 60), "Yes, Choose Slot", action_id="CONFIRM_OVERWRITE")
        btn_no = Button((420, 350), (280, 60), "No, Cancel", action_id="SAVE_BACK")
        
        self.view.linksToSubsystemObjects([title, msg, msg2, msg3, btn_yes, btn_no])

    def perform_save(self):
        p1 = self.session.characters[0]
        p2 = self.session.characters[1]
        
        save_entry = {
            "name": self.temp_name,
            "node": self.session.currentSceltaId,
            "turn": self.session.currentPlayerId,
            "p1_abilities": p1.abilities,
            "p2_abilities": p2.abilities
        }
        
        self.save_data[str(self.selected_slot)] = save_entry
        self.fileManager.saveFile("saves.json", self.save_data)
        self.is_saved = True
        self.view.setScene("GAME")
        self.updateView()

    def perform_load(self, slot):
        slot_key = str(slot)
        if slot_key not in self.save_data:
            return
            
        data = self.save_data[slot_key]
        self.readGameFile() # Recarga historia
        
        self.session.currentSceltaId = data["node"]
        self.session.currentPlayerId = data["turn"]
        self.session.characters[0].abilities = data["p1_abilities"]
        self.session.characters[1].abilities = data["p2_abilities"]
        
        # Sincronizar iterador
        self.iterator._position = data["node"]
        
        self.is_saved = True
        self.view.setScene("GAME")
        self.updateView()

    def showExitConfirm(self):
        self.view.setScene("EXIT_CONFIRM")

        title = Text((160, 180), "Vuoi chiudere senza salvare?", (255, 255, 255))

        btn_yes = Button((250, 260), (300, 60), "Si", action_id="EXIT_YES")
        btn_no  = Button((250, 340), (300, 60), "No", action_id="EXIT_NO")
        btn_back = Button((250, 420), (300, 60), "Back", action_id="EXIT_BACK")

        self.view.linksToSubsystemObjects([title, btn_yes, btn_no, btn_back])

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

        # Players logic
        players = self._get_players_list()
        p1_name, p1_abilities = "P1", "None"
        p2_name, p2_abilities = "P2", "None"

        if isinstance(players, list) and len(players) >= 1:
            p1 = players[0]
            p1_name = getattr(p1, "nickname", "P1")
            p1_abs_raw = getattr(p1, "abilities", [])
            p1_abilities = ", ".join(item.replace("_", " ") for item in p1_abs_raw) if p1_abs_raw else "None"
            
            if len(players) >= 2:
                p2 = players[1]
                p2_name = getattr(p2, "nickname", "P2")
                p2_abs_raw = getattr(p2, "abilities", [])
                p2_abilities = ", ".join(item.replace("_", " ") for item in p2_abs_raw) if p2_abs_raw else "None"

        title = Text((-1, 40), "INFO MENU", (255, 255, 255), font_size=FONT_SIZE_NORMAL, is_title=True)

        # Back arrow top-left
        back_arrow = Button((20, 20), (45, 45), text="", icon_path="assets/icons/back.png", icon_size=35, action_id="INFO_BACK")

        # Player stats: {Name}: {abilities}
        p1_stats = MultiLineText((-1, 110), f"{p1_name}: {p1_abilities}", 600, (255, 255, 255), font_size=FONT_SIZE_NORMAL)
        p2_stats = MultiLineText((-1, 150), f"{p2_name}: {p2_abilities}", 600, (255, 255, 255), font_size=FONT_SIZE_NORMAL)

        # Buttons
        btn_endings = Button((250, 220), (300, 50), "Endings", action_id="INFO_ENDINGS")
        btn_save = Button((250, 280), (300, 50), "Save game", action_id="INFO_SAVE")
        btn_load = Button((250, 340), (300, 50), "Load game", action_id="INFO_LOAD")
        btn_vol  = self.make_volume_button(position=(250, 400), size=(300, 50))
        btn_main_menu = Button((250, 460), (300, 50), "Main Menu", action_id="GO_MAIN_MENU")

        self.view.linksToSubsystemObjects([
            title, back_arrow, p1_stats, p2_stats, 
            btn_endings, btn_save, btn_load, btn_vol, btn_main_menu
        ])

    # =====================
    # GIOCO
    # =====================
    def updateView(self):
        current = self.session.currentSceltaId
        scelta = self.session.scelteCollection.__getScelta__(current)
        player = self.session.getCurrentPlayer()

        abilities_str = ", ".join(item.replace("_", " ") for item in player.abilities) if player.abilities else "None"
        
        objects = [
            Text((50, 20), f"Level: {scelta.level}", (200, 200, 0), font_size=FONT_SIZE_BUTTON),
            MultiLineText((50, 80), scelta.text, 700, font_size=FONT_SIZE_NORMAL),
            
            # Quenda e habilidades na parte inferior esquerda
            Text((150, 20), f"Turn: {player.nickname}", (200, 200, 0), font_size=FONT_SIZE_BUTTON),
            MultiLineText((350, 20), f"Abilities: {abilities_str}", 700, (200, 200, 0), font_size=FONT_SIZE_BUTTON),
        ]

        if player.image_path:
            try:
                pos_x = 50 
                pos_y = 100
                img_obj = Image((pos_x, pos_y), player.image_path)
                objects.append(img_obj)
            except Exception as e:
                print(f"[View] Erro ao cargar imaxe de personaxe {player.id}: {e}")

        if scelta.leftText:
            objects.append(Button((50, 420), (320, 80), scelta.leftText, action_id="CHOICE_LEFT"))
        if scelta.rightText:
            # Substituímos "Exit" ou "Quit" por "Main Menu" se aparece nunha escolla
            btn_text = scelta.rightText
            if btn_text.lower() in ("exit", "quit"):
                btn_text = "Main Menu"
            objects.append(Button((430, 420), (320, 80), btn_text, action_id="CHOICE_RIGHT"))

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

        if next_s.key == "EXIT":
            self.showMainMenu()
            return

        self.session.updateCurrentScelta(next_s.key)
        # Aplicamos a quenda indicada polo novo nodo
        self.session.switchTurn(forced_turn=next_s.turn)
        self.is_saved = False # Marcamos como non gardado ao tomar unha decisión
        self.updateView()

    # =====================
    # EVENTI
    # =====================
    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Se estamos no xogo e hai cambios sen gardar, preguntamos
                if not self.is_saved and self.view.current_scene in ("GAME", "INFO"):
                    self.showExitConfirm()
                else:
                    self.running = False

            # tasto I per aprire/chiudere info
            if event.type == pygame.KEYDOWN:
                if self.view.current_scene == "NAMING":
                    if event.key == pygame.K_RETURN:
                        if self.temp_name.strip():
                            self.perform_save()
                    elif event.key == pygame.K_BACKSPACE:
                        self.temp_name = self.temp_name[:-1]
                        self.showNamingScreen()
                    else:
                        # Limitar nome a 15 caracteres
                        if len(self.temp_name) < 15 and event.unicode.isalnum() or event.unicode == ' ':
                            self.temp_name += event.unicode
                            self.showNamingScreen()

                elif event.key == pygame.K_i and self.view.current_scene == "GAME":
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

                        if action == "GO_MAIN_MENU":
                            self.showMainMenu()
                            continue

                        if action == "CHOICE_LEFT":
                            self.nextScelta("left")
                            continue

                        if action == "CHOICE_RIGHT":
                            self.nextScelta("right")
                            continue

                        if action == "INFO_ENDINGS":
                            print("Endings clicked")
                            continue

                        if action == "INFO_SAVE":
                            self.showSaveSlots()
                            continue

                        if action == "INFO_LOAD":
                            self.showLoadMenu()
                            continue

                        if action.startswith("SAVE_SLOT_"):
                            slot = int(action.split("_")[-1])
                            self.selected_slot = slot
                            if str(slot) in self.save_data:
                                self.showOverwriteWarning(slot)
                            else:
                                self.temp_name = ""
                                self.showNamingScreen()
                            continue

                        if action == "CONFIRM_OVERWRITE":
                            self.temp_name = ""
                            self.showNamingScreen()
                            continue

                        if action.startswith("LOAD_SLOT_"):
                            slot = int(action.split("_")[-1])
                            self.perform_load(slot)
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
                            self.readGameFile()
                            self.is_saved = True # Nova partida empeza como "gardada" (sen cambios)
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
                        pass # Xestionado por ACTION:CHOICE_LEFT/RIGHT arriba

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
