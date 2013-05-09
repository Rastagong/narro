# -*-coding:iso-8859-1 -*
import pygame, pdb,math
from pygame.locals import *
from .constantes import *
from .horloge import *
from .interrupteur import *
from .evenementConcret import *

class Mobile(EvenementConcret):
    """Classe représentant un évènement mobile, à savoir PNJ ou joueur, qui sont ses classes filles."""

    def __init__(self, jeu, gestionnaire, nom, x, y, c, fichier, couleurTransparente, persoCharset, vitesseDeplacement=VITESSE_DEPLACEMENT_MOBILE_PAR_DEFAUT, dureeAnimation=DUREE_ANIMATION_MOBILE_PAR_DEFAUT, directionDepart=DIRECTION_DEPART_MOBILE_PAR_DEFAUT, dureeAnimationSP=DUREE_ANIMATION_SP_PAR_DEFAUT, longueurSprite=LONGUEUR_SPRITE_PAR_DEFAUT, largeurSprite=LARGEUR_SPRITE_PAR_DEFAUT):
        """Initialise le mobile.
        Paramètres  :
        <jeu> est l'application entière.
        <gestionnaire> est une instance du gestionnaire d'évènements.
        <nom> est l'identifiant du mobile.
        <x><y> est la position initiale du mobile en indices de tiles.
        <c> est l'indice de la couche sur laquelle le mobile est placé.
        <fichier> est le nom de l'image située dans le dossier des ressources qui représente le mobile.
        <couleurTransparente> désigne la couleur transparente du <fichier>. 
        <persoCharset> désigne la partie de l'image correspondant au perso à afficher.
        Paramètres facultatifs :
        <directionDepart> désigne la direction que prend le mobile au départ. Valeur par défaut dans les constantes.
        <vitesseDeplacement> désigne la vitesse de déplacement en pixels par seconde.
        <dureeAnimation> désigne le nombre de millisecondes, au sein d'un tile ou pas, entre deux animations. Valeur par défaut dans les constantes.
        <dureeAnimationSP> désigne la durée en millisecondes entre deux animations sur place. Valeur par défaut dans les constantes.
        <largeurSprite> est la largeur du sprite. Valeur par défaut dans les constantes.
        <longueurSprite> est la longueur du sprite. Valeur par défaut dans les constantes."""
        EvenementConcret.__init__(self, jeu, gestionnaire)
        self._direction, self._directionRegard = directionDepart, directionDepart
        self._nom,  self._nomTileset = nom, fichier
        self._positionCarte = Rect(x*32, y*32, longueurSprite, largeurSprite)
        self._positionCarteOld, self._positionCarteFuture = self._positionCarte.copy(), self._positionCarte.copy()
        self._xTilePrecedent, self._yTilePrecedent = self._positionCarte.left/32, self._positionCarte.top/32
        self._xTileSuivant, self._yTileSuivant = self._positionCarte.left/32, self._positionCarte.top/32
        self._c, self._cOld = c, c
        self._vitesseDeplacement, self._dureeAnimationSP, self._dureeAnimation = vitesseDeplacement, dureeAnimationSP, dureeAnimation
        self._couleurTransparente, self._persoCharset = couleurTransparente, persoCharset
        self._pied, self._enMarche = Interrupteur(True), Interrupteur(True)
        self._etapeMarche, self._etapeAnimation, self._sensAnimation, self._pixelsParcourus = 1, 1, 1, 0
    
    def traiter(self):
        """Traite l'évènement"""
        super().traiter()

    def _deplacement(self, direction):
        """Gère une action de déplacement (un pas, un regard, ou une attente)"""

    def _initialiserDeplacement(self, tempsAttente, joueur=False, appuiJoueur=False, direction="Aucune"):
        """Initialise un déplacement"""
        hauteurTile = self._jeu.carteActuelle.hauteurTile
        self._gestionnaire.registerPosition(self._nom, int(self._positionCarte.left / hauteurTile), int(self._positionCarte.top / hauteurTile), self._c, joueur=joueur, appuiJoueur=appuiJoueur, direction=direction)
        self._ajusterPositionSource(False,self._direction)
        self._jeu.carteActuelle.poserPNJ(self._positionCarte, self._c, self._positionSource, self._nomTileset, self._couleurTransparente, self._nom)
        self._tempsPrecedent, self._deltaTimer = 0, 0
        Horloge.initialiser(id(self), 1, tempsAttente)
        Horloge.initialiser(id(self), 2, 1)
    
    def _getPositionCarteSuivante(self, direction):
        """Retourne le positionCarte du mobile qu'il aura une fois son déplacement fini"""
        if direction == "Haut" or direction == "Bas":
            return self._positionCarte.move(0, (self._jeu.carteActuelle.hauteurTile if direction == "Bas" else -self._jeu.carteActuelle.hauteurTile))
        if direction == "Gauche" or direction == "Droite":
            return self._positionCarte.move((self._jeu.carteActuelle.hauteurTile if direction == "Droite" else -self._jeu.carteActuelle.hauteurTile), 0)
    
    def _determinerAnimation(self, surPlace=False):
        """Adapte le pied actuel et le fait d'être en marche à l'étape d'animation actuelle s'il est temps de changer d'animation (selon l'horloge n°2). 
        <surPlace> doit valoir <True> quand on est en animation sur place.
        Retourne <True> quand un changement d'animation est nécessaire."""
        if Horloge.sonner(id(self), 2) is True or surPlace is True:
            if self._etapeAnimation == 1:
                self._enMarche.activer()
                self._pied.inverser()
                self._etapeAnimation, self._sensAnimation = 2, 1
            elif self._etapeAnimation == 2:
                self._enMarche.desactiver()
                self._etapeAnimation += self._sensAnimation
            elif self._etapeAnimation == 3:
                self._enMarche.activer()
                self._pied.inverser()
                self._etapeAnimation, self._sensAnimation = 2, -1
            if surPlace is False:
                Horloge.initialiser(id(self), 2, self._dureeAnimation)
            return True
        else:
            return False

    def _ajusterPositionSource(self, enMarche, direction):
        """Donne la position source du PNJ en marche ou en fin de parcours, en fonction de la direction"""
        hauteurTile = self._jeu.carteActuelle.hauteurTile
        self._positionSource.left, self._positionSource.top = 0, 0
        self._positionSource.move_ip(self._persoCharset[0] * self._positionSource.width * 3, self._persoCharset[1] * self._positionSource.height * 4)
        self._positionSource.move_ip(self._positionSource.width, 0)
        if direction.count("Bas") == 1:
            pass
        elif direction.count("Gauche") == 1:
            self._positionSource.move_ip(0, 1 * self._positionSource.height)
        elif direction.count("Droite") == 1:
            self._positionSource.move_ip(0, 2 * self._positionSource.height)
        elif direction.count("Haut") == 1:
            self._positionSource.move_ip(0, 3 * self._positionSource.height)
        """if self._etapeMarche == 1 or self._etapeMarche == self._frequenceDeplacement:
            enMarche = False
        else:
            enMarche = True"""
        if enMarche is True: #Si le PNJ est en marche
            if self._pied.voir() is True: #Si on est sur le pied gauche
                self._positionSource.move_ip(-self._positionSource.width, 0)
            else:
                self._positionSource.move_ip(self._positionSource.width, 0)
        if direction[0] == "V" or direction[0] == "R":
            direction = direction[1:]
        self._directionRegard = str(direction)  

    def _calculerNouvellesCoordonnees(self, tempsActuel, direction):
        deltaTimer = (tempsActuel - self._tempsPrecedent) / 1000
        avancee = (self._vitesseDeplacement * deltaTimer)
        return (avancee, deltaTimer)

    def _majCoordonnees(self, tempsActuel, direction, deltaTimer, avancee):
        self._tempsPrecedent, self._avancee, self._deltaTimer = tempsActuel, round(avancee), deltaTimer
        if self._pixelsParcourus + self._avancee > 32:
            self._avancee = 32 - self._pixelsParcourus
        self._avanceeOrientee = self._avancee
        if direction == "Gauche" or direction == "Haut":
            self._avanceeOrientee *= -1
        if direction == "Haut" or direction == "Bas":
            return (self._positionCarte.left, self._positionCarte.top + self._avanceeOrientee)
        elif direction == "Gauche" or direction == "Droite":
            return (self._positionCarte.left + self._avanceeOrientee, self._positionCarte.top)

    def _getX(self):
        return self._positionCarte.left

    def _getY(self):
        return self._positionCarte.top

    def _getC(self):
        return self._c

    def _getXTile(self):
        return int(self._positionCarte.left / 32)

    def _getYTile(self):
        return int(self._positionCarte.top / 32)

    def _getXTileOld(self):
        return int(self._positionCarteOld.left / 32)

    def _getYTileOld(self):
        return int(self._positionCarteOld.top / 32)

    def _getXTileSuivant(self):
        return self._xTileSuivant

    def _getYTileSuivant(self):
        return self._yTileSuivant

    def _getXTilePrecedent(self):
        return self._xTilePrecedent

    def _getYTilePrecedent(self):
        return self._yTilePrecedent

    def _getPositionTile(self):
        return (_getXTile(), getYTile())

    def _getTilePrecedent(self):
        return (_getXTilePrecedent(), getYTilePrecedent())

    def _getTileSuivant(self):
        return (_getXTileSuivant(), getYTileSuivant())

    def _getPersoCharset(self):
        return self._persoCharset

    def _setPersoCharset(self, new):
        self._persoCharset = new

    def _getNomTileset(self):
        return self._nomTileset
    
    def _setNomTileset(self, new):
        self._nomTileset = new

    x, _x = property(_getX), property(_getX)
    y, _y = property(_getY), property(_getY)
    _xTile, xTile = property(_getXTile), property(_getXTile)
    _yTile, yTile = property(_getYTile), property(_getYTile)
    xTilePrecedent = property(_getXTilePrecedent)
    yTilePrecedent = property(_getYTilePrecedent)
    _xTileOld, xTileOld = property(_getXTileOld), property(_getXTileOld)
    _yTileOld, yTileOld = property(_getYTileOld), property(_getYTileOld)
    xTileSuivant = property(_getXTileSuivant)
    yTileSuivant = property(_getYTileSuivant)
    _positionTile, positionTile = property(_getPositionTile), property(_getPositionTile)
    _tileSuivant, tileSuivant = property(_getTileSuivant), property(_getTileSuivant)
    _tilePrecedent, tilePrecedent = property(_getTilePrecedent), property(_getTilePrecedent)
    c = property(_getC)
    nomTileset = property(_getNomTileset, _setNomTileset)
    persoCharset = property(_getPersoCharset, _setPersoCharset)
