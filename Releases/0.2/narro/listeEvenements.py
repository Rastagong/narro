# -*-coding:iso-8859-1 -*
import pygame,random
from pygame.locals import *
from .constantes import *
from .evenement import *
from .boiteOutils import *
from .interrupteur import *
from .evenementConcret import *
from .pnj import *

if SESSION_DEBUG:
    from debugger import *

class LanceurPensee(EvenementConcret):
    def __init__(self, jeu, x, y, c, penseeADire, gestionnaire):
        EvenementConcret.__init__(self,jeu,gestionnaire)
        self._etapePensee, self._penseeADire, self._x, self._y = 0, penseeADire, x, y
        self._penseePossible = Interrupteur(self._boiteOutils.penseeAGerer, inverser=True)
        self._joueurDessus = False

    def onJoueurProche(self, x, y, c, direction):
        self._joueurDessus = False

    def traiter(self):
        if self._joueurDessus == True:
            if self._penseeADire == "Arrivee":
                self._penseePossible.majSelonBooleen(self._boiteOutils.penseeAGerer, inverser=True)
                if self._etapePensee == 0 and self._penseePossible.voir() is True:
                    self._boiteOutils.ajouterPensee("J'y étais. Une annonce étrange. Étrange, oui.", vitesse=10, tempsLecture=5000)
                    self._penseePossible.majSelonBooleen(self._boiteOutils.penseeAGerer, inverser=True)
                    self._etapePensee += 1
                elif self._etapePensee == 1 and self._penseePossible.voir() is True:
                    self._boiteOutils.ajouterPensee("C'est mon deuxième passage ici.", vitesse=10)
                    self._etapePensee += 1

    def onJoueurDessus(self, x, y, c, direction):
        self._joueurDessus = True

class AnimateurToucheAction(Evenement):
    def __init__(self, jeu, gestionnaire):
        super().__init__(jeu, gestionnaire)
        self._xJoueur, self._yJoueur = self._gestionnaire.xJoueur, self._gestionnaire.yJoueur
        self._xJoueurOld, self._yJoueurOld = self._xJoueur, self._yJoueur
        self._animation, self._rayon = False, 0

    def traiter(self):
        if self._animation is False and self._gestionnaire.appuiJoueur is True:
            self._animation = True
            self._rayon += 2
            self._boiteOutils.ajouterTransformation(False, "Action Joueur", rayon=self._rayon)
            self._boiteOutils.jouerSon("Whip", "Whip Action Joueur", volume=VOLUME_MUSIQUE/1.5)
            Horloge.initialiser(id(self), "Maj rayon", 1)
        elif self._animation == True and Horloge.sonner(id(self), "Maj rayon") is True:
            self._rayon += 2
            self._boiteOutils.ajouterTransformation(False, "Action Joueur", rayon=self._rayon)
            tempsActuel = pygame.time.get_ticks()
            Horloge.initialiser(id(self), "Maj rayon", 10)
            self._tempsPrecedent = tempsActuel
            if self._rayon == 30:
                self._animation, self._rayon = False, 0
        elif self._animation is False and Horloge.sonner(id(self), "Maj rayon") is True:
            self._boiteOutils.retirerTransformation(False, "Action Joueur")


class Panneau(EvenementConcret):
    def __init__(self, jeu, gestionnaire, message, *directionsMessage):
        super().__init__(jeu, gestionnaire)
        self._message, self._directionsMessage, self._penseePossible = message, directionsMessage, InterrupteurInverse(self._boiteOutils.penseeAGerer)

    def _onJoueurInteractionCote(self, x, y, c, direction):
        if direction in self._directionsMessage and self._penseePossible.voir() is True:
            self._boiteOutils.ajouterPensee(self._message)

class Activateur(EvenementConcret):
    def __init__(self, jeu, gestionnaire, nomInterrupteur, valeur=-1, inverseur=False):
        EvenementConcret.__init__(self, jeu, gestionnaire)
        self._nomInterrupteur, self._valeur, self._inverseur = nomInterrupteur, valeur, inverseur

    def onJoueurDessus(self, x, y, c, direction):
        if isinstance(self._valeur, bool) is True:
            self._boiteOutils.interrupteurs[self._nomInterrupteur].majSelonBooleen(self._valeur)
        elif self._inverseur is True:
            self._boiteOutils.interrupteurs[self._nomInterrupteur].inverser()

class Teleporteur(EvenementConcret):
    def __init__(self, jeu, gestionnaire, nomCarte, x=-1, y=-1, c=-1, direction=-1, transition=True, condition=True, noCondition=True, fonctionAvant=False, parametresFAvant=[], fonctionApres=False):
        """Téléporte le joueur sur la carte <nomCarte>.
        * On peut spécifier une position de destination <x><y><c> avec une <direction> à l'arrivée. Quand ce n'est pas spécifié, le joueur se retrouve à la même position sur l'autre carte.
        * Une <transition> a lieu sauf quand cela vaut <False>.
        * Il est possible de n'exécuter la téléportation que lorsque l'interrupteur <condition> est activé et/ou l'interrupteur <noCondition> désactivé.
        * Une <fonctionAvant>, identifiée par une <str> (à lier à une méthode du téléporteur) peut être appelée avec ses <parametresFAvant> juste avant la téléportation.
          Elle bloque la téléportation jusqu'à ce qu'elle retourne <True> (elle est appelée à chaque traitement du téléporteur).
        * Une <fonctionApres> peut être appelée juste après la téléportation."""
        EvenementConcret.__init__(self, jeu, gestionnaire)
        self._nomCarte, self._transition, self._teleportationRetardee, self._etapeTexteTransition = nomCarte, True, False, 0
        self._xDestination, self._yDestination, self._coucheDestination, self._directionDestination, self._condition, self._noCondition = x, y, c, direction, condition, noCondition
        self._coefNoircisseur, self._fonctionAvant, self._fonctionApres, self._resultatFonctionAvant, self._executionTeleportation = 1, fonctionAvant, fonctionApres, True, False
        self._parametresFonctionAvant = parametresFAvant
        if self._fonctionAvant == "texteTransition":
            self._fonctionAvant = self._texteTransition
        self._penseePossible = InterrupteurInverse(self._boiteOutils.penseeAGerer)

    def onJoueurDessus(self, x, y, c, direction):
        teleportationAutoriseeCondition, teleportationAutoriseeNoCondition = False, False
        if self._condition is True: #Pas de condition spécifiée, on téléporte
            teleportationAutoriseeCondition = True
        elif self._condition in self._boiteOutils.interrupteurs.keys(): #Condition spécifiée : on ne téléporte que si l'interrupteur est activé
            if self._boiteOutils.interrupteurs[self._condition].voir() is True:
                teleportationAutoriseeCondition = True
        if self._noCondition is True:
            teleportationAutoriseeNoCondition = True
        elif self._noCondition in self._boiteOutils.interrupteurs.keys(): #NoCondition spécifiée : on ne téléporte que si l'interrupteur est désactivé
            if self._boiteOutils.interrupteurs[self._noCondition].voir() is False:
                teleportationAutoriseeNoCondition = True
        if teleportationAutoriseeCondition is True and teleportationAutoriseeNoCondition is True and self._boiteOutils.getJoueurMouvement() is True: 
            if self._xDestination == -1:
                self._xDestination = x
            if self._yDestination == -1:
                self._yDestination = y
            if self._coucheDestination == -1:
                self._coucheDestination = c
            if self._directionDestination == -1:
                self._directionDestination = direction
            if self._transition is False:
                self._executionTeleportation = True
            else: #Transition de téléportation
                Horloge.initialiser(id(self), 1, 300)
                self._teleportationRetardee = True

    def traiter(self):
        if self._teleportationRetardee is True and self._executionTeleportation is False: #On est en transition
            if Horloge.sonner(id(self), 1) is False: #On gère la transition, ce n'est pas fini
                self._coefNoircisseur += 1
                self._boiteOutils.ajouterTransformation(True, "Noir", coef=self._coefNoircisseur)
                self._boiteOutils.mettreToutAChanger()
            else: #On téléporte enfin
                self._executionTeleportation = True
        elif self._executionTeleportation is True: #On téléporte (transition finie ou téléportation sans transition)
            if self._fonctionAvant != False: #S'il faut exécuter une fonction avant
                self._resultatFonctionAvant = self._fonctionAvant(self._parametresFonctionAvant)
            if self._resultatFonctionAvant is True: #Si la fonction avant dit qu'on peut téléporter // Si aucune fonction avant n'est à appeler
                self._boiteOutils.teleporterSurCarte(self._nomCarte, self._xDestination, self._yDestination, self._coucheDestination, self._directionDestination)
                self._executionTeleportation, self._teleportationRetardee = False, False
                if self._fonctionApres is not False: 
                    self._fonctionApres()

    def _texteTransition(self, texte):
        if self._etapeTexteTransition == 0 and self._penseePossible.voir() is True: #Première étape : noir total et affichage du texte, on ne téléporte pas
            self._boiteOutils.joueurLibre.desactiver()
            self._boiteOutils.ajouterTransformation(True, "NoirTotal")
            self._boiteOutils.ajouterPensee(texte, tempsLecture=0)
            self._etapeTexteTransition += 1
            return False
        elif self._etapeTexteTransition == 1 and self._penseePossible.voir() is True: #Deuxième étape : texte affiché, on peut téléporter
            self._boiteOutils.joueurLibre.activer()
            self._etapeTexteTransition += 1
            return True
        elif self._etapeTexteTransition == 2:
            return True
        else:
            return False


class ModulateurMusique(Evenement):
    def __init__(self, jeu, gestionnaire):
        super().__init__(jeu, gestionnaire)
        self._volume =  pygame.mixer.music.get_volume()
        self._xJoueur, self._yJoueur = self._gestionnaire.xJoueur, self._gestionnaire.yJoueur
        self._xJoueurOld, self._yJoueurOld, self._besoinInitialisation = self._xJoueur, self._yJoueur, True

    def traiter(self):
        self._xJoueurOld, self._yJoueurOld = self._xJoueur, self._yJoueur
        (self._xJoueur, self._yJoueur) = self._boiteOutils.getCoordonneesJoueur()
        if self._xJoueur != self._xJoueurOld or self._yJoueur != self._yJoueurOld or self._besoinInitialisation is True:
            self._boiteOutils.gererVolumeSonsFixes(self._xJoueur, self._yJoueur)
            self._besoinInitialisation = False



