# -*-coding:utf-8 -*
import pygame, math, narro.directions, narro.tmxreader, numpy, os, sys
from pygame.locals import *
from narro import *
import pygame.surfarray as surfarray
from collections import OrderedDict
from .tile import *
from .constantes import *
from .observateur import *
from .zonePensee import *

if SESSION_DEBUG:
    import pdb


class Carte(Observateur):
    """Classe représentant une carte au niveau des données"""
    def __init__(self, nomCarte, jeu): 
        """Initialise la carte à exécuter  <carte> à partir des données issues de son fichier SQMAP.
        Cette méthode se charge surtout du transfert du format de carte .narromap à celui du Narro Engine (purement mémoriel)."""
        Observateur.__init__(self)
        self._carteTiled = tmxreader.TileMapParser().parse_decode(os.path.join(DOSSIER_RESSOURCES, nomCarte + ".tmx"))
        self._nom, self._description = self._carteTiled.properties.get("nom", nomCarte), self._carteTiled.properties.get("description", "")
        self._musique = self._carteTiled.properties.get("musique", "")
        self._longueur, self._largeur = self._carteTiled.width, self._carteTiled.height
        self._nombreCouches, self._hauteurTile = len(self._carteTiled.layers), self._carteTiled.tilewidth
        self._scrollingX, self._scrollingY = 0,0
        self._jeu, self._toutAChanger = jeu, True
        self._dicoSurfaces, self._tiles, self._tileRect, self._tilesEtendus, self._blocsRef, self._pnj, i = dict(), list(), Rect(0, 0, 32, 32), dict(), list(), dict(), 0
        self._subTilesEtendus, self._subTilesBlittes, self._ecran = dict(), list(), Rect(0, 0, self._longueur*32, self._largeur*32)
        self._scrollingPossible, self._etapeScrolling = False, 0
        self._surfaceZonePensee, self._positionZonePensee, self._besoinAffichageZonePensee, self._faceActuelle = None, None, False, False
        self._emplacementScrollingX, self._emplacementScrollingY = int(int(FENETRE["longueurFenetre"]/2) / 32)*32, int(int(FENETRE["largeurFenetre"]/2)/32)*32
        self._ecranVisible = Rect(0, 0, FENETRE["longueurFenetre"], FENETRE["largeurFenetre"])
        self._positionsDepart, self._polices = dict(), dict()
        self._ajouterPolice(NOM_FICHIER_POLICE_PAR_DEFAUT, TAILLE_POLICE_SPLASH_SCREEN)
        self._fenetre, self._blitFrame = self._jeu.fenetre, False
        self._transformationsGlobales, self._transformationsParties, self._parametresTransformations = list(), list(), dict()
        self._idParametres, self._donneesParametres, self._messagesCollision = dict(), dict(), list()

        self._dicoGid = dict()
        for tileset in self._carteTiled.tile_sets:
            for image in tileset.images:
                self._ajouterSurface(False, image.source, False, tileset=tileset, mobile=False)
            
        self._tilesLayers = []
        i, x, y = 0, 0, 0
        while i < self._nombreCouches:
            x = 0
            self._tilesLayers.append(pygame.Surface((self._longueur * 32, self._largeur * 32), flags=SRCALPHA))
            self._pnj[i] = dict()
            while x < self._longueur:
                y = 0
                self._tiles.append(list())
                while y < self._largeur:
                    self._tiles[x].append(Tile(self._nombreCouches))
                    gid = self._carteTiled.layers[i].content2D[x][y]
                    if gid != 0: #Bloc plein
                        if gid not in self._tilesEtendus.keys(): #Tile plein standard
                            self._tiles[x][y].bloc.append(Bloc(infos=self._dicoGid[gid]))
                            surfaceTileset, positionSource = self._dicoSurfaces[self._dicoGid[gid][0]]["Source"], self._dicoGid[gid][2]
                            self._tilesLayers[i].blit(surfaceTileset, (x * self._hauteurTile, y * self._hauteurTile), area=positionSource) 
                        else: #Tile étendu formé de sous-tiles
                            self._tiles[x][y].bloc.append(Bloc(vide=True)) #On met un tile vide en la position de réf du tile étendu ; ce sera complété avec un sous-tile étendu
                            if i == 0:
                                self._tilesLayers[i].fill((0,0,0), (x * self._hauteurTile, y * self._hauteurTile, self._hauteurTile, self._hauteurTile))
                            ####
                            positionSource = self._dicoGid[gid][2]
                            longueurTileset, largeurTileset = int(positionSource[2]/self._hauteurTile), int(positionSource[3]/self._hauteurTile)
                            xMin, yMin = x, y - largeurTileset + 1
                            xMax, yMax, xActuel, yActuel, i2 = xMin + longueurTileset, yMin + largeurTileset, xMin, yMin, 0
                            (praticabilites, couches) = self._tilesEtendus[gid] 
                            couches = [i if c == -1 else int(c) for c in couches] #-1 est la valeur par défaut pour dire la couche du tile étendu 
                            while yActuel < yMax:
                                xActuel = xMin
                                while xActuel < xMax:
                                    self._subTilesEtendus.setdefault((xActuel, yActuel, couches[i2]), [])
                                    positionSourceSubTile = positionSource[0] + ((xActuel-xMin)*self._hauteurTile), positionSource[1] + ((yActuel-yMin)*self._hauteurTile), self._hauteurTile, self._hauteurTile
                                    self._subTilesEtendus[(xActuel, yActuel, couches[i2])].append((couches[i2], praticabilites[i2], positionSourceSubTile, self._dicoGid[gid][0]))
                                    if (xActuel <= x or yActuel <= y) and couches[i2] <= i:
                                        self._completerAvecTileEtendu(xActuel,yActuel,couches[i2])
                                    xActuel, i2 = xActuel + 1, i2 + 1
                                yActuel += 1
                    else: #Bloc vide
                        self._tiles[x][y].bloc.append(Bloc(vide=True))
                        if i == 0: #Sur la couche 0, il faut mettre du noir pour les blocs vides
                            self._tilesLayers[i].fill((0,0,0), (x * self._hauteurTile, y * self._hauteurTile, self._hauteurTile, self._hauteurTile))
                    if (x,y,i) in self._subTilesEtendus.keys() and (x,y,i) not in self._subTilesBlittes: #Un sous-tile étendu en cette position qu'on n'a pas encore blitté
                        self._completerAvecTileEtendu(x,y,i)
                    if i == self._nombreCouches - 1:
                        self._tiles[x][y].recalculerPraticabilites()
                    y += 1
                x += 1
            i += 1
        del self._dicoGid

    def _completerAvecTileEtendu(self, x, y, c, initialisation=True):
        for tileEtendu in self._subTilesEtendus[x,y,c]:
            if initialisation:
                self._tiles[x][y].ajouterTileEtendu(*tileEtendu)
            surfaceTileset, positionSource = self._dicoSurfaces[tileEtendu[3]]["Source"], tileEtendu[2]
            self._tilesLayers[c].blit(surfaceTileset, (x * self._hauteurTile, y * self._hauteurTile), area=positionSource) 
            self._subTilesBlittes.append((x,y,c))

    def _completerDicoGids(self, nomTileset, tileset, longueur, largeur):
        """Lors du chargement d'un tileset dans _ajouterSurface (quand une carte est créée), cette fonction se charge de faire correspondre à chaque tile du tileset les infos
        qui lui correspondent. 1 Tile dans le tileset = 1 GID = 1 position source, 1 praticabilité, 1 nom de tileset"""
        gid, idTileset, x, y, tileWidth, tileHeight = int(tileset.firstgid), 0, 0, 0, int(tileset.tilewidth), int(tileset.tileheight)
        tilesEtendus = tileset.properties.get("tileEtendu", False)
        while y < largeur:
            x = 0
            while x < longueur:
                if len(tileset.tiles) > 0:
                    praticabilite = tileset.tiles[idTileset].properties.get("Praticabilite", False) == "True"
                else: #Tileset importé d'ailleurs, les praticabilités n'ont pas été indiquées
                    praticabilite = True
                self._dicoGid[gid] = nomTileset, praticabilite, (x, y, tileWidth, tileHeight)
                if tilesEtendus: #On récupère les praticabilités et couches des sous-tiles
                    if "Praticabilites" in tileset.tiles[idTileset].properties.keys():
                        praticabilitesTile =tileset.tiles[idTileset].properties["Praticabilites"].split(",") 
                        praticabilitesTile = [praticabiliteTile == "True" for praticabiliteTile in praticabilitesTile]
                    else:
                        praticabilitesTile = [praticabilite] * ( int(tileWidth/self._hauteurTile) * int(tileHeight/self._hauteurTile) )
                    if "Couches" in tileset.tiles[idTileset].properties.keys():
                        couchesTile = tileset.tiles[idTileset].properties["Couches"].split(",") 
                    else:
                        couchesTile = [-1] * ( int(tileWidth/self._hauteurTile) * int(tileHeight/self._hauteurTile) )
                    self._tilesEtendus[gid] = praticabilitesTile, couchesTile
                gid, idTileset, x = gid + 1, idTileset + 1, x + tileWidth #increments
            y += tileHeight


    def _ajouterSurface(self, positionSource, cheminVersTileset,couleurTransparente, tileset=False, mobile=True):
        """Ajoute la surface correspondant à un bloc dans le dico de surfaces, si elle n'y est pas déjà. 
        Pour les tilesets, on ajoute la surface entière seulement. Pour les mobiles, on enregistre aussi la partie du tileset qui nous intéresse.
        Pour les tilesets, on complète le dico de GIDs (lors de la création de la carte)."""
        nomTileset = os.path.basename(cheminVersTileset)
        if nomTileset not in self._dicoSurfaces:
            self._dicoSurfaces[nomTileset] = dict()
            try:
                self._dicoSurfaces[nomTileset]["Source"] = pygame.image.load(os.path.join(DOSSIER_RESSOURCES,nomTileset))
                if tileset is not False:
                    self._completerDicoGids(nomTileset, tileset, self._dicoSurfaces[nomTileset]["Source"].get_width(), self._dicoSurfaces[nomTileset]["Source"].get_height())
            except pygame.error as erreur:
                print( MESSAGE_ERREUR_CHARGEMENT_TILESET.format(nomTileset), str(erreur) )
        if mobile is True and positionSource not in self._dicoSurfaces[nomTileset].keys():  #On ne conserve les sous-surfaces que des mobiles
            self._dicoSurfaces[nomTileset][positionSource] = pygame.Surface((positionSource[2],positionSource[3]), flags=SRCALPHA).convert_alpha()
            self._dicoSurfaces[nomTileset][positionSource].blit(self._dicoSurfaces[nomTileset]["Source"], (0,0), area=positionSource)
        elif mobile is False and positionSource is not False: #pour changerBloc : on retourne la sous-surface pour la blitter sur les tiles layers
            return self._dicoSurfaces[nomTileset]["Source"].subsurface(positionSource)

    def changerBloc(self, x, y, c, nomTileset, positionSource, couleurTransparente, praticabilite, vide=False, permanente=False, nomModif=None):
        if self.tileExistant(x,y) is True and c < self.nombreCouches:
            bloc, jeu = self._tiles[x][y].bloc[c], self._jeu
            if vide is False:
                bloc = Bloc(nomTileset=nomTileset, positionSource=positionSource, couleurTransparente=couleurTransparente, praticabilite=praticabilite)
                self._tiles[x][y].bloc[c] = bloc
                surfaceBloc = self._ajouterSurface(positionSource, nomTileset, couleurTransparente, tileset=False, mobile=False)
                self._tilesLayers[c].fill((0,0,0,0), rect=Rect(x*self._hauteurTile, y*self._hauteurTile, self._hauteurTile, self._hauteurTile))
                self._tilesLayers[c].blit(surfaceBloc, (x*self._hauteurTile, y*self._hauteurTile) )
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
            if permanente:
                self._jeu.ajouterModificationCarte(self._nom, nomModif, x, y, c, nomTileset, positionSource, couleurTransparente, praticabilite, vide=vide)
            self._tiles[x][y].modifierPraticabilite(c, praticabilite)
            if (x,y,c) in self._tilesEtendus.keys():
                self._completerAvecTileEtendu(x, y, c, initialisation=False)
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

    def _traiterPositionRelative(self, positionCarte, positionRelative):
        positionFinale = positionCarte.copy()
        positionFinale.width, positionFinale.height = positionCarte.width, positionCarte.height
        return positionFinale.move(positionRelative.left, positionRelative.top)
        
    def _prevenirCollision(self, pnjCogne, pnjCogneur, positionCogneur):
        self._messagesCollision.append((pnjCogne, pnjCogneur, positionCogneur))

    def deplacementPossible(self, positionCarte, c, nomPNJ, verifPrecise=False, positionCollision=False, positionVisible=False, ecranVisible=False, exclusionCollision=[], collisionEffective=False, axeTiles=True):
        """Indique si un déplacement en <x><y><c> est possible. Retourne un 2-tuple avec :
        * <True> si un PNJ peut être positionné en <x><y><c>, sinon <False>. Si <xOld>,<yOld> sont fournis, ne prend pas en compte le PNJ à cette position pour les collisions.
        * La praticabilité est vérifiée via des Rect quand <verifPrecise> vaut <True>.
        * Vérifie que l'objet est visible à l'écran quand <ecranVisible> vaut <True>.
        * Ne prend pas en compte les collisions avec tout PNJ dont le nom est présent dans la liste <exclusionCollision>.
        * Le tile qui vient d'être quitté."""
        deplacementPossible = True
        if positionCollision is False:
            positionCollision = positionCarte
        else:
            positionCollision = self._traiterPositionRelative(positionCarte, positionCollision)
        if not positionVisible:
            positionVisible = positionCarte
        else:
            positionVisible = self._traiterPositionRelative(positionCarte, positionVisible)
        if self._ecran.contains(positionCarte) == 0: #Si la position d'arrivée existe dans la carte
            deplacementPossible = False
        if ecranVisible is True and not (self._ecranVisible.contains(positionVisible) or self._ecranVisible.colliderect(positionVisible)):
            deplacementPossible = False
        pnjsEnCollision = [pnj for pnj in self._pnj[c].values() if pnj.nomPNJ != nomPNJ and pnj.nomPNJ not in exclusionCollision and (pnj.positionCollision.colliderect(positionCollision) == 1 and (not axeTiles or (pnj.positionCarteSuivante == positionCarte or pnj.positionCarteSuivante == False)))]
        if len(pnjsEnCollision) > 0:
            deplacementPossible = False
            if collisionEffective:
                for pnj in pnjsEnCollision:
                    self._prevenirCollision(pnj.nomPNJ, nomPNJ, positionCarte)
        if deplacementPossible:
            for (x,y) in self._determinerPresenceSurTiles(positionCarte.left, positionCarte.top, positionCarte.width, positionCarte.height):
                if self.tilePraticable(x, y, c) is False: #Si le tile est impraticable
                    self._tileRect.left, self._tileRect.top = x*32, y*32
                    if (verifPrecise and positionCollision.colliderect(self._tileRect)) or (not verifPrecise):
                        deplacementPossible = False
        return deplacementPossible

    def supprimerPNJ(self, nomPNJ, couche):
        """Supprime un PNJ à l'écran."""
        if nomPNJ in self._pnj[couche].keys():
            del self._pnj[couche][nomPNJ]
            self._toutAChanger = True

    def poserPNJ(self, positionCarte, c, positionSource, nomTileset, couleurTransparente, nomPNJ, positionCarteSuivante=False, positionCollision=False, positionVisible=False):
        """Ordonne l'affichage à l'écran d'un PNJ à une nouvelle position et l'effacement du PNJ à sa position précedente"""
        hauteurTile = self._hauteurTile
        x,y = float(positionCarte.left), float(positionCarte.top)
        if nomPNJ not in self._pnj[c].keys():
            self._pnj[c][nomPNJ] = Bloc(self._jeu, pnj=True, nomPNJ=nomPNJ, nomTileset=nomTileset, positionCarte=positionCarte, positionCarteSuivante=positionCarteSuivante, positionSource=positionSource, positionCollision=positionCollision, positionVisible=positionVisible)
        pnj = self._pnj[c][nomPNJ]
        if not positionCollision:
            positionCollision = pnj.positionCollision
        if not positionVisible:
            positionVisible =  pnj.positionVisible
        if pnj.positionCollision != positionCollision:
            pnj.positionCollision = positionCollision
        if pnj.positionVisible != positionVisible:
            pnj.positionVisible = positionVisible
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
    
    def mettreToutAChanger(self):
        self._toutAChanger = True

    def _coordonneeScrollingPossible(self, coor, abs=False):
        """Retourne <True> si <coor> est dans un emplacement où le scrolling est possible. 
        Paramètre : quand <abs> vaut <True>, il s'agit non pas d'une ordonnée, mais d'une abscisse."""
        if abs is False: #Ordonnée
            return coor == self._emplacementScrollingY
        else: #Abscisse
            return coor == self._emplacementScrollingX

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
            elif (direction == "Gauche" or direction == "Droite") and scrollingPossibleX is True:
                self._scrollingPossible, self._directionScrolling = True, direction
    
    def gererScrolling(self, changement, direction):
        """Gère le scrolling"""
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
            if info is not None:
                self._surfaceZonePensee, self._besoinAffichageZonePensee = info.copy(), True
        elif isinstance(instance, ZonePensee) is True and nomAttribut == "_positionSurface":
            if info is not None:
                self._positionZonePensee = list(info)
        elif isinstance(instance, ZonePensee) is True and nomAttribut == "_faceActuelle":
            self._faceActuelle = info.copy() if isinstance(info, pygame.Surface) else False

    def _transformerPartie(self, surface, nomPnj, positionVisible, positionCarte, **p):
        """Applique une transformation individuellement à chaque <surface> (mobile) lors de sa pose."""
        for nomTransformation in self._transformationsParties:
            p = self._parametresTransformations[nomTransformation]
            if nomTransformation == "AlphaFixe":
                """pixels = surfarray.pixels_alpha(surface)
                positionsNulles = numpy.where(pixels == 0)
                pixels[:,:] = p["alpha"]
                pixels[positionsNulles] = 0"""
                surface.set_alpha(None)
                surface.set_alpha(p["alpha"])
            elif nomTransformation == "Action Joueur" and nomPnj == "Joueur":
                centre = positionCarte.move(-self._scrollingX, -self._scrollingY).center
                pygame.draw.circle(self._fenetre, (255,255,255), centre, p["rayon"], 1)
            elif "Rouge" in nomTransformation and nomPnj == p["nom"]:
                pixels = surfarray.pixels3d(surface) #On exclut la zone de pensée
                pixels[:,:,1:] = 0

    def _ajouterPolice(self, fichierPolice, taillePolice):
        if fichierPolice not in self._polices.keys():
            self._polices[fichierPolice] = dict()
        if taillePolice not in self._polices[fichierPolice].keys():
            self._polices[fichierPolice][taillePolice] = pygame.font.Font(os.path.join(DOSSIER_RESSOURCES, fichierPolice), taillePolice)

    def _appliquerTransformationGlobale(self, nomTransformation, **p):
        """Applique la transformation globale <nomTransformation> avec le dico de paramètres <p>."""
        if nomTransformation == "Alpha":
            surface = self._fenetre.copy()
            self._fenetre.fill((0,0,0))
            surface.set_alpha(None)
            surface.set_alpha(0)
            surface.set_alpha(p["alpha"])
            self._fenetre.blit(surface, (0,0))
        if nomTransformation == "Rouge":
            pixels = surfarray.pixels3d(self._fenetre)[:FENETRE["longueurFenetre"], :FENETRE["largeurFenetre"]] #On exclut la zone de pensée
            pixels[:,:,1:] = 0
        elif nomTransformation == "Noir" or nomTransformation == "NoirTransition":
            pixels = surfarray.pixels3d(self._fenetre)[:FENETRE["longueurFenetre"],:FENETRE["largeurFenetre"]]
            pixels /= p["coef"]
            if p["coef"] >= 12:
                pixels[:] = (0,0,0)
        elif nomTransformation == "NoirTotal":
            pixels = surfarray.pixels3d(self._fenetre)[:FENETRE["longueurFenetre"],:FENETRE["largeurFenetre"]]
            pixels[:] = (0,0,0)
        elif nomTransformation == "Glow":
            nomPNJ, c = p["nomPNJ"], p["couche"]
            if nomPNJ in self._pnj[c].keys():
                x, y = self._pnj[c][nomPNJ].positionCarte.left - self._scrollingX, self._pnj[c][nomPNJ].positionCarte.top - self._scrollingY
                x1, y1, x2, y2 = x-32 if x-32 >= 0 else 0, y-32 if y-32 >= 0 else 0, x+64 if x+64 <= FENETRE["longueurFenetre"] else FENETRE["longueurFenetre"], y+64 if y+64 <= FENETRE["largeurFenetre"] else FENETRE["largeurFenetre"]
                #On limite les coordonnées du carré autour du cercle aux limites de la fenêtre
                cerclePossible = False
                if x1 < x2 and y1 < y2: #On évite les problèmes quand le cercle est en dehors de l'écran à l'arrière...
                    xCentre, yCentre, (xPixels, yPixels), pixels, cerclePossible = x+16, y+16, numpy.mgrid[x1:x2, y1:y2], surfarray.pixels3d(self._fenetre)[x1:x2,y1:y2], True
                if cerclePossible and 0 not in pixels.shape: #...comme à l'avant
                    distancesCarrees = (xPixels - xCentre) ** 2 + (yPixels - yCentre) ** 2
                    pixels[distancesCarrees <= 32 ** 2] *= 5
        elif nomTransformation == "Fog":
            idParam = id(self._parametresTransformations[nomTransformation])
            if self._idParametres.get(nomTransformation, False) == idParam:
                fog, tempsPrecedent = self._donneesParametres[nomTransformation]["fog"], self._donneesParametres[nomTransformation]["tempsPrecedent"]
                fogScrollX = self._donneesParametres[nomTransformation]["fogScrollX"]
            else:
                fog = pygame.image.load(os.path.join(DOSSIER_RESSOURCES, "fog.png"))
                surfarray.pixels_alpha(fog)[:] = 150
                self._donneesParametres[nomTransformation] = {"fog":fog, "tempsPrecedent":pygame.time.get_ticks(), "fogScrollX":0}
                self._idParametres[nomTransformation], tempsPrecedent = idParam, self._donneesParametres[nomTransformation]["tempsPrecedent"]
                fogScrollX = self._donneesParametres[nomTransformation]["fogScrollX"]
            tempsActuel = pygame.time.get_ticks() 
            avancee = ((tempsActuel - tempsPrecedent) / 1000) * VITESSE_DEFILEMENT_FOG
            if avancee >= 1.0:
                self._donneesParametres[nomTransformation]["tempsPrecedent"] = tempsActuel
                fogScrollX += avancee
                self._donneesParametres[nomTransformation]["fogScrollX"] = fogScrollX
            #We calculate where the junction between two scroll images will be on screen
            xScrollRelatif = (((self._scrollingX+fogScrollX) / FENETRE["longueurFenetre"]) - int((self._scrollingX+fogScrollX) / FENETRE["longueurFenetre"])) * FENETRE["longueurFenetre"]
            yScrollRelatif = ((self._scrollingY / FENETRE["largeurFenetre"]) - int(self._scrollingY / FENETRE["largeurFenetre"])) * FENETRE["largeurFenetre"]
            fogPositions = dict()
            #Four images on screen
            if xScrollRelatif > 0 and yScrollRelatif > 0:
                fogPositions[0] = Rect(xScrollRelatif, yScrollRelatif, FENETRE["longueurFenetre"]-xScrollRelatif, FENETRE["largeurFenetre"]-yScrollRelatif)
                fogPositions[1] = Rect(0, yScrollRelatif, xScrollRelatif, FENETRE["largeurFenetre"]-yScrollRelatif)
                fogPositions[2] = Rect(xScrollRelatif, 0, FENETRE["longueurFenetre"]-xScrollRelatif, yScrollRelatif)
                fogPositions[3] = Rect(0, 0, xScrollRelatif, yScrollRelatif)
            elif xScrollRelatif > 0:
                fogPositions[0] = Rect(xScrollRelatif, 0, FENETRE["longueurFenetre"]-xScrollRelatif, FENETRE["largeurFenetre"])
                fogPositions[1] = Rect(0, 0, xScrollRelatif, FENETRE["largeurFenetre"])
            elif yScrollRelatif > 0:
                fogPositions[0] = Rect(0, yScrollRelatif, FENETRE["longueurFenetre"], FENETRE["largeurFenetre"]-yScrollRelatif)
                fogPositions[2] = Rect(0, 0, FENETRE["longueurFenetre"], yScrollRelatif)
            else:
                fogPositions[0] = Rect(0,0, FENETRE["longueurFenetre"], FENETRE["largeurFenetre"])
            i = 0
            while i < 4:
                coord = (0,0) if i == 0 else (FENETRE["longueurFenetre"]-xScrollRelatif,0) if i == 1 else (0, FENETRE["largeurFenetre"]-yScrollRelatif) if i == 2 else (FENETRE["longueurFenetre"]-xScrollRelatif, FENETRE["largeurFenetre"]-yScrollRelatif)
                self._fenetre.blit(fog.subsurface(fogPositions[i]), coord)
                i += 1
                while i not in fogPositions.keys() and i < 4:
                    i += 1
        elif nomTransformation == "RemplirNoir":
            self._fenetre.fill((0,0,0), rect=(0,0,FENETRE["longueurFenetre"],FENETRE["largeurFenetre"]))
        elif "SplashText" in nomTransformation:
            idParam = id(p)
            if self._idParametres.get(nomTransformation, False) == idParam:
                surfaceTexte = self._donneesParametres[nomTransformation]
            else:
                self._idParametres[nomTransformation] = id(p)
                couleurFond, police, taille = p.get("couleurFond", None), p.get("police", NOM_FICHIER_POLICE_PAR_DEFAUT), p.get("taille", TAILLE_POLICE_SPLASH_SCREEN)
                self._ajouterPolice(police, taille)
                surfaceTexte = self._polices[police][taille].render(p["texte"], p["antialias"], p["couleurTexte"], couleurFond)
                self._donneesParametres[nomTransformation] = surfaceTexte
            if p.get("position", False) is not False:
                position = p["position"]
            else:
                position = self._pnj[p["couche"]][p["nomPNJ"]].positionCarte.move(-16, -surfaceTexte.get_height())
                position.move_ip(-self._scrollingX, -self._scrollingY)
            self._fenetre.blit(surfaceTexte, position)
        elif nomTransformation == "Nuit":
            self._fenetre.fill((0,0,0), rect=(0,0,FENETRE["longueurFenetre"],FENETRE["largeurFenetre"]))
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

    def _afficherZonePensee(self, affichageComplet=False):
        """S'il y a quelque chose à afficher, réaffiche la zone de pensée. 
        <affichageComplet> est un booléen qui vaut <True> lorsque pygame.display.flip est appelée à la suite de l'appel de la fonction."""
        positionZoneEntiere = (0, FENETRE["largeurFenetre"], FENETRE["longueurFenetre"], FENETRE["largeurFenetreReelle"] - FENETRE["largeurFenetre"])
        self._fenetre.fill(COULEUR_FOND_ZONE_PENSEE,rect=positionZoneEntiere)
        if self._surfaceZonePensee is not None:
            self._fenetre.blit(self._surfaceZonePensee, self._positionZonePensee)
        if self._faceActuelle is not False:
            self._fenetre.blit(self._faceActuelle, positionZoneEntiere)
        if affichageComplet is False:
            pygame.display.update(positionZoneEntiere)
        self._besoinAffichageZonePensee = False

    def _afficherBlocPnj(self, c, nomPnj):
        """Affiche un PNJ sur un bloc"""
        pnj = self._pnj[c][nomPnj]
        positionVisible, positionCarte = pnj.positionVisible, pnj.positionCarte
        if self._ecranVisible.contains(positionCarte) or self._ecranVisible.colliderect(positionCarte):
            positionCollage = positionVisible.move(-self._scrollingX, -self._scrollingY)
            if len(self._transformationsParties) > 0:
                surfaceCollage = self._dicoSurfaces[pnj.nomTileset][(pnj.positionSource.left, pnj.positionSource.top, pnj.positionSource.width, pnj.positionSource.height)].copy()
                self._transformerPartie(surfaceCollage, nomPnj, positionVisible, positionCarte)
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
                couche = self._tilesLayers[coucheActuelle]
                if len(self._transformationsParties) > 0:
                    self._transformerPartie(couche, False, (0,0), (0,0))
                self._fenetre.blit(couche, (0,0), area=self._ecranVisible)
                nomsPnjs = sorted(self._pnj[coucheActuelle], key=lambda nomPNJ: self._pnj[coucheActuelle][nomPNJ].positionCarte.top)
                #Tri des PNJs selon leur ordonnée (de manière croissante) : on affiche ceux en haut de l'écran avant ceux en bas, pour avoir une superposition
                for nomPnj in nomsPnjs: 
                    self._afficherBlocPnj(coucheActuelle, nomPnj)
                coucheActuelle += 1
            self._afficherZonePensee(affichageComplet=True)
            self._transformerSurfaceGlobalement()
            self._blitFrame = True
        
        if self._blitFrame is True:
            if LIMITER_FPS:
                self._jeu.horlogeFps.tick(NOMBRE_MAX_DE_FPS)
            else:
                self._jeu.horlogeFps.tick()
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

    def _setIdParametres(self, val):
        self._idParametres = val

    def _getIdParametres(self):
        return self._idParametres

    def _getTiles(self):
        return self._tiles

    def _getMessagesCollision(self):
        return self._messagesCollision

    def _setMessagesCollision(self, nouveauxMessages):
        self._messagesCollision = nouveauxMessages

    def _getPnj(self):
        return self._pnj
    
    def _setPnj(self, nouveauxPnj):
        self._pnj = nouveauxPnj

    nombreCouches = property(_getNombreCouches)
    hauteurTile = property(_getHauteurTile)
    nom = property(_getNom)
    longueur = property(_getLongueur)
    largeur = property(_getLargeur)
    tiles = property(_getTiles)
    pnj = property(_getPnj, _setPnj)
    idParametres = property(_getIdParametres, _setIdParametres)
    transformationsGlobales = property(_getTransformationsGlobales, _setTransformationsParties)
    transformationsParties = property(_getTransformationsParties, _setTransformationsParties)
    parametresTransformations = property(_getParametresTransformations)
    messagesCollision = property(_getMessagesCollision, _setMessagesCollision)
