import unittest
from unittest.mock import MagicMock, patch
import sys

mock_pygame = MagicMock()
sys.modules["pygame"] = mock_pygame

from controller import MainController
from model import Character, GameSession, Scelta, ScelteCollection

class TestSprint3ExitInfoEndings(unittest.TestCase):

    def setUp(self):
        mock_pygame.reset_mock()
        mock_font = MagicMock()
        mock_font.size.return_value = (100, 30)
        mock_pygame.font.Font.return_value = mock_font
        mock_pygame.font.SysFont.return_value = mock_font
        mock_pygame.mouse.get_pos.return_value = (0, 0)
        
        with patch('controller.FileManager') as MockFileManager:
            self.mock_fm = MockFileManager.return_value
            self.mock_fm.loadSaves.return_value = {"unlocked_endings": ["END_1"]}
            self.controller = MainController()
            self.controller.view = MagicMock()
            self.controller.audio = MagicMock()

    def setup_mock_session(self):
        s1 = Scelta("0", [], [], "Start", "", "", [], [], level=1)
        e1 = Scelta("END_1", [], [], "Ending 1", "", "", [], [], is_end=True, level=1, ending_title="The Beginning")
        e2 = Scelta("END_2", [], [], "Ending 2", "", "", [], [], is_end=True, level=2, ending_title="The End")
        collection = ScelteCollection({"0": s1, "END_1": e1, "END_2": e2})
        
        p1 = Character(0, "Lulucia", ["FIRE"])
        p2 = Character(1, "Partner", [])
        self.controller.session = GameSession(collection, [p1, p2], currentSceltaId="0")

    def test_info_menu_status(self):
        self.setup_mock_session()
        self.controller.showInfoMenu()
        
        args, _ = self.controller.view.setSceneObjects.call_args
        objects = args[0]
        
        texts = []
        for obj in objects:
            if hasattr(obj, 'content'):
                texts.append(obj.content)
            elif hasattr(obj, 'text'):
                texts.append(obj.text)
        
        found = any("Lulucia" in t and "FIRE" in t for t in texts)
        self.assertTrue(found, "Character status (ability) not found in Info Menu")

    def test_endings_gallery(self):
        self.setup_mock_session()
        self.controller.save_data = {"unlocked_endings": ["END_1"]}
        
        self.controller.showEndingsMenu()
        
        args, _ = self.controller.view.setSceneObjects.call_args
        objects = args[0]
        
        texts = [obj.content for obj in objects if hasattr(obj, 'content')]
        
        self.assertIn("• The Beginning", texts)
        self.assertIn("• ???????????????", texts)

    def test_exit_confirm_flow(self):
        self.controller.showExitConfirm()
        
        self.assertEqual(self.controller.view.setScene.call_args[0][0], "EXIT_CONFIRM")
        
        args, _ = self.controller.view.setSceneObjects.call_args
        objects = args[0]
        
        button_ids = [obj.action_id for obj in objects if hasattr(obj, 'action_id')]
        self.assertIn("EXIT_YES", button_ids)
        self.assertIn("EXIT_SAVE_QUIT", button_ids)
        self.assertIn("EXIT_BACK", button_ids)

if __name__ == "__main__":
    unittest.main()
