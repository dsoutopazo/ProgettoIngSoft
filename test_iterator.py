import unittest
from model import Scelta, ScelteCollection, ScelteIterator

class TestScelta(unittest.TestCase):
    """
    Test per la classe Scelta.
    """
    def test_scelta_initialization(self):
        s = Scelta(
            key="0",
            nextRight=[(["chiave"], "2")], 
            nextLeft=[([], "1")],               
            text="Room 0",
            rightText="Go Right",
            leftText="Go Left",
            rightObjects=[],
            leftObjects=[],
            turn=0,
            level=1
        )
        self.assertEqual(s.key, "0")
        self.assertIsInstance(s.nextRight, list)
        self.assertEqual(s.turn, 0)
        self.assertEqual(s.level, 1)

    def test_scelta_equality(self):
        # Initializing with required fields
        s1 = Scelta("1", [], [], "t", "r", "l", [], [])
        s2 = Scelta("2", [], [], "t", "r", "l", [], [])
        self.assertNotEqual(s1, s2)

class TestScelteCollection(unittest.TestCase):
    """
    Test per la classe ScelteCollection.
    """
    def setUp(self):
        self.s1 = Scelta("1", [], [], "Text1", "R", "L", [], [])
        self.s2 = Scelta("2", [], [], "Text2", "R", "L", [], [])
        data = {'1': self.s1, '2': self.s2}
        self.collection = ScelteCollection(data)

    def test_initialization(self):
        self.assertIsInstance(self.collection, ScelteCollection)

    def test_get_scelta_valid(self):
        result = self.collection.__getScelta__('1')
        self.assertEqual(result, self.s1)

    def test_get_scelta_invalid(self):
        # Deve lanciare KeyError se la chiave non esiste
        with self.assertRaises(KeyError):
            self.collection.__getScelta__('999')


class TestScelteIterator(unittest.TestCase):
    """
    Test per la logica di navigazione.
    USIAMO CHIAVI NUMERICHE "0", "1", "2" COME NEL GIOCO REALE.
    """
    def setUp(self):
        # Scenario:
        # "0" (Start) -> Sinistra (libera) -> "1"
        # "0" (Start) -> Destra (richiede 'chiave') -> "2"
        
        self.scelta_1 = Scelta("1", [], [], "Stanza 1", "-", "-", [], [])
        self.scelta_2 = Scelta("2", [], [], "Stanza 2", "-", "-", [], [])
        
        self.scelta_0 = Scelta(
            key="0", # La chiave iniziale OBBLIGATORIA
            nextLeft=[([], "1")],                 
            nextRight=[(["chiave"], "2")],  
            text="Inizio", rightText="Vai a 2", leftText="Vai a 1",
            rightObjects=[],
            leftObjects=[]
        )

        data = {
            "0": self.scelta_0,
            "1": self.scelta_1,
            "2": self.scelta_2
        }
        
        self.collection = ScelteCollection(data)
        self.iterator = ScelteIterator(self.collection)
        # L'iteratore inizierà internamente in "0", il che è corretto ora.

    def test_has_more(self):
        self.assertTrue(self.iterator.hasMore())

    def test_get_left_no_requirements(self):
        inventory = []
        # Siamo in "0", andiamo a sinistra -> "1"
        next_scelta = self.iterator.getLeft(inventory)
        self.assertEqual(next_scelta.key, "1")

    def test_get_right_missing_requirement(self):
        inventory = ["oggetto_errato"]
        # Siamo in "0" (l'iteratore mantiene lo stato), tentiamo di andare a destra senza chiave
        # Il tuo codice deve lanciare ValueError
        with self.assertRaises(ValueError):
             self.iterator.getRight(inventory)

    def test_get_right_met_requirement(self):
        inventory = ["chiave"]
        # Reset dell'iteratore per assicurarsi che siamo in "0"
        self.iterator._position = "0"
        
        next_scelta = self.iterator.getRight(inventory)
        self.assertEqual(next_scelta.key, "2")

if __name__ == '__main__':
    unittest.main()