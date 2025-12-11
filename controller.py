import pygame
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

    def parseScelteData(self, sceltaData: dict) -> ScelteCollection:
        scelte = {}
        for key, data in sceltaData.items():
            scelta = Scelta(
                key=key,
                text=data.get("text", ""),
                nextRight=data.get("nextRight", []),
                nextLeft=data.get("nextLeft", []),
                rightText=data.get("rightText", ""),
                leftText=data.get("leftText", ""),
                rightObjects=data.get("rightObjects", []),
                leftObjects=data.get("leftObjects", [])
            )
            scelte[key] = scelta
        return ScelteCollection(scelte)

    def parseCharactersData(self, charactersData: dict) -> list[Character]:
        characters = []
        for char_id_str in charactersData:
            data = charactersData[char_id_str]
            char_id = int(char_id_str)
            abilities = data.get("abilities", [])
            nickname = data.get("nickname", f"Player {char_id}")
            characters.append(Character(char_id, nickname, abilities))
        return characters

    def readGameFile(self, fileName: str = "storia.json"):
        try:
            scelteData, charactersData = self.fileManager.loadFile(fileName)
        except Exception as e:
            print(f"Errore fatale durante il caricamento del file: {e}")
            sys.exit(1)

        if not scelteData or not charactersData:
            raise ValueError("Errore: Dati del file di gioco non validi.")

        scelteCollection = self.parseScelteData(scelteData)
        characters =       self.parseCharactersData(charactersData)

        self.session = GameSession(scelteCollection, characters)
        self.iterator = iter(scelteCollection)

    def updateView(self):
        if not self.session:
            return

        # Controllo di sicurezza: se la sessione è su EXIT, non renderizzare nulla
        if self.session.currentSceltaId == "EXIT":
            return

        current_scelta = self.session.scelteCollection.__getScelta__(self.session.currentSceltaId)
        current_player = self.session.getCurrentPlayer()
        
        self.view.root.children = [] 
        objects_to_render = []
        
        story_text = Text((50, 50), current_scelta.text, color=(255, 255, 255))
        objects_to_render.append(story_text)
        
        player_info = Text((50, 10), f"Turno di: {current_player.nickname} | Abilità: {current_player.abilities}", color=(200, 200, 0))
        objects_to_render.append(player_info)
        
        if current_scelta.leftText:
            btn_left = Button((50, 400), (300, 50), text=current_scelta.leftText)
            objects_to_render.append(btn_left)
        
        if current_scelta.rightText:
            btn_right = Button((450, 400), (300, 50), text=current_scelta.rightText)
            objects_to_render.append(btn_right)

        self.view.linksToSubsystemObjects(objects_to_render)

    def nextScelta(self, direction):
        current_player = self.session.getCurrentPlayer()
        current_scelta_obj = self.session.scelteCollection.__getScelta__(self.session.currentSceltaId)
        
        self.iterator._position = self.session.currentSceltaId

        try:
            next_scelta_obj = None

            if direction == "left":
                if current_scelta_obj.leftObjects:
                    print(f"Obtido: {current_scelta_obj.leftObjects}")
                    current_player.updateAbilities(current_scelta_obj.leftObjects)
                next_scelta_obj = self.iterator.getLeft(current_player.abilities)
            elif direction == "right":
                if current_scelta_obj.rightObjects:
                    print(f"Obtido: {current_scelta_obj.rightObjects}")
                    current_player.updateAbilities(current_scelta_obj.rightObjects)
                next_scelta_obj = self.iterator.getRight(current_player.abilities)
            
            if next_scelta_obj:
                print(f"Avanzando a: {next_scelta_obj.key}")
                
                if next_scelta_obj.key == "EXIT":
                    print("GAME OVER / VITTORIA - Chiusura gioco...")
                    self.running = False
                    return

                self.session.updateCurrentScelta(next_scelta_obj.key)
                self.session.switchTurn()
                self.updateView()

        except ValueError as e:
            print(f"Azione non consentita: {e}")

    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                click_messages = self.view.checkClick(event.pos)
                
                # Controllo per evitare crash se si clicca dopo la fine
                if self.session.currentSceltaId == "EXIT":
                    return

                current_scelta = self.session.scelteCollection.__getScelta__(self.session.currentSceltaId)
                
                for msg in click_messages:
                    if current_scelta.leftText in msg:
                        self.nextScelta("left")
                    elif current_scelta.rightText in msg:
                        self.nextScelta("right")

    def gameLoop(self):
        self.view.initScreen() 
        self.readGameFile()    
        self.updateView()      
        
        self.running = True
        clock = pygame.time.Clock()

        while self.running:
            self.handleEvents() 
            self.view.render()  
            clock.tick(60)      

        pygame.quit()
        sys.exit()

