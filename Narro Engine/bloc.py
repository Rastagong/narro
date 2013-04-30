# -*-coding:iso-8859-1 -*
import pygame
from pygame.locals import *
from constantes import *


class Bloc:
    """Classe représentant un bloc, c'est-à-dire une image sur une couche donnée d'un tile """

    def __init__(self, jeu, config=None, coor=None, nomTileset=None, praticabilite=None, couleurTransparente=None, positionSource=None, positionCarte=None, positionCarteSuivante=None, nomPNJ=None, pnj=False, toutDonne=False, vide=False, enMouvement=False):
        """__init__(positionSource, carte, bloc)
        Initialise un bloc dont le tile est à <positionSource> dans un tileset nommé <nomTileset>. <pnj> vaut True si c'est un PNJ. """
        self._vide = False
        if pnj is False and toutDonne is False and vide is False:
            longueur, largeur = int(mapXML.getAttribute("width")), int(mapXML.getAttribute("height"))
            indiceBloc = (largeur * coor[1]) + coor[0]
            gid = int(mapXML.getElementsByTagName("layer")[coor[2]].getElementsByTagName("data")[0].getElementsByTagName("tile")[indiceBloc].getAttribute("gid"))
            if gid in dicoGeneral.keys(): #Les infos de ce bloc sont déjà connues, on les recopie
                self._nomTileset, self._couleurTransparente, self._vide = dicoGeneral[gid][0], dicoGeneral[gid][1], False   
                self._praticabilite, self._positionSource = dicoGeneral[gid][2], dicoGeneral[gid][3]    
            elif gid == 0: #Gid 0 signifie bloc vide
                self._vide = True
            else: #Ce bloc n'est pas vide et non connu, on trouve ses infos
                self._vide = False
                gidTileset = 0
                for gidActuel in dicoGIDs.keys(): #Recherche du tileset
                    if gid >= gidActuel:
                        gidTileset = gidActuel
                nomTileset = dicoGIDs[gidTileset]
                self._nomTileset, self._couleurTransparente = DOSSIER_RESSOURCES+dicoTilesets[nomTileset][0], dicoTilesets[nomTileset][1]
                self._couleurTransparente = hex_to_rgb(self._couleurTransparente)
                idLocal = gid - gidTileset
                for tilesetXML in mapXML.getElementsByTagName("tileset"):
                    if tilesetXML.getAttribute("name") == dicoGIDs[gidTileset]:
                        proprisTileTileset = tilesetXML.getElementsByTagName("tile")[idLocal].getElementsByTagName("properties")[0]
                        proprisTileTileset = proprisTileTileset.getElementsByTagName("property")
                        for propri in proprisTileTileset:
                            if propri.getAttribute("name") == "Praticabilite":
                                self._praticabilite = propri.getAttribute("value")
                        longueurTileset = int(tilesetXML.getElementsByTagName("image")[0].getAttribute("width")) / 32
                        largeurTileset = int(tilesetXML.getElementsByTagName("image")[0].getAttribute("height")) / 32
                        self._positionSource = ( (idLocal%longueurTileset)*32, (idLocal//longueurTileset)*32, 32, 32)
                        dicoGeneral[gid] = (self._nomTileset, self._couleurTransparente, self._praticabilite, self._positionSource)
        elif pnj is False and toutDonne is True: #Les blocs de ref sont construits directement à partir des données
            self._nomTileset, self._praticabilite, self._vide = DOSSIER_RESSOURCES + nomTileset, praticabilite, False
            self._positionSource, self._couleurTransparente, self._vide = positionSource, couleurTransparente, vide
        elif vide is True:
            self._vide, self._praticabilite = True, True
        elif pnj is True:
            self._positionSource, self._nomTileset, self._couleurTransparente, self._nomPNJ, self._positionCarte = positionSource, nomTileset, couleurTransparente, nomPNJ, positionCarte
            self._positionCarteSuivante = positionCarteSuivante
    
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

    positionSource = property(_getPositionSource, _setPositionSource)
    positionCarte = property(_getPositionCarte, _setPositionCarte)
    positionCarteSuivante = property(_getPositionCarteSuivante, _setPositionCarteSuivante)
    nomPNJ = property(_getNomPNJ, _setNomPNJ)
    nomTileset = property(_getNomTileset, _setNomTileset)
    couleurTransparente = property(_getCouleurTransparente, _setCouleurTransparente)
    vide = property(_getVide, _setVide)
    praticabilite = property(_getPraticabilite, _setPraticabilite)

