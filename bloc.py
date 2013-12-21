# -*-coding:utf-8 -*
import pygame
from pygame.locals import *
from .constantes import *


class Bloc:
    """Classe représentant un bloc, c'est-à-dire une image sur une couche donnée d'un tile """

    def __init__(self, infos=False, nomTileset=None, praticabilite=None, couleurTransparente=None, positionSource=None, positionCarte=None, positionCollision=False, positionVisible=False, positionCarteSuivante=None, nomPNJ=None, pnj=False, vide=False, enMouvement=False):
        """__init__(positionSource, carte, bloc)
        Initialise un bloc dont le tile est à <positionSource> dans un tileset nommé <nomTileset>. <pnj> vaut True si c'est un PNJ. """
        self._vide, self._pont = False, False
        if pnj is False and vide is False: #Un bloc plein sur la carte
            if infos: #Lors de la création de la carte
                self._nomTileset, self._praticabilite, self._positionSource = infos[0], infos[1], infos[2]
            else:  #Méthode changerBloc
                self._positionSource, self._nomTileset, self._couleurTransparente = positionSource, nomTileset, couleurTransparente
            self._couleurTransparente, self._vide = (0,0,0), False
            pontsPositions = {"base_out_atlas.png": [(416, 512, 32, 32), (448, 512, 32, 32), (480, 512, 32, 32)]} #Liste des tiles de ponts, par tileset
            self._pont = self._nomTileset in pontsPositions.keys() and self._positionSource in pontsPositions[self._nomTileset]
        elif vide is True:
            self._vide, self._praticabilite = True, True
        elif pnj is True:
            self._positionSource, self._nomTileset, self._couleurTransparente, self._nomPNJ, self._positionCarte = positionSource, nomTileset, couleurTransparente, nomPNJ, positionCarte
            self._positionCarteSuivante, self._positionCollision, self._positionVisible = positionCarteSuivante, positionCollision, positionVisible
            if self._positionCollision is False:
                self._positionCollision = Rect(0, 0, self._positionCarte.width, self._positionCarte.height)
            if self._positionVisible is False:
                self._positionVisible = Rect(0, 0, 0, 0)

    def _getPositionSource(self):
        return self._positionSource

    def _setPositionSource(self, nouvellePositionSource):
        self._positionSource = nouvellePositionSource   

    def _getPositionCarte(self):
        return self._positionCarte

    def _setPositionCarte(self, nouvellePositionCarte):
        self._positionCarte = nouvellePositionCarte   

    def _getPositionCarteSuivante(self):
        return self._positionCarteSuivante

    def _setPositionCarteSuivante(self, nouvellePositionCarteSuivante):
        self._positionCarteSuivante = nouvellePositionCarteSuivante 

    def _setPositionVisible(self, nouvellePosition):
        self._positionVisible = nouvellePosition

    def _getPositionVisible(self):
        positionVisibleFinale = self._positionCarte.copy()
        positionVisibleFinale.width, positionVisibleFinale.height = self._positionVisible.width, self._positionVisible.height
        return positionVisibleFinale.move(self._positionVisible.left, self._positionVisible.top)

    def _setPositionCollision(self, nouvellePosition):
        self._positionCollision = nouvellePosition

    def _getPositionCollision(self):
        positionCollisionFinale = self._positionCarte.copy()
        positionCollisionFinale.width, positionCollisionFinale.height = self._positionCollision.width, self._positionCollision.height
        return positionCollisionFinale.move(self._positionCollision.left, self._positionCollision.top)

    def _getNomTileset(self):
        return self._nomTileset

    def _getPraticabilite(self):
        return self._praticabilite

    def _setPraticabilite(self, nouvelleValeur):
        self._praticabilite = nouvelleValeur

    def _getVide(self):
        return self._vide

    def _setVide(self, nouveauVide):
        self._vide = nouveauVide

    def _getNomPNJ(self):
        return self._nomPNJ

    def _setNomPNJ(self, nouveauNomPNJ):
        self._nomPNJ = nouveauNomPNJ
    
    def _setNomTileset(self, nouveauNomTileset):
        self._nomTileset = nouveauNomTileset

    def _getCouleurTransparente(self):
        return self._couleurTransparente

    def _setCouleurTransparente(self, nouvelleCouleurTransparente):
        self._couleurTransparente = nouvelleCouleurTransparente

    def _getPont(self):
        return self._pont

    positionSource = property(_getPositionSource, _setPositionSource)
    positionCarte = property(_getPositionCarte, _setPositionCarte)
    positionCarteSuivante = property(_getPositionCarteSuivante, _setPositionCarteSuivante)
    positionVisible = property(_getPositionVisible, _setPositionVisible)
    positionCollision = property(_getPositionCollision, _setPositionCollision)
    nomPNJ = property(_getNomPNJ, _setNomPNJ)
    nomTileset = property(_getNomTileset, _setNomTileset)
    couleurTransparente = property(_getCouleurTransparente, _setCouleurTransparente)
    vide = property(_getVide, _setVide)
    praticabilite = property(_getPraticabilite, _setPraticabilite)
    pont = property(_getPont)

