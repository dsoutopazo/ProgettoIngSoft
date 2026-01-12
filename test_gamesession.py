import unittest
from model import Character, Scelta, GameSession

class TestGameSession(unittest.TestCase):

    def setUp(self):
        """
        # Definiamo qui i personaggi e una collezione di scelte complesse
        """
        # 1. Creiamo i personaggi per la sessione di test
        self.char1 = Character(id=0, nickname="Ezio")
        self.char2 = Character(id=1, nickname="Altair")
        self.characters = [self.char1, self.char2]

        # 2. Creiamo una collezione di scelte usando il dataclass 'Scelta'
        self.scelte_dict = {
            "0": Scelta(
                key="0",
                text="Sei di fronte a un castello.",
                rightText="Entra dalla porta principale",
                leftText="Cerca un passaggio segreto",
                nextRight=[([], "1_PORTA")], # Se non hai oggetti, vai a "1_PORTA"
                nextLeft=[([], "1_SEGRETO")] # Se non hai oggetti, vai a "1_SEGRETO"
            ),
            "1_PORTA": Scelta(
                key="1_PORTA",
                text="La porta è sorvegliata.",
                rightText="",
                leftText="",
                nextRight=[],
                nextLeft=[]
            )
        }

        # 3. Creiamo l'istanza di GameSession che useremo per i test
        self.session = GameSession(
            scelteCollection=self.scelte_dict,
            characters=self.characters,
            currentPlayerId=0,
            currentSceltaId="0"
        )

    def test_initialization_with_defaults(self):
        """
        # Test: Verifica l'inizializzazione usando i valori di default (ID giocatore e scelta).
        """
        session = GameSession(scelteCollection=self.scelte_dict, characters=self.characters)
        self.assertEqual(session.currentPlayerId, 0, "L'ID del giocatore di default dovrebbe essere 0")
        self.assertEqual(session.currentSceltaId, "0", "L'ID della scelta di default dovrebbe essere '0'")
        self.assertListEqual(session.characters, self.characters)
        self.assertDictEqual(session.scelteCollection, self.scelte_dict)

    def test_initialization_with_specific_values(self):
        """
        # Test: Verifica l'inizializzazione passando valori specifici per gli ID.
        """
        session = GameSession(
            scelteCollection=self.scelte_dict,
            characters=self.characters,
            currentPlayerId=1,
            currentSceltaId="1_PORTA"
        )
        self.assertEqual(session.currentPlayerId, 1)
        self.assertEqual(session.currentSceltaId, "1_PORTA")

    def test_getCurrentPlayer(self):
        """
        # Test: Verifica che il metodo getCurrentPlayer() restituisca il personaggio corretto.
        """
        # All'inizio, il giocatore corrente è il primo (ID 0)
        self.assertIs(self.session.getCurrentPlayer(), self.char1, "Non ha restituito il giocatore corretto all'inizio")

        # Se cambiamo l'ID manualmente, deve restituire il nuovo giocatore corretto
        self.session.currentPlayerId = 1
        self.assertIs(self.session.getCurrentPlayer(), self.char2, "Non ha restituito il giocatore corretto dopo un cambio manuale")

    def test_switchTurn_progression_and_wraparound(self):
        """
        # Test: Verifica che switchTurn() faccia avanzare il turno e torni all'inizio
        # alla fine della lista (effetto 'wrap-around').
        """
        # Il turno iniziale è del giocatore 0
        self.assertEqual(self.session.getCurrentPlayer().nickname, "Ezio")

        # Dopo un cambio, il turno passa al giocatore 1
        self.session.switchTurn()
        self.assertEqual(self.session.currentPlayerId, 1)
        self.assertEqual(self.session.getCurrentPlayer().nickname, "Altair")

        # Dopo un altro cambio, il turno deve tornare al giocatore 0
        self.session.switchTurn()
        self.assertEqual(self.session.currentPlayerId, 0)
        self.assertEqual(self.session.getCurrentPlayer().nickname, "Ezio")

    def test_updateCurrentScelta(self):
        """
        # Test: Verifica che l'ID della scelta corrente venga aggiornato correttamente.
        """
        self.assertEqual(self.session.currentSceltaId, "0")
        
        new_id = "1_PORTA"
        self.session.updateCurrentScelta(new_id)
        
        self.assertEqual(self.session.currentSceltaId, new_id)

    def test_edge_case_get_player_with_no_characters(self):
        """
        # Test di caso limite: cosa succede se si prova a ottenere un giocatore
        # quando la lista dei personaggi è vuota.
        # Ci si aspetta un errore di tipo IndexError.
        """
        session_vuota = GameSession(scelteCollection=self.scelte_dict, characters=[])
        with self.assertRaises(IndexError, msg="Dovrebbe sollevare un IndexError con una lista di personaggi vuota"):
            session_vuota.getCurrentPlayer()

    def test_edge_case_switch_turn_with_no_characters(self):
        """
        # Test di caso limite: cosa succede se si prova a cambiare turno
        # quando la lista dei personaggi è vuota.
        # L'operazione modulo (%) su zero non è definita, quindi ci si aspetta un ZeroDivisionError.
        """
        session_vuota = GameSession(scelteCollection=self.scelte_dict, characters=[])
        with self.assertRaises(ZeroDivisionError, msg="Dovrebbe sollevare un ZeroDivisionError con una lista di personaggi vuota"):
            session_vuota.switchTurn()

if __name__ == '__main__':
    unittest.main()