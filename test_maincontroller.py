import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import sys
from model import Character, Scelta, ScelteCollection, GameSession, FileManager, SingletonMeta
from controller import MainController

class TestMainController(unittest.TestCase):

    def setUp(self):
        """
        # Configurazione iniziale per ogni test.
        # Resettiamo il singleton FileManager e facciamo il mock di pygame e delle classi UI.
        """
        SingletonMeta._instances = {}
        
        # Mock di pygame per evitare l'inizializzazione
        self.pygame_mock = MagicMock()
        self.pygame_mock.QUIT = 256
        self.pygame_mock.MOUSEBUTTONDOWN = 1025
        self.pygame_mock.time.Clock.return_value.tick = MagicMock()
        self.pygame_mock.event.get.return_value = []
        
        # Mock della vista
        self.view_mock = MagicMock()
        self.view_mock.root = MagicMock()
        self.view_mock.root.children = []
        self.view_mock.root.checkClick = MagicMock(return_value=[])
        self.view_mock.initScreen = MagicMock()
        self.view_mock.render = MagicMock()
        self.view_mock.setSceneObjects = MagicMock()
        self.view_mock.checkClick = MagicMock(return_value=[])
        
        # Patchiamo le classi UI usate dal controller per evitare dipendenze da pygame/assets
        self.obj_patchers = [
            patch('controller.Button', MagicMock()),
            patch('controller.Text', MagicMock()),
            patch('controller.Image', MagicMock()),
            patch('controller.MultiLineText', MagicMock()),
            patch('controller.pygame', self.pygame_mock),
            patch('controller.GameView', return_value=self.view_mock)
        ]
        
        for p in self.obj_patchers:
            p.start()
            
        self.controller = MainController()

    def tearDown(self):
        for p in self.obj_patchers:
            p.stop()

    def test_initialization(self):
        # Il setup già crea il controller, ma qui lo ricreiamo per testare l'init pulito
        controller = MainController()
        self.assertIsNotNone(controller.fileManager)
        self.assertIsNotNone(controller.view)
        self.assertIsNone(controller.session)
        self.assertIsNone(controller.iterator)
        self.assertFalse(controller.running)

    def test_parseScelteData(self):
        scelta_data = {
            "0": {
                "text": "Inizio",
                "nextRight": [([], "1")],
                "nextLeft": [([], "2")],
                "rightText": "Vai a destra",
                "leftText": "Vai a sinistra",
                "rightObjects": ["chiave"],
                "leftObjects": [],
                "turn": 0,
                "level": 1
            },
            "1": {
                "text": "Stanza 1",
                "nextRight": [],
                "nextLeft": [],
                "rightText": "",
                "leftText": "",
                "rightObjects": [],
                "leftObjects": [],
                "turn": 0,
                "level": 1
            }
        }
        
        result = self.controller.parseScelteData(scelta_data)
        
        self.assertIsInstance(result, ScelteCollection)
        scelta_0 = result.__getScelta__("0")
        self.assertEqual(scelta_0.text, "Inizio")
        self.assertEqual(scelta_0.rightText, "Vai a destra")
        self.assertEqual(scelta_0.leftText, "Vai a sinistra")

    def test_parseScelteData_with_missing_fields(self):
        scelta_data = {
            "0": {
                "text": "Test"
            }
        }
        
        result = self.controller.parseScelteData(scelta_data)
        scelta = result.__getScelta__("0")
        
        self.assertEqual(scelta.text, "Test")
        self.assertEqual(scelta.rightText, "")
        self.assertEqual(scelta.leftText, "")
        self.assertEqual(scelta.nextRight, [])
        self.assertEqual(scelta.nextLeft, [])

    def test_parseCharactersData(self):
        characters_data = {
            "0": {
                "nickname": "Ezio",
                "abilities": ["Assassinio", "Furtività"]
            },
            "1": {
                "nickname": "Altair",
                "abilities": ["Combattimento"]
            }
        }
        
        result = self.controller.parseCharactersData(characters_data)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].id, 0)
        self.assertEqual(result[0].nickname, "Ezio")
        self.assertListEqual(result[0].abilities, ["Assassinio", "Furtività"])

    def test_parseCharactersData_with_default_nickname(self):
        characters_data = {
            "5": {
                "abilities": ["Magia"]
            }
        }
        
        result = self.controller.parseCharactersData(characters_data)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, 5)
        self.assertEqual(result[0].nickname, "Player 5")

    def test_parseCharactersData_with_empty_abilities(self):
        characters_data = {
            "0": {
                "nickname": "Test",
                "abilities": []
            }
        }
        
        result = self.controller.parseCharactersData(characters_data)
        
        self.assertEqual(len(result), 1)
        self.assertListEqual(result[0].abilities, [])

    def test_readGameFile_success(self):
        mock_data = {
            "nodes": {
                "0": {
                    "text": "Inizio",
                    "nextRight": [],
                    "nextLeft": [],
                    "rightText": "",
                    "leftText": "",
                    "rightObjects": [],
                    "leftObjects": [],
                    "turn": 0,
                    "level": 1
                }
            },
            "characters": {
                "0": {
                    "nickname": "Test",
                    "abilities": []
                }
            }
        }
        mock_file_content = json.dumps(mock_data)
        
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            self.controller.readGameFile("test.json")
            
            self.assertIsNotNone(self.controller.session)
            self.assertIsInstance(self.controller.session, GameSession)
            self.assertIsNotNone(self.controller.iterator)

    def test_readGameFile_file_not_found(self):
        with patch.object(self.controller.fileManager, 'loadFile', side_effect=FileNotFoundError("File not found")):
            with self.assertRaises(FileNotFoundError):
                self.controller.readGameFile("nonexistent.json")



    def test_readGameFile_default_filename(self):
        mock_data = {
            "nodes": {
                "0": {
                    "text": "Test",
                    "nextRight": [],
                    "nextLeft": [],
                    "rightText": "",
                    "leftText": "",
                    "rightObjects": [],
                    "leftObjects": []
                }
            },
            "characters": {
                "0": {
                    "nickname": "Test",
                    "abilities": []
                }
            }
        }
        mock_file_content = json.dumps(mock_data)
        
        with patch('builtins.open', mock_open(read_data=mock_file_content)) as mock_file:
            self.controller.readGameFile()
            mock_file.assert_called_with("storia.json", 'r', encoding='utf-8')

    def test_updateView_with_exit_scelta(self):
        scelta = Scelta(
            key="EXIT", text="Game Over", nextLeft=[], nextRight=[], rightText="", leftText="",
            rightObjects=[], leftObjects=[], turn=0, level=1
        )
        
        character = Character(id=0, nickname="Test", abilities=[])
        scelte_collection = ScelteCollection({"EXIT": scelta})
        mock_session = GameSession(scelteCollection=scelte_collection, characters=[character], currentSceltaId="EXIT")
        
        self.controller.session = mock_session
        self.controller.updateView()
        self.assertEqual(mock_session.currentSceltaId, "EXIT")

    def test_updateView_normal_flow(self):
        scelta = Scelta(
            key="0", text="Test text", nextRight=[], nextLeft=[], rightText="Right", leftText="Left",
            rightObjects=[], leftObjects=[], turn=0, level=1
        )
        
        character = Character(id=0, nickname="TestPlayer", abilities=["Ability1"])
        
        scelte_collection = ScelteCollection({"0": scelta})
        mock_session = GameSession(
            scelteCollection=scelte_collection,
            characters=[character],
            currentSceltaId="0"
        )
        
        self.controller.session = mock_session
        self.view_mock.root.children = []
        self.view_mock.root.checkClick = MagicMock(return_value=[])
        
        self.controller.updateView()
        
        self.view_mock.setSceneObjects.assert_called_once()

    def test_nextScelta_left_direction(self):
        scelta_0 = Scelta(
            key="0", text="Inizio", nextLeft=[([], "1")], nextRight=[], rightText="", leftText="Vai a sinistra",
            rightObjects=[], leftObjects=[], turn=0, level=1
        )
        scelta_1 = Scelta(
            key="1", text="Stanza 1", nextLeft=[], nextRight=[], rightText="", leftText="",
            rightObjects=[], leftObjects=[], turn=0, level=1
        )
        
        character = Character(id=0, nickname="Test", abilities=[])
        scelte_collection = ScelteCollection({"0": scelta_0, "1": scelta_1})
        session = GameSession(scelteCollection=scelte_collection, characters=[character], currentSceltaId="0")
        session.last_viewed_level = 1  # Evita trigger level intro
        
        self.controller.session = session
        self.controller.iterator = iter(scelte_collection)
        self.controller.updateView = MagicMock()
        
        self.controller.nextScelta("left")
        
        self.assertEqual(self.controller.session.currentSceltaId, "1")
        self.controller.updateView.assert_called_once()

    def test_nextScelta_right_direction(self):
        scelta_0 = Scelta(
            key="0", text="Inizio", nextLeft=[], nextRight=[([], "2")], rightText="Vai a destra", leftText="",
            rightObjects=[], leftObjects=[], turn=0, level=1
        )
        scelta_2 = Scelta(
            key="2", text="Stanza 2", nextLeft=[], nextRight=[], rightText="", leftText="",
            rightObjects=[], leftObjects=[], turn=0, level=1
        )
        
        character = Character(id=0, nickname="Test", abilities=[])
        scelte_collection = ScelteCollection({"0": scelta_0, "2": scelta_2})
        session = GameSession(scelteCollection=scelte_collection, characters=[character], currentSceltaId="0")
        session.last_viewed_level = 1
        
        self.controller.session = session
        self.controller.iterator = iter(scelte_collection)
        self.controller.updateView = MagicMock()
        
        self.controller.nextScelta("right")
        
        self.assertEqual(self.controller.session.currentSceltaId, "2")
        self.controller.updateView.assert_called_once()

    def test_nextScelta_exit_scelta(self):
        scelta_0 = Scelta(
            key="0", text="Inizio", nextLeft=[([], "EXIT")], nextRight=[], rightText="", leftText="Exit",
            rightObjects=[], leftObjects=[], turn=0, level=1
        )
        scelta_exit = Scelta(
            key="EXIT", text="Game Over", nextLeft=[], nextRight=[], rightText="", leftText="",
            rightObjects=[], leftObjects=[], turn=0, level=1
        )
        
        character = Character(id=0, nickname="Test", abilities=[])
        scelte_collection = ScelteCollection({"0": scelta_0, "EXIT": scelta_exit})
        session = GameSession(scelteCollection=scelte_collection, characters=[character], currentSceltaId="0")
        
        self.controller.session = session
        self.controller.iterator = iter(scelte_collection)
        self.controller.showMainMenu = MagicMock()
        self.controller.running = True
        
        self.controller.nextScelta("left")
        
        self.controller.showMainMenu.assert_called_once()

    def test_nextScelta_value_error(self):
        scelta_0 = Scelta(
            key="0", text="Inizio", nextLeft=[], nextRight=[(["chiave"], "2")], rightText="Vai", leftText="",
            rightObjects=[], leftObjects=[], turn=0, level=1
        )
        character = Character(id=0, nickname="Test", abilities=[])
        scelte_collection = ScelteCollection({"0": scelta_0})
        session = GameSession(scelteCollection=scelte_collection, characters=[character], currentSceltaId="0")
        
        self.controller.session = session
        self.controller.iterator = iter(scelte_collection)
        # La funzione lancia ValueError se i requisiti non sono soddisfatti
        with self.assertRaises(ValueError):
            self.controller.nextScelta("right")
        # La scelta attuale non deve cambiare (anche se l'eccezione interrompe il flusso prima)
        self.assertEqual(self.controller.session.currentSceltaId, "0")

    def test_nextScelta_updates_abilities(self):
        scelta_0 = Scelta(
            key="0", text="Inizio", nextLeft=[([], "1")], nextRight=[], rightText="", leftText="Vai",
            leftObjects=["chiave"], rightObjects=[], turn=0, level=1
        )
        scelta_1 = Scelta(
            key="1", text="Stanza 1", nextLeft=[], nextRight=[], rightText="", leftText="",
            rightObjects=[], leftObjects=[], turn=0, level=1
        )
        character = Character(id=0, nickname="Test", abilities=[])
        scelte_collection = ScelteCollection({"0": scelta_0, "1": scelta_1})
        session = GameSession(scelteCollection=scelte_collection, characters=[character], currentSceltaId="0")
        session.last_viewed_level = 1
        
        self.controller.session = session
        self.controller.iterator = iter(scelte_collection)
        self.controller.updateView = MagicMock()
        
        self.controller.nextScelta("left")
        
        self.assertIn("chiave", character.abilities)

    def test_handleEvents_quit_event(self):
        mock_event_quit = MagicMock()
        mock_event_quit.type = 256
        
        with patch('controller.pygame.event.get', return_value=[mock_event_quit]):
            self.controller.running = True
            self.controller.handleEvents()
            self.assertFalse(self.controller.running)

    def test_handleEvents_mouse_click_left(self):
        scelta = Scelta(
            key="0", text="Test", nextLeft=[([], "1")], nextRight=[], rightText="", leftText="Left Button",
            rightObjects=[], leftObjects=[], turn=0, level=1
        )
        scelta_1 = Scelta(
            key="1", text="Test 1", nextLeft=[], nextRight=[], rightText="", leftText="",
            rightObjects=[], leftObjects=[], turn=0, level=1
        )
        character = Character(id=0, nickname="Test", abilities=[])
        scelte_collection = ScelteCollection({"0": scelta, "1": scelta_1})
        session = GameSession(scelteCollection=scelte_collection, characters=[character], currentSceltaId="0")
        
        self.controller.session = session
        self.controller.iterator = iter(scelte_collection)
        self.controller.nextScelta = MagicMock()
        self.view_mock.checkClick.return_value = ["ACTION:CHOICE_LEFT"]
        
        mock_event_click = MagicMock()
        mock_event_click.type = 1025
        mock_event_click.pos = (100, 100)
        
        with patch('controller.pygame.event.get', return_value=[mock_event_click]):
            self.controller.handleEvents()
            self.controller.nextScelta.assert_called_once_with("left")

    def test_handleEvents_mouse_click_right(self):
        scelta = Scelta(
            key="0", text="Test", nextLeft=[], nextRight=[([], "2")], rightText="Right Button", leftText="Left Button",
            rightObjects=[], leftObjects=[], turn=0, level=1
        )
        scelta_2 = Scelta(
            key="2", text="Test 2", nextLeft=[], nextRight=[], rightText="", leftText="",
            rightObjects=[], leftObjects=[], turn=0, level=1
        )
        character = Character(id=0, nickname="Test", abilities=[])
        scelte_collection = ScelteCollection({"0": scelta, "2": scelta_2})
        session = GameSession(scelteCollection=scelte_collection, characters=[character], currentSceltaId="0")
        
        self.controller.session = session
        self.controller.nextScelta = MagicMock()
        self.view_mock.checkClick.return_value = ["ACTION:CHOICE_RIGHT"]
        
        mock_event_click = MagicMock()
        mock_event_click.type = 1025
        mock_event_click.pos = (500, 400)
        
        with patch('controller.pygame.event.get', return_value=[mock_event_click]):
            self.controller.handleEvents()
            self.controller.nextScelta.assert_called_once_with("right")

    def test_handleEvents_exit_scelta_click(self):
        scelta = Scelta(
            key="EXIT", text="Game Over", nextLeft=[], nextRight=[], rightText="", leftText="",
            rightObjects=[], leftObjects=[], turn=0, level=1
        )
        character = Character(id=0, nickname="Test", abilities=[])
        scelte_collection = ScelteCollection({"EXIT": scelta})
        session = GameSession(scelteCollection=scelte_collection, characters=[character], currentSceltaId="EXIT")
        
        self.controller.session = session
        self.controller.nextScelta = MagicMock()
        self.view_mock.checkClick.return_value = ["Any button"]
        
        mock_event_click = MagicMock()
        mock_event_click.type = 1025
        mock_event_click.pos = (100, 100)
        
        with patch('controller.pygame.event.get', return_value=[mock_event_click]):
            self.controller.handleEvents()
            self.controller.nextScelta.assert_not_called()

    def test_gameLoop_initialization(self):
        mock_data = {
            "nodes": {
                "0": {
                    "text": "Test",
                    "nextRight": [],
                    "nextLeft": [],
                    "rightText": "",
                    "leftText": "",
                    "rightObjects": [],
                    "leftObjects": [],
                    "turn": 0,
                    "level": 1
                }
            },
            "characters": {
                "0": {
                    "nickname": "Test",
                    "abilities": []
                }
            }
        }
        mock_file_content = json.dumps(mock_data)
        
        mock_clock = MagicMock()
        mock_clock.tick = MagicMock()
        
        mock_event_empty = MagicMock()
        mock_event_empty.type = None
        
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            with patch('sys.exit'):
                with patch('controller.pygame.time.Clock', return_value=mock_clock):
                    with patch('controller.pygame.event.get', return_value=[mock_event_empty]):
                        call_count = [0]
                        def stop_loop():
                            call_count[0] += 1
                            if call_count[0] > 0:
                                self.controller.running = False
                        
                        self.controller.handleEvents = MagicMock(side_effect=stop_loop)
                        
                        try:
                            self.controller.gameLoop()
                        except SystemExit:
                            pass
                        
                        self.view_mock.initScreen.assert_called_once()

if __name__ == '__main__':
    unittest.main()
