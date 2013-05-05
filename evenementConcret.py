# -*-coding:iso-8859-1 -*
import pygame
from pygame.locals import *
from .constantes import *
from .evenement import *

class EvenementConcret(Evenement):
    """Classe représentant un évènement concret, c'est-à-dire un évènement lié à une carte."""

    def __init__(self, jeu, gestionnaire):
        """<gestionnaire> est une instance du gestionnaire d'évènements"""
        Evenement.__init__(self, jeu, gestionnaire)
        self._xJoueur, self._yJoueur, self._joueurBouge =  [-1, -1], [-1, -1], [True, True]
        self._xJoueurOld, self._yJoueurOld =  [-1, -1], [-1, -1]

    def onJoueurProche(self, x, y, c, direction):
        """Fonction appelée lorsque le joueur se trouve à proximité de l'évènement (à une case près sauf en diagonale).
        <x> et <y> sont ses coordonnées, exprimées en indices de tiles, sa direction est <direction>. <c> est sa couche."""

    def onJoueurDessus(self, x, y, c, direction):
        """Fonction appelée lorsque le joueur se trouve à l'emplacement même de l'évènement, au tile de coordonnées <x>,<y> sur la couche <c>.
        Sa direction est <direction>."""

    def _onJoueurInteractionQuelconque(self, x, y, c, direction):
        """Fonction appelée lors de toute interaction avec le joueur, quelle qu'elle soit. Doit être redéfinie."""

    def onJoueurInteraction(self, x, y, c, direction, enFace=False, dessus=False):
        """Fonction appelée lorsque le joueur interagit avec l'évènement, quelle que soit sa position par rapport à lui.
        <enFace> vaut <True> quand le joueur est en face de l'évènement, <dessus> vaut <True> quand ils sont sur la même position.
        ATTENTION : Cette fonction n'est PAS à redéfinir.
        Des actions à exécuter lors de toute interaction peuvent être définies dans _onJoueurInteractionQuelconque."""
        self._onJoueurInteractionQuelconque(x, y, c, direction)
        if dessus is False and enFace is False:
            self._onJoueurInteractionCote(x, y, c, direction)
        if dessus is False and enFace is True:
            self._onJoueurInteractionFace(x, y, c, direction)
        if dessus is True and enFace is False:
            self._onJoueurInteractionDessus(x, y, c, direction)

    def _onJoueurInteractionDessus(self, x, y, c, direction):
        """Fonction appelée lorsque le joueur se trouve à l'emplacement même de l'évènement ET appuie sur Entrée.
        Il est de direction <direction>, au tile de coordonnées <x>,<y> sur la couche <c>."""

    def _onJoueurInteractionCote(self, x, y, c, direction):
        """Fonction appelée lorsque le joueur, situé à proximité et tourné vers l'évènement, a appuyé sur Entrée pour interagir avec lui,
        mais qu'ils ne sont pas tournés l'un vers l'autre. Le joueur est situé au tile de coordonnées <x><y>, couche <c> et a <direction> pour direction."""

    def _onJoueurInteractionFace(self, x, y, c, direction):
        """Fonction appelée lorsque le joueur, situé à proximité et tourné vers l'évènement, a appuyé sur Entrée pour interagir avec lui, 
        et qu'ils sont tournés l'un vers l'autre. Le joueur est situé au tile de coordonnées <x><y>, couche <c> et a <direction> pour direction."""

    def _majInfosJoueur(self, i=0):
        self._xJoueurOld[i], self._yJoueurOld[i] = self._xJoueur[i], self._yJoueur[i]
        self._xJoueur[i], self._yJoueur[i] = self._gestionnaire.xJoueur, self._gestionnaire.yJoueur
        self._joueurProche, self._joueurBouge[i] = False, False
        self._gestionnaire.majActionsJoueur(self._nom) #On vérifie si le joueur est proche (cf. onJoueurProche)
        if self._xJoueur[i] != self._xJoueurOld[i] or self._yJoueur[i] != self._yJoueurOld[i]:
            self._joueurBouge[i] = True
