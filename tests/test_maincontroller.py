import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import sys
from model import Character, Scelta, ScelteCollection, GameSession, FileManager, SingletonMeta
from controller import MainController

class TestMainController(unittest.TestCase):

    def setUp(self):
        """
        # Configuración inicial para cada test.
        # Reseteamos el singleton FileManager y mockeamos pygame.
        """
        SingletonMeta._instances = {}
        
        # Mock de pygame para evitar inicialización
        self.pygame_mock = MagicMock()
        self.pygame_mock.QUIT = 256
        self.pygame_mock.MOUSEBUTTONDOWN = 1025
        self.pygame_mock.time.Clock.return_value.tick = MagicMock()
        self.pygame_mock.event.get.return_value = []
        
        # Mock de la vista
        self.view_mock = MagicMock()
        self.view_mock.root = MagicMock()
        self.view_mock.root.children = []
        self.view_mock.root.checkClick = MagicMock(return_value=[])
        self.view_mock.initScreen = MagicMock()
        self.view_mock.render = MagicMock()
        self.view_mock.linksToSubsystemObjects = MagicMock()
        self.view_mock.checkClick = MagicMock(return_value=[])
        
        # Configuramos mocks básicos
        with patch('controller.pygame', self.pygame_mock):
            with patch('controller.GameView', return_value=self.view_mock):
                self.controller = MainController()

    def test_initialization(self):
        """
        # Test: Verifica la inicialización del MainController.
        # Debe crear instancias de FileManager, GameView y establecer valores por defecto.
        """
        with patch('controller.pygame', MagicMock()):
            with patch('controller.GameView', return_value=MagicMock()):
                controller = MainController()
                
                self.assertIsNotNone(controller.fileManager)
                self.assertIsNotNone(controller.view)
                self.assertIsNone(controller.session)
                self.assertIsNone(controller.iterator)
                self.assertFalse(controller.running)

    def test_parseScelteData(self):
        """
        # Test: Verifica que parseScelteData convierte correctamente un diccionario
        # en una ScelteCollection.
        """
        scelta_data = {
            "0": {
                "text": "Inizio",
                "nextRight": [([], "1")],
                "nextLeft": [([], "2")],
                "rightText": "Vai a destra",
                "leftText": "Vai a sinistra",
                "rightObjects": ["chiave"],
                "leftObjects": []
            },
            "1": {
                "text": "Stanza 1",
                "nextRight": [],
                "nextLeft": [],
                "rightText": "",
                "leftText": "",
                "rightObjects": [],
                "leftObjects": []
            }
        }
        
        result = self.controller.parseScelteData(scelta_data)
        
        self.assertIsInstance(result, ScelteCollection)
        scelta_0 = result.__getScelta__("0")
        self.assertEqual(scelta_0.text, "Inizio")
        self.assertEqual(scelta_0.rightText, "Vai a destra")
        self.assertEqual(scelta_0.leftText, "Vai a sinistra")

    def test_parseScelteData_with_missing_fields(self):
        """
        # Test: Verifica que parseScelteData maneja campos faltantes usando valores por defecto.
        """
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
        """
        # Test: Verifica que parseCharactersData convierte correctamente un diccionario
        # en una lista de Character.
        """
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
        self.assertEqual(result[1].id, 1)
        self.assertEqual(result[1].nickname, "Altair")

    def test_parseCharactersData_with_default_nickname(self):
        """
        # Test: Verifica que parseCharactersData genera un nickname por defecto
        # cuando no se proporciona uno.
        """
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
        """
        # Test: Verifica que parseCharactersData maneja correctamente
        # personajes sin habilidades.
        """
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
        """
        # Test: Verifica que readGameFile carga correctamente un archivo de juego válido.
        """
        mock_data = {
            "nodes": {
                "0": {
                    "text": "Inizio",
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
        
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            self.controller.readGameFile("test.json")
            
            self.assertIsNotNone(self.controller.session)
            self.assertIsInstance(self.controller.session, GameSession)
            self.assertIsNotNone(self.controller.iterator)

    def test_readGameFile_file_not_found(self):
        """
        # Test: Verifica que readGameFile maneja correctamente cuando el archivo no existe.
        # Debe terminar el programa con sys.exit(1).
        """
        # Necesitamos mockear el fileManager.loadFile para que lance FileNotFoundError
        with patch.object(self.controller.fileManager, 'loadFile', side_effect=FileNotFoundError("File not found")):
            with patch('controller.sys.exit', side_effect=SystemExit) as mock_exit:
                # sys.exit(1) debería lanzar SystemExit
                with self.assertRaises(SystemExit):
                    self.controller.readGameFile("nonexistent.json")
                mock_exit.assert_called_once_with(1)

    def test_readGameFile_invalid_data(self):
        """
        # Test: Verifica que readGameFile lanza ValueError cuando los datos no son válidos.
        """
        mock_data = {
            "nodes": {},
            "characters": {}
        }
        mock_file_content = json.dumps(mock_data)
        
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            with self.assertRaises(ValueError):
                self.controller.readGameFile("test.json")

    def test_readGameFile_default_filename(self):
        """
        # Test: Verifica que readGameFile usa "storia.json" como nombre de archivo por defecto.
        """
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

    def test_updateView_without_session(self):
        """
        # Test: Verifica que updateView no hace nada si no hay sesión.
        """
        self.controller.session = None
        self.controller.updateView()
        
        # No debe lanzar excepciones
        self.assertIsNone(self.controller.session)

    def test_updateView_with_exit_scelta(self):
        """
        # Test: Verifica que updateView no actualiza la vista si currentSceltaId es "EXIT".
        """
        # Creamos una sesión mock
        mock_session = MagicMock()
        mock_session.currentSceltaId = "EXIT"
        self.controller.session = mock_session
        
        initial_children_count = len(self.view_mock.root.children) if hasattr(self.view_mock.root, 'children') else 0
        self.controller.updateView()
        
        # No debe cambiar la vista
        self.assertEqual(mock_session.currentSceltaId, "EXIT")

    def test_updateView_normal_flow(self):
        """
        # Test: Verifica que updateView actualiza correctamente la vista con los datos de la sesión.
        """
        # Configuramos datos de prueba
        scelta = Scelta(
            key="0",
            text="Test text",
            nextRight=[],
            nextLeft=[],
            rightText="Right",
            leftText="Left",
            rightObjects=[],
            leftObjects=[]
        )
        
        character = Character(id=0, nickname="TestPlayer", abilities=["Ability1"])
        
        scelte_collection = ScelteCollection({"0": scelta})
        mock_session = GameSession(
            scelteCollection=scelte_collection,
            characters=[character],
            currentSceltaId="0"
        )
        
        self.controller.session = mock_session
        
        # Mock del root de la vista
        self.view_mock.root.children = []
        self.view_mock.root.checkClick = MagicMock(return_value=[])
        
        self.controller.updateView()
        
        # Verificamos que se llamó a linksToSubsystemObjects
        self.view_mock.linksToSubsystemObjects.assert_called_once()

    def test_nextScelta_left_direction(self):
        """
        # Test: Verifica que nextScelta navega correctamente a la izquierda.
        """
        # Configuramos escenario de prueba
        scelta_0 = Scelta(
            key="0",
            text="Inizio",
            nextLeft=[([], "1")],
            nextRight=[],
            rightText="",
            leftText="Vai a sinistra",
            leftObjects=[],
            rightObjects=[]
        )
        
        scelta_1 = Scelta(
            key="1",
            text="Stanza 1",
            nextLeft=[],
            nextRight=[],
            rightText="",
            leftText="",
            leftObjects=[],
            rightObjects=[]
        )
        
        character = Character(id=0, nickname="Test", abilities=[])
        scelte_collection = ScelteCollection({"0": scelta_0, "1": scelta_1})
        session = GameSession(
            scelteCollection=scelte_collection,
            characters=[character],
            currentSceltaId="0"
        )
        
        self.controller.session = session
        self.controller.iterator = iter(scelte_collection)
        self.controller.updateView = MagicMock()
        
        self.controller.nextScelta("left")
        
        # Verificamos que se actualizó la scelta actual
        self.assertEqual(self.controller.session.currentSceltaId, "1")
        # Verificamos que se actualizó la vista
        self.controller.updateView.assert_called_once()

    def test_nextScelta_right_direction(self):
        """
        # Test: Verifica que nextScelta navega correctamente a la derecha.
        """
        scelta_0 = Scelta(
            key="0",
            text="Inizio",
            nextLeft=[],
            nextRight=[([], "2")],
            rightText="Vai a destra",
            leftText="",
            leftObjects=[],
            rightObjects=[]
        )
        
        scelta_2 = Scelta(
            key="2",
            text="Stanza 2",
            nextLeft=[],
            nextRight=[],
            rightText="",
            leftText="",
            leftObjects=[],
            rightObjects=[]
        )
        
        character = Character(id=0, nickname="Test", abilities=[])
        scelte_collection = ScelteCollection({"0": scelta_0, "2": scelta_2})
        session = GameSession(
            scelteCollection=scelte_collection,
            characters=[character],
            currentSceltaId="0"
        )
        
        self.controller.session = session
        self.controller.iterator = iter(scelte_collection)
        self.controller.updateView = MagicMock()
        
        self.controller.nextScelta("right")
        
        self.assertEqual(self.controller.session.currentSceltaId, "2")
        self.controller.updateView.assert_called_once()

    def test_nextScelta_exit_scelta(self):
        """
        # Test: Verifica que nextScelta detiene el juego cuando llega a "EXIT".
        """
        scelta_0 = Scelta(
            key="0",
            text="Inizio",
            nextLeft=[([], "EXIT")],
            nextRight=[],
            rightText="",
            leftText="Exit",
            leftObjects=[],
            rightObjects=[]
        )
        
        scelta_exit = Scelta(
            key="EXIT",
            text="Game Over",
            nextLeft=[],
            nextRight=[],
            rightText="",
            leftText="",
            leftObjects=[],
            rightObjects=[]
        )
        
        character = Character(id=0, nickname="Test", abilities=[])
        scelte_collection = ScelteCollection({"0": scelta_0, "EXIT": scelta_exit})
        session = GameSession(
            scelteCollection=scelte_collection,
            characters=[character],
            currentSceltaId="0"
        )
        
        self.controller.session = session
        self.controller.iterator = iter(scelte_collection)
        self.controller.updateView = MagicMock()
        self.controller.running = True
        
        self.controller.nextScelta("left")
        
        # Verificamos que el juego se detuvo
        self.assertFalse(self.controller.running)

    def test_nextScelta_value_error(self):
        """
        # Test: Verifica que nextScelta maneja correctamente ValueError
        # cuando no se pueden cumplir los requisitos.
        """
        scelta_0 = Scelta(
            key="0",
            text="Inizio",
            nextLeft=[],
            nextRight=[(["chiave"], "2")],  # Requiere "chiave"
            rightText="Vai",
            leftText="",
            leftObjects=[],
            rightObjects=[]
        )
        
        character = Character(id=0, nickname="Test", abilities=[])  # Sin "chiave"
        scelte_collection = ScelteCollection({"0": scelta_0})
        session = GameSession(
            scelteCollection=scelte_collection,
            characters=[character],
            currentSceltaId="0"
        )
        
        self.controller.session = session
        self.controller.iterator = iter(scelte_collection)
        
        # No debe lanzar excepción, solo imprimir mensaje
        self.controller.nextScelta("right")
        
        # La scelta actual no debe cambiar
        self.assertEqual(self.controller.session.currentSceltaId, "0")

    def test_nextScelta_updates_abilities(self):
        """
        # Test: Verifica que nextScelta actualiza las habilidades del jugador
        # cuando se obtienen objetos.
        """
        scelta_0 = Scelta(
            key="0",
            text="Inizio",
            nextLeft=[([], "1")],
            nextRight=[],
            rightText="",
            leftText="Vai",
            leftObjects=["chiave"],  # Otorga "chiave"
            rightObjects=[]
        )
        
        scelta_1 = Scelta(
            key="1",
            text="Stanza 1",
            nextLeft=[],
            nextRight=[],
            rightText="",
            leftText="",
            leftObjects=[],
            rightObjects=[]
        )
        
        character = Character(id=0, nickname="Test", abilities=[])
        scelte_collection = ScelteCollection({"0": scelta_0, "1": scelta_1})
        session = GameSession(
            scelteCollection=scelte_collection,
            characters=[character],
            currentSceltaId="0"
        )
        
        self.controller.session = session
        self.controller.iterator = iter(scelte_collection)
        self.controller.updateView = MagicMock()
        
        self.controller.nextScelta("left")
        
        # Verificamos que se agregó la habilidad
        self.assertIn("chiave", character.abilities)

    def test_handleEvents_quit_event(self):
        """
        # Test: Verifica que handleEvents detiene el juego cuando se recibe el evento QUIT.
        """
        # Mock de eventos pygame
        mock_event_quit = MagicMock()
        mock_event_quit.type = 256  # Valor de pygame.QUIT
        
        with patch('controller.pygame.event.get', return_value=[mock_event_quit]):
            self.controller.running = True
            self.controller.handleEvents()
            self.assertFalse(self.controller.running)

    def test_handleEvents_mouse_click_left(self):
        """
        # Test: Verifica que handleEvents procesa correctamente un clic del mouse
        # en el botón izquierdo.
        """
        scelta = Scelta(
            key="0",
            text="Test",
            nextLeft=[([], "1")],
            nextRight=[],
            rightText="",
            leftText="Left Button",
            leftObjects=[],
            rightObjects=[]
        )
        
        scelta_1 = Scelta(
            key="1",
            text="Test 1",
            nextLeft=[],
            nextRight=[],
            rightText="",
            leftText="",
            leftObjects=[],
            rightObjects=[]
        )
        
        character = Character(id=0, nickname="Test", abilities=[])
        scelte_collection = ScelteCollection({"0": scelta, "1": scelta_1})
        session = GameSession(
            scelteCollection=scelte_collection,
            characters=[character],
            currentSceltaId="0"
        )
        
        self.controller.session = session
        self.controller.iterator = iter(scelte_collection)
        self.controller.nextScelta = MagicMock()
        self.view_mock.checkClick.return_value = ["Left Button clicked"]
        
        mock_event_click = MagicMock()
        mock_event_click.type = 1025  # Valor de pygame.MOUSEBUTTONDOWN
        mock_event_click.pos = (100, 100)
        
        with patch('controller.pygame.event.get', return_value=[mock_event_click]):
            self.controller.handleEvents()
            self.controller.nextScelta.assert_called_once_with("left")

    def test_handleEvents_mouse_click_right(self):
        """
        # Test: Verifica que handleEvents procesa correctamente un clic del mouse
        # en el botón derecho.
        """
        scelta = Scelta(
            key="0",
            text="Test",
            nextLeft=[],
            nextRight=[([], "2")],
            rightText="Right Button",
            leftText="Left Button",  # No puede estar vacío porque "" in cualquier string es True
            leftObjects=[],
            rightObjects=[]
        )
        
        scelta_2 = Scelta(
            key="2",
            text="Test 2",
            nextLeft=[],
            nextRight=[],
            rightText="",
            leftText="",
            leftObjects=[],
            rightObjects=[]
        )
        
        character = Character(id=0, nickname="Test", abilities=[])
        scelte_collection = ScelteCollection({"0": scelta, "2": scelta_2})
        session = GameSession(
            scelteCollection=scelte_collection,
            characters=[character],
            currentSceltaId="0"
        )
        
        self.controller.session = session
        self.controller.nextScelta = MagicMock()
        self.view_mock.checkClick.return_value = ["Right Button clicked"]
        
        mock_event_click = MagicMock()
        mock_event_click.type = 1025  # Valor de pygame.MOUSEBUTTONDOWN
        mock_event_click.pos = (500, 400)
        
        with patch('controller.pygame.event.get', return_value=[mock_event_click]):
            self.controller.handleEvents()
            self.controller.nextScelta.assert_called_once_with("right")

    def test_handleEvents_exit_scelta_click(self):
        """
        # Test: Verifica que handleEvents no procesa clics cuando currentSceltaId es "EXIT".
        """
        scelta = Scelta(
            key="EXIT",
            text="Game Over",
            nextLeft=[],
            nextRight=[],
            rightText="",
            leftText="",
            leftObjects=[],
            rightObjects=[]
        )
        
        character = Character(id=0, nickname="Test", abilities=[])
        scelte_collection = ScelteCollection({"EXIT": scelta})
        session = GameSession(
            scelteCollection=scelte_collection,
            characters=[character],
            currentSceltaId="EXIT"
        )
        
        self.controller.session = session
        self.controller.nextScelta = MagicMock()
        self.view_mock.checkClick.return_value = ["Any button"]
        
        mock_event_click = MagicMock()
        mock_event_click.type = 1025  # Valor de pygame.MOUSEBUTTONDOWN
        mock_event_click.pos = (100, 100)
        
        with patch('controller.pygame.event.get', return_value=[mock_event_click]):
            self.controller.handleEvents()
            # No debe llamar a nextScelta cuando está en EXIT
            self.controller.nextScelta.assert_not_called()

    def test_gameLoop_initialization(self):
        """
        # Test: Verifica que gameLoop inicializa correctamente los componentes.
        """
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
        
        # Mock de clock
        mock_clock = MagicMock()
        mock_clock.tick = MagicMock()
        
        # Mock de eventos para terminar el loop inmediatamente
        mock_event_empty = MagicMock()
        mock_event_empty.type = None
        
        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            with patch('sys.exit'):
                with patch('controller.pygame.time.Clock', return_value=mock_clock):
                    with patch('controller.pygame.event.get', return_value=[mock_event_empty]):
                        # Hacemos que running sea False después de la primera iteración
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
                        
                        # Verificamos que se inicializó la pantalla y se cargó el archivo
                        self.view_mock.initScreen.assert_called_once()
                        self.assertIsNotNone(self.controller.session)

if __name__ == '__main__':
    unittest.main()
