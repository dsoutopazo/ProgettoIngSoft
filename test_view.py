
import unittest
from unittest.mock import patch, MagicMock
from view import Screen, RenderObject, Text, Image, Button, GameView

class TestRenderObject(unittest.TestCase):
    """
    Test per la classe base RenderObject (Composite Pattern).
    Non richiede mocking di Pygame poiché gestisce solo logica strutturale.
    """
    
    def test_add_children(self):
        """
        # Test: Verifica che i figli vengano aggiunti correttamente alla lista.
        """
        parent = RenderObject()
        child1 = RenderObject()
        child2 = RenderObject()
        
        parent.addChildren([child1, child2])
        
        self.assertEqual(len(parent.children), 2)
        self.assertIn(child1, parent.children)
        self.assertIn(child2, parent.children)

    def test_render_propagation(self):
        """
        # Test: Verifica che il metodo render venga chiamato ricorsivamente sui figli.
        """
        parent = RenderObject()
        child_mock = MagicMock()
        
        # Aggiungiamo un mock come figlio per vedere se viene chiamato
        parent.children.append(child_mock)
        
        # Simuliamo una surface di pygame
        dummy_surface = MagicMock()
        parent.render(dummy_surface)
        
        child_mock.render.assert_called_once_with(dummy_surface)

    def test_check_click_propagation(self):
        """
        # Test: Verifica che il checkClick raccolga i risultati da tutti i figli.
        """
        parent = RenderObject()
        
        # Creiamo due figli mock con comportamenti diversi
        child1 = MagicMock()
        child1.checkClick.return_value = ["Click 1"]
        
        child2 = MagicMock()
        child2.checkClick.return_value = [] # Nessun click qui
        
        parent.children = [child1, child2]
        
        results = parent.checkClick((100, 100))
        
        self.assertEqual(results, ["Click 1"])
        child1.checkClick.assert_called_with((100, 100))
        child2.checkClick.assert_called_with((100, 100))


class TestGUIElements(unittest.TestCase):
    """
    Test per gli elementi grafici (Screen, Text, Button, Image).
    Questi richiedono il mocking di Pygame.
    """

    def setUp(self):
        # Patchiamo 'view.pygame' per evitare che apra finestre vere o cerchi font/immagini
        self.pygame_patcher = patch('view.pygame')
        self.mock_pygame = self.pygame_patcher.start()
        self.mock_pygame.mouse.get_pos.return_value = (0, 0)
    def tearDown(self):
        self.pygame_patcher.stop()

    def test_screen_initialization(self):
        """
        # Test: Verifica che Screen inizializzi Pygame e crei la finestra con le dimensioni giuste.
        """
        screen = Screen(width=1024, height=768)
        screen.initScreen()
        
        self.mock_pygame.init.assert_called_once()
        self.mock_pygame.display.set_mode.assert_called_once_with((1024, 768))
        self.mock_pygame.display.set_caption.assert_called_with("The adventures of Lulucia")

    def test_text_initialization_and_render(self):
        """
        # Test: Verifica che Text inizializzi i font e faccia il blit sulla superficie.
        """
        # Setup del mock per il font
        mock_font_obj = MagicMock()
        mock_rendered_text = MagicMock()
        mock_font_obj.render.return_value = mock_rendered_text
        self.mock_pygame.font.SysFont.return_value = mock_font_obj
        
        with patch('view.os.path.exists', return_value=False):
            txt = Text((0, 0), "Hello")
        
        # Verifica init
        self.mock_pygame.font.SysFont.assert_called_with("Arial", 32, bold=True)
        
        # Verifica render
        dummy_surface = MagicMock()
        txt.render(dummy_surface)
        
        # Controlla che abbia renderizzato il testo e fatto il blit
        mock_font_obj.render.assert_called_with("Hello", True, (255, 255, 255))
        dummy_surface.blit.assert_called_with(mock_rendered_text, (0, 0))

    def test_image_initialization(self):
        """
        # Test: Verifica che Image carichi l'immagine dal percorso specificato.
        """
        path = "sprite.png"
        img = Image((10, 10), path)
        
        self.mock_pygame.image.load.assert_called_with(path)

    def test_button_interaction_hit(self):
        """
        # Test: Verifica che il bottone rilevi il click quando le coordinate sono dentro il rect.
        """
        # Il costruttore di Button chiama pygame.Rect. Poiché pygame è mockato,
        # self.rect sarà un oggetto MagicMock.
        btn = Button((50, 50), (100, 30), "Click Me")
        
        # Configuriamo il comportamento del mock Rect: collidepoint restituisce True
        btn.rect.collidepoint.return_value = True
        
        result = btn.checkClick((60, 60))
        
        # Verifica
        btn.rect.collidepoint.assert_called_with((60, 60))
        self.assertEqual(result, ["Button 'Click Me' clicked"])

    def test_button_interaction_miss(self):
        """
        # Test: Verifica che il bottone ignori il click quando le coordinate sono fuori.
        """
        btn = Button((50, 50), (100, 30), "Click Me")
        
        # Configuriamo il comportamento del mock Rect: collidepoint restituisce False
        btn.rect.collidepoint.return_value = False
        
        result = btn.checkClick((0, 0))
        
        self.assertEqual(result, [])


class TestGameView(unittest.TestCase):
    """
    Test per la classe Facade GameView.
    """
    
    def setUp(self):
        self.pygame_patcher = patch('view.pygame')
        self.mock_pygame = self.pygame_patcher.start()
        self.mock_pygame.mouse.get_pos.return_value = (0, 0)

    def tearDown(self):
        self.pygame_patcher.stop()

    def test_initialization(self):
        """
        # Test: Verifica che GameView crei Screen e Root.
        """
        gv = GameView()
        self.assertIsInstance(gv.screen, Screen)
        self.assertIsInstance(gv.root, RenderObject)

    def test_setSceneObjects(self):
        """
        # Test: Verifica che gli oggetti vengano passati alla root.
        """
        gv = GameView()
        obj1 = MagicMock()
        
        gv.setSceneObjects([obj1])
        
        self.assertIn(obj1, gv.root.children)

    def test_render_cycle(self):
        """
        # Test: Verifica l'intero ciclo di render (fill, render figli, flip).
        """
        gv = GameView()
        gv.initScreen() 
        gv.menu_bg = None # Assicuriamoci che non usi l'immagine per testare il fill
        
        gv.render()
        
        # Verifica che lo schermo venga pulito
        gv.screen.screen.fill.assert_called_with((20, 20, 20))
        # Verifica flip del buffer
        self.mock_pygame.display.flip.assert_called_once()

    def test_checkClick_delegation(self):
        """
        # Test: Verifica che GameView deleghi il click alla root.
        """
        gv = GameView()
        
        # Sostituiamo la root con un mock per controllare la chiamata
        gv.root = MagicMock()
        gv.root.checkClick.return_value = ["Event"]
        
        res = gv.checkClick((50, 50))
        
        gv.root.checkClick.assert_called_with((50, 50))
        self.assertEqual(res, ["Event"])

if __name__ == '__main__':
    unittest.main()