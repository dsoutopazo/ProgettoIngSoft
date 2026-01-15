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
        self.gallery_page = 0
        self.quit_after_save = False
        self.audio = AudioManager()

    # =====================
    # MUSICA
    # =====================
    def play_menu_music(self):
        self.audio.play_menu_music()

    def fadeout_menu_music(self, ms=1200):
        self.audio.fadeout_music(ms)

    def cycle_volume(self):
        self.audio.cycle_volume()
        self.refresh_scene()

    def make_volume_button(self, position=(250, 440), size=(300, 60)):
        return Button(
            position, size,
            f"Volume: {self.audio.volume_levels[self.audio.volume_index][0]}",
            icon_path="assets/icons/volume.png",
            icon_size=28,
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
    # FILE DI GIOCO
    # =====================
    def parseScelteData(self, sceltaData, intros=None):
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
                level=data.get("level", 1),
                ending_title=data.get("ending_title")
            )
        return ScelteCollection(scelte, intros)

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

    def readGameFile(self, fileName="storia.json", show_intro=True):
        scelteData, charactersData, intros = self.fileManager.loadFile(fileName)
        self.session = GameSession(
            self.parseScelteData(scelteData, intros),
            self.parseCharactersData(charactersData),
        )
        self.iterator = iter(self.session.scelteCollection)
        if show_intro:
            self.showLevelIntro(1)

    # =====================
    # MENU
    # =====================
    def showMainMenu(self):
        self.view.setScene("MENU")
        self.play_menu_music()

        title = Text((-1, 80), "The Adventures of Lulucia", (255, 255, 0), font_size=FONT_SIZE_TITLE, is_title=True)

        btn_new = Button((250, 220), (300, 60), "New Game", icon_path="assets/icons/play.png", icon_size=48)
        btn_load = Button((250, 300), (300, 60), "Load Game", icon_path="assets/icons/flop disk.png", icon_size=48)
        btn_vol = self.make_volume_button(position=(250, 380))
        btn_end = Button((250, 460), (300, 60), "Endings Gallery", action_id="INFO_ENDINGS")

        self.view.setSceneObjects([title, btn_new, btn_load, btn_vol, btn_end])

    def showLoadMenu(self):
        prev_scene = self.view.current_scene
        self.view.setScene("LOAD")
        self.play_menu_music()
        self.save_data = self.fileManager.loadSaves()
        
        title = Text((-1, 50), "Load Game", font_size=FONT_SIZE_TITLE, is_title=False)
        objects = [title]
        
        back_action = "GO_MAIN_MENU" if prev_scene == "MENU" else "INFO_MENU"
        back_arrow = Button((20, 20), (45, 45), text="", icon_path="assets/icons/back.png", icon_size=35, action_id=back_action)
        objects.append(back_arrow)

        positions = [(250, 180), (250, 260), (250, 340)]
        
        for i in range(1, 4):
            slot_key = str(i)
            name = self.save_data.get(slot_key, {}).get("name", "Empty Slot")
            btn = Button(positions[i-1], (300, 60), f"Slot {i}: {name}", action_id=f"LOAD_SLOT_{i}")
            objects.append(btn)
            
        self.view.setSceneObjects(objects)

    def _get_players_list(self):
        for attr in ("characters", "players", "characterList", "charactersList"):
            if hasattr(self.session, attr):
                val = getattr(self.session, attr)
                if isinstance(val, list):
                    return val
        return None

    def showInfoMenu(self):
        self.view.setScene("INFO")

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

        title = Text((-1, 40), "INFO MENU", (255, 255, 255), font_size=FONT_SIZE_TITLE, is_title=False)

        back_arrow = Button((20, 20), (45, 45), text="", icon_path="assets/icons/back.png", icon_size=35, action_id="INFO_BACK")

        p1_stats = MultiLineText((-1, 110), f"{p1_name}: {p1_abilities}", 600, (255, 255, 255), font_size=FONT_SIZE_NORMAL)
        p2_stats = MultiLineText((-1, 150), f"{p2_name}: {p2_abilities}", 600, (255, 255, 255), font_size=FONT_SIZE_NORMAL)

        # Buttons
        btn_endings = Button((250, 220), (300, 50), "Endings", action_id="INFO_ENDINGS")
        btn_save = Button((250, 280), (300, 50), "Save game", action_id="INFO_SAVE")
        btn_load = Button((250, 340), (300, 50), "Load game", action_id="INFO_LOAD")
        btn_vol  = self.make_volume_button(position=(250, 400), size=(300, 50))
        btn_main_menu = Button((250, 460), (300, 50), "Main Menu", action_id="GO_MAIN_MENU")

        self.view.setSceneObjects([
            title, back_arrow, p1_stats, p2_stats, 
            btn_endings, btn_save, btn_load, btn_vol, btn_main_menu
        ])

    def showSaveSlots(self):
        prev_scene = self.view.current_scene
        self.view.setScene("SAVE")
        self.save_data = self.fileManager.loadSaves()
        
        title = Text((-1, 50), "Select a Save Slot", font_size=FONT_SIZE_TITLE, is_title=False)
        objects = [title]

        back_action = "GO_MAIN_MENU" if prev_scene == "MENU" else "INFO_MENU"
        back_arrow = Button((20, 20), (45, 45), text="", icon_path="assets/icons/back.png", icon_size=35, action_id=back_action)
        objects.append(back_arrow)

        positions = [(250, 180), (250, 260), (250, 340)]
        
        for i in range(1, 4):
            slot_key = str(i)
            name = self.save_data.get(slot_key, {}).get("name", "Empty Slot")
            btn = Button(positions[i-1], (300, 60), f"Slot {i}: {name}", action_id=f"SAVE_SLOT_{i}")
            objects.append(btn)
            
        self.view.setSceneObjects(objects)

    def showNamingScreen(self):
        self.view.setScene("NAMING")
        title = Text((-1, 100), "Enter a name for your save:", is_title=True)
        name_display = Text((-1, 200), f"> {self.temp_name} <", (0, 255, 0))
        hint = Text((-1, 300), "Use letters/numbers and press ENTER to confirm", font_size=FONT_SIZE_SMALL)
        btn_back = Button((250, 400), (300, 60), "Cancel", action_id="SAVE_BACK")
        self.view.setSceneObjects([title, name_display, hint, btn_back])

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
        
        self.view.setSceneObjects([title, msg, msg2, msg3, btn_yes, btn_no])

    def saveGame(self):
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
        
        if self.quit_after_save:
            self.running = False
        else:
            self.view.setScene("GAME")
            self.updateView()

    def loadGame(self, slot):
        slot_key = str(slot)
        if slot_key not in self.save_data:
            return
            
        data = self.save_data[slot_key]
        self.readGameFile(show_intro=False)
        
        self.session.currentSceltaId = data["node"]
        scelta = self.session.scelteCollection.__getScelta__(data["node"])
        self.session.last_viewed_level = scelta.level
        self.session.currentPlayerId = data["turn"]
        self.session.characters[0].abilities = data["p1_abilities"]
        self.session.characters[1].abilities = data["p2_abilities"]
        
        self.iterator._position = data["node"]
        
        self.is_saved = True
        self.view.setScene("GAME")
        self.updateView()

    def showEndingsMenu(self):
        prev_scene = self.view.current_scene
        if self.view.current_scene != "ENDINGS":
            self.last_scene_before_gallery = prev_scene
            self.gallery_page = 0

        self.view.setScene("ENDINGS")
        self.save_data = self.fileManager.loadSaves()
        unlocked = self.save_data.get("unlocked_endings", [])

        if self.session is None:
            self.readGameFile()
        
        title = Text((-1, 40), "ENDINGS GALLERY", font_size=FONT_SIZE_TITLE, is_title=False)
        objects = [title]

        back_action = "GO_MAIN_MENU" if prev_scene == "MENU" else "INFO_MENU"
        back_arrow = Button((20, 20), (45, 45), text="", icon_path="assets/icons/back.png", icon_size=35, action_id=back_action)
        objects.append(back_arrow)
        
        all_items = []
        endings_by_level = {}
        for key, node in self.session.scelteCollection._collection.items():
            if node.is_end:
                lvl = node.level
                if lvl not in endings_by_level: endings_by_level[lvl] = []
                endings_by_level[lvl].append(node)
        
        for lvl in sorted(endings_by_level.keys()):
            all_items.append({"type": "LEVEL", "val": lvl})
            for end_node in endings_by_level[lvl]:
                all_items.append({"type": "ENDING", "val": end_node})

        # Paginazione
        per_page = 8
        total_pages = math.ceil(len(all_items) / per_page)
        start_idx = self.gallery_page * per_page
        page_items = all_items[start_idx : start_idx + per_page]

        y_offset = 120
        for item in page_items:
            if item["type"] == "LEVEL":
                lvl = item["val"]
                obj = Text((50, y_offset), f"Level {lvl}", font_size=FONT_SIZE_BUTTON)
                objects.append(obj)
            else:
                end_node = item["val"]
                if end_node.key in unlocked:
                    color = (0, 255, 0) if "WIN" in end_node.key else (255, 50, 50)
                    display_text = f"• {end_node.ending_title}"
                else:
                    color = (100, 100, 100)
                    display_text = "• ???????????????"
                obj = Text((80, y_offset), display_text, color, font_size=FONT_SIZE_NORMAL)
                objects.append(obj)
            y_offset += 42

        if self.gallery_page > 0:
            objects.append(Button((50, 520), (120, 50), "Prev", action_id="GALLERY_PREV"))
        
        if (self.gallery_page + 1) < total_pages:
            objects.append(Button((630, 520), (120, 50), "Next", action_id="GALLERY_NEXT"))

        page_info = Text((-1, 575), f"Page {self.gallery_page + 1} of {total_pages}", font_size=FONT_SIZE_SMALL)
        objects.append(page_info)

        self.view.setSceneObjects(objects)

    def showLevelIntro(self, level):
        self.view.setScene("LEVEL_INTRO")
        intro_text = self.session.scelteCollection.level_introductions.get(str(level), "Your journey continues...")
        
        bg_modal = Button((100, 80), (600, 420), text="", color=(30, 30, 30), hover_color=(30, 30, 30))
        
        title = Text((-1, 150), f"LEVEL {level}", font_size=FONT_SIZE_TITLE, is_title=False)
        desc = MultiLineText((-1, 230), intro_text, 500, font_size=FONT_SIZE_NORMAL)
        btn_continue = Button((250, 430), (300, 60), "Continue", action_id="LEVEL_CONTINUE")
        
        self.view.setSceneObjects([bg_modal, title, desc, btn_continue])
        self.session.last_viewed_level = level

    def showExitConfirm(self):
        self.view.setScene("EXIT_CONFIRM")

        title = Text((-1, 180), "Quit without saving?", (255, 255, 255))

        btn_yes = Button((250, 260), (300, 60), "Yes, Quit", action_id="EXIT_YES")
        btn_save_quit = Button((250, 340), (300, 60), "Save and quit", action_id="EXIT_SAVE_QUIT")
        btn_back = Button((250, 420), (300, 60), "Back", action_id="EXIT_BACK")

        self.view.setSceneObjects([title, btn_yes, btn_save_quit, btn_back])


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
                print(f"[View] Errore nel caricamento dell'immagine del personaggio {player.id}: {e}")

        if scelta.leftText:
            objects.append(Button((50, 420), (320, 80), scelta.leftText, action_id="CHOICE_LEFT"))
        if scelta.rightText:
            btn_text = scelta.rightText
            if btn_text.lower() in ("exit", "quit"):
                btn_text = "Main Menu"
            objects.append(Button((430, 420), (320, 80), btn_text, action_id="CHOICE_RIGHT"))

        objects.append(
            Button(
                (754, 10), (36, 36),
                text="",
                icon_path="assets/icons/info.png",
                icon_size=35,
                action_id="INFO_MENU",
            )
        )

        self.view.setSceneObjects(objects)

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

        # Check for new level (or restart of Level 1)
        # Se il livello cambia o se si torna al livello 1 venendo da un livello superiore (riavvio)
        if next_s.level > self.session.last_viewed_level or (next_s.level == 1 and self.session.last_viewed_level > 1):
            self.session.updateCurrentScelta(next_s.key)
            self.session.switchTurn(forced_turn=next_s.turn)
            self.is_saved = False
            self.showLevelIntro(next_s.level)
            return

        self.session.updateCurrentScelta(next_s.key)
        # Applichiamo il turno indicato dal nuovo nodo
        self.session.switchTurn(forced_turn=next_s.turn)
        self.is_saved = False # Segniamo come non salvato al momento di prendere una decisione
        
        # Se è un finale, lo salviamo nella lista globale dei sbloccati
        if next_s.is_end:
            self.save_data = self.fileManager.loadSaves()
            if "unlocked_endings" not in self.save_data:
                self.save_data["unlocked_endings"] = []
            if next_s.key not in self.save_data["unlocked_endings"]:
                self.save_data["unlocked_endings"].append(next_s.key)
                self.fileManager.saveFile("saves.json", self.save_data)

        self.updateView()

    # =====================
    # EVENTI
    # =====================
    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if not self.is_saved and self.view.current_scene in ("GAME", "INFO"):
                    self.showExitConfirm()
                else:
                    self.running = False

            if event.type == pygame.KEYDOWN:
                if self.view.current_scene == "NAMING":
                    if event.key == pygame.K_RETURN:
                        if self.temp_name.strip():
                            self.saveGame()
                    elif event.key == pygame.K_BACKSPACE:
                        self.temp_name = self.temp_name[:-1]
                        self.showNamingScreen()
                    else:
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
                            self.showEndingsMenu()
                            continue

                        if action == "GALLERY_NEXT":
                            self.gallery_page += 1
                            self.showEndingsMenu()
                            continue

                        if action == "GALLERY_PREV":
                            self.gallery_page -= 1
                            self.showEndingsMenu()
                            continue

                        if action == "INFO_SAVE":
                            self.quit_after_save = False
                            self.showSaveSlots()
                            continue

                        if action == "EXIT_SAVE_QUIT":
                            self.quit_after_save = True
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
                            self.loadGame(slot)
                            continue

                        if action == "LEVEL_CONTINUE":
                            self.view.setScene("GAME")
                            self.updateView()
                            continue

                        if action == "EXIT_YES":
                            self.running = False
                            continue

                        if action == "EXIT_NO":
                            self.quit_after_save = False
                            self.view.setScene("GAME")
                            self.updateView()
                            continue

                        if action == "EXIT_BACK":
                            self.quit_after_save = False
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

                    # Logica classica per MENU/LOAD/GAME (testo)
                    if self.view.current_scene == "MENU":
                        if "New Game" in msg:
                            self.readGameFile()
                            self.is_saved = True # La nuova partita inizia come "salvata" (senza modifiche)
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
                        pass # Gestito da ACTION:CHOICE_LEFT/RIGHT sopra

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
