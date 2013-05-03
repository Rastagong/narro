# -*-coding:iso-8859-1 -*
import pygame, pdb,math
from pygame.locals import *
from .constantes import *
from .horloge import *
from .interrupteur import *
from .evenementConcret import *

class Mobile(EvenementConcret):
    """Classe repr�sentant un �v�nement mobile, � savoir PNJ ou joueur, qui sont ses classes filles."""

    def __init__(self, jeu, gestionnaire, nom, x, y, c, fichier, couleurTransparente, persoCharset, vitesseDeplacement=VITESSE_DEPLACEMENT_MOBILE_PAR_DEFAUT, dureeAnimation=DUREE_ANIMATION_MOBILE_PAR_DEFAUT, directionDepart=DIRECTION_DEPART_MOBILE_PAR_DEFAUT, dureeAnimationSP=DUREE_ANIMATION_SP_PAR_DEFAUT, longueurSprite=LONGUEUR_SPRITE_PAR_DEFAUT, largeurSprite=LARGEUR_SPRITE_PAR_DEFAUT):
        """Initialise le mobile.
        Param�tres  :
        <jeu> est l'application enti�re.
        <gestionnaire> est une instance du gestionnaire d'�v�nements.
        <nom> est l'identifiant du mobile.
        <x><y> est la position initiale du mobile en indices de tiles.
        <c> est l'indice de la couche sur laquelle le mobile est plac�.
        <fichier> est le nom de l'image situ�e dans le dossier des ressources qui repr�sente le mobile.
        <couleurTransparente> d�signe la couleur transparente du <fichier>. 
        <persoCharset> d�signe la partie de l'image correspondant au perso � afficher.
        Param�tres facultatifs :
        <directionDepart> d�signe la direction que prend le mobile au d�part. Valeur par d�faut dans les constantes.
        <vitesseDeplacement> d�signe la vitesse de d�placement en pixels par seconde.
        <dureeAnimation> d�signe le nombre de millisecondes, au sein d'un tile ou pas, entre deux animations. Valeur par d�faut dans les constantes.
        <dureeAnimationSP> d�signe la dur�e en millisecondes entre deux animations sur place. Valeur par d�faut dans les constantes.
        <largeurSprite> est la largeur du sprite. Valeur par d�faut dans les constantes.
        <longueurSprite> est la longueur du sprite. Valeur par d�faut dans les constantes."""
        EvenementConcret.__init__(self, jeu, gestionnaire)
        self._direction, self._directionRegard = directionDepart, directionDepart
        self._nom,  self._nomTileset = nom, DOSSIER_RESSOURCES+fichier
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
        """Traite l'�v�nement"""
        super().traiter()

    def _deplacement(self, direction):
        """G�re une action de d�placement (un pas, un regard, ou une attente)"""

    def _initialiserDeplacement(self, tempsAttente, joueur=False, appuiJoueur=False, direction="Aucune"):
        """Initialise un d�placement"""
        hauteurTile = self._jeu.carteActuelle.hauteurTile
        """self._x, self._xOld = (self._x * hauteurTile), (self._x * hauteurTile)
        self._y, self._yOld = (self._y * hauteurTile), (self._y * hauteurTile)"""
        self._gestionnaire.registerPosition(self._nom, int(self._positionCarte.left / hauteurTile), int(self._positionCarte.top / hauteurTile), self._c, joueur=joueur, appuiJoueur=appuiJoueur, direction=direction)
        self._ajusterPositionSource(False,self._direction)
        self._jeu.carteActuelle.poserPNJ(self._positionCarte, self._c, self._positionSource, self._nomTileset, self._couleurTransparente, self._nom)
        self._tempsPrecedent, self._deltaTimer = 0, 0
        Horloge.initialiser(id(self), 1, tempsAttente)
        Horloge.initialiser(id(self), 2, 1)
    
    def _getPositionCarteSuivante(self, direction):
        """Retourne le positionCarte du mobile qu'il aura une fois son d�placement fini"""
        if direction == "Haut" or direction == "Bas":
            return self._positionCarte.move(0, (self._jeu.carteActuelle.hauteurTile if direction == "Bas" else -self._jeu.carteActuelle.hauteurTile))
        if direction == "Gauche" or direction == "Droite":
            return self._positionCarte.move((self._jeu.carteActuelle.hauteurTile if direction == "Droite" else -self._jeu.carteActuelle.hauteurTile), 0)
    
    def _determinerAnimation(self, surPlace=False):
        """Adapte le pied actuel et le fait d'�tre en marche � l'�tape d'animation actuelle s'il est temps de changer d'animation (selon l'horloge n�2). 
        <surPlace> doit valoir <True> quand on est en animation sur place.
        Retourne <True> quand un changement d'animation est n�cessaire."""
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

    def _nouvellesCoordonnees(self, tempsActuel, direction):
        self._deltaTimer = (tempsActuel - self._tempsPrecedent) / 1000
        self._tempsPrecedent = tempsActuel
        self._avancee = math.floor(self._vitesseDeplacement * self._deltaTimer)
        if self._avancee == 0:
            self._avancee = 1
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
    xTileSuivant = property(_getXTileSuivant)
    yTileSuivant = property(_getYTileSuivant)
    _positionTile, positionTile = property(_getPositionTile), property(_getPositionTile)
    _tileSuivant, tileSuivant = property(_getTileSuivant), property(_getTileSuivant)
    _tilePrecedent, tilePrecedent = property(_getTilePrecedent), property(_getTilePrecedent)
    c = property(_getC)
    nomTileset = property(_getNomTileset, _setNomTileset)
    persoCharset = property(_getPersoCharset, _setPersoCharset)
