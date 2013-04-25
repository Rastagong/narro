import pygame,random
import pympler.summary, pympler.muppy, pympler.tracker, pympler.refbrowser
from pympler.classtracker import ClassTracker
from tkinter import *
from pygame.locals import *
import numpy as N
import pygame.surfarray as A
from constantes import *
from evenement import *
from boiteOutils import *
from interrupteur import *
from evenementConcret import *
from pnj import *

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

class Panneau(EvenementConcret):
    def __init__(self, jeu, gestionnaire, message, *directionsMessage):
        super().__init__(jeu, gestionnaire)
        self._message, self._directionsMessage, self._penseePossible = message, directionsMessage, InterrupteurInverse(self._boiteOutils.penseeAGerer)

    def _onJoueurInteractionCote(self, x, y, c, direction):
        if direction in self._directionsMessage and self._penseePossible.voir() is True:
            self._boiteOutils.ajouterPensee(self._message)

class Paiement(EvenementConcret):
    def __init__(self, jeu, gestionnaire):
        EvenementConcret.__init__(self, jeu, gestionnaire)

    def _onJoueurInteractionDessus(self, x, y, c, direction):
        EvenementConcret._onJoueurInteractionDessus(self, x, y, c, direction)
        if direction is "Haut" and self._boiteOutils.interrupteurs["DrapDonne"].voir() is True and self._boiteOutils.interrupteurs["DrapPaiement"].voir() is False:
            self._boiteOutils.interrupteurs["DrapPaiement"].activer()
            self._boiteOutils.jouerSon("sonPiece", "paiementDrap")

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

class Debugger(Evenement):
    def __init__(self, jeu, gestionnaire, methode=False):
        print("start")
        super().__init__(jeu, gestionnaire)
        self._debugFait, self._methode = 0, methode
        if self._methode is not False:
            if self._methode == "Instance":
                self._tracker = ClassTracker()
                self._tracker.track_class(Evenement)
                self._tracker.create_snapshot("Initialisation")
            elif self._methode == "Fuites":
                self._tracker = pympler.tracker.SummaryTracker()
                self._tracker.print_diff()
            Horloge.initialiser(id(self), 1, 3000)

    def cmp(self, obj):
        return str(type(obj))

    def traiter(self):
        if Horloge.sonner(id(self), 1) is True:
            if self._methode == "Instance":
                if self._debugFait < 3:
                    self._tracker.create_snapshot("Etape n°" + str(self._debugFait))
                    self._debugFait += 1
                    Horloge.initialiser(id(self), 1, 3000)
                else:
                    self._tracker.stats.print_summary()
            elif self._methode == "Fuites":
                self._tracker.print_diff()
                Horloge.initialiser(id(self), 1, 3000)

class Narrateur(Evenement):
    def __init__(self, jeu, gestionnaire):
        super().__init__(jeu, gestionnaire)
        self._penseePossible, self._etape = InterrupteurInverse(self._boiteOutils.penseeAGerer), 0
    
    def traiter(self):
        x, y = self._gestionnaire.xJoueur, self._gestionnaire._yJoueur
        if self._boiteOutils.nomCarte == "TSM-Auberge":
            if self._etape == 0 and self._penseePossible.voir() is True:
                self._boiteOutils.ajouterPensee("Je n'étais pas si mal, ce soir-là, dans cette petite auberge.")
                self._boiteOutils.ajouterPensee("Une paie suffisante, des cuistots agréables,", tempsLecture=2000)
                self._boiteOutils.ajouterPensee("quelques voyageurs à servir de temps à autre.")
                self._boiteOutils.ajouterPensee("Tout ce dont une servante pouvait rêver.", tempsLecture=0)
                self._etape += 1
            if self._etape == 1 and self._penseePossible.voir() is True: #Pensée précédente écrite
                self._boiteOutils.interrupteurs["Ordre1A"].activer()
                self._etape += 1
            if self._etape == 2 and self._boiteOutils.interrupteurs["Mission1"].voir() is True:
                self._boiteOutils.ajouterPensee("La Muette, c'est moi. Je ne parle jamais, ou presque.", tempsLecture=2250)
                self._etape += 1
        if self._boiteOutils.nomCarte == "TSM-Chemin":
            if self._etape == 3:
                self._boiteOutils.interrupteurs["CheminRetour"].activer()
                self._boiteOutils.ajouterPensee("Je devais traverser les collines pour revenir.", vitesse=75)
                self._boiteOutils.ajouterPensee("Le soleil n'était pas encore très haut.", vitesse=75)
                self._etape += 1
        if self._boiteOutils.nomCarte == "TSM-Champs":
            if self._etape == 0:
                self._etape = 4
            if self._etape == 4 and x >= 42 and y >=  49:
                self._boiteOutils.interrupteurs["RocherVu"].activer()
                self._etape += 1
            elif self._etape == 5 and x >= 10 and x <= 24 and y <= 51 and y >= 43:
                Horloge.initialiser(id(self), "Promenade champs", 5000)
                self._etape += 1
            elif self._etape == 6 and Horloge.sonner(id(self), "Promenade champs") is True and x >= 10 and x <= 24 and y <= 51 and y >= 43:
                self._boiteOutils.interrupteurs["JoueurSeulChamps"].activer()

class Paysan(PNJ):
    def __init__(self, jeu, gestionnaire, nom):
        if nom == "Paysan":
            x, y, c, self._penseeDite = 23, 44, 2, False
            fichier, couleurTransparente, persoCharset, dureeDeplacement = "Paysan.png", (0,0,0), (0,0), DUREE_DEPLACEMENT_MOBILE_PAR_DEFAUT
            repetitionActions, directionDepart = True, "Bas"
            listeActions = ["VBas1000", "Bas"] * 6
            self._cheminMoisson = ["Depart"]
        elif nom == "Paysanne":
            x, y, c = 36, 27, 2
            fichier,  couleurTransparente, persoCharset = "Paysanne.png", (0,0,0), (0,0)
            repetitionActions, directionDepart, dureeDeplacement = True, "Bas", 500
            trajetPommier = ["VGauche750", "Haut", "Gauche", "Gauche", "Gauche", "Gauche", "Gauche", "Bas"]
            listeActions = (trajetPommier * 6) + ["VGauche750", "Haut"] + (30 * ["Droite"]) + ["Bas"]
        super().__init__(jeu, gestionnaire, nom, x, y, c, fichier, couleurTransparente, persoCharset, repetitionActions, listeActions, directionDepart=directionDepart, dureeDeplacement=dureeDeplacement)

    def _gererEtape(self):
        if self._nom == "Paysan":
            if self._etapeTraitement == 1 and self._etapeMarche == 1 and isinstance(self._etapeAction/2, int) == False:
                if len(self._cheminMoisson) == 1:
                    self._cheminMoisson.append("Fin")
                else:
                    self._cheminMoisson.insert(len(self._cheminMoisson) - 1, "Tronçon")
                self._boiteOutils.changerBloc(int(self._x/32), int(self._y/32), 0, "TerrainChampsJaunes.png", (224, 480, 32, 32), (0,0,0), True)
            if self._etapeTraitement == 2 and self._etapeMarche == 1 and self._boiteOutils.interrupteurs["JoueurSeulChamps"].voir() is True:
                self._lancerTrajetEtoile(self._boiteOutils.cheminVersJoueur, self._x/32, self._y/32, self._c)
                self._etapeTraitement += 1
            if self._etapeTraitement == 3 and self._etapeMarche == 1:
                self._majInfosJoueur()
                if self._joueurProche is True:
                    if self._penseeDite == False:
                        self._boiteOutils.ajouterPensee("Holà ! On a besoin de mains pour la moisson. Ça te dit de nous aider ?")
                        self._penseeDite = True
                    self._lancerTrajet(self._boiteOutils.deplacementSPVersPnj("Joueur", 500, self._x/32, self._y/32), True)
                if self._joueurBouge[0] is True:
                    self._lancerTrajetEtoile(self._boiteOutils.cheminVersJoueur, self._x/32, self._y/32, self._c)

class Drapier(PNJ):
    def __init__(self, jeu, gestionnaire):
        x, y, c = 4, 16, 2
        nom, fichier, couleurTransparente, persoCharset = "Drapier", "People1.png", (0,0,0), (0,1)
        listeActions, repetitionActions, directionDepart = ["Aucune"], False, "Bas"
        super().__init__(jeu, gestionnaire, nom, x, y, c, fichier, couleurTransparente, persoCharset, repetitionActions, listeActions, directionDepart=directionDepart)
        self._penseePossible, self._etapeSon, self._penseeDite = InterrupteurInverse(self._boiteOutils.penseeAGerer), 0, False
    
    def _gererEtape(self):
        if self._etapeTraitement == 1 and self._boiteOutils.interrupteurs["ActionDrapier"].voir() is True:
            self._lancerTrajet(["VBas500"], True)
            self._etapeTraitement += 1
        if self._etapeTraitement == 2 and self._boiteOutils.interrupteurs["ActionDrapier"].voir() is False:
            self._finirDeplacementSP()
            self._lancerTrajet(["Aucune"], False)
            self._boiteOutils.jouerSon("sonPiece", "paiementClient")
            self._etapeTraitement -= 1
        if self._etapeTraitement == 2 and self._boiteOutils.interrupteurs["ChapeauPose"].voir() is True:
            self._boiteOutils.interrupteurs["ActionDrapier"].desactiver()
            self._boiteOutils.interrupteurs["EntreeMarchand"].activer()
            self._finirDeplacementSP()
            self._lancerTrajet("Droite", "Droite", "VDroite1000", "Gauche", "Gauche", "VHaut2500", "Gauche", "VHaut2500", "Droite", "Droite", "Droite", "VDroite1000", False)
            self._etapeTraitement += 1
        if self._etapeTraitement == 3:
            if self._deplacementBoucle is False:
                self._boiteOutils.changerBloc(7, 16, 2, -1, -1, -1, -1, vide=True)
                self._lancerTrajet("Gauche","Gauche","VBas1000", "Aucune", False)
                self._etapeTraitement += 1
            elif self._etapeAction == 4 and self._etapeSon == 0:
                self._boiteOutils.jouerSon("sonPlacard", "PlacardChapeau1", duree=2500, fixe=True, evenementFixe="Drapier")
                self._etapeSon += 1
            elif self._etapeAction == 6 and self._etapeSon == 1:
                self._boiteOutils.jouerSon("sonPlacard", "PlacardChapeau2", duree=2500, fixe=True, evenementFixe="Drapier")
                self._etapeSon += 1
        if self._etapeTraitement == 4 and self._deplacementBoucle is False:
            self._boiteOutils.interrupteurs["ChapeauDonne"].activer()
            self._boiteOutils.jouerSon("sonPiece", "paiementClient")
            self._etapeTraitement += 1
        if self._etapeTraitement == 5 and self._boiteOutils.interrupteurs["ActionDrapier"].voir() is True:
            self._lancerTrajet(["VBas500"], True)
            self._etapeTraitement += 1
        if self._etapeTraitement == 5 and self._boiteOutils.interrupteurs["JoueurComptoir"].voir() is True and self._penseeDite is False:
            self._boiteOutils.ajouterPensee("Ah, bonjour la Muette ! Un drap ? Vois donc avec Cristina.")
            self._penseeDite = True
            self._boiteOutils.interrupteurs["JoueurDrap"].activer()
            self._etapeTraitement += 1
        if self._etapeTraitement == 5 and self._boiteOutils.interrupteurs["DrapComptoir"].voir() is True:
            self._lancerTrajet("Droite", "Droite", False)
            self._etapeTraitement = 7
        if self._etapeTraitement == 6 and self._boiteOutils.interrupteurs["ActionDrapier"].voir() is False:
            self._finirDeplacementSP()
            self._lancerTrajet(["Aucune"], False)
            self._majInfosJoueur()
            if not (self._xJoueur[0] == 4 and self._yJoueur[0] == 19):
                self._boiteOutils.jouerSon("sonPiece", "paiementClient")
            self._etapeTraitement -= 1
        if self._etapeTraitement == 7 and self._boiteOutils.interrupteurs["DrapDonne"].voir() is True:
            self._lancerTrajet("Gauche", "Gauche", "RBas", False)
            self._etapeTraitement += 1
        if self._etapeTraitement == 8 and self._deplacementBoucle is False:
            self._boiteOutils.ajouterPensee("Et voilà, trois pieds de lin. Ça fera dix couronnes.")
            self._lancerTrajet("VBas1000", False)
            self._etapeTraitement += 1
        if self._etapeTraitement == 9 and self._boiteOutils.interrupteurs["DrapPaiement"].voir() is True:
            self._finirDeplacementSP()
            self._lancerTrajet("VBas1000", "RBas", False)
            self._boiteOutils.ajouterPensee("Merci beaucoup, et à très bientôt !")
            self._etapeTraitement += 1

class FemmeDrapier(PNJ):
    def __init__(self, jeu, gestionnaire):
        x, y, c = 10, 3, 2
        nom, fichier, couleurTransparente, persoCharset = "FemmeDrapier", "People1.png", (0,0,0), (1,1)
        listeActions, repetitionActions, directionDepart = ["Aucune"], False, "Bas"
        super().__init__(jeu, gestionnaire, nom, x, y, c, fichier, couleurTransparente, persoCharset, repetitionActions, listeActions, directionDepart=directionDepart)
        self._penseePossible, self._trouve, self._penseeDite = InterrupteurInverse(self._boiteOutils.penseeAGerer), False, False

    def _gererEtape(self):
        if self._etapeTraitement == 1 and self._boiteOutils.interrupteurs["AttenteChapeau"].voir() is True:
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._x/32, self._y/32, self._c, 8, 16)
            self._etapeTraitement += 1
        if self._etapeTraitement == 2 and self._deplacementBoucle is False and self._x/32 == 8 and self._y/32 == 16:
            self._lancerTrajet("VGauche1000", False)
            self._etapeTraitement += 1
        if self._etapeTraitement == 3 and self._deplacementBoucle is False:
            self._boiteOutils.changerBloc(7, 16, 2, "Interieur.png", (480, 384, 32, 32), (0,0,0), False)
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._x/32, self._y/32, self._c, 11, 3, regardFinal="Bas")
            self._boiteOutils.interrupteurs["ChapeauPose"].activer()
            self._etapeTraitement += 1
        if self._etapeTraitement == 4 and self._deplacementBoucle is False and self._boiteOutils.interrupteurs["JoueurDrap"].voir() is True:
            self._etapeTraitement += 1
        if self._etapeTraitement == 5 and (self._etapeMarche == 1 or self._listeActions[self._etapeAction][0] == "V"):
            self._majInfosJoueur()
            if self._joueurProche is True and self._trouve is False:
                self._lancerTrajet(self._boiteOutils.deplacementSPVersPnj("Joueur", 500, self._x/32, self._y/32), True)
                if self._penseeDite is False:
                    self._boiteOutils.ajouterPensee("Suis-moi, je crois avoir ce qu'il te faut.", tempsLecture=0)
                    self._penseeDite = True
                self._trouve = True
            if self._joueurBouge[0] is True:
                self._finirDeplacementSP()
                self._trouve = False
                self._lancerTrajetEtoile(self._boiteOutils.cheminVersJoueur, self._x/32, self._y/32, self._c)
            if self._penseeDite is True and self._penseePossible.voir() is True and (self._etapeMarche == 1 or self._listeActions[self._etapeAction] == "V"):
                self._finirDeplacementSP()
                self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._x/32, self._y/32, self._c, 5, 8, regardFinal="Haut")
                self._etapeTraitement += 1
        if self._etapeTraitement == 6 and self._deplacementBoucle is False and self._x/32 == 5 and self._y/32 == 8:
            self._lancerTrajet("VHaut2500", False)
            self._boiteOutils.jouerSon("sonPlacard", "rechercheDrap", fixe=True, duree=2500, evenementFixe="FemmeDrapier")
            self._etapeTraitement += 1
        if self._etapeTraitement == 7 and self._deplacementBoucle is False:
            self._finirDeplacementSP()
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._x/32, self._y/32, self._c, 8, 16)
            self._boiteOutils.interrupteurs["DrapComptoir"].activer()
            self._etapeTraitement += 1
        if self._etapeTraitement == 8 and self._deplacementBoucle is False and self._x/32 == 8 and self._y/32 == 16:
            self._lancerTrajet("VGauche1000", "RBas", False)
            self._etapeTraitement += 1
        if self._etapeTraitement == 9 and self._deplacementBoucle is False:
            self._boiteOutils.interrupteurs["DrapDonne"].activer()

class ClientDrapier(PNJ):
    avancee = dict()

    def __init__(self, jeu, gestionnaire, nom):
        poseDepart, self._pnjEcran, self._roleComptoir, self._etapeComptoir = True, True, False, 0
        if nom is "Vieillard":
            x, y, c = 4, 19, 2
            fichier, couleurTransparente, persoCharset = "People1.png", (0,0,0), (2,1)
            listeActions, repetitionActions, directionDepart = ["Aucune"], False, "Haut"
        elif nom is "Boulangere":
            x, y, c = 4, 20, 2
            fichier, couleurTransparente, persoCharset = "Boulangere.png", (0,0,0), (0,0)
            listeActions, repetitionActions, directionDepart = ["Aucune"], False, "Haut"
            ClientDrapier.avancee[nom] = Interrupteur(False)
        elif nom is "Jeune":
            x, y, c = 4, 21, 2
            fichier, couleurTransparente, persoCharset = "People1.png", (0,0,0), (2,0)
            listeActions, repetitionActions, directionDepart = ["Aucune"], False, "Haut"
            ClientDrapier.avancee[nom] = Interrupteur(False)
        elif nom is "Marchand":
            x, y, c = 8, 28, 2
            fichier, couleurTransparente, persoCharset = "People2.png", (0,0,0), (3,0)
            listeActions, repetitionActions, directionDepart, poseDepart = ["Aucune"], False, "Haut", False
            ClientDrapier.avancee[nom], self._pnjEcran = Interrupteur(True), False
        super().__init__(jeu, gestionnaire, nom, x, y, c, fichier, couleurTransparente, persoCharset, repetitionActions, listeActions, directionDepart=directionDepart,poseDepart=poseDepart)
        self._penseePossible = InterrupteurInverse(self._boiteOutils.penseeAGerer)

    def _gererEtape(self):
        if self._nom is "Marchand" and self._boiteOutils.interrupteurs["EntreeMarchand"].voir() is True and Horloge.alarmeExiste(id(self), "Arrivee marchand") is False:
            Horloge.initialiser(id(self), "Arrivee marchand", 1000)
        if self._nom is "Marchand" and Horloge.sonner(id(self), "Arrivee marchand") is True and self._etapeTraitement == 0:
            self._pnjEcran, self._poseDepart = True, True
        if self._nom is "Marchand" and self._etapeTraitement == 1:
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._x/32, self._y/32, self._c, 4, 22)
            self._etapeTraitement += 1
        if self._nom is "Marchand" and self._etapeTraitement == 2 and self._deplacementBoucle is False:
            self._courage = False
            self._lancerTrajet("Haut", "Aucune", False)
            self._etapeTraitement += 1
        if self._nom is "Marchand" and self._etapeTraitement == 3 and self._deplacementBoucle is False:
            ClientDrapier.avancee["Marchand"].desactiver()
            self._etapeTraitement += 1
        if (self._nom is "Vieillard" or self._nom is "Jeune" or self._nom is "Boulangere" or self._nom is "Marchand") and self._x/32 == 4 and self._y/32 == 19 and self._deplacementBoucle is False and self._etapeComptoir == 0:
            self._roleComptoir, self._etapeComptoir = True, 1
            if self._nom is "Marchand":
                self._courage = True
        if (self._nom is "Vieillard" or self._nom is "Jeune" or self._nom is "Boulangere" or self._nom is "Marchand") and self._roleComptoir is True:
            if self._etapeComptoir == 1:
                self._finirDeplacementSP()
                self._lancerTrajet(["VHaut500"], True)
                Horloge.initialiser(id(self), "Attente comptoir1", 2000)
                if self._nom is "Boulangere":
                    self._boiteOutils.interrupteurs["AttenteChapeau"].activer()
                self._etapeComptoir += 1
            if self._etapeComptoir == 2 and Horloge.sonner(id(self), "Attente comptoir1") is True:
                self._finirDeplacementSP()
                self._lancerTrajet(["Aucune"], False)
                self._boiteOutils.interrupteurs["ActionDrapier"].activer()
                if self._nom is not "Boulangere":
                    Horloge.initialiser(id(self), "Attente comptoir2", 2000)
                self._etapeComptoir += 1
            if self._etapeComptoir == 3 and ((self._nom is not "Boulangere" and Horloge.sonner(id(self), "Attente comptoir2") is True) or (self._nom is "Boulangere" and self._boiteOutils.interrupteurs["ChapeauDonne"].voir() is True)):
                    self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._x/32, self._y/32, 2, 8, 28)
                    self._boiteOutils.interrupteurs["ActionDrapier"].desactiver()
                    self._boiteOutils.interrupteurs["QueueDrapier"].activer()
                    self._etapeComptoir += 1
            if self._etapeComptoir == 4 and self._deplacementBoucle is False and self._x/32 == 8 and self._y/32 == 28:
                self._boiteOutils.supprimerPNJ(self._nom, self._c)
                self._pnjEcran = False
                self._etapeComptoir = 0
        elif  (self._nom is "Jeune" or self._nom is "Boulangere" or self._nom is "Marchand") and self._boiteOutils.interrupteurs["QueueDrapier"].voir() is True and self._pnjEcran is True and self._deplacementBoucle is False:
            self._lancerTrajet(["Haut","Aucune"], False)
            ClientDrapier.avancee[self._nom].activer()
            toutLeMondeAAvance = True
            for pnj in ClientDrapier.avancee.keys():
                if ClientDrapier.avancee[pnj].voir() is False:
                    toutLeMondeAAvance = False
                #print(pnj,ClientDrapier.avancee[pnj].voir())
            if toutLeMondeAAvance is True:
                self._boiteOutils.interrupteurs["QueueDrapier"].desactiver()
                for interrup in ClientDrapier.avancee.values():
                    interrup.desactiver()

class Table(EvenementConcret):
    def __init__(self, jeu, gestionnaire, nom):
        super().__init__(jeu, gestionnaire)
        self._nom = nom

    def _onJoueurInteractionFace(self, xJoueur, yJoueur, c, direction):
        if self._boiteOutils.interrupteurs["Mission1"].voir() is True and self._boiteOutils.interrupteurs["PlatPosé"].voir() is False: #Si la Maid doit poser le plat MAIS pas encore fait
            (x,y) = self._boiteOutils.getCoordonneesEvenement(self._nom)
            self._boiteOutils.changerBloc(x, y, 2, "Interieur.png", (320, 320, 32, 32), (255, 255, 255), False)
            self._boiteOutils.interrupteurs["PlatPosé"].activer()

class Cuistot(PNJ):
    def __init__(self, jeu, gestionnaire, nom):
        self._etapeSon, self._iterations = 0, 0
        if nom is "Cuistot1":
            x, y, c = 6, 27, 2
            fichier, couleurTransparente, persoCharset = "Cuistot.png", (0,0,0), (0,0)
            repetitionActions, directionDepart = True, "Bas"
            dureeDeplacement = 400 #350
            frequenceAnimation = 200 #4
            frequenceDeplacement = 16 #16
            intelligence = False
            self._listeActions1 = ["Bas","Droite","Bas","VBas2500","Haut","Gauche","Gauche","Gauche","Haut","VHaut2500","Gauche","Gauche","VHaut2500"]
            self._listeActions2 = ["Droite","VHaut1000","Droite","VHaut2500","Droite","VHaut500","Droite","VHaut500"]
            self._listeActions3 = ["Droite","Droite","Droite","Droite","Droite","Droite","VHaut2500","Gauche","Gauche","Gauche","VHaut2500","Gauche","Gauche","Gauche"]
            self._listeActions4 = ["VHaut700","Gauche","VHaut700","Droite"]
            self._tileChange = False
            self._listeActionsOriginale = self._listeActions1 + self._listeActions2 + self._listeActions3 + self._listeActions4
            listeActions = list(self._listeActionsOriginale)
            self._infini, self._penseeDuc = False, False
        elif nom is "Cuistot2":
            x, y, c = 15, 27, 2
            fichier, couleurTransparente, persoCharset = "Cuistot.png", (0,0,0), (0,0)
            repetitionActions, directionDepart = False, "Bas"
            dureeDeplacement = 400#350
            frequenceAnimation = 200 #4
            frequenceDeplacement = 16 #16
            intelligence = True
            listeActions = ["Bas"]
        super().__init__(jeu,gestionnaire,nom,x,y,c,fichier,couleurTransparente,persoCharset,repetitionActions,listeActions,dureeDeplacement=dureeDeplacement,frequenceAnimation=frequenceAnimation, frequenceDeplacement=frequenceDeplacement, directionDepart=directionDepart,intelligence=intelligence)
        self._penseePossible = InterrupteurInverse(self._boiteOutils.penseeAGerer)

    def _initialiserDeplacement(self, *args, **argsv):
        super()._initialiserDeplacement(*args, **argsv)
        if self._nom is "Cuistot2":
            self._positionNonne = self._boiteOutils.getCoordonneesEvenement("Nonne")
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._x/32, self._y/32, self._c, self._positionNonne[0], self._positionNonne[1], arretAvant=True, regardAvant=True)

    def _gererSonsCuisine(self):
        if self._etapeAction == 3 and self._etapeSon == 0:
            self._boiteOutils.jouerSon("sonGrain","Grain", duree=2500, fixe=True, evenementFixe="Cuistot1")
            self._etapeSon += 1
        elif (self._etapeAction == 8 and self._etapeSon == 1) or (self._etapeAction == 15 and self._etapeSon == 3):
            self._boiteOutils.jouerSon("sonCouteau", "Couteau", nombreEcoutes=3, fixe=True, evenementFixe="Cuistot1")
            self._etapeSon += 1
        elif self._etapeAction == 11 and self._etapeSon == 2:
            self._boiteOutils.jouerSon("sonEau","Eau", duree=2500, fixe=True, evenementFixe="Cuistot1")
            self._etapeSon += 1
        elif (self._etapeAction == 25 and self._etapeSon == 4) or (self._etapeAction == 29 and self._etapeSon == 5):
            self._boiteOutils.jouerSon("sonPlacard","Placard", duree=2500, fixe=True, evenementFixe="Cuistot1")
            self._etapeSon = 0

    def _gererEtape(self):
        #Cuistot1
        if self._nom is "Cuistot1":
            if self._etapeTraitement == 1 and self._etapeAction < len(self._listeActions):
                self._gererSonsCuisine()
            if self._etapeTraitement == 1 and self._etapeAction == 15 and self._tileChange is False:
                self._boiteOutils.changerBloc(3, 26, 3, "Interieur.png", (320, 320, 32, 32), (255, 255, 255), False)
                self._tileChange = True
            if self._etapeTraitement == 1 and self._etapeAction == len(self._listeActions):
                self._iterations += 1
                self._etapeSon = 0
            if self._etapeTraitement == 1 and self._etapeMarche == 1 and self._boiteOutils.interrupteurs["Ordre1A"].voir() is True:
                self._majInfosJoueur()
                self._lancerTrajetEtoile(self._boiteOutils.cheminVersJoueur, self._x/32, self._y/32, self._c)
                self._etapeTraitement += 1
            if self._etapeTraitement == 2 and self._etapeMarche == 1:
                self._majInfosJoueur()
                if self._joueurBouge[0] is True:
                    self._lancerTrajetEtoile(self._boiteOutils.cheminVersJoueur, self._x/32, self._y/32, self._c)
                if self._joueurProche is True and self._deplacementBoucle is False: #Si on a atteint le joueur (fin de nos actions + joueur proche)
                    self._boiteOutils.ajouterPensee("— Eh, la Muette ! Viens donc voir par ici, j'ai du boulot pour toi.", tempsLecture=0)
                    self._etapeTraitement += 1
            if self._etapeTraitement == 3:
                    self._majInfosJoueur()
                    if self._etapeMarche == 1:
                        self._majInfosJoueur(i=1)
                    if self._joueurBouge[1] is True and self._etapeMarche == 1:
                        self._lancerTrajetEtoile(self._boiteOutils.cheminVersJoueur, self._x/32, self._y/32, self._c)
                    if self._penseePossible.voir() is False and self._joueurProche is True and self._deplacementBoucle is False:
                        self._lancerTrajet(self._boiteOutils.deplacementSPVersPnj("Joueur", 0, self._x/32, self._y/32), False)
                        self._infini = True
                        self._etapeTraitement += 1
                    elif self._penseePossible.voir() is True and self._joueurProche is True and self._deplacementBoucle is False:
                        self._lancerTrajet(self._boiteOutils.deplacementSPVersPnj("Joueur", 1000, self._x/32, self._y/32), False)
                        self._majInfosJoueur(i=1)
                        self._infini = False
                        self._etapeTraitement += 1
            if self._etapeTraitement == 4:
                self._majInfosJoueur()
                if self._deplacementBoucle is True and self._joueurProche is False and self._infini is True:
                    self._finirDeplacementSP()
                if self._deplacementBoucle is True and self._joueurProche is False and self._infini is False:
                    self._finirDeplacementSP()
                if self._deplacementBoucle is True and self._joueurProche is True and self._infini is True and self._penseePossible.voir() is True:
                    self._finirDeplacementSP()
                if self._deplacementBoucle is False and self._joueurProche is False:
                    self._lancerTrajetEtoile(self._boiteOutils.cheminVersJoueur, self._x/32, self._y/32, self._c)
                    self._majInfosJoueur(i=1)
                    self._etapeTraitement -= 1
                elif self._deplacementBoucle is False and self._joueurProche is True:
                    self._etapeTraitement += 1
            if self._etapeTraitement == 5 and self._penseePossible.voir() is True:
                self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._x/32, self._y/32, self._c, 3, 26, regardAvant=True, arretAvant=True)
                self._boiteOutils.jouerSon("Interlude", "musiqueInterlude", nombreEcoutes=0, volume=VOLUME_LONGUE_MUSIQUE)
                self._etapeTraitement += 1
            if self._etapeTraitement == 6 and self._x/32 == 3 and self._y/32 == 27:
                self._majInfosJoueur()
                if self._joueurProche is True and self._penseePossible.voir() is True:
                    self._lancerTrajet(self._boiteOutils.deplacementSPVersPnj("Joueur", 0, self._x/32, self._y/32), False)
                    self._boiteOutils.ajouterPensee("Tiens, prends ce plat et porte-le dans la grande chambre à l'étage.", tempsLecture=1000)
                    self._boiteOutils.changerBloc(3, 26, 3, -1, -1, -1, -1, vide=True)
                    self._etapeTraitement += 1
            if self._etapeTraitement == 7 and self._penseePossible.voir() is True:
                self._boiteOutils.interrupteurs["Mission1"].activer()
                self._finirDeplacementSP()
                self._etapeTraitement += 1
            if self._etapeTraitement == 8 and self._deplacementBoucle is False:
                self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._x/32, self._y/32, self._c, 6, 27)
                self._etapeTraitement += 1
            if self._etapeTraitement == 9 and self._deplacementBoucle is False and self._x/32 == 6 and self._y/32 == 27:
                self._lancerTrajet(self._listeActionsOriginale, True)
                self._etapeSon = 0
                self._etapeTraitement += 1
            if self._etapeTraitement == 10:
                self._gererSonsCuisine()
                if self._etapeMarche == 1 and self._boiteOutils.interrupteurs["PlatPosé"].voir() is True:
                    self._seTeleporter(34, 36, "Haut")
                    self._lancerTrajetEtoile(self._boiteOutils.cheminVersJoueur, self._x/32, self._y/32, self._c, )
                    self._majInfosJoueur()
                    self._etapeTraitement += 1
            if self._etapeTraitement == 11 and (self._etapeMarche == 1 or self._listeActions[self._etapeAction][0] == "V"):
                self._majInfosJoueur()
                if self._joueurBouge[0] is True:
                    self._finirDeplacementSP()
                    self._lancerTrajetEtoile(self._boiteOutils.cheminVersJoueur, self._x/32, self._y/32, self._c)
                    self._trouve = False
                if self._joueurProche is True:
                    if self._trouve is False:
                        self._lancerTrajet(self._boiteOutils.deplacementSPVersPnj("Joueur", 1000, self._x/32, self._y/32), True)
                        self._trouve = True
                    if self._penseeDuc is False:
                        self._boiteOutils.ajouterPensee("Oh, la Muette, que j'ai besoin de toi ! Le jeune duc dort ici ce soir…")
                        self._boiteOutils.ajouterPensee("Et il nous manque un drap pour son lit !")
                        self._boiteOutils.ajouterPensee("Rends-toi chez le drapier, William t'y conduira en carriole.", tempsLecture=0)
                        self._penseeDuc = True
                if self._penseeDuc is True and self._penseePossible.voir() is True:
                    self._boiteOutils.interrupteurs["OrdreDrapier"].activer()
                    self._etapeTraitement += 1
            if self._etapeTraitement == 12:
                self._finirDeplacementSP()
                self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._x/32, self._y/32, self._c, 6, 27)
                self._etapeTraitement += 1
            if self._etapeTraitement == 13 and self._x/32 == 6 and self._y/32 == 27:
                self._lancerTrajet(self._listeActionsOriginale, True)
                self._etapeSon = 0
                self._etapeTraitement += 1
            if self._etapeTraitement == 14:
                self._gererSonsCuisine()
        #
        #Cuistot2
        if self._nom is "Cuistot2":
            if self._etapeTraitement == 1:
                if self._deplacementBoucle is False and self._boiteOutils.positionProcheEvenement(self._x/32,self._y/32,"Nonne") is True: #On est arrivé à la nonne
                    self._boiteOutils.interrupteurs["NonneTrouvee"].activer()
                    self._etapeTraitement += 1
            if self._etapeTraitement == 2 and self._boiteOutils.interrupteurs["NonneEnMarche"].voir() is True:
                self._positionNonne = self._boiteOutils.getCoordonneesEvenement("Nonne")
                self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._x/32, self._y/32, self._c, self._positionNonne[0], self._positionNonne[1], arretAvant=True, regardAvant=True)
                self._etapeTraitement += 1
            if self._etapeTraitement == 3 and self._etapeMarche == 1:
                self._positionNonneOld = list(self._positionNonne)
                self._positionNonne = self._boiteOutils.getCoordonneesEvenement("Nonne")
                if self._positionNonne[0] != self._positionNonneOld[0] or self._positionNonne[1] != self._positionNonneOld[1]:
                    self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._x/32, self._y/32, self._c, self._positionNonne[0], self._positionNonne[1], arretAvant=True, regardAvant=True, blocsExclus=self._blocsExclusTrajet)
                if self._deplacementBoucle is False and self._positionNonne[0] == 25 and self._positionNonne[1] == 35:
                    self._boiteOutils.interrupteurs["NonneArrivee"].activer()
                    self._etapeTraitement += 1
            if self._etapeTraitement == 4 and self._boiteOutils.interrupteurs["NonneOrdre"].voir() is True:
                self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._x/32, self._y/32, self._c, 23, 38)
                self._etapeTraitement += 1
            if self._etapeTraitement == 5 and self._deplacementBoucle is False and (self._x/32) == 23 and (self._y/32) == 38:
                self._changerDureeDeplacement(500)
                self._lancerTrajet(["VDroite1000","Bas","Droite","Droite","VHaut1000","Droite","Droite","Haut","Haut","Haut","Gauche","Gauche","VBas1000","Gauche","Gauche","Bas","Bas"], True)
                self._etapeTraitement += 1
            if self._etapeTraitement == 6 and self._boiteOutils.interrupteurs["PlatPosé"].voir() is True and self._etapeMarche == 1:
                    self._seTeleporter(23, 38, "Droite")
                    self._lancerTrajet(["VDroite200"],True)
                    self._etapeTraitement += 1
            if self._etapeTraitement == 7:
                self._majInfosJoueur()
                if self._xJoueur[0] <= 30 and self._yJoueur[0] >= 28:
                    self._boiteOutils.changerBloc(24, 38, 2, "Interieur.png", (320, 320, 32, 32), (255, 255, 255), False)
                    self._finirDeplacementSP()
                    self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._x/32, self._y/32, self._c, 8, 37)
                    self._boiteOutils.interrupteurs["RepasNonne"].activer()
                    self._etapeTraitement += 1
            if self._etapeTraitement == 8 and self._x/32 == 8 and self._y/32 == 37 and self._deplacementBoucle is False:
                self._lancerTrajet(["VGauche500"], False)
                self._etapeTraitement += 1
            if self._etapeTraitement == 9 and self._deplacementBoucle is False:
                self._boiteOutils.changerBloc(7, 37, 1, -1, -1, -1, -1, vide=True)
                self._lancerTrajet(["Gauche","Gauche","VDroite500"], False)
                self._etapeTraitement += 1
            if self._etapeTraitement == 10 and self._deplacementBoucle is False:
                self._lancerTrajet(["Gauche","Gauche","Gauche","Gauche"], False)
                self._boiteOutils.changerBloc(7, 37, 1, "TileMurs2.png", (64, 32, 32, 32), (255, 255, 255), False)
                self._etapeTraitement += 1
            if self._etapeTraitement == 11 and self._deplacementBoucle is False:
                self._lancerTrajet(["VHaut1000"], True)
                self._etapeTraitement += 1

class Nonne(PNJ):
    def __init__(self, jeu, gestionnaire, x, y, c, directionDepart):
        nom = "Nonne"
        fichier, couleurTransparente, persoCharset = "Nonne.png", (0,0,0), (0,0)
        repetitionActions, listeActions  = False, ["Aucune"]
        dureeDeplacement, frequenceAnimation, frequenceDeplacement = 400, 200, 16
        super().__init__(jeu,gestionnaire,nom,x,y,c,fichier,couleurTransparente,persoCharset,repetitionActions,listeActions,dureeDeplacement=dureeDeplacement,frequenceAnimation=frequenceAnimation, frequenceDeplacement=frequenceDeplacement, directionDepart=directionDepart)
        self._trajetAleatoire, self._xArrivee, self._yArrivee, self._xArriveeOld, self._yArriveeOld = False, -1, -1, -1, -1

    def _gererEtape(self):
        if self._etapeTraitement == 1  and self._boiteOutils.interrupteurs["NonneTrouvee"].voir() is True:
            self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._x/32, self._y/32, self._c, 25, 35)
            self._boiteOutils.interrupteurs["NonneEnMarche"].activer()
            self._trajetAleatoire = False
            self._etapeTraitement += 1
        if self._etapeTraitement == 2 and self._boiteOutils.interrupteurs["NonneArrivee"].voir() is True:
            self._lancerTrajet( self._boiteOutils.regardVersPnj("Cuistot2", self._x/32, self._y/32), False)
            self._etapeTraitement += 1
        if self._etapeTraitement == 3 and self._deplacementBoucle is False:
            directionSurPlace = "V" + self._directionRegard + str(2500)
            self._lancerTrajet([directionSurPlace], False)
            self._etapeTraitement += 1
        if self._etapeTraitement == 4 and self._deplacementBoucle is False:
            self._lancerTrajet(["RBas"], False)
            self._boiteOutils.interrupteurs["NonneOrdre"].activer()
            self._changerDureeDeplacement(500)
            self._etapeTraitement += 1
        if self._etapeTraitement == 5 and self._deplacementBoucle is False:
            if self._boiteOutils.interrupteurs["RepasNonne"].voir() is True:
                self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._x/32, self._y/32, self._c, 23, 38)
                self._etapeTraitement += 1
            else:
                self._trajetAleatoire = True
                self._genererLancerTrajetAleatoire(22, 28, 34, 36, xExclu=self._x/32, yExclu=self._y/32)
        if self._etapeTraitement == 6 and (self._x/32) == 23 and (self._y/32) == 38 and self._deplacementBoucle is False:
            self._lancerTrajet(["VDroite300"],True)
            self._etapeTraitement += 1

    def _genererLancerTrajetAleatoire(self, x1, x2, y1, y2, xExclu=-1, yExclu=-1):
        xExclu, yExclu = int(xExclu), int(yExclu)
        while (self._xArrivee == self._xArriveeOld and self._yArrivee == self._yArriveeOld) or (self._xArrivee == xExclu and self._yArrivee == yExclu):
            self._xArrivee, self._yArrivee = random.randint(x1, x2), random.randint(y1, y2)
        self._xArriveeOld, self._yArriveeOld = self._xArrivee, self._yArrivee
        self._lancerTrajetEtoile(self._boiteOutils.cheminVersPosition, self._x/32, self._y/32, self._c, self._xArrivee, self._yArrivee, balade=True, frequencePauseBalade=2)

    def _debloquerCollision(self, collisionNormaleEnFait=False):
        if self._trajetAleatoire is True and collisionNormaleEnFait is False:
            xFutur, yFutur = self._jeu.carteActuelle.coordonneesAuTileSuivant(self._listeActions[self._etapeAction], self._x, self._y)
            if xFutur == self._xArrivee and yFutur == self._yArrivee: #Si on est bloqué à la case d'arrivée
                self._genererLancerTrajetAleatoire(22, 28, 34, 36)
            else: #Si on a une collision normale
                self._debloquerCollision(collisionNormaleEnFait=True) #On gère la collision normalement
        else:
            super()._debloquerCollision()
