# -*-coding:iso-8859-1 -*
import pygame, pdb,math
from pygame.locals import *
from constantes import *
from horloge import *
from interrupteur import *
from mobile import *



class PNJ(Mobile):
    """Classe représentant un PNJ"""

    def __init__(self,jeu,gestionnaire,nom,x,y,c,fichier,couleurTransparente,persoCharset,repetitionActions,listeActions,dureeDeplacement=DUREE_DEPLACEMENT_MOBILE_PAR_DEFAUT,frequenceAnimation=FREQUENCE_ANIMATION_MOBILE_PAR_DEFAUT, frequenceDeplacement=FREQUENCE_DEPLACEMENT_MOBILE_PAR_DEFAUT, directionDepart=DIRECTION_DEPART_MOBILE_PAR_DEFAUT, intelligence=INTELLIGENCE_PAR_DEFAUT, courage=COURAGE_PAR_DEFAUT, poseDepart=True, longueurSprite=LONGUEUR_SPRITE_PAR_DEFAUT, largeurSprite=LARGEUR_SPRITE_PAR_DEFAUT):
        """Initialise le PNJ
        Paramètres obligatoires :
        <jeu> est l'application entière.
        <gestionnaire> est une instance du gestionnaire d'évènements.
        <nom> est l'identifiant du mobile.
        <x><y> est la position initiale du mobile en indices de tiles.
        <c> est l'indice de la couche sur laquelle est posée le PNJ.
        <fichier> est le nom de l'image située dans le dossier des ressources qui représente le mobile.
        <couleurTransparente> désigne la couleur transparente du <fichier>. 
        <persoCharset> désigne la partie de l'image correspondant au perso à afficher.
        <repetitionAction> est un booléen. Quand il vaut <True>, les actions sont répétées en boucle.
        <listeActions> est une liste des actions que le PNJ doit suivre.
        Paramètres facultatifs :
        <dureeDeplacement> désigne, en millisecondes, le temps que doit prendre un déplacement d'un tile à un autre. Valeur par défaut dans les constantes.
        <frequenceAnimation> désigne le nombre de millisecondes, au sein d'un tile ou pas, entre deux animations. Valeur par défaut dans les constantes.
        <frequenceDeplacement> désigne le nombre de déplacements du mobile au sein d'un tile (sans qu'il y ait forcément animation). Valeur par déf. dans les constantes.
        <directionDepart> désigne la direction que prend le mobile au départ. Valeur par défaut dans les constantes.
        <intelligence> est un booléen qui permet au PNJ de débloquer une situation de collision quand il vaut <True>.
        <courage> est un booléen qui définit l'attitude du PNJ en cas de collision : quand le PNJ n'est pas courageux, il abandonne ses actions.
        <poseDepart> est un booléen qui vaut <False> quand le PNJ ne doit pas être posé dès le départ.
        <largeurSprite> est la largeur du sprite. Valeur par défaut dans les constantes.
        <longueurSprite> est la longueur du sprite. Valeur par défaut dans les constantes."""
        Mobile.__init__(self,jeu,gestionnaire,nom,x,y,c,fichier,couleurTransparente,persoCharset,dureeDeplacement=dureeDeplacement,frequenceAnimation=frequenceAnimation,frequenceDeplacement=frequenceDeplacement,directionDepart=directionDepart)
        self._deplacementBoucle, self._etapeAction, self._collision = True, 0, False
        self._repetitionActions, self._listeActions = repetitionActions, listeActions
        self._regardFait, self._trajetEtoileEnCours, self._intelligence, self._poseDepart, self._courage = False, False, intelligence, poseDepart, courage
        self._fonctionTrajet, self._argsTrajet, self._argsvTrajet, self._blocsExclusTrajet = None, None, None, []
        self._xJoueur, self._yJoueur, self._joueurBouge =  [-1, -1], [-1, -1], [True, True]
        self._xJoueurOld, self._yJoueurOld =  [-1, -1], [-1, -1]
        self._positionSource = Rect(0, 0, longueurSprite, largeurSprite)

    def onJoueurProche(self, x, y, c, direction):
        super().onJoueurProche(x, y, c, direction)
        self._joueurProche = True
    
    def _majInfosJoueur(self, i=0):
        self._xJoueurOld[i], self._yJoueurOld[i] = self._xJoueur[i], self._yJoueur[i]
        self._xJoueur[i], self._yJoueur[i] = self._gestionnaire.xJoueur, self._gestionnaire.yJoueur
        self._joueurProche, self._joueurBouge[i] = False, False
        self._gestionnaire.majActionsJoueur(self._nom) #On vérifie si le joueur est proche (cf. onJoueurProche)
        if self._xJoueur[i] != self._xJoueurOld[i] or self._yJoueur[i] != self._yJoueurOld[i]:
            self._joueurBouge[i] = True
    
    def traiter(self):
        """Traite l'évènement"""
        super().traiter()
        if self._etapeTraitement is 0 and self._poseDepart is True:
            self._initialiserDeplacement(1, direction=self._directionRegard)
            self._etapeTraitement += 1
        else:
            self._gererEtape()
        self._gererActions()

    def _gererEtape(self):
        """Gère une étape"""

    def _gererActions(self):
        if self._deplacementBoucle is True:
            if self._etapeAction < len(self._listeActions):
                self._deplacement(self._listeActions[self._etapeAction])
            else:
                if self._repetitionActions is True:
                    Horloge.initialiser(id(self), 1,0)
                    self._etapeAction = 0
                else:
                    self._deplacementBoucle = False

    def _lancerTrajetEtoile(self, *args, **argsv):
        """Méthode appelée pour lancer un trajet A*. Elle enregistre la fonction appelée et les paramètres pour relancer le trajet en cas de collision."""
        Horloge.initialiser(id(self), 1, 1)
        self._etapeMarche = 1
        self._fonctionTrajet, self._argsTrajet, self._argsvTrajet = args[0], list(args[1:]), argsv
        trajet = self._fonctionTrajet(*self._argsTrajet, **self._argsvTrajet)
        self._lancerTrajet(trajet, False, nouvelleIntelligence=True)

    def _debloquerCollision(self):
        """Méthode qui ne s'applique qu'aux PNJ intelligents et qui peut être redéfinie. 
        Quand il y a collision, elle est appelée, permettant ainsi de débloquer la situation."""
        if self._intelligence is True and self._courage is True:
            self._collision = True
            self._blocsExclusTrajet = [ self._jeu.carteActuelle.coordonneesAuTileSuivant(self._listeActions[self._etapeAction], self._positionCarte.left, self._positionCarte.top) ]
            self._argsvTrajet["blocsExclus"], self._argsTrajet[0], self._argsTrajet[1] = self._blocsExclusTrajet, self._positionCarte.left/32, self._positionCarte.top/32
            trajet = self._fonctionTrajet(*self._argsTrajet, **self._argsvTrajet)
            self._lancerTrajet(trajet, False, nouvelleIntelligence=True)

    def _lancerTrajet(self, *args, nouvelleIntelligence=False):
        """Lance un nouveau trajet (liste d'actions <nouveauTrajet>) au PNJ.
        Si <repetition> vaut <True>, la liste d'actions fonctionne en boucle.
        <nouvelleIntelligence> ne vaut <True> que quand le trajet est lancé depuis <_lancerTrajetEtoile> : il s'agit d'un trajet A*, donc où il faut être intelligent.
        Les paramètres principaux <nouveauTrajet> et <repetition> peuvent être fournirs de deux manière : 
            - Soit on donne la liste <nouveauTrajet> puis le booléen <repetition>
            - Soit on donne les actions composant le trajet les unes après les autres, en finissant par le booléen <repetition>"""
        if len(args) == 2 and isinstance(args[0], list):
            nouveauTrajet, repetition = args[0], args[1]
        else:
            nouveauTrajet, repetition = args[:len(args) - 1], args[len(args) - 1]
        self._listeActions, self._intelligence = nouveauTrajet, nouvelleIntelligence
        self._etapeAction, self._pixelsParcourus, self._repetitionActions, self._deplacementBoucle = 0, 0, repetition, True
        Horloge.initialiser(id(self), 1, 1)

    def _determinerDirectionSP(self, direction):
        """Retourne la direction coresspondant à la direction SP."""
        if "VHaut" in direction:
            return "Haut"
        elif "VBas" in direction:
            return "Bas"
        elif "Gauche" in direction:
            return "Gauche"
        elif "Droite" in direction:
            return "Droite"

    def _seTeleporter(self, xTile, yTile, direction, couche=-1):
        """Téléporte le PNJ sur le tile <xTile><yTile><couche>, avec un regard en <direction>."""
        if couche == -1:
            couche = self._c
        self._ajusterPositionSource(False, direction)
        self._positionCarteOld.left, self._positionCarteOld.top = self._positionCarte.left, self._positionCarte.top
        self._positionCarte.left, self._positionCarte.top = xTile*self._jeu.carteActuelle.hauteurTile, yTile*self._jeu.carteActuelle.hauteurTile
        self._boiteOutils.teleporterSurPosition(self._positionCarte, couche, self._positionSource, self._nomTileset, self._couleurTransparente, self._nom)
        self._gestionnaire.registerPosition(self._nom, self._xTile, self._yTile, self._c, direction=self._directionRegard)

    def _deplacement(self, direction):
        """Gère une action de déplacement (un pas, un regard, ou une attente)"""
        hauteurTile = self._jeu.carteActuelle.hauteurTile
        if direction is "Aucune":
            self._ajusterPositionSource(False, self._directionRegard) 
            if self._poseDepart is True:
                self._jeu.carteActuelle.poserPNJ(self._positionCarte, self._c, self._positionSource, self._nomTileset, self._couleurTransparente, self._nom)
            self._etapeAction += 1
        elif direction is "RelanceEtoile" and Horloge.sonner(id(self), 1) is True:
            self._blocsExclusTrajet = [ self._jeu.carteActuelle.coordonneesAuTileSuivant(self._listeActions[self._etapeAction], self._positionCarte.left, self._positionCarte.top) ]
            self._argsvTrajet["blocsExclus"], self._argsTrajet[0], self._argsTrajet[1] = self._blocsExclusTrajet, self._positionCarte.left/32, self._positionCarte.top/32
            trajet = self._fonctionTrajet(*self._argsTrajet, **self._argsvTrajet)
            self._lancerTrajet(trajet, False, nouvelleIntelligence=True)
            Horloge.initialiser(id(self), 1, 1000)
        elif type(direction) is int: #Une attente
            if self._etapeMarche == 1: #On débute l'attente : initialisation de l'horloge
                Horloge.initialiser(id(self), 1,direction)
                self._etapeMarche += 1
            if Horloge.sonner(id(self), 1) is True: #Fin de l'attente : on change d'étape de déplacement, on remet celle de marche à 1
                self._etapeAction += 1
                self._etapeMarche = 1
                Horloge.initialiser(id(self), 1, 1)
        elif direction in ("Haut","Bas","Gauche","Droite"): #Un pas
            if Horloge.sonner(id(self), 1) is True: #Si le temps d'attente pour l'étape de marche suivante est passé
                if self._pixelsParcourus < hauteurTile: #Si le déplacement n'est pas fini
                    deplacementPossible = False
                    (self._positionCarteFuture.left, self._positionCarteFuture.top) = self._coordonneesEtapeMarcheSuivante(direction=direction)
                    if self._etapeMarche == 1: #On ne vérifie si on peut se déplacer qu'en étape 1
                        self._positionCarteSuivante = self._getPositionCarteSuivante(direction)
                        self._xTilePrecedent, self._yTilePrecedent = self._xTile, self._yTile
                        self._xTileSuivant, self._yTileSuivant =  self._positionCarteSuivante.left/32, self._positionCarteSuivante.top/32
                        deplacementPossible = self._jeu.carteActuelle.deplacementPossible(self._positionCarteSuivante, self._c, self._nom)
                    if deplacementPossible is True or self._etapeMarche > 1:
                        self._regardFait, self._collision = False, False
                        self._positionCarteOld.left, self._positionCarteOld.top = self._positionCarte.left, self._positionCarte.top
                        self._positionCarte.left, self._positionCarte.top = self._positionCarteFuture.left, self._positionCarteFuture.top
                        self._determinerAnimation()
                        self._ajusterPositionSource(self._enMarche.voir(), direction)
                        self._jeu.carteActuelle.poserPNJ(self._positionCarte, self._c, self._positionSource, self._nomTileset, self._couleurTransparente, self._nom, positionCarteSuivante=self._positionCarteSuivante)
                        Horloge.initialiser(id(self), 1, self._dureeMicroDeplacement) #On lance une autre étape
                        self._pixelsParcourus += self._getProchainNombrePixels()
                        self._etapeMarche += 1
                    else: #Il y a collision, on ne peut pas quitter le tile, donc on réinitialise
                        self._pixelsParcourus, self._etapeMarche = 0,1
                        Horloge.initialiser(id(self), 1, 1)
                        if self._regardFait == False: #Si on ne s'est pas encore tourné dans la direction du blocage
                            self._ajusterPositionSource(False, direction) 
                            self._gestionnaire.registerPosition(self._nom, self._xTile, self._yTile, self._c, direction=self._directionRegard)
                            self._jeu.carteActuelle.poserPNJ(self._positionCarte, self._c, self._positionSource, self._nomTileset, self._couleurTransparente, self._nom)
                            self._regardFait = True
                        if self._courage is False:
                            self._listeActions = ["Aucune"]
                        self._debloquerCollision()
                else: #Le déplacement est fini, on réinitialise
                    self._gestionnaire.registerPosition(self._nom, self._xTile, self._yTile, self._c, direction=self._directionRegard)
                    self._etapeMarche, self._pixelsParcourus = 1,0
                    Horloge.initialiser(id(self), 1, 0)
                    self._etapeAction += 1
            else:
                nouvelleAnimation = self._determinerAnimation() #On regarde s'il faut une nouvelle animation...
                if nouvelleAnimation: #Qu'on applique si c'est le cas
                    self._ajusterPositionSource(self._enMarche.voir(), direction)
                    self._jeu.carteActuelle.poserPNJ(self._positionCarte, self._c, self._positionSource, self._nomTileset, self._couleurTransparente, self._nom)
        elif direction in ("RHaut","RGauche","RDroite","RBas"): #Regard dans une direction
            self._ajusterPositionSource(False, direction) 
            self._gestionnaire.registerPosition(self._nom, self._xTile, self._yTile, self._c, direction=self._directionRegard)
            self._jeu.carteActuelle.poserPNJ(self._positionCarte, self._c, self._positionSource, self._nomTileset, self._couleurTransparente, self._nom)
            self._etapeAction += 1
        elif  "VHaut" in direction or "VBas" in direction or "VGauche" in direction or "VDroite" in direction:
            if Horloge.sonner(id(self), 1) is True:
                if self._etapeMarche == 1:
                    self._dureeSP = int(direction.replace("VHaut",'').replace("VBas",'').replace("VGauche",'').replace("VDroite",''))
                    self._frequenceAnimationSP = math.floor(self._dureeSP / self._dureeAnimationSP) + 1
                if self._etapeMarche < self._frequenceAnimationSP or self._dureeSP == 0:
                    direction = self._determinerDirectionSP(direction)
                    self._determinerAnimation(surPlace=True)
                    self._ajusterPositionSource(self._enMarche.voir(), direction)
                    self._jeu.carteActuelle.poserPNJ(self._positionCarte, self._c, self._positionSource, self._nomTileset, self._couleurTransparente, self._nom)
                    self._etapeMarche += 1
                    Horloge.initialiser(id(self), 1, self._dureeAnimationSP)
                else:
                    self._finirDeplacementSP()

    def _finirDeplacementSP(self):
        self._etapeMarche = 1
        Horloge.initialiser(id(self), 1, 1)
        Horloge.initialiser(id(self), 2, 1)
        self._etapeAction += 1
