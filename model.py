
from __future__ import annotations
from collections.abc import Iterable, Iterator
from typing import Any
from dataclasses import dataclass
import json

@dataclass
class Scelta:
    ''' Represents a single choice '''
    key:          str  # unique key of the choice
    nextRight:    list[tuple[list[str], str]]  # list of tuples (required objects, next choice key)
    nextLeft:     list[tuple[list[str], str]]  # list of tuples (required objects, next choice key)
    text:         str  # text of the choice
    rightText:    str  # text of the right button
    leftText:     str  # text of the left button
    rightObjects: list[str]  # objects obtained by choosing right
    leftObjects:  list[str]  # objects obtained by choosing left
    level:        int = 1  # level of the choice
    ending:       str = "NO"  # ending type: "NO", "WIN", "FAIL"
    endingTitle:  str = ""  # descriptive title of the ending (if it's an ending)
    

class ScelteIterator(Iterator):
    ''' Iterator for the collection of choices '''

    _position: str = "0"
    _reverse: bool = False

    def __init__(self, collection: ScelteCollection):
        self._collection = collection
        self._reverse =    False
        self._position =   "0"

    def getLeft(self, objects: list[str]) -> Scelta:
        '''Returns the choice to the left'''
        options = self._collection.__getScelta__(self._position).nextLeft
        for option in options:
            required_objects, next_key = option
            if all(obj in objects for obj in required_objects):
                self._position = next_key
                # Handle EXIT - it's not a real node, raise special exception
                if next_key == "EXIT":
                    raise KeyError("EXIT")
                return self._collection.__getScelta__(next_key)
        raise ValueError("The no-objects path is not available for the left of Scelta key " + self._position)

    def getRight(self, objects: list[str]) -> Scelta:
        '''Returns the choice to the right'''
        options = self._collection.__getScelta__(self._position).nextRight
        for option in options:
            required_objects, next_key = option
            if all(obj in objects for obj in required_objects):
                self._position = next_key
                # Handle EXIT - it's not a real node, raise special exception
                if next_key == "EXIT":
                    raise KeyError("EXIT")
                return self._collection.__getScelta__(next_key)
        raise ValueError("The no-objects path is not available for the right of Scelta key " + self._position)

    def hasMore(self) -> bool:
        '''Returns True if there are more choices to process'''
        current_scelta = self._collection.__getScelta__(self._position)
        return bool(current_scelta.nextLeft or current_scelta.nextRight)

    def __next__(self) -> Any:
        '''Returns the next choice'''
        return self.getRight([])


class ScelteCollection(Iterable):
    ''' Collection of choices'''
    
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

# Character: represents a game character

class Character():
    def __init__(self, id: int, nickname: str = None, abilities: list = []):
        self.id = id
        if nickname: self.nickname = nickname
        else:        self.nickname = f"Player {id}"
        self.abilities = abilities
    
    def updateAbilities(self, newAbilities: list):
        for ability in newAbilities:
            if ability not in self.abilities:
                self.abilities = self.abilities + newAbilities


# GameSession: represents the current game session state

class GameSession():
    def __init__(self, scelteCollection: ScelteCollection,characters: list[Character], currentPlayerId: int = 0, currentSceltaId: str = "0"):
        self.characters = characters
        self.currentPlayerId = currentPlayerId
        self.currentSceltaId = currentSceltaId
        self.scelteCollection = scelteCollection
    
    def getCurrentPlayer(self) -> Character:
        return self.characters[self.currentPlayerId]
    
    def switchTurn(self):
        self.currentPlayerId = (self.currentPlayerId + 1) % len(self.characters)
    
    def updateCurrentScelta(self, newSceltaId):
        self.currentSceltaId = newSceltaId
