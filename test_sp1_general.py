import unittest
from unittest.mock import MagicMock, patch
import sys
import os

mock_pygame = MagicMock()
sys.modules["pygame"] = mock_pygame

from controller import MainController
from model import Scelta, ScelteCollection, Character, GameSession

class TestSprint1Story(unittest.TestCase):

    def setUp(self):
        mock_pygame.reset_mock()
        mock_font = MagicMock()
        mock_font.size.return_value = (100, 30)
        mock_pygame.font.Font.return_value = mock_font
        mock_pygame.font.SysFont.return_value = mock_font
        mock_pygame.mouse.get_pos.return_value = (0, 0)

        with patch('controller.FileManager') as MockFileManager:
            self.mock_fm = MockFileManager.return_value
            self.mock_fm.loadSaves.return_value = {}
            self.controller = MainController()
            self.controller.view = MagicMock()
            self.controller.audio = MagicMock()

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
