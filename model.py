
from __future__ import annotations
from collections.abc import Iterable, Iterator
from typing import Any
from dataclasses import dataclass

@dataclass
class Scelta:
    ''' Rappresenta una singola scelta '''
    key:       str  # chiave univoca della scelta
    nextRight: list[tuple[list[str], str]]  # lista di tuple (oggetti necessari, key della scelta successiva)
    nextLeft:  list[tuple[list[str], str]]  # lista di tuple (oggetti necessari, key della scelta successiva)
    text:      str  # testo della scelta
    rightText: str  # testo del botone della scelta a destra
    leftText:  str  # testo del botone della scelta a sinistra
    

class ScelteIterator(Iterator):
    ''' Iteratore per la collezione di scelte '''

    _position: str = "0"
    _reverse: bool = False

    def __init__(self, collection: ScelteCollection):
        self._collection = collection
        self._reverse =    False
        self._position =   "0"

    def getLeft(self, objects: list[str]) -> Scelta:
        '''Restituisce la scelta a sinistra'''
        options = self._collection.__getScelta__(self._position).nextLeft
        for option in options:
            required_objects, next_key = option
            if all(obj in objects for obj in required_objects):
                self._position = next_key
                return self._collection.__getScelta__(next_key)
        raise ValueError("The no-objets path is not available for the left of Scelta key " + self._position)

    def getRight(self, objects: list[str]) -> Scelta:
        '''Restituisce la scelta a destra'''
        options = self._collection.__getScelta__(self._position).nextRight
        for option in options:
            required_objects, next_key = option
            if all(obj in objects for obj in required_objects):
                self._position = next_key
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

