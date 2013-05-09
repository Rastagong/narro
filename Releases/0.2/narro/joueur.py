# -*-coding:iso-8859-1 -*
import pygame,pdb,math
from pygame.locals import *
from .constantes import *
from .horloge import *
from .interrupteur import *
from .mobile import *
from .observable import *



class Joueur(Mobile, Observable):
    """Classe représentant le joueur"""

    def __init__(self, jeu, gestionnaire, x, y, c, fichier=FICHIER_JOUEUR_PAR_DEFAUT, persoCharset=CHARSET_JOUEUR_PAR_DEFAUT, couleurTransparente=COULEUR_TRANSPARENTE_FICHIER_JOUEUR_PAR_DEFAUT, vitesseDeplacement=VITESSE_DEPLACEMENT_JOUEUR_PAR_DEFAUT, dureeAnimation=DUREE_ANIMATION_JOUEUR_PAR_DEFAUT, nom=NOM_EVENEMENT_JOUEUR_PAR_DEFAUT, directionDepart=DIRECTION_DEPART_MOBILE_PAR_DEFAUT, longueurSprite=LONGUEUR_SPRITE_PAR_DEFAUT, largeurSprite=LARGEUR_SPRITE_PAR_DEFAUT):
        """Initialise le joueur
        Paramètres obligatoires :
        <jeu> est l'application entière.
        <gestionnaire> est une instance du gestionnaire d'évènements.
        <x><y> est la position initiale du mobile en indices de tiles.
        <c> est l'indice de la couche sur laquelle est posé le joueur.
        Paramètres facultatifs :
        <fichier> est le nom de l'image située dans le dossier des ressources qui représente le mobile. Valeur par défaut dans les constantes.
        <persoCharset> désigne la partie du <fichier> correspondant au joueur. Valeur par défaut dans les constantes.
        <couleurTransparente> désigne la couleur transparente du <fichier>. Valeur par défaut dans les constantes.
        <vitesseDeplacement> désigne la vitesse de déplacement en pixels par seconde.
        <dureeAnimation> désigne le nombre de millisecondes, au sein d'un tile ou pas, entre deux animations. Valeur par défaut dans les constantes.
        <nom> désigne le <str> identifiant l'évènement Joueur. Valeur par défaut dans les constantes.
        <directionDepart> désigne la direction que prend le joueur au départ. Valeur par défaut dans les constantes.
        <largeurSprite> est la largeur du sprite. Valeur par défaut dans les constantes.
        <longueurSprite> est la longueur du sprite. Valeur par défaut dans les constantes."""
        Observable.__init__(self, "_positionCarte.left", "_positionCarte.top", "_c")
        Mobile.__init__(self,jeu,gestionnaire,nom,x,y,c,fichier,couleurTransparente,persoCharset,vitesseDeplacement=vitesseDeplacement,dureeAnimation=dureeAnimation, directionDepart=directionDepart)
        self._directions = dict(Haut=False,Bas=False,Gauche=False,Droite=False)
        self._derniereDirection = "Aucune"
        self._regardDansDirection = dict(Haut=False, Bas=False, Droite=False, Gauche=False)
        self._jeu.joueur, self._appuiValidation, self._regardAttente, self._directionAttente, self._mouvement = self, False, True, str(self._direction), False
        self._persoCharset = persoCharset
        self._positionSource = Rect(0, 0, longueurSprite, largeurSprite)

    def traiter(self):
        Mobile.traiter(self)
        if self._etapeTraitement is 0:
            self._initialiserDeplacement(1, joueur=True, appuiJoueur=False, direction=self._directionRegard)
            self._nomCarte = self._boiteOutils.nomCarte
            hauteurTile = self._jeu.carteActuelle.hauteurTile
            self._tempsPrecedent, self._deltaTimer = 0, 0
            self._etapeTraitement += 1
        if self._etapeTraitement is 1:
            self._analyserAction()
            self._deplacement()
            
    def transfertCarte(self, x, y, c, direction):
        """Prépare l'apparition sur une nouvelle carte, en <x><y><c> avec un regard en <direction>."""
        self._cOld, self._c = c, c
        self._positionCarte.left, self._positionCarte.top, self._mouvement = x * self._jeu.carteActuelle.hauteurTile, y * self._jeu.carteActuelle.hauteurTile, False
        self._etapeMarche, self._etapeTraitement, self._pixelsParcourus = 1, 0, 0
        self._derniereDirection = "Aucune"
        self._regardDansDirection = dict(Haut=False, Bas=False, Droite=False, Gauche=False)
        self._direction, self._directionRegard = direction, direction

    def _analyserAction(self):
        """Analyse la touche fléchée sur laquelle a appuyé le joueur et ajuste la direction du prochain déplacement en conséquence"""
        event = self._jeu.event
        if event.type is KEYDOWN and self._boiteOutils.joueurLibre.voir() is True:
            if event.key == K_z:
                if self._etapeMarche > 1:
                    self._gestionnaire.registerPosition(self._nom, self._xTilePrecedent, self._yTilePrecedent, self._c, joueur=True, appuiJoueur=True, direction=self._directionRegard)
                else:
                    self._gestionnaire.registerPosition(self._nom, self._xTile, self._yTile, self._c, joueur=True, appuiJoueur=True, direction=self._directionRegard)
                self._appuiValidation = True
            if event.key == K_LEFT or event.key == K_RIGHT or event.key == K_DOWN or event.key == K_LEFT or event.key == K_UP:
                if event.key == K_LEFT: 
                    self._directions["Gauche"] = True
                    self._derniereDirection = "Gauche"
                elif event.key == K_RIGHT:
                    self._directions["Droite"] = True
                    self._derniereDirection = "Droite"
                elif event.key == K_UP:
                    self._directions["Haut"] = True
                    self._derniereDirection = "Haut"
                elif event.key == K_DOWN:
                    self._directions["Bas"] = True
                    self._derniereDirection = "Bas"
        elif event.type is KEYUP:
            if event.key == K_z:
                self._appuiValidation = False
                if self._etapeMarche > 1:
                    self._gestionnaire.registerPosition(self._nom, self._xTilePrecedent, self._yTilePrecedent, self._c, joueur=True, appuiJoueur=False, direction=self._directionRegard)
                else:
                    self._gestionnaire.registerPosition(self._nom, self._xTile, self._yTile, self._c, joueur=True, appuiJoueur=False, direction=self._directionRegard)
            if event.key == K_LEFT or event.key == K_RIGHT or event.key == K_DOWN or event.key == K_LEFT or event.key == K_UP:
                if event.key == K_LEFT: 
                    self._directions["Gauche"] = False
                elif event.key == K_RIGHT:
                    self._directions["Droite"] = False
                elif event.key == K_UP:
                    self._directions["Haut"] = False
                elif event.key == K_DOWN:
                    self._directions["Bas"] = False
        if self._etapeMarche == 1:
            nombreAppuis = 0
            for (directionActuelle,booleen) in self._directions.items():
                if booleen is True:
                    nombreAppuis += 1
                    directionChoisie = str(directionActuelle)
            if nombreAppuis == 0: #Quand il n'y a aucun appui, pas de direction
                self._majRegards()
                self._direction = "Aucune"
            elif nombreAppuis == 1: #Quand il y a un seul appui, la direction est celle de l'unique appui
                self._majRegards()
                self._direction = str(directionChoisie)
            elif nombreAppuis > 1: #Quand il y a plusieurs appuis, on prend le plus récent
                self._direction = str(self._derniereDirection)
                self._majRegards()
    
    def _majRegards(self):
        """Indique que le joueur doit, avant de se déplacer, regarder dans la direction de déplacement sauf dans celle qu'il emprunte déjà"""
        for directionActuelle,regard in self._regardDansDirection.items():
            if directionActuelle != self._direction and self._direction != "Aucune":
                self._regardDansDirection[directionActuelle] = False

    def teleporterSurPosition(self, xTile, yTile, direction, couche=-1):
        if couche == -1:
            couche = self._c
        self._ajusterPositionSource(self, direction)
        self._positionCarteOld.left, self._positionCarteOld.top = self._positionCarte.left, self._positionCarte.top
        self._xTilePrecedent, self._yTilePrecedent = self._xTile, self._yTile
        self._positionCarte.left, self._positionCarte.top = xTile*self._jeu.carteActuelle.hauteurTile, yTile*self._jeu.carteActuelle.hauteurTile
        self._boiteOutils.teleporterSurPosition(self._positionCarte, couche, self._positionSource, self._nomTileset, self._couleurTransparente, self._nom)
        self._gestionnaire.registerPosition(self._nom, self._xTile, self._yTile, couche, joueur=True, appuiJoueur=False, direction=self._directionRegard)
        Horloge.initialiser(id(self), 1, 1)
        self._jeu.carteActuelle.initialiserScrolling(self._positionCarte.left, self._positionCarte.top)
        self._etapeMarche, self._pixelsParcourus, self._regardAttente, self._directionAttente = 1,0, False, str(self._direction)

    def _deplacement(self):
        """Gère le déplacement"""
        hauteurTile = self._jeu.carteActuelle.hauteurTile
        carte = self._jeu.carteActuelle
        direction = self._direction
        if direction != "Aucune":
            if self._regardDansDirection[direction] == True: #Si on a déjà regardé dans la direction
                tempsActuel = pygame.time.get_ticks()
                avancee, deltaTimer = self._calculerNouvellesCoordonnees(tempsActuel, direction)
                if avancee >= 1.0:
                    if self._pixelsParcourus < hauteurTile: #Si le déplacement n'est pas fini
                        deplacementPossible = False
                        (self._positionCarteFuture.left, self._positionCarteFuture.top) = self._majCoordonnees(tempsActuel, direction, deltaTimer, avancee)
                        if self._etapeMarche == 1:
                            self._positionCarteSuivante = self._getPositionCarteSuivante(direction)
                            self._xTilePrecedent, self._yTilePrecedent = self._xTile, self._yTile
                            self._xTileSuivant, self._yTileSuivant =  self._positionCarteSuivante.left/32, self._positionCarteSuivante.top/32
                            deplacementPossible = self._jeu.carteActuelle.deplacementPossible(self._positionCarteSuivante, self._c, self._nom)
                        if deplacementPossible is True or self._etapeMarche > 1:
                            if self._etapeMarche == 1:
                                carte.verifierScrollingPossible(self._xTilePrecedent*32, self._yTilePrecedent*32, direction)
                            self._positionCarteOld.left, self._positionCarteOld.top = self._positionCarte.left, self._positionCarte.top
                            self._positionCarte.left, self._positionCarte.top = self._positionCarteFuture.left, self._positionCarteFuture.top
                            carte.gererScrolling(self._avanceeOrientee,direction)
                            if self._determinerAnimation():
                                self._ajusterPositionSource(self._enMarche.voir(), direction) #On trouve la position source du PNJ en marche
                            self._jeu.carteActuelle.poserPNJ(self._positionCarte, self._c, self._positionSource, self._nomTileset, self._couleurTransparente, self._nom, positionCarteSuivante=self._positionCarteSuivante)
                            self._pixelsParcourus += self._avancee
                            self._etapeMarche += 1
                        else: #Il y a collision, on ne peut pas quitter le tile, donc on réinitialise
                            self._pixelsParcourus, self._etapeMarche, self._directionAttente = 0, 1, str(self._direction)
                            self._tempsPrecedent = pygame.time.get_ticks()
                            self._direction = "Aucune"
                    else: #Le déplacement est fini, on réinitialise
                        self._gestionnaire.registerPosition(self._nom, self._xTile, self._yTile, self._c, joueur=True, appuiJoueur=False, direction=self._directionRegard)
                        self._etapeMarche, self._pixelsParcourus, self._regardAttente, self._directionAttente = 1,0, False, str(self._direction)
                        self._mouvement = self._positionCarte.left != self._positionCarteOld.left or self._positionCarte.top != self._positionCarteOld.top
                        self._direction = "Aucune"
                        self._tempsPrecedent = pygame.time.get_ticks()
            else: #Si on n'a pas regardé, on regarde
                self._positionCarteOld.left, self._positionCarteOld.top = self._positionCarte.left, self._positionCarte.top
                self._ajusterPositionSource(False, direction) #On trouve la position source du PNJ en marche
                self._jeu.carteActuelle.poserPNJ(self._positionCarte, self._c, self._positionSource, self._nomTileset, self._couleurTransparente, self._nom)
                self._regardDansDirection[direction] = True
        else:
            self._tempsPrecedent = pygame.time.get_ticks()
            if self._regardAttente is False:
                self._ajusterPositionSource(False, self._directionAttente) #On trouve la position source du PNJ en marche
                self._jeu.carteActuelle.poserPNJ(self._positionCarte, self._c, self._positionSource, self._nomTileset, self._couleurTransparente, self._nom)
                self._regardAttente = True

    
    def _getDirection(self):
        return self._direction

    def _getAppuiValidation(self):
        return self._appuiValidation

    def _getMouvement(self):
        return self._mouvement

    direction = property(_getDirection)
    appuiValidation = property(_getAppuiValidation)
    mouvement = property(_getMouvement)
