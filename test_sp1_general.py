import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Rimossa la modifica globale a sys.modules che causava conflitti
# sys.modules["pygame"] = mock_pygame 

from controller import MainController
from model import Scelta, ScelteCollection, Character, GameSession
import view
import controller

class TestSprint1Story(unittest.TestCase):

    def setUp(self):
        # Patching di pygame nei moduli dove viene usato
        self.view_pygame_patcher = patch('view.pygame')
        self.controller_pygame_patcher = patch('controller.pygame')
        
        self.mock_view_pygame = self.view_pygame_patcher.start()
        self.mock_controller_pygame = self.controller_pygame_patcher.start()
        
        # Configurazione comune dei mock
        for mock_pg in [self.mock_view_pygame, self.mock_controller_pygame]:
            mock_pg.mouse.get_pos.return_value = (0, 0)
            mock_pg.display.set_mode.return_value = MagicMock()
            mock_pg.event.get.return_value = []
            
            # Creazione di un mock font riutilizzabile
            mock_font = MagicMock()
            mock_font.size.return_value = (100, 30)
            mock_font.render.return_value = MagicMock()
            
            mock_pg.font.Font.return_value = mock_font
            mock_pg.font.SysFont.return_value = mock_font

        with patch('controller.FileManager') as MockFileManager:
            self.mock_fm = MockFileManager.return_value
            self.mock_fm.loadSaves.return_value = {}
            self.controller = MainController()
            self.controller.view = MagicMock() # Mockiamo la view intera per evitare render reale se possibile, ma il test usa view reale?
            # nota: il test test_visualize_options ispeziona self.controller.view.scneneObjects...
            # Se MainController istanzia GameView reale, questa userà il pygame mockato.
            # Ma qui sovrascriviamo self.controller.view = MagicMock(). 
            # Se il test si aspetta una view reale, dobbiamo non sovrascriverla o configurare il mock.
            # Ri-leggendo i test successivi:
            # test_visualize_options usa self.controller.view.setSceneObjects.call_args 
            # quindi si aspetta che self.controller.view sia un MOCK.
            self.controller.audio = MagicMock()

    def tearDown(self):
        self.view_pygame_patcher.stop()
        self.controller_pygame_patcher.stop()

    def setup_simple_story(self):
        s0 = Scelta(
            key="0", 
            nextRight=[([], "MOUNTAIN_PATH")],
            nextLeft=[([], "FOREST_PATH")], 
            text="Initial encounter. Choose your path.", 
            rightText="Go Mountain",
            leftText="Go Forest", 
            rightObjects=["SHIELD"],
            leftObjects=["SWORD"],
            level=1
        )
        s_forest = Scelta("FOREST_PATH", [], [], "You are in the forest.", "", "", [], [], level=1)
        s_mountain = Scelta("MOUNTAIN_PATH", [], [], "You are on the mountain.", "", "", [], [], level=1)
        
        collection = ScelteCollection({"0": s0, "FOREST_PATH": s_forest, "MOUNTAIN_PATH": s_mountain})
        char = Character(id=0, nickname="Lulucia", abilities=[])
        char2 = Character(id=1, nickname="Partner", abilities=[])
        
        self.controller.session = GameSession(collection, [char, char2], currentSceltaId="0")
        self.controller.iterator = iter(collection)

    def test_visualize_options(self):
        self.setup_simple_story()
        self.controller.updateView()
        
        args, _ = self.controller.view.setSceneObjects.call_args
        objects = args[0]
        
        button_texts = [obj.text for obj in objects if hasattr(obj, 'text')]
        self.assertIn("Go Forest", button_texts)
        self.assertIn("Go Mountain", button_texts)
        
        action_ids = [obj.action_id for obj in objects if hasattr(obj, 'action_id')]
        self.assertIn("CHOICE_LEFT", action_ids)
        self.assertIn("CHOICE_RIGHT", action_ids)

    def test_click_and_consequences(self):
        self.setup_simple_story()
        
        self.controller.nextScelta("left")
        
        self.assertEqual(self.controller.session.currentSceltaId, "FOREST_PATH")
        self.assertIn("SWORD", self.controller.session.getCurrentPlayer().abilities)

        self.setup_simple_story()
        self.controller.nextScelta("right")
        
        self.assertEqual(self.controller.session.currentSceltaId, "MOUNTAIN_PATH")
        self.assertIn("SHIELD", self.controller.session.getCurrentPlayer().abilities)

if __name__ == "__main__":
    unittest.main()
