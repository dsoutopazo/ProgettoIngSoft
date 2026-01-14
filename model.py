
from __future__ import annotations
from collections.abc import Iterable, Iterator
from typing import Any
from dataclasses import dataclass
import json
import os

@dataclass
class Scelta:
    ''' Rappresenta una singola scelta '''
    key:          str  # chiave univoca della scelta
    nextRight:    list[tuple[list[str], str]]  # lista di tuple (oggetti necessari, key della scelta successiva)
    nextLeft:     list[tuple[list[str], str]]  # lista di tuple (oggetti necessari, key della scelta successiva)
    text:         str  # testo della scelta
    rightText:    str  # testo del botone della scelta a destra
    leftText:     str  # testo del botone della scelta a sinistra
    rightObjects: list[str]  # oggetti ottenuti scegliendo a destra
    leftObjects:  list[str]  # oggetti ottenuti scegliendo a sinistra
    turn:         int = 0    # ID do personaxe que ten a quenda
    is_end:       bool = False # Indica se é un final (vitoria/derrota)
    level:        int = 1    # Nivel ao que pertence o nodo
    

class ScelteIterator(Iterator):
    ''' Iteratore per la collezione di scelte '''

    _position: str = "0"
    _reverse: bool = False

    def __init__(self, collection: ScelteCollection):
        self._collection = collection
        self._reverse =    False
        self._position =   "0"

    def getLeft(self, objects: list[str]) -> Scelta:
        '''Restituisce la scelt a a sinistra'''
        options = self._collection.__getScelta__(self._position).nextLeft
        for option in options:
            required_objects, next_key = option
            if all(obj in objects for obj in required_objects):
                self._position = next_key
                if next_key == "EXIT":
                    return Scelta(key="EXIT", nextRight=[], nextLeft=[], text="", rightText="", leftText="", rightObjects=[], leftObjects=[])
                return self._collection.__getScelta__(next_key)
        raise ValueError("The no-objets path is not available for the left of Scelta key " + self._position)

    def getRight(self, objects: list[str]) -> Scelta:
        '''Restituisce la scelta a destra'''
        options = self._collection.__getScelta__(self._position).nextRight
        for option in options:
            required_objects, next_key = option
            if all(obj in objects for obj in required_objects):
                self._position = next_key
                if next_key == "EXIT":
                    return Scelta(key="EXIT", nextRight=[], nextLeft=[], text="", rightText="", leftText="", rightObjects=[], leftObjects=[])
                return self._collection.__getScelta__(next_key)
        raise ValueError("The no-objets path is not available for the right of Scelta key " + self._position)

    def hasMore(self) -> bool:
        '''Restituisce True se ci sono altre scelte da processare'''
        current_scelta = self._collection.__getScelta__(self._position)
        return bool(current_scelta.nextLeft or current_scelta.nextRight)

    def __next__(self) -> Any:
        '''Restituisce la prossima scelta'''
        return self.getRight([])


class ScelteCollection(Iterable):
    ''' Collezione di scelte'''
    
    def __init__(self, collection: dict[Scelta]):
        self._collection = collection or {}
 
    def __getScelta__(self, key: str) -> Scelta:
        return self._collection[key]
    
    def __iter__(self) -> ScelteIterator:
        return ScelteIterator(self)
    
    def add_scelte(self, scelte: dict[Scelta]) -> None:
        self._collection.update(scelte)


# Singleton FileManager

class SingletonMeta(type):
    _instances = {}

    def __call__(cls):
        if cls not in cls._instances:
            instance = super().__call__()
            cls._instances[cls] = instance
        return cls._instances[cls]

class FileManager(metaclass=SingletonMeta):
    def loadFile(self, fileName: str):
        try:
            with open(fileName, 'r', encoding='utf-8') as f:
                data = json.load(f)
                scelteInfo = data.get("nodes", {})
                charactersInfo = data.get("characters", {})
            return scelteInfo, charactersInfo
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: {fileName} file not found.")
        except json.JSONDecodeError:
            raise

    def saveFile(self, fileName: str, data: dict):
        try:
            with open(fileName, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving file {fileName}: {e}")

    def loadSaves(self, fileName: str = "saves.json"):
        try:
            if not os.path.exists(fileName):
                return {}
            with open(fileName, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

# Character: rappresenta un personaggio del gioco

class Character():
    def __init__(self, id: int, nickname: str = None, abilities: list = [], image_path: str = None):
        self.id = id
        if nickname: self.nickname = nickname
        else:        self.nickname = f"Player {id}"
        self.abilities = abilities
        self.image_path = image_path
    
    def updateAbilities(self, newAbilities: list):
        for ability in newAbilities:
            if ability not in self.abilities:
                self.abilities = self.abilities + newAbilities


# GameSession: rappresenta lo stato della partita in corso

class GameSession():
    def __init__(self, scelteCollection: ScelteCollection,characters: list[Character], currentPlayerId: int = 0, currentSceltaId: str = "0"):
        self.characters = characters
        self.currentPlayerId = currentPlayerId
        self.currentSceltaId = currentSceltaId
        self.scelteCollection = scelteCollection
    
    def getCurrentPlayer(self) -> Character:
        return self.characters[self.currentPlayerId]
    
    def switchTurn(self, forced_turn=None):
        if forced_turn is not None:
            self.currentPlayerId = forced_turn
        else:
            self.currentPlayerId = (self.currentPlayerId + 1) % len(self.characters)
    
    def updateCurrentScelta(self, newSceltaId):
        self.currentSceltaId = newSceltaId
