# -*-coding:iso-8859-1 -*
from .bloc import *
import pygame, configparser
from pygame.locals import *

class Tile:
    """Classe représentant un tile, cad une case de la carte"""
    def __init__(self, nombreCouches):
        self._bloc, self._praticabilite, self._nombreCouches = list(), [False]*nombreCouches, nombreCouches

    def modifierPraticabilite(self, indice, nouvelleValeur, recalcul=True):
        self._bloc[indice].praticabilite = nouvelleValeur
        if recalcul is True:
            self.recalculerPraticabilites()

    def recalculerPraticabilites(self):
        i, toutFaux =  0, False
        while i < self._nombreCouches:
            praticabiliteActuelle = self._bloc[i].praticabilite
            if praticabiliteActuelle is False:
                toutFaux = True
            if toutFaux is True:
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
