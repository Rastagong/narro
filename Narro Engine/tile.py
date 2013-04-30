# -*-coding:iso-8859-1 -*
from bloc import *
import pygame, configparser
from pygame.locals import *

class Tile:
    """Classe représentant un tile, cad une case de la carte"""
    def __init__(self, x, y, config, blocsRef, nombreCouches, jeu, hauteurTile):
        self._bloc, self._praticabilite, self._jeu, c = list(), list(), jeu, 0
        while c < nombreCouches:
            praticabiliteActuelle = config.getboolean("Tiles", str(x) + "+" + str(y) + "+" + str(c))
            self._praticabilite.append(praticabiliteActuelle)
            c += 1
        c = 0
        while c < nombreCouches: 
            indiceBlocRef = config.getint("Blocs", str(x) + "+" + str(y) + "+" + str(c))
            self._bloc.append(blocsRef[indiceBlocRef])
            c += 1

    def modifierPraticabilite(self, indice, nouvelleValeur, recalcul=True):
        self._bloc[indice].praticabilite = nouvelleValeur
        if recalcul is True:
            self.recalculerPraticabilites()

    def recalculerPraticabilites(self):
        i, toutFaux =  0, False
        while i < self._jeu.carteActuelle.nombreCouches:
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
