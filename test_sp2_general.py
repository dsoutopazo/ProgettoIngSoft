import unittest
from unittest.mock import MagicMock, patch, mock_open
import sys
import json

from controller import MainController
from model import Character, GameSession, Scelta, ScelteCollection
import view
import controller

class TestSprint2MenuSaveLoad(unittest.TestCase):

    def setUp(self):
        self.view_pygame_patcher = patch('view.pygame')
        self.controller_pygame_patcher = patch('controller.pygame')
        
        self.mock_view_pygame = self.view_pygame_patcher.start()
        self.mock_controller_pygame = self.controller_pygame_patcher.start()
        
        for mock_pg in [self.mock_view_pygame, self.mock_controller_pygame]:
            mock_pg.mouse.get_pos.return_value = (0, 0)
            mock_pg.display.set_mode.return_value = MagicMock()
            mock_pg.event.get.return_value = []
            
            mock_font = MagicMock()
            mock_font.size.return_value = (100, 30)
            mock_font.render.return_value = MagicMock()
            
            mock_pg.font.Font.return_value = mock_font
            mock_pg.font.SysFont.return_value = mock_font
        
        with patch('controller.FileManager') as MockFileManager:
            self.mock_fm = MockFileManager.return_value
            self.mock_fm.loadSaves.return_value = {"1": {"name": "Test Save", "node": "0"}}
            self.controller = MainController()
            self.controller.view = MagicMock()
            self.controller.audio = MagicMock()
            
    def tearDown(self):
        self.view_pygame_patcher.stop()
        self.controller_pygame_patcher.stop()

    def test_start_menu_visualization(self):
        self.controller.showMainMenu()
        
        args, _ = self.controller.view.setSceneObjects.call_args
        objects = args[0]
        
        button_texts = [obj.text for obj in objects if hasattr(obj, 'text')]
        self.assertIn("New Game", button_texts)
        self.assertIn("Load Game", button_texts)

    def test_save_workflow(self):
        s0 = Scelta("0", [], [], "Start", "", "", [], [])
        collection = ScelteCollection({"0": s0})
        self.controller.session = GameSession(collection, [Character(0, "Hero")], currentSceltaId="0")
        
        self.controller.showSaveSlots()
        self.assertEqual(self.controller.view.setScene.call_args[0][0], "SAVE")
        
        self.controller.selected_slot = 2
        self.controller.temp_name = "Sprint 2 Save"
        
        with patch('model.Character', spec=Character) as MockChar:
            self.controller.session.characters = [MagicMock(abilities=[]), MagicMock(abilities=[])]
            self.controller.saveGame()
        
        self.mock_fm.saveFile.assert_called_once()
        args = self.mock_fm.saveFile.call_args[0]
        self.assertEqual(args[0], "saves.json")
        self.assertEqual(args[1]["2"]["name"], "Sprint 2 Save")

    def test_load_workflow(self):
        self.controller.showLoadMenu()
        
        args, _ = self.controller.view.setSceneObjects.call_args
        objects = args[0]
        slot_buttons = [obj.action_id for obj in objects if hasattr(obj, 'action_id') and "LOAD_SLOT" in str(obj.action_id)]
        self.assertTrue(len(slot_buttons) > 0)

        with patch.object(self.controller, 'readGameFile') as mock_read:
            self.controller.save_data = {
                "1": {
                    "name": "Test Save", 
                    "node": "NODE_X", 
                    "turn": 0, 
                    "p1_abilities": ["POWER"], 
                    "p2_abilities": []
                }
            }
            s_x = Scelta("NODE_X", [], [], "Node X", "", "", [], [], level=1)
            collection = ScelteCollection({"NODE_X": s_x})
            self.controller.session = GameSession(collection, [Character(0), Character(1)], currentSceltaId="0")
            self.controller.iterator = MagicMock()
            
            self.controller.loadGame(1)
            
            self.assertEqual(self.controller.session.currentSceltaId, "NODE_X")
            self.controller.session.characters[0].abilities = ["POWER"]

if __name__ == "__main__":
    unittest.main()
