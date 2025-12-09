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
    def __init__(self, collection: ScelteCollection):
        pass

def getLeft(self, objects: list[str]) -> Scelta:
    '''Restituisce la scelta a sinistra'''
    pass

def getRight(self, objects: list[str]) -> Scelta:
    '''Restituisce la scelta a destra'''
    pass

def hasMore(self) -> bool:
    '''Restituisce True se ci sono altre scelte da processare'''
    pass

def __next__(self) -> Any:
    '''Restituisce la prossima scelta'''
    pass

class ScelteCollection(Iterable):
    ''' Collezione di scelte'''
    def __init__(self, collection: dict[Scelta]):
        pass

    def __getScelta__(self, key: str) -> Scelta:
        pass

    def __iter__(self) -> ScelteIterator:
        pass

    def add_scelte(self, scelte: dict[Scelta]) -> None:
        pass