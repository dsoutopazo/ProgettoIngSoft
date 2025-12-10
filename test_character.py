import unittest
from model import Character 

class TestCharacter(unittest.TestCase):

    def test_full_initialization(self):
        """
        # Test: Verifica l'inizializzazione di un personaggio con tutti i parametri.
        # Controlla che id, nickname e abilità siano impostati correttamente.
        """
        char = Character(id=1, nickname="Aragorn", abilities=["Spada", "Sopravvivenza"])
        self.assertEqual(char.id, 1)
        self.assertEqual(char.nickname, "Aragorn")
        self.assertListEqual(char.abilities, ["Spada", "Sopravvivenza"])

    def test_initialization_with_default_nickname(self):
        """
        # Test: Verifica l'inizializzazione solo con un ID.
        # Il nickname dovrebbe essere generato automaticamente come "Player {id}".
        # NOTA: Questo test fallirà con il codice originale a causa di un bug.
        """
        char = Character(id=5)
        self.assertEqual(char.id, 5)
        # Il codice originale ha un bug e non assegna il nickname di default.
        # Dopo la correzione, questo test passerà.
        self.assertEqual(char.nickname, "Player 5")
        self.assertListEqual(char.abilities, [])

    def test_initialization_with_default_abilities(self):
        """
        # Test: Verifica l'inizializzazione senza una lista di abilità.
        # L'attributo 'abilities' dovrebbe essere una lista vuota.
        """
        char = Character(id=2, nickname="Legolas")
        self.assertIsInstance(char.abilities, list)
        self.assertEqual(len(char.abilities), 0)

    def test_updateAbilities_add_new_abilities(self):
        """
        # Test: Aggiunta di nuove abilità a una lista vuota.
        """
        char = Character(id=3, nickname="Gimli", abilities=[])
        new_abilities = ["Ascia", "Barba lunga"]
        char.updateAbilities(new_abilities)
        # A causa del bug, la lista sarà ["Ascia", "Barba lunga", "Ascia", "Barba lunga"]
        # Ci aspettiamo che il test fallisca per evidenziare il problema.
        self.assertCountEqual(char.abilities, ["Ascia", "Barba lunga"], "Le abilità non sono state aggiunte correttamente.")

    def test_updateAbilities_add_only_existing(self):
        """
        # Test: Tentativo di aggiungere abilità che sono già presenti.
        # La lista di abilità del personaggio non dovrebbe cambiare.
        """
        initial_abilities = ["Furtività", "Arco"]
        char = Character(id=7, nickname="Frodo", abilities=initial_abilities.copy())
        # Qui il bug non si manifesta perché nessuna abilità è nuova,
        # quindi la condizione nell'if non è mai vera.
        char.updateAbilities(["Arco"])
        self.assertCountEqual(char.abilities, initial_abilities, "La lista di abilità è cambiata inaspettatamente.")


if __name__ == '__main__':
    unittest.main()