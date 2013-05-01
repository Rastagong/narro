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
        self._jeu = jeu
        self._evenements = dict(concrets=dict(), abstraits=dict())
        self._nomCarte, self._boiteOutils, self._positionsARegistrer, self._evenementsATuer = None, BoiteOutils(self._jeu), [], []
        self._initialiserEvenements()
        if SESSION_DEBUG:
            self._evenements["abstraits"]["Divers"]["Debugger"] = Debugger(self._jeu, self)

    def _initialiserEvenements(self):
        """Fonction � red�finir au sein de chaque projet"""
        pass

    def chargerEvenements(self, nomCarte):
        """Fonction � red�finir au sein de chaque projet"""
        pass

    def initialiserBoiteOutils(self):
        self._boiteOutils.initialiser()
    
    def gererEvenements(self, nomCarteActuelle):
        """G�re tous les �v�nements"""
        self._nomCarte = nomCarteActuelle
        for categorieEvenements in self._evenements["abstraits"].values():
            for evenement in categorieEvenements.values():
                evenement.traiter()
        if nomCarteActuelle in self._evenements["concrets"]:
            for cle,infosEvenement in self._evenements["concrets"][nomCarteActuelle].items():
                infosEvenement[0].traiter()
        self._tuerEvenementsATuer()

    def ajouterEvenementATuer(self, typeEvenement, categorieEvenement, nomEvenement):
        """Ajoute un �v�nement � tuer � la fin du traitement des �v�nements. 
        On ne peut pas le faire pendant le traitement des �v�nements car �a changerait la taille du dico pendant l'it�ration."""
        self._evenementsATuer.append((typeEvenement, categorieEvenement, nomEvenement))

    def _tuerEvenementsATuer(self):
        """A la fin du traitement des �v�nements, tue tous les �v�nements � tuer."""
        for (typeEvenement, categorieEvenement, nomEvenement) in self._evenementsATuer:
            self._evenements[typeEvenement][categorieEvenement].pop(nomEvenement)
        del self._evenementsATuer[:]

    def registerPosition(self, nom, x, y, c, joueur=False, appuiJoueur=False, direction="Aucune"):
        """Enregistre la position d'un �v�nement nomm� <nom> � la position <x><y><c> sur la carte. Elle est exprim�e en indices de tiles.
        Elle n'est pas trait�e dans cette fonction : elle est seulement ajout�e � une liste, trait�e dans traiterPositions. 
        De cette mani�re, les notifs de position aux �v�nements ont toutes lieu APRES les traitements des �v�nements.
        Cet ordre permet de g�rer plus pr�cis�ment des algorithmes.""" 
        self._positionsARegistrer.append( (nom, x, y, c, joueur, appuiJoueur, direction) )

    def traiterPositions(self):
        """Parcoure les positions enregistr�es et les traite : enregistrement dans le dico des �v�nements, notifs de position."""
        for position in self._positionsARegistrer:
            self._traiterPosition(position)
        self._positionsARegistrer[:] = []
        
    def actualiserSonsFixes(self):
       self._boiteOutils.actualiserSonsFixes()

    def majActionsJoueur(self, nomEvenement):
        """Pr�vient l'�v�nement nomm�e <nomEvenement> des actions du joueur."""
        infosEvenement, position = self._evenements["concrets"][self._nomCarte][nomEvenement], self._positionJoueur
        evenement, abs, ord, directionEvenement = infosEvenement[0], infosEvenement[1][0], infosEvenement[1][1], infosEvenement[2]
        nom, x, y, c, joueur, appui, directionJoueur = position[0], position[1], position[2], position[3], position[4], position[5], position[6]
        self._prevenirEvenementActionJoueur(evenement, x, y, c, appui, directionJoueur, abs, ord, directionEvenement)

    def _traiterPosition(self, position):
        """Traite une position <position>."""
        nom, x, y, c, joueur, appuiJoueur, direction = position[0], position[1], position[2], position[3], position[4], position[5], position[6]
        for cle in self._evenements["concrets"][self._nomCarte].keys(): #On met � jour les infos de l'�v�nement
            if cle == nom:
                self._evenements["concrets"][self._nomCarte][cle][1] = (x,y)
                self._evenements["concrets"][self._nomCarte][cle][2] = direction
        if joueur is True: #On pr�vient les �v�nements de l'activit� du joueur quand il est proche, appuie, etc...
            if LOG_COORDONNEES_JOUEUR is True:
                print("Joueur", x, y, c)
            self._xJoueur, self._yJoueur, self._cJoueur, self._appuiValidationJoueur, self._directionJoueur = x, y, c, appuiJoueur, direction
            self._positionJoueur = position
            for infosEvenement in self._evenements["concrets"][self._nomCarte].values():
                evenement, abs, ord, directionActuelle = infosEvenement[0], infosEvenement[1][0], infosEvenement[1][1], infosEvenement[2]
                if isinstance(evenement,Joueur) is False: #On ne pr�vient pas le joueur de ses propres actions ! :D
                    self._prevenirEvenementActionJoueur(evenement, x, y, c, appuiJoueur, direction, abs, ord, directionActuelle)

    def _prevenirEvenementActionJoueur(self, evenement, x, y, c, appui, directionJoueur, abs, ord, directionEvenement):
        """Pr�vient un �v�nement <evenement> des actions du joueur."""
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
    
    def _getAppuiValidationJoueur(self):
        return self._appuiJoueur

    def _getNomCarte(self):
        return self._nomCarte

    evenements = property(_getEvenements)
    boiteOutils = property(_getBoiteOutils)
    xJoueur = property(_getXJoueur)
    yJoueur = property(_getYJoueur)
    cJoueur = property(_getCJoueur)
    directionJoueur = property(_getDirectionJoueur)
    appuiValidationJoueur = property(_getAppuiValidationJoueur)
    nomCarte = property(_getNomCarte)
