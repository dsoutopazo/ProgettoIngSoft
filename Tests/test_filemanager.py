
import unittest
import json
from unittest.mock import patch, mock_open
from model import FileManager, SingletonMeta

class TestFileManager(unittest.TestCase):

    def setUp(self):
        """
        # Questo metodo viene eseguito prima di ogni test.
        # Resetta l'istanza singleton per garantire l'isolamento dei test.
        """
        SingletonMeta._instances = {}

    def test_singleton_instance(self):
        """
        # Test per verificare che FileManager sia un singleton.
        # Due istanze dovrebbero essere lo stesso oggetto.
        """
        fm1 = FileManager()
        fm2 = FileManager()
        self.assertIs(fm1, fm2, "FileManager non sta implementando correttamente il pattern Singleton.")

    def test_loadFile_success(self):
        """
        # Test del caricamento di un file JSON valido.
        # Utilizziamo mock_open per simulare l'apertura di un file.
        """
        # Dati di esempio che simulano il contenuto di un file JSON
        mock_data = {
            "nodes":      {"node1": "info1"},
            "characters": {"char1": "info_char1"}
        }
        mock_file_content = json.dumps(mock_data)

        # Usiamo patch per intercettare la chiamata a open
        with patch('builtins.open', mock_open(read_data=mock_file_content)) as mock_file:
            fm = FileManager()
            scelteInfo, charactersInfo = fm.loadFile("dummy_path.json")

            # Verifichiamo che il file sia stato "aperto" nella modalità corretta
            mock_file.assert_called_once_with("dummy_path.json", 'r', encoding='utf-8')

            # Verifichiamo che i dati restituiti siano corretti
            self.assertEqual(scelteInfo, mock_data["nodes"])
            self.assertEqual(charactersInfo, mock_data["characters"])

    def test_loadFile_file_not_found(self):
        """
        # Test per verificare che venga sollevata l'eccezione FileNotFoundError.
        # Simuliamo che il file non esista.
        """
        # Configuriamo il mock per sollevare FileNotFoundError
        with patch('builtins.open', side_effect=FileNotFoundError) as mock_open_file:
            fm = FileManager()

            # Verifichiamo che la chiamata a loadFile sollevi FileNotFoundError
            with self.assertRaises(FileNotFoundError):
                fm.loadFile("non_existent_file.json")

    def test_loadFile_json_decode_error(self):
        """
        # Test per verificare che venga sollevata l'eccezione JSONDecodeError.
        # Simuliamo un contenuto di file JSON non valido.
        """
        invalid_json_content = '{"nodes": {"node1": "info1"}, "characters":'

        with patch('builtins.open', mock_open(read_data=invalid_json_content)):
            fm = FileManager()

            # Verifichiamo che la chiamata a loadFile sollevi JSONDecodeError
            with self.assertRaises(json.JSONDecodeError):
                fm.loadFile("invalid_json.json")

    def test_loadFile_returns_tuple(self):
        """
        # Test per verificare che il metodo loadFile restituisca una tupla.
        """
        mock_data = {
            "nodes": {"node1": "info1"},
            "characters": {"char1": "info_char1"}
        }
        mock_file_content = json.dumps(mock_data)

        with patch('builtins.open', mock_open(read_data=mock_file_content)):
            fm = FileManager()
            result = fm.loadFile("dummy_path.json")

            # Controlliamo se il risultato è una tupla
            self.assertIsInstance(result, tuple, "Il metodo loadFile dovrebbe restituire una tupla.")

if __name__ == '__main__':
    unittest.main()