import unittest
from model import Character, Scelta, GameSession

class TestGameSession(unittest.TestCase):

    def setUp(self):
        """
        Configurazione dell'ambiente di test basata sul nuovo formato dati (JSON) dello Sprint 2.
        Simuliamo qui il caricamento dei dati aggiornati (Lulucia, The Avenger, The Agile).
        """
        # 1. Creiamo i personaggi (Aggiornati con i nuovi campi)
        # CORREZIONE: Usiamo 'image_path' invece di 'image' come definito in model.py
        self.char1 = Character(
            id=0, 
            nickname="The Avenger", 
            abilities=[], 
            image_path="assets/characters/p1.png" 
        )
        self.char2 = Character(
            id=1, 
            nickname="The Agile", 
            abilities=[], 
            image_path="assets/characters/p2.png"
        )
        self.characters = [self.char1, self.char2]

        # 2. Creiamo una collezione di scelte (Basata sui nodi del JSON "nodes")
        # Nota: Usiamo argomenti nominali (keyword arguments) per evitare errori di ordine
        self.scelte_dict = {
            "0": Scelta(
                key="0",
                turn=0,
                text="In Lulucia, The Avenger and The Agile seek the ruler...",
                rightText="Give Dragon Fruit",
                leftText="Give Deck of Cards",
                leftObjects=["cards"],
                rightObjects=["dragon_fruit"],
                nextRight=[([], "1_PIT_GUIDED")],
                nextLeft=[([], "1_PIT_ALONE")],
                is_end=False,
                level=1
            ),
            "1_PIT_ALONE": Scelta(
                key="1_PIT_ALONE",
                turn=1,
                text="The Seer refused. You find a big pit...",
                rightText="Tell The Avenger 'I will catch you'",
                leftText="Kick down tree for a bridge",
                leftObjects=["tree_bridge"],
                rightObjects=[],
                nextRight=[([], "FAIL_JUMP")],
                nextLeft=[([], "2_TENTS_P1")],
                is_end=False,
                level=1
            )
        }

        # 3. Creiamo l'istanza di GameSession
        self.session = GameSession(
            scelteCollection=self.scelte_dict,
            characters=self.characters,
            currentPlayerId=0,
            currentSceltaId="0"
        )

    def test_initialization_with_defaults(self):
        """
        Test: Verifica l'inizializzazione usando i nuovi dati di default.
        """
        session = GameSession(scelteCollection=self.scelte_dict, characters=self.characters)
        
        # Verifichiamo ID e Scelta iniziali
        self.assertEqual(session.currentPlayerId, 0, "L'ID del giocatore di default dovrebbe essere 0")
        self.assertEqual(session.currentSceltaId, "0", "L'ID della scelta di default dovrebbe essere '0'")
        
        # Verifichiamo che i personaggi siano corretti (The Avenger, The Agile)
        self.assertEqual(session.characters[0].nickname, "The Avenger")
        self.assertEqual(session.characters[1].nickname, "The Agile")

    def test_initialization_with_specific_values(self):
        """
        Test: Verifica l'inizializzazione in un nodo intermedio (es. 1_PIT_ALONE).
        """
        session = GameSession(
            scelteCollection=self.scelte_dict,
            characters=self.characters,
            currentPlayerId=1,      # Nel nodo 1_PIT_ALONE gioca l'ID 1
            currentSceltaId="1_PIT_ALONE"
        )
        self.assertEqual(session.currentPlayerId, 1)
        self.assertEqual(session.currentSceltaId, "1_PIT_ALONE")
        self.assertEqual(session.getCurrentPlayer().nickname, "The Agile")

    def test_getCurrentPlayer(self):
        """
        Test: Verifica che il metodo getCurrentPlayer() restituisca l'oggetto Character corretto.
        """
        # All'inizio, il giocatore corrente è ID 0 -> The Avenger
        self.assertIs(self.session.getCurrentPlayer(), self.char1)
        self.assertEqual(self.session.getCurrentPlayer().nickname, "The Avenger")

        # Se cambiamo l'ID manualmente a 1 -> The Agile
        self.session.currentPlayerId = 1
        self.assertIs(self.session.getCurrentPlayer(), self.char2)
        self.assertEqual(self.session.getCurrentPlayer().nickname, "The Agile")

    def test_switchTurn_progression_and_wraparound(self):
        """
        Test: Verifica il ciclo standard dei turni (0 -> 1 -> 0).
        """
        # Turno iniziale: 0 (The Avenger)
        self.assertEqual(self.session.currentPlayerId, 0)

        # Primo cambio -> 1 (The Agile)
        self.session.switchTurn()
        self.assertEqual(self.session.currentPlayerId, 1)
        self.assertEqual(self.session.getCurrentPlayer().nickname, "The Agile")

        # Secondo cambio -> 0 (Torna a The Avenger)
        self.session.switchTurn()
        self.assertEqual(self.session.currentPlayerId, 0)
        self.assertEqual(self.session.getCurrentPlayer().nickname, "The Avenger")

    def test_switchTurn_forced(self):
        """
        Test NUOVO: Verifica la funzionalità 'forced_turn'.
        Questo è utile perché la nuova struttura JSON definisce turni fissi per ogni nodo.
        """
        # Siamo a 0. Forziamo il turno a 0 (anche se normalmente andrebbe a 1)
        self.session.switchTurn(forced_turn=0)
        self.assertEqual(self.session.currentPlayerId, 0)

        # Forziamo il turno a 1
        self.session.switchTurn(forced_turn=1)
        self.assertEqual(self.session.currentPlayerId, 1)

    def test_updateCurrentScelta(self):
        """
        Test: Verifica che l'ID della scelta corrente venga aggiornato correttamente.
        """
        self.assertEqual(self.session.currentSceltaId, "0")
        
        new_id = "1_PIT_ALONE"
        self.session.updateCurrentScelta(new_id)
        
        self.assertEqual(self.session.currentSceltaId, new_id)

    def test_edge_case_get_player_with_no_characters(self):
        """
        Test caso limite: Cosa succede se la lista dei personaggi è vuota.
        Ci aspettiamo un IndexError.
        """
        session_vuota = GameSession(scelteCollection=self.scelte_dict, characters=[])
        with self.assertRaises(IndexError):
            session_vuota.getCurrentPlayer()

    def test_edge_case_switch_turn_with_no_characters(self):
        """
        Test caso limite: Cambio turno senza personaggi.
        Ci aspettiamo un ZeroDivisionError (modulo su zero).
        """
        session_vuota = GameSession(scelteCollection=self.scelte_dict, characters=[])
        with self.assertRaises(ZeroDivisionError):
            session_vuota.switchTurn()

if __name__ == '__main__':
    unittest.main()