# -*-coding:iso-8859-1 -*
import pygame, directions
from collections import OrderedDict
from pygame.locals import *
from constantes import *
from joueur import *
from pnj import *
from listeEvenements import *
from boiteOutils import *

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
        module = __import__("listeEvenements" + PROJET, fromlist=[])
        globals().update(vars(module))
        directionDefaut = DIRECTION_DEPART_MOBILE_PAR_DEFAUT
        if PROJET == "TSM":
            self._evenements["concrets"]["TSM-Auberge"] = OrderedDict()
            self._evenements["concrets"]["TSM-Drapier"] = OrderedDict()
            self._evenements["concrets"]["TSM-Chemin"] = OrderedDict()
            self._evenements["concrets"]["TSM-Champs"] = OrderedDict()
            self._evenements["concrets"]["GT-Foret1"] = OrderedDict()
            #self._evenements["concrets"]["GT-Foret1"]["Joueur"] = [ Joueur(self._jeu, self, 0, 27, 1, fichier="Maid.png"), (0,27), directionDefaut]
            self._evenements["concrets"]["TSM-Auberge"]["Joueur"] = [ Joueur(self._jeu, self, 9, 30, 2, fichier="Maid.png"), (9,30), directionDefaut]
            #self._evenements["concrets"]["TSM-Drapier"]["Joueur"] = [ Joueur(self._jeu, self, 7, 28, 2, fichier="Maid.png"), (7, 28), directionDefaut]
            #self._evenements["concrets"]["TSM-Chemin"]["Joueur"] = [ Joueur(self._jeu, self, 5, 15, 3, fichier="Maid.png"), (5, 15), directionDefaut]
            #self._evenements["concrets"]["TSM-Champs"]["Joueur"] = [ Joueur(self._jeu, self, 6, 59, 2, fichier="Maid.png"), (6, 59), directionDefaut]
            j, self._positionJoueur = self._jeu.joueur, None
            self._xJoueur, self._yJoueur, self._cJoueur, self._directionJoueur, self._appuiValidationJoueur = j.x/32, j.y/32, j.c, j.direction, j.appuiValidation
            self._evenements["abstraits"]["Divers"] = dict()
            self._evenements["abstraits"]["Divers"]["Narrateur"] = Narrateur(self._jeu, self)
            self._evenements["abstraits"]["Divers"]["ModulateurMusique"] = ModulateurMusique(self._jeu, self)
        elif PROJET == "LD26":
            self._evenements["concrets"]["LD26-Ferme"] = OrderedDict()
            self._evenements["concrets"]["LD26-Foret"] = OrderedDict()
            self._evenements["concrets"]["LD26-Fin"] = OrderedDict()
            #self._evenements["concrets"]["LD26-Ferme"]["Joueur"] = [ Joueur(self._jeu, self, 15, 10, 2, fichier="Anna.png"), (12, 24), "Bas"]
            #self._evenements["concrets"]["LD26-Foret"]["Joueur"] = [ Joueur(self._jeu, self, 38, 1, 2, fichier="Anna.png"), (38,1), "Bas"]
            self._evenements["concrets"]["LD26-Fin"]["Joueur"] = [ Joueur(self._jeu, self, 0, 16, 2, fichier="Anna.png"), (0, 16), "Droite"]
            j, self._positionJoueur = self._jeu.joueur, None
            self._xJoueur, self._yJoueur, self._cJoueur, self._directionJoueur, self._appuiValidationJoueur = j.x/32, j.y/32, j.c, j.direction, j.appuiValidation
            self._evenements["abstraits"]["Divers"] = dict()
            self._evenements["abstraits"]["Divers"]["Narrateur"] = Narrateur(self._jeu, self)
            self._evenements["abstraits"]["Divers"]["ModulateurMusique"] = ModulateurMusique(self._jeu, self)
            self._evenements["abstraits"]["Divers"]["PanierFleurs"] = PanierFleurs(self._jeu, self)

    def chargerEvenements(self, nomCarte):
        if PROJET == "TSM":
            self._chargerEvenementsTSM(nomCarte)
        elif PROJET == "LD26":
            self._chargerEvenementsLD26(nomCarte)

    def _chargerEvenementsLD26(self, nomCarte):
        if nomCarte == "LD26-Ferme":
            self._evenements["concrets"]["LD26-Ferme"]["Mere"] = [ Mere(self._jeu, self), (13, 9), "Bas"]
            self._evenements["concrets"]["LD26-Ferme"]["Scholar"] = [Scholar(self._jeu, self), (2, 29), "Haut"]
            self._evenements["concrets"]["LD26-Ferme"]["Sortie"] = [ Teleporteur(self._jeu, self, "LD26-Foret", 0, 45, 2, "Haut", condition="ScholarParti", fonctionAvant="texteTransition", parametresFAvant="So began our journey."), (2, 29), "Aucune"]
        elif nomCarte == "LD26-Foret":
            self._evenements["concrets"]["LD26-Foret"]["Scholar"] = [Scholar2(self._jeu, self), (2, 46), "Gauche"]
            self._evenements["concrets"]["LD26-Foret"]["Panneau"] = [Panneau(self._jeu, self), (2, 28), "Bas"]
            self._evenements["concrets"]["LD26-Foret"]["Porte"] = [Porte(self._jeu, self), (1, 28), "Bas"]
            self._evenements["concrets"]["LD26-Foret"]["Cle1"] = [Cle(self._jeu, self), (39, 40), "Bas"]
            self._evenements["concrets"]["LD26-Foret"]["Cle2"] = [Cle(self._jeu, self), (39, 41), "Bas"]
            self._evenements["concrets"]["LD26-Foret"]["Sortie1"] = [ Teleporteur(self._jeu, self, "LD26-Fin", 0, 16, 2, "Haut", fonctionAvant="texteTransition", parametresFAvant="And it continued, over and over. Until night."), (38, 0), "Aucune"]
            self._evenements["concrets"]["LD26-Foret"]["Sortie2"] = [ Teleporteur(self._jeu, self, "LD26-Fin", 0, 16, 2, "Haut", fonctionAvant="texteTransition", parametresFAvant="And it continued, over and over. Until night."), (39, 0), "Aucune"]
        elif nomCarte == "LD26-Fin":
            self._evenements["concrets"]["LD26-Fin"]["Scholar"] = [Scholar3(self._jeu, self), (2, 16), "Gauche"]
            self._evenements["concrets"]["LD26-Fin"]["Monstre"] = [Monstre(self._jeu, self), (9, 1), "Bas"]

    def _chargerEvenementsTSM(self, nomCarte):
        if nomCarte == "TSM-Auberge" and len(self._evenements["concrets"]["TSM-Auberge"]) == 1:
            self._evenements["concrets"]["TSM-Auberge"]["Cuistot1"] = [ Cuistot(self._jeu, self, "Cuistot1"), (6, 27), "Bas"]
            self._evenements["concrets"]["TSM-Auberge"]["Cuistot2"] = [ Cuistot(self._jeu, self, "Cuistot2"), (15, 27), "Haut"]
            self._evenements["concrets"]["TSM-Auberge"]["Nonne"] = [ Nonne(self._jeu, self, 10, 43, 2, "Haut"), (10, 43), "Bas"]
            self._evenements["concrets"]["TSM-Auberge"]["Table1"] = [ Table(self._jeu, self, "Table1"), (22,16), "Haut"]
            self._evenements["concrets"]["TSM-Auberge"]["Table2"] = [ Table(self._jeu, self, "Table2"), (22,16), "Gauche"]
            self._evenements["concrets"]["TSM-Auberge"]["Table3"] = [ Table(self._jeu, self, "Table3"), (22,17), "Gauche"]
            self._evenements["concrets"]["TSM-Auberge"]["Table4"] = [ Table(self._jeu, self, "Table4"), (22,17), "Bas"]
            self._evenements["concrets"]["TSM-Auberge"]["Table5"] = [ Table(self._jeu, self, "Table5"), (23,17), "Bas"]
            self._evenements["concrets"]["TSM-Auberge"]["Table6"] = [ Table(self._jeu, self, "Table6"), (23,17), "Droite"]
            self._evenements["concrets"]["TSM-Auberge"]["Sortie1"] = [ Teleporteur(self._jeu, self, "TSM-Drapier", 7, 28, 2, "Haut", condition="OrdreDrapier", fonctionAvant="texteTransition", parametresFAvant="Ainsi donc, je me rendis chez le drapier."), (9,43), "Aucune"]
            self._evenements["concrets"]["TSM-Auberge"]["Sortie2"] = [ Teleporteur(self._jeu, self, "TSM-Drapier", 7, 28, 2, "Haut", condition="OrdreDrapier", fonctionAvant="texteTransition", parametresFAvant="Ainsi donc, je me rendis chez le drapier."), (10,43), "Aucune"]
        elif nomCarte == "TSM-Drapier" and len(self._evenements["concrets"]["TSM-Drapier"]) == 1:
            self._evenements["concrets"]["TSM-Drapier"]["Drapier"] = [ Drapier(self._jeu, self), (4,16), "Bas" ]
            self._evenements["concrets"]["TSM-Drapier"]["FemmeDrapier"] = [ FemmeDrapier(self._jeu, self), (10,3), "Bas" ]
            self._evenements["concrets"]["TSM-Drapier"]["Vieillard"] = [ ClientDrapier(self._jeu, self, "Vieillard"), (4,19), "Haut" ]
            self._evenements["concrets"]["TSM-Drapier"]["Boulangere"] = [ ClientDrapier(self._jeu, self, "Boulangere"), (4,20), "Haut" ]
            self._evenements["concrets"]["TSM-Drapier"]["Marchand"] = [ ClientDrapier(self._jeu, self, "Marchand"), (8,28), "Haut" ]
            self._evenements["concrets"]["TSM-Drapier"]["Jeune"] = [ ClientDrapier(self._jeu, self, "Jeune"), (4,21), "Haut" ]
            self._evenements["concrets"]["TSM-Drapier"]["Comptoir"] = [Activateur(self._jeu, self, "JoueurComptoir", valeur=True), (4, 19), "Aucune"]
            self._evenements["concrets"]["TSM-Drapier"]["Paiement"] = [Paiement(self._jeu, self), (4, 19), "Aucune"]
            self._evenements["concrets"]["TSM-Drapier"]["Sortie1"] = [ Teleporteur(self._jeu, self, "TSM-Chemin", 5, 15, 3, "Bas", condition="DrapPaiement", noCondition="CheminRetour", fonctionAvant="texteTransition", parametresFAvant="C'est sur le chemin du retour que cela eut lieu."), (7, 28), "Aucune"]
            self._evenements["concrets"]["TSM-Drapier"]["Sortie2"] = [ Teleporteur(self._jeu, self, "TSM-Chemin", 5, 15, 3, "Bas", condition="DrapPaiement", noCondition="CheminRetour", fonctionAvant="texteTransition", parametresFAvant="C'est sur le chemin du retour que cela eut lieu."), (8, 28), "Aucune"]
            self._evenements["concrets"]["TSM-Drapier"]["Sortie3"] = [ Teleporteur(self._jeu, self, "TSM-Chemin", 5, 15, 3, "Bas", condition="CheminRetour"), (7, 28), "Aucune"]
            self._evenements["concrets"]["TSM-Drapier"]["Sortie4"] = [ Teleporteur(self._jeu, self, "TSM-Chemin", 5, 15, 3, "Bas", condition="CheminRetour"), (7, 28), "Aucune"]
        elif nomCarte == "TSM-Chemin" and len(self._evenements["concrets"]["TSM-Chemin"]) == 1: 
            self._evenements["concrets"]["TSM-Chemin"]["Panneau"] = [ Panneau(self._jeu, self, "Vers le haut des collines.", "Haut"), (32,2), "Aucune"]
            self._evenements["concrets"]["TSM-Chemin"]["SortieChamps"] = [ Teleporteur(self._jeu, self, "TSM-Champs", 6, 59, 2, "Haut"), (4, 0), "Aucune"]
            self._evenements["concrets"]["TSM-Chemin"]["SortieDrapier"] = [ Teleporteur(self._jeu, self, "TSM-Drapier", 7, 28, 2, "Haut"), (5, 15), "Aucune"]
        elif nomCarte ==  "TSM-Champs" and len(self._evenements["concrets"]["TSM-Champs"]) == 1:
            self._evenements["concrets"]["TSM-Champs"]["SortieChemin"] = [ Teleporteur(self._jeu, self, "TSM-Chemin", 4, 0, 3, "Bas"), (6, 59), "Aucune"]
            self._evenements["concrets"]["TSM-Champs"]["Paysan"] = [ Paysan(self._jeu, self, "Paysan"), (23, 44), "Bas"]
            self._evenements["concrets"]["TSM-Champs"]["Paysanne"] = [ Paysan(self._jeu, self, "Paysanne"), (36, 27), "Bas"]

    def initialiserBoiteOutils(self):
        self._boiteOutils.initialiser()
    
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
            self._xJoueur, self._yJoueur, self._cJoueur, self._appuiValidationJoueur, self._directionJoueur = x, y, c, appuiJoueur, direction
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
