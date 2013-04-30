import pygame, configparser, math, directions, numpy
from pygame.locals import *
import pygame.surfarray as surfarray
from collections import OrderedDict
from tile import *
from constantes import *
from observateur import *
from zonePensee import *

if SESSION_DEBUG:
    import pdb

class Carte(Observateur):
    """Classe représentant une carte au niveau des données"""
    def __init__(self, config, jeu): 
        """Initialise la carte à exécuter  <carte> à partir des données issues de son fichier SQMAP.
        Cette méthode se charge surtout du transfert du format de carte .narromap à celui du Narro Engine (purement mémoriel)."""
        Observateur.__init__(self)
        self._longueur, self._largeur = config.getint("Generalites","Longueur"), config.getint("Generalites","Largeur")
        self._hauteurTile = 32
        self._nombreCouches = config.getint("Generalites","Couches")
        self._nom, self._description = config.get("Generalites","Nom"), config.get("Generalites","Description")
        self._musique, nombreRefs = config.get("Generalites","Musique"), config.getint("Generalites","Nombre ref")
        self._scrollingX, self._scrollingY = 0,0
        self._jeu, self._toutAChanger = jeu, True
        self._dicoSurfaces, self._tiles, self._blocsRef, self._pnj, self._tilesReserves, i = self._jeu.dicoSurfaces, list(), dict(), dict(), dict(), 0
        #self._surface = pygame.Surface((FENETRE["longueurFenetre"], FENETRE["largeurFenetre"]), flags=HWSURFACE|SRCALPHA)
        self._ecran = Rect(0, 0, self._longueur*32, self._largeur*32)
        while i < self._nombreCouches:
            self._pnj[i], self._tilesReserves[i]  = dict(), dict()
            i += 1
        i = 0
        self._scrollingPossible, self._etapeScrolling = False, 0
        self._surfaceZonePensee, self._positionZonePensee, self._besoinAffichageZonePensee = None, None, False
        self._emplacementScrollingX, self._emplacementScrollingY = int(int(FENETRE["longueurFenetre"]/2) / 32)*32, int(int(FENETRE["largeurFenetre"]/2)/32)*32
        self._ecranVisible = Rect(0, 0, FENETRE["longueurFenetre"], FENETRE["largeurFenetre"])
        self._positionsDepart = dict()
        gPos = lambda u,a: config.getint( "Bloc ref" + str(u) + "." + "Position source", str(a) )
        gTranspa = lambda u,a: config.getint( "Bloc ref" + str(u) + "." + "Couleur transparente", str(a) )
        while i < nombreRefs:
            if i > 0:
                cheminTileset = config.get("Bloc ref"+str(i),"Chemin image")
                praticabilite = config.getboolean("Bloc ref"+str(i),"Praticabilite")
                positionSource = (gPos(i,0), gPos(i,1), gPos(i,2), gPos(i,3))
                couleurTransparente = (gTranspa(i,0), gTranspa(i,1), gTranspa(i,2))
                self._blocsRef[i] = Bloc(jeu, nomTileset=cheminTileset, praticabilite=praticabilite, couleurTransparente=couleurTransparente, positionSource=positionSource, toutDonne=True)
            else: #Bloc vide
                self._blocsRef[i] = Bloc(jeu, vide=True)
            i += 1

        self._tilesLayers = []
        i = 0
        while i < self._nombreCouches:
            self._tilesLayers.append(pygame.Surface((self._longueur * 32, self._largeur * 32), flags=SRCALPHA|HWSURFACE).convert_alpha())
            i += 1

        i = 0
        while i < self._longueur:
            self._tiles.append(list())
            a = 0
            while a < self._largeur:
                self._tiles[i].append(Tile(i, a, config, self._blocsRef, self._nombreCouches, self._jeu, self._hauteurTile))
                coucheActuelle = 0
                while coucheActuelle < self._nombreCouches:
                    if self._tiles[i][a].bloc[coucheActuelle].vide == False:
                        nomTilesetActuel = self._tiles[i][a].bloc[coucheActuelle].nomTileset
                        positionSource = self._tiles[i][a].bloc[coucheActuelle].positionSource
                        self._ajouterSurface(positionSource, nomTilesetActuel, self._tiles[i][a].bloc[coucheActuelle].couleurTransparente)
                        self._tilesLayers[coucheActuelle].blit(self._dicoSurfaces[nomTilesetActuel][positionSource], (i*32, a*32) )
                    elif coucheActuelle == 0:
                        self._tilesLayers[coucheActuelle].fill( (0,0,0), (i*32, a*32, 32, 32))
                    coucheActuelle += 1
                a += 1
            i += 1

        i = 0

        self._fenetre, self._blitFrame = self._jeu.fenetre, False
        self._transformationsGlobales, self._transformationsParties, self._parametresTransformations = list(), list(), dict()

    def changerBloc(self, x, y, c, nomTileset, positionSource, couleurTransparente, praticabilite, vide=False):
        if self.tileExistant(x,y) is True and c < self.nombreCouches:
            bloc, jeu = self._tiles[x][y].bloc[c], self._jeu
            if vide is False:
                bloc = Bloc(jeu,pnj=False,toutDonne=True, nomTileset=nomTileset, positionSource=positionSource, couleurTransparente=couleurTransparente, praticabilite=praticabilite)
                self._tiles[x][y].bloc[c] = bloc
                self._ajouterSurface(positionSource, DOSSIER_RESSOURCES+nomTileset, couleurTransparente)
                self._tilesLayers[c].blit(self._dicoSurfaces[DOSSIER_RESSOURCES + nomTileset][positionSource], (x*self._hauteurTile, y*self._hauteurTile) )
            else:
                bloc, praticabilite = Bloc(jeu, vide=True), True
                self._tiles[x][y].bloc[c] = bloc
                absi, ordo, i, a = x*self._hauteurTile, y*self._hauteurTile, 0, 0
                couleurEntierementTransparente = Color(0,0,0,0)
                while i < self._hauteurTile: #On rend transparent les pixels du tile désormais vide
                    a = 0
                    while a < self._hauteurTile:
                        self._tilesLayers[c].set_at((absi+i, ordo+a), couleurEntierementTransparente)
                        a += 1
                    i += 1
            self._tiles[x][y].modifierPraticabilite(c, praticabilite)
            self.mettreToutAChanger()


    def tileExistant(self,x,y):
        """Retourne True si le tile de coordonnées <x>,<y> existe"""
        return x >= 0 and x < self._longueur and y >= 0 and y < self._largeur

    def tilePraticable(self, x, y, c):
        if x < len(self._tiles):
            if y < len(self._tiles[x]):
                if c < len(self._tiles[x][y].praticabilite):
                    return self._tiles[x][y].praticabilite[c]
                else:
                    return False
            else:
                return False
        else:
            return False

    def _ajouterSurface(self, positionSource, nomTileset,couleurTransparente):
        """Ajoute la surface correspondant à un bloc dans le dico de surfaces, si elle n'y est pas déjà."""
        if nomTileset not in self._dicoSurfaces:
            self._dicoSurfaces[nomTileset] = dict()
            try:
                """surface = pygame.image.load(nomTileset).convert_alpha()
                self._dicoSurfaces[nomTileset]["Source"] = pygame.Surface((surface.get_width(), surface.get_height()), flags=HWSURFACE|SRCALPHA)
                self._dicoSurfaces[nomTileset]["Source"].blit(surface, (0,0))"""
                self._dicoSurfaces[nomTileset]["Source"] = pygame.image.load(nomTileset).convert_alpha()
            except pygame.error as erreur:
                print( MESSAGE_ERREUR_CHARGEMENT_TILESET.format(nomTileset), str(erreur) )
        if positionSource not in self._dicoSurfaces[nomTileset].keys():
            self._dicoSurfaces[nomTileset][positionSource] = self._dicoSurfaces[nomTileset]["Source"].subsurface(pygame.Rect(positionSource))
    
    def _determinerPresenceSurTiles(self, x, y, longueur, largeur):
        abscisses, ordonnees, x, y, longueur, largeur, i = [], [], (x / 32), (y/32), int(longueur/32), int(largeur/32), 0
        abscisses = list(range(math.floor(x), math.ceil(x) + longueur))
        ordonnees = list(range(math.floor(y), math.ceil(y) + largeur))
        listeTilesPresence = [(absa, ordo) for absa in abscisses for ordo in ordonnees]
        return listeTilesPresence

    def coordonneesAuTileSuivant(self, direction, x, y):
        """Retourne les deux coordonnées au tile suivant en fonction de la direction."""
        xReponse, yReponse = int(x/32), int(y/32)
        if direction is "Gauche" or direction is "Droite":
            xReponse = int( directions.ajusterCoordonneesLorsDeplacement(x, direction) / 32)
        elif direction is "Haut" or direction is "Bas":
            yReponse = int( directions.ajusterCoordonneesLorsDeplacement(y, direction) / 32)
        return (xReponse, yReponse)

    def deplacementPossible(self, positionCarte, c, nomPNJ):
        """Indique si un déplacement en <x><y><c> est possible. Retourne un 2-tuple avec :
        * <True> si un PNJ peut être positionné en <x><y><c>, sinon <False>. Si <xOld>,<yOld> sont fournis, ne prend pas en compte le PNJ à cette position pour les collisions.
        * Le tile qui vient d'être quitté."""
        deplacementPossible = True
        if self._ecran.contains(positionCarte) == 0: #Si la position d'arrivée existe dans la carte
            deplacementPossible = False
        pnjsEnCollision = [pnj for pnj in self._pnj[c].values() if pnj.nomPNJ != nomPNJ and (pnj.positionCarte.colliderect(positionCarte) == 1 and (pnj.positionCarteSuivante == positionCarte or pnj.positionCarteSuivante == False))]
        if len(pnjsEnCollision) > 0:
            deplacementPossible = False
        for (x,y) in self._determinerPresenceSurTiles(positionCarte.left, positionCarte.top, positionCarte.width, positionCarte.height):
            if self.tilePraticable(x, y, c) is False: #Si le tile est impraticable
                deplacementPossible = False
        return deplacementPossible

    def supprimerPNJ(self, nomPNJ, couche):
        """Supprime un PNJ à l'écran."""
        if nomPNJ in self._pnj[couche].keys():
            del self._pnj[couche][nomPNJ]
            self._toutAChanger = True

    def poserPNJ(self, positionCarte, c, positionSource, nomTileset, couleurTransparente, nomPNJ, positionCarteSuivante=False):
        """Ordonne l'affichage à l'écran d'un PNJ à une nouvelle position et l'effacement du PNJ à sa position précedente"""
        hauteurTile = self._hauteurTile
        x,y = float(positionCarte.left), float(positionCarte.top)
        if nomPNJ not in self._pnj[c].keys():
            self._pnj[c][nomPNJ] = Bloc(self._jeu, pnj=True, nomPNJ=nomPNJ, nomTileset=nomTileset, positionCarte=positionCarte, positionCarteSuivante=positionCarteSuivante, positionSource=positionSource)
        pnj = self._pnj[c][nomPNJ]
        if pnj.positionSource != positionSource:
            pnj.positionSource = positionSource
        if pnj.nomTileset != nomTileset:
            pnj.nomTileset = nomTileset
        if pnj.couleurTransparente != couleurTransparente:
            pnj.couleurTransparente = couleurTransparente
        if pnj.positionCarte != positionCarte:
            pnj.positionCarte = positionCarte
        if pnj.positionCarteSuivante != positionCarteSuivante:
            pnj.positionCarteSuivante = positionCarteSuivante
        self._toutAChanger = True
        self._ajouterSurface( (positionSource.left, positionSource.top, positionSource.width, positionSource.height), nomTileset, couleurTransparente)
    
    def _transformerPartie(self, surface):
        """Applique une transformation individuellement à chaque <surface> (mobile, tile...) lors de sa pose."""
        for nomTransformation in self._transformationsParties:
            p = self._parametresTransformations[nomTransformation]
            if nomTransformation == "AlphaFixe":
                pixels = surfarray.pixels_alpha(surface)
                positionsNulles = numpy.where(pixels == 0)
                pixels[:,:] = p["alpha"]
                pixels[positionsNulles] = 0

    def mettreToutAChanger(self):
        self._toutAChanger = True

    def _coordonneeScrollingPossible(self, coor, abs=False):
        """Retourne <True> si <coor> est dans un emplacement où le scrolling est possible. 
        Paramètre : quand <abs> vaut <True>, il s'agit non pas d'une ordonnée, mais d'une abscisse."""
        if abs is False: #Ordonnée
            return coor == self._emplacementScrollingY
        else: #Abscisse
            return coor == self._emplacementScrollingX

    def _coordonneeDansPartieAffichable(self, x, y, longueur=1, largeur=1):
        """Retourne <True> si la coordonnée est dans une partie affichable à l'écran selon le scrolling actuel."""
        position = Rect(x, y, longueur, largeur)
        return (self._ecranVisible.contains(position) == 1) or (self._ecranVisible.contains(position) == 0 and self._ecranVisible.colliderect(position) == 1)
    
    def verifierScrollingPossible(self, x, y, direction):
        """Vérifie si le scrolling est possible pour faciliter le traitement dans gererScrolling"""
        self._scrollingPossible, scrollingDirection = False, True
        if direction == "Bas" and int(self._scrollingY / 32) + int(FENETRE["largeurFenetre"]/32) >= self._largeur:
            scrollingDirection = False
        if direction == "Haut" and self._scrollingY == 0:
            scrollingDirection = False
        if direction == "Droite" and int(self._scrollingX / 32) + int(FENETRE["longueurFenetre"]/32) >= self._longueur:
            scrollingDirection = False
        if direction == "Gauche" and self._scrollingX == 0:
            scrollingDirection = False
        if scrollingDirection is True:
            x, y = x - self._scrollingX, y - self._scrollingY
            scrollingPossibleX = self._coordonneeScrollingPossible(x, abs=True)
            scrollingPossibleY = self._coordonneeScrollingPossible(y, abs=False)
            if (direction == "Haut" or direction == "Bas") and scrollingPossibleY is True:
                self._scrollingPossible, self._directionScrolling = True, direction
                Horloge.initialiser(id(self), 1, 1, comptageTempsPasse=True)
            elif (direction == "Gauche" or direction == "Droite") and scrollingPossibleX is True:
                self._scrollingPossible, self._directionScrolling = True, direction
                Horloge.initialiser(id(self), 1, 1, comptageTempsPasse=True)
    
    def gererScrolling(self, changement, direction):
        """Gère le scrolling"""
        #if Horloge.sonner(id(self), 1) is True:
        if True:
            #direction, changement, attente  = self._directionScrolling, 2, 250/16
            if (direction == "Droite" or direction == "Gauche") and self._scrollingPossible is True:
                self._scrollingX += changement
                self.mettreToutAChanger()
                self._ecranVisible.move_ip(changement, 0)
                return True
            elif (direction == "Bas" or direction == "Haut") and self._scrollingPossible is True:
                self._scrollingY += changement
                self.mettreToutAChanger()
                self._ecranVisible.move_ip(0, changement)
                return True
            else:
                return False

    def initialiserScrolling(self, x, y):
        """Après la création de la carte, initialise le scrolling à la position du joueur si nécessaire.
        <x> est l'abscisse du joueur, <y> son ordonnée. Ces coordonnées sont données en pixels."""
        self._ecranVisible.top, self._ecranVisible.left = 0, 0
        scrollingAInitialiserX, scrollingAInitialiserY, x, y = True, True, x, y
        if FENETRE["largeurFenetre"] >= self._largeur * 32: #Carte petite
            scrollingAInitialiserY = False
        if FENETRE["longueurFenetre"] >= self._longueur * 32:
            scrollingAInitialiserX = False
        if x < self._emplacementScrollingX: #On est dans une partie de la carte où le scrolling est inutile
            scrollingAInitialiserX = False
        if y < self._emplacementScrollingY:
            scrollingAInitialiserY = False
        if scrollingAInitialiserX is True:
            self._scrollingX = x - self._emplacementScrollingX #A chaque instant, on a x - scrollingX = emplacementScrollingX, d'où cette relation
            if int(FENETRE["longueurFenetre"]/32) + int(self._scrollingX/32) >= self._longueur: #Quand on est aux bords de la carte
                self._scrollingX = (self._longueur*32) - FENETRE["longueurFenetre"]
        if scrollingAInitialiserY is True:
            self._scrollingY = y - self._emplacementScrollingY
            if int(FENETRE["largeurFenetre"]/32) + int(self._scrollingY/32) >= self._largeur:
                self._scrollingY = (self._largeur*32) - FENETRE["largeurFenetre"]
        self._ecranVisible = Rect(0, 0, FENETRE["longueurFenetre"], FENETRE["largeurFenetre"])
        self._ecranVisible.move_ip(self._scrollingX, self._scrollingY)

    def obsOnNouvelleObservation(self, instance, nomAttribut, info):
        if isinstance(instance, ZonePensee) is True and nomAttribut == "_surface":
            self._surfaceZonePensee, self._besoinAffichageZonePensee = info.copy(), True
        elif isinstance(instance, ZonePensee) is True and nomAttribut == "_positionSurface":
            self._positionZonePensee = list(info)
    
    def _afficherZonePensee(self, affichageComplet=False):
        """S'il y a quelque chose à afficher, réaffiche la zone de pensée. 
        <affichageComplet> est un booléen qui vaut <True> lorsque pygame.display.flip est appelée à la suite de l'appel de la fonction."""
        positionZoneEntiere = (0, FENETRE["largeurFenetre"], FENETRE["longueurFenetre"], FENETRE["largeurFenetreReelle"] - FENETRE["largeurFenetre"])
        self._fenetre.fill(COULEUR_FOND_ZONE_PENSEE,rect=positionZoneEntiere)
        if self._surfaceZonePensee is not None:
            self._fenetre.blit(self._surfaceZonePensee, self._positionZonePensee)
        if affichageComplet is False:
            pygame.display.update(positionZoneEntiere)
        self._besoinAffichageZonePensee, self._blitFrame = False, True

    def _appliquerTransformationGlobale(self, nomTransformation, **p):
        """Applique la transformation globale <nomTransformation> avec le dico de paramètres <p>."""
        if nomTransformation == "Rouge":
            pixels = surfarray.pixels3d(self._fenetre)[:FENETRE["longueurFenetre"], :FENETRE["largeurFenetre"]] #On exclut la zone de pensée
            pixels[:,:,1:] = 0
        elif nomTransformation == "Noir":
            pixels = surfarray.pixels3d(self._fenetre)[:FENETRE["longueurFenetre"],:FENETRE["largeurFenetre"]]
            pixels /= p["coef"]
            if p["coef"] >= 12:
                pixels[:] = (0,0,0)
        elif nomTransformation == "NoirTotal":
            pixels = surfarray.pixels3d(self._fenetre)[:FENETRE["longueurFenetre"],:FENETRE["largeurFenetre"]]
            pixels[:] = (0,0,0)
        elif nomTransformation == "RemplirNoir":
            self._fenetre.fill((0,0,0))
        elif "SplashText" in nomTransformation:
            if "couleurFond" in p.keys():
                couleurFond=p["couleurFond"]
            else:
                couleurFond=None
            surfaceTexte = self._jeu.zonePensee.polices["splashText"].render(p["texte"], p["antialias"], p["couleurTexte"], couleurFond)
            self._fenetre.blit(surfaceTexte, p["position"])
        elif nomTransformation == "Nuit":
            self._fenetre.fill((0,0,0))
            c = 0
            while c < self._nombreCouches: 
                for nomPnj in self._pnj[c]: 
                    self._afficherBlocPnj(c, nomPnj)
                c += 1


    def _transformerSurfaceGlobalement(self, affichageComplet=False):
        """A chaque frame, regarde s'il y a des transformations globales à appliquer, et les exécute lorsque c'est le cas.
        <affichageComplet> doit valoir <True> si la fonction doit mettre à jour l'écran entier elle-même (car personne ne le fait après).
        Retourne <True> quand la fonction s'est occupée de la mise à jour de l'écran (car on le lui a demandé ET qu'il y avait des transfos à traiter)."""
        if len(self._transformationsGlobales) > 0: #S'il y a des transformations à opérer
            longueurFenetre, largeurFenetre = FENETRE["longueurFenetre"], FENETRE["largeurFenetre"]
            for nomTransformation in self._transformationsGlobales:
                self._appliquerTransformationGlobale(nomTransformation, **self._parametresTransformations[nomTransformation]) #On applique la transfo
            if affichageComplet:
                pygame.display.flip()
                return True
            else:
                return False
        else:
            return False

    def _afficherBlocPnj(self, c, nomPnj):
        """Affiche un PNJ sur un bloc"""
        pnj = self._pnj[c][nomPnj]
        positionCollage = pnj.positionCarte.move(-self._scrollingX, -self._scrollingY)
        if len(self._transformationsParties) > 0:
            surfaceCollage = self._dicoSurfaces[pnj.nomTileset][(pnj.positionSource.left, pnj.positionSource.top, pnj.positionSource.width, pnj.positionSource.height)].copy()
            self._transformerPartie(surfaceCollage)
        else:
            surfaceCollage = self._dicoSurfaces[pnj.nomTileset][(pnj.positionSource.left, pnj.positionSource.top, pnj.positionSource.width, pnj.positionSource.height)]
        self._fenetre.blit(surfaceCollage, positionCollage)
    
    def afficher(self):
        """Cette méthode gère l'affichage de la carte"""
        self._blitFrame = False
        if self._toutAChanger is True:
            coucheActuelle = 0
            self._fenetre.fill((0,0,0))
            while coucheActuelle < self._nombreCouches: 
                self._fenetre.blit(self._tilesLayers[coucheActuelle], (0,0), area=self._ecranVisible)
                nomsPnjs = sorted(self._pnj[coucheActuelle], key=lambda nomPNJ: self._pnj[coucheActuelle][nomPNJ].positionCarte.top)
                #Tri des PNJs selon leur ordonnée (de manière croissante) : on affiche ceux en haut de l'écran avant ceux en bas, pour avoir une superposition
                for nomPnj in nomsPnjs: 
                    self._afficherBlocPnj(coucheActuelle, nomPnj)
                coucheActuelle += 1
            self._transformerSurfaceGlobalement()
            self._afficherZonePensee(affichageComplet=True)
            #self._fenetre.blit(self._surface, (0,0))
            self._blitFrame = True

        if self._besoinAffichageZonePensee is True:
            self._afficherZonePensee(affichageComplet=self._blitFrame)

        if self._blitFrame is True:
            self._jeu.horlogeFps.tick(120)
            pygame.display.flip()

    def _getNombreCouches(self):
        """Retourne le nombre de couches défini sur la carte"""
        return self._nombreCouches

    def _getHauteurTile(self):
        """Retourne la hauteur d'un tile sur la carte"""
        return self._hauteurTile

    def _getNom(self):
        return self._nom

    def _getLongueur(self):
        return self._longueur

    def _getLargeur(self):
        return self._largeur

    def _getTransformationsGlobales(self):
        return self._transformationsGlobales

    def _setTransformationsGlobales(self, val):
        self._transformationsGlobales = val

    def _getTransformationsParties(self):
        return self._transformationsParties

    def _setTransformationsParties(self, val):
        self._transformationsParties = val

    def _getParametresTransformations(self):
        return self._parametresTransformations

    def _getTiles(self):
        return self._tiles

    nombreCouches = property(_getNombreCouches)
    hauteurTile = property(_getHauteurTile)
    nom = property(_getNom)
    longueur = property(_getLongueur)
    largeur = property(_getLargeur)
    tiles = property(_getTiles)
    transformationsGlobales = property(_getTransformationsGlobales, _setTransformationsParties)
    transformationsParties = property(_getTransformationsParties, _setTransformationsParties)
    parametresTransformations = property(_getParametresTransformations)
