# -*-coding:iso-8859-1 -*
import pygame, narro.directions
from narro import *
from collections import OrderedDict
from pygame.locals import *
from .constantes import *
from .joueur import *
from .pnj import *
from .listeEvenements import *
from .boiteOutils import *

class GestionnaireEvenements():
    def __init__(self, jeu):
        """Initialise le gestionnaire
        <jeu> est l'objet de classe <Jeu>, qui contient toute l'application"""
        self._jeu, self._nomCarte = jeu, None
        self._evenements = dict(concrets=dict(), abstraits=dict())
        self._boiteOutils, self._positionsARegistrer, self._evenementsATuer, self._appuiJoueur = BoiteOutils(self._jeu, self._getInterrupteurs(), self._getVariables()), [], [], False
        self._initialiserEvenements()
        if SESSION_DEBUG:
            self._evenements["abstraits"]["Divers"]["Debugger"] = Debugger(self._jeu, self)

    def _getInterrupteurs(self):
        """Fonction à redéfinir au sein de chaque projet"""

    def _getVariables(self):
        """Fonction à redéfinir au sein de chaque projet"""

    def _initialiserEvenements(self):
        """Fonction à redéfinir au sein de chaque projet"""
        pass

    def chargerEvenements(self, nomCarte):
        """Fonction à redéfinir au sein de chaque projet"""
        pass

    def initialiserBoiteOutils(self):
        self._boiteOutils.initialiser()
        return self._boiteOutils
    
    def gererEvenements(self, nomCarteActuelle):
        """Gère tous les évènements"""
        self._nomCarte = nomCarteActuelle
        for categorieEvenements in self._evenements["abstraits"].values():
            for evenement in categorieEvenements.values():
                evenement.traiter()
        if nomCarteActuelle in self._evenements["concrets"]:
            for cle,infosEvenement in self._evenements["concrets"][nomCarteActuelle].items():
                infosEvenement[0].traiter()
        self._tuerEvenementsATuer()

    def ajouterEvenementATuer(self, typeEvenement, categorieEvenement, nomEvenement):
        """Ajoute un évènement à tuer à la fin du traitement des évènements. 
        On ne peut pas le faire pendant le traitement des évènements car ça changerait la taille du dico pendant l'itération."""
        self._evenementsATuer.append((typeEvenement, categorieEvenement, nomEvenement))

    def _tuerEvenementsATuer(self):
        """A la fin du traitement des évènements, tue tous les évènements à tuer."""
        for (typeEvenement, categorieEvenement, nomEvenement) in self._evenementsATuer:
            self._evenements[typeEvenement][categorieEvenement].pop(nomEvenement)
        del self._evenementsATuer[:]

    def registerPosition(self, nom, x, y, c, joueur=False, appuiJoueur=False, direction="Aucune"):
        """Enregistre la position d'un évènement nommé <nom> à la position <x><y><c> sur la carte. Elle est exprimée en indices de tiles.
        Elle n'est pas traitée dans cette fonction : elle est seulement ajoutée à une liste, traitée dans traiterPositions. 
        De cette manière, les notifs de position aux évènements ont toutes lieu APRES les traitements des évènements.
        Cet ordre permet de gérer plus précisément des algorithmes.""" 
        self._positionsARegistrer.append( (nom, x, y, c, joueur, appuiJoueur, direction) )

    def traiterPositions(self):
        """Parcoure les positions enregistrées et les traite : enregistrement dans le dico des évènements, notifs de position."""
        for position in self._positionsARegistrer:
            self._traiterPosition(position)
        self._positionsARegistrer[:] = []
        
    def actualiserSonsFixes(self):
       self._boiteOutils.actualiserSonsFixes()

    def majActionsJoueur(self, nomEvenement):
        """Prévient l'évènement nommée <nomEvenement> des actions du joueur."""
        infosEvenement, position = self._evenements["concrets"][self._nomCarte][nomEvenement], self._positionJoueur
        evenement, abs, ord, directionEvenement = infosEvenement[0], infosEvenement[1][0], infosEvenement[1][1], infosEvenement[2]
        nom, x, y, c, joueur, appui, directionJoueur = position[0], position[1], position[2], position[3], position[4], position[5], position[6]
        self._prevenirEvenementActionJoueur(evenement, x, y, c, appui, directionJoueur, abs, ord, directionEvenement)

    def _traiterPosition(self, position):
        """Traite une position <position>."""
        nom, x, y, c, joueur, appuiJoueur, direction = position[0], position[1], position[2], position[3], position[4], position[5], position[6]
        for cle in self._evenements["concrets"][self._nomCarte].keys(): #On met à jour les infos de l'évènement
            if cle == nom:
                self._evenements["concrets"][self._nomCarte][cle][1] = (x,y)
                self._evenements["concrets"][self._nomCarte][cle][2] = direction
        if joueur is True: #On prévient les évènements de l'activité du joueur quand il est proche, appuie, etc...
            if LOG_COORDONNEES_JOUEUR is True:
                print("Joueur", x, y, c)
            self._xJoueur, self._yJoueur, self._cJoueur, self._appuiJoueur, self._directionJoueur = x, y, c, appuiJoueur, direction
            self._positionJoueur = position
            for infosEvenement in self._evenements["concrets"][self._nomCarte].values():
                evenement, abs, ord, directionActuelle = infosEvenement[0], infosEvenement[1][0], infosEvenement[1][1], infosEvenement[2]
                if isinstance(evenement,Joueur) is False: #On ne prévient pas le joueur de ses propres actions ! :D
                    self._prevenirEvenementActionJoueur(evenement, x, y, c, appuiJoueur, direction, abs, ord, directionActuelle)

    def _prevenirEvenementActionJoueur(self, evenement, x, y, c, appui, directionJoueur, abs, ord, directionEvenement):
        """Prévient un évènement <evenement> des actions du joueur."""
        if ( (abs == x+1 or abs == x-1) and ord == y) or ( (ord == y+1 or ord == y-1) and abs == x):
            evenement.onJoueurProche(x, y, c, directionJoueur)
            if appui is True:
                (xVisee, yVisee) = directions.ajusterCoupleCoordonneesLorsDeplacement(x,y,directionJoueur,enTile=True)
                if xVisee == abs and yVisee == ord:
                    if directionJoueur == directions.directionContraire(directionEvenement):
                        evenement.onJoueurInteraction(x, y, c, directionJoueur, enFace=True)
                    else:
                        evenement.onJoueurInteraction(x, y, c, directionJoueur, enFace=False)
                else:
                    evenement.onJoueurProche(x, y, c, directionJoueur)
        elif abs == x and ord == y:
            evenement.onJoueurDessus(x, y, c, directionJoueur)
            if appui is True:
                evenement.onJoueurInteraction(x, y, c, directionJoueur, enFace=False, dessus=True)

    ##Accesseurs et mutateurs
    #
    #
    def _getEvenements(self):
        return self._evenements

    def _getBoiteOutils(self):
        return self._boiteOutils

    def _getXJoueur(self):
        return self._xJoueur

    def _getYJoueur(self):
        return self._yJoueur

    def _getCJoueur(self):
        return self._cJoueur

    def _getDirectionJoueur(self):
        return self._directionJoueur
    
    def _getAppuiJoueur(self):
        return self._appuiJoueur

    def _getNomCarte(self):
        return self._nomCarte

    evenements = property(_getEvenements)
    boiteOutils = property(_getBoiteOutils)
    xJoueur = property(_getXJoueur)
    yJoueur = property(_getYJoueur)
    cJoueur = property(_getCJoueur)
    directionJoueur = property(_getDirectionJoueur)
    appuiJoueur = property(_getAppuiJoueur)
    nomCarte = property(_getNomCarte)
