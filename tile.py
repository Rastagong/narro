# -*-coding:utf-8 -*
from .bloc import *
import pygame, configparser
from pygame.locals import *

class Tile:
    """Classe représentant un tile, cad une case de la carte"""
    def __init__(self, nombreCouches):
        self._bloc, self._praticabilite, self._nombreCouches, self._blocsSupplementaires = list(), [False]*nombreCouches, nombreCouches, dict()

    def modifierPraticabilite(self, indice, nouvelleValeur, recalcul=True):
        self._bloc[indice].praticabilite = nouvelleValeur
        if recalcul is True:
            self.recalculerPraticabilites()

    def ajouterTileEtendu(self, couche, praticabilite, positionSource, nomTileset):
        self._blocsSupplementaires.setdefault(couche, [])
        self._blocsSupplementaires[couche].append((praticabilite, positionSource, nomTileset))
        self.recalculerPraticabilites()

    def recalculerPraticabilites(self):
        i, toutFaux =  0, False
        while i < len(self._bloc):
            praticabiliteActuelle = self._bloc[i].praticabilite
            if praticabiliteActuelle is False:
                toutFaux = True
            if praticabiliteActuelle is True and i == 0 and self._bloc[i].vide is True: #Bloc vide en couche 0 : c'est du vide, donc impraticable
                toutFaux = True
            if i in self._blocsSupplementaires.keys():
                for (praticabiliteBlocSupplementaire, positionSource, nomTileset) in self._blocsSupplementaires[i]:
                    if praticabiliteBlocSupplementaire is False:
                        toutFaux = True
            if toutFaux is True and self._bloc[i].pont is False:
                self._praticabilite[i] = False
            else:
                self._praticabilite[i] = True
            i += 1

    def _getBloc(self):
        return self._bloc
    
    def _getPraticabilite(self):
        return self._praticabilite

    bloc = property(_getBloc)
    praticabilite = property(_getPraticabilite)
