# -*-coding:iso-8859-1 -*
import pygame
from pygame.locals import *
from .constantes import *
from .evenement import *

class EvenementConcret(Evenement):
    """Classe repr�sentant un �v�nement concret, c'est-�-dire un �v�nement li� � une carte."""

    def __init__(self, jeu, gestionnaire):
        """<gestionnaire> est une instance du gestionnaire d'�v�nements"""
        Evenement.__init__(self, jeu, gestionnaire)
        self._xJoueur, self._yJoueur, self._joueurBouge =  [-1, -1], [-1, -1], [True, True]
        self._xJoueurOld, self._yJoueurOld =  [-1, -1], [-1, -1]

    def onJoueurProche(self, x, y, c, direction):
        """Fonction appel�e lorsque le joueur se trouve � proximit� de l'�v�nement (� une case pr�s sauf en diagonale).
        <x> et <y> sont ses coordonn�es, exprim�es en indices de tiles, sa direction est <direction>. <c> est sa couche."""

    def onJoueurDessus(self, x, y, c, direction):
        """Fonction appel�e lorsque le joueur se trouve � l'emplacement m�me de l'�v�nement, au tile de coordonn�es <x>,<y> sur la couche <c>.
        Sa direction est <direction>."""

    def _onJoueurInteractionQuelconque(self, x, y, c, direction):
        """Fonction appel�e lors de toute interaction avec le joueur, quelle qu'elle soit. Doit �tre red�finie."""

    def onJoueurInteraction(self, x, y, c, direction, enFace=False, dessus=False):
        """Fonction appel�e lorsque le joueur interagit avec l'�v�nement, quelle que soit sa position par rapport � lui.
        <enFace> vaut <True> quand le joueur est en face de l'�v�nement, <dessus> vaut <True> quand ils sont sur la m�me position.
        ATTENTION : Cette fonction n'est PAS � red�finir.
        Des actions � ex�cuter lors de toute interaction peuvent �tre d�finies dans _onJoueurInteractionQuelconque."""
        self._onJoueurInteractionQuelconque(x, y, c, direction)
        if dessus is False and enFace is False:
            self._onJoueurInteractionCote(x, y, c, direction)
        if dessus is False and enFace is True:
            self._onJoueurInteractionFace(x, y, c, direction)
        if dessus is True and enFace is False:
            self._onJoueurInteractionDessus(x, y, c, direction)

    def _onJoueurInteractionDessus(self, x, y, c, direction):
        """Fonction appel�e lorsque le joueur se trouve � l'emplacement m�me de l'�v�nement ET appuie sur Entr�e.
        Il est de direction <direction>, au tile de coordonn�es <x>,<y> sur la couche <c>."""

    def _onJoueurInteractionCote(self, x, y, c, direction):
        """Fonction appel�e lorsque le joueur, situ� � proximit� et tourn� vers l'�v�nement, a appuy� sur Entr�e pour interagir avec lui,
        mais qu'ils ne sont pas tourn�s l'un vers l'autre. Le joueur est situ� au tile de coordonn�es <x><y>, couche <c> et a <direction> pour direction."""

    def _onJoueurInteractionFace(self, x, y, c, direction):
        """Fonction appel�e lorsque le joueur, situ� � proximit� et tourn� vers l'�v�nement, a appuy� sur Entr�e pour interagir avec lui, 
        et qu'ils sont tourn�s l'un vers l'autre. Le joueur est situ� au tile de coordonn�es <x><y>, couche <c> et a <direction> pour direction."""

    def _majInfosJoueur(self, i=0):
        self._xJoueurOld[i], self._yJoueurOld[i] = self._xJoueur[i], self._yJoueur[i]
        self._xJoueur[i], self._yJoueur[i] = self._gestionnaire.xJoueur, self._gestionnaire.yJoueur
        self._joueurProche, self._joueurBouge[i] = False, False
        self._gestionnaire.majActionsJoueur(self._nom) #On v�rifie si le joueur est proche (cf. onJoueurProche)
        if self._xJoueur[i] != self._xJoueurOld[i] or self._yJoueur[i] != self._yJoueurOld[i]:
            self._joueurBouge[i] = True
