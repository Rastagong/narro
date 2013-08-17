# -*-coding:utf-8 -*
import pygame
from pygame.locals import *
from .constantes import *
from .horloge import *
from .interrupteur import *



class Evenement:
    """Classe mère représentant un évènement"""

    def __init__(self, jeu, gestionnaireEvenements):
        """Initialise l'évènement
        <jeu> est l'objet de classe <Jeu>, qui contient toute l'application"""
        self._jeu = jeu
        self._etapeTraitement, self._gestionnaire = 0, gestionnaireEvenements
        self._boiteOutils = self._gestionnaire.boiteOutils
        self._xJoueur, self._yJoueur, self._joueurBouge =  [-1, -1], [-1, -1], [True, True]
        self._xJoueurOld, self._yJoueurOld =  [-1, -1], [-1, -1]

    def _majInfosJoueur(self, i=0):
        self._xJoueurOld[i], self._yJoueurOld[i] = self._xJoueur[i], self._yJoueur[i]
        self._xJoueur[i], self._yJoueur[i] = self._gestionnaire.xJoueur, self._gestionnaire.yJoueur
        self._joueurBouge[i] = False
        if self._xJoueur[i] != self._xJoueurOld[i] or self._yJoueur[i] != self._yJoueurOld[i]:
            self._joueurBouge[i] = True

    def traiter(self):
        """Traite l'événement"""

