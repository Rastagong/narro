# -*-coding:iso-8859-1 -*
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

    def traiter(self):
        """Traite l'événement"""

