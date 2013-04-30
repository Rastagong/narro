# -*-coding:iso-8859-1 -*
import configparser, xml.dom.minidom, os, interacteur
from collections import OrderedDict

class Appli:
	def __init__(self):
		pass

	def initialiser(self):
		self.DOSSIER_RESSOURCES = "../Ressources/"
		listeCartes = os.listdir(self.DOSSIER_RESSOURCES)
		listeCartes = [carte for carte in listeCartes if ".tmx" in carte and "~" not in carte and ".swp" not in carte]
		i, choixPossibles = 0, list()
		message = "Quelle carte voulez-vous convertir ?\n"
		while i < len(listeCartes):
			message += str(i+1) + ". " + listeCartes[i] + "\n"
			choixPossibles.append(i+1)
			i += 1
		monInteracteur = interacteur.Interacteur()
		choixJoueur = monInteracteur.recupererChoixDuJoueur(choixPossibles, message)
		self.nomFichier = self.DOSSIER_RESSOURCES + listeCartes[choixJoueur-1]
		self.configXML = xml.dom.minidom.parse(self.nomFichier)

	def obtenirGeneralites(self):
		self.longueur, self.largeur = int(self.mapXML.getAttribute("width")), int(self.mapXML.getAttribute("height"))
		proprisCarte = self.mapXML.getElementsByTagName("properties")[0]
		for propriCarte in proprisCarte.getElementsByTagName("property"):
			if propriCarte.getAttribute("name") == "Nom":
				self.nom = propriCarte.getAttribute("value")
			if propriCarte.getAttribute("name") == "Description":
				self.description = propriCarte.getAttribute("value")
			if propriCarte.getAttribute("name") == "Musique":
				self.musique = propriCarte.getAttribute("value")

	def transformerHexaEnRGB(self, couleurHexa):
		return (int(couleurHexa[:2],16), int(couleurHexa[2:4],16), int(couleurHexa[4:],16)) #Chaque membre est transformé en base 10 avec la fct int

	def obtenirTilesEtBlocs(self):
		self.dicoGIDs, self.dicoTilesets, self.dicoGeneral = dict(), dict(), dict()
		tilesetsXML = self.mapXML.getElementsByTagName("tileset")
		for tilesetXML in tilesetsXML:
			self.dicoGIDs[int(tilesetXML.getAttribute("firstgid"))] = tilesetXML.getAttribute("name")
			self.dicoTilesets[tilesetXML.getAttribute("name")] = (tilesetXML.getElementsByTagName("image")[0].getAttribute("source"), tilesetXML.getElementsByTagName("image")[0].getAttribute("trans") )
		self.dicoGIDs = OrderedDict( sorted(self.dicoGIDs.items()) )
		self.nombreCouches = len(self.mapXML.getElementsByTagName("layer"))
		x, y, c, self.blocsRef, self.tiles, self.blocs = 0,0,0, list(), dict(), dict()
		self.blocsRef.append( ("None", (-1,-1,-1,), True, (-1,-1,-1,-1) ) ) #Bloc vide
		while c < self.nombreCouches:
			couche = self.mapXML.getElementsByTagName("layer")[c].getElementsByTagName("data")[0]
			tiles = couche.getElementsByTagName("tile")
			x,y = 0,0 
			for tile in tiles:
				if x >= self.longueur: #On a dépassé une ligne, on passe à la suivante
					x, y = 0, y+1
				gid = int(tile.getAttribute("gid"))
				if gid == 0: #Bloc vide
					self.blocs[x,y,c] = 0
				elif gid in self.dicoGeneral.keys(): #Bloc déjà connu, on fait référence à celui-ci
					self.blocs[x,y,c] = self.dicoGeneral[gid]
				else: #Bloc inconnu, il faut tout déterminer
					for gidActuel in self.dicoGIDs.keys():
						if gid >= gidActuel:
							gidTileset = gidActuel
					refTileset = self.dicoGIDs[gidTileset]
					nomTileset, couleurTransparente = self.dicoTilesets[refTileset][0], self.dicoTilesets[refTileset][1]
					couleurTransparente = self.transformerHexaEnRGB(couleurTransparente)
					for tilesetXML in tilesetsXML:
						if gidTileset == int(tilesetXML.getAttribute("firstgid")):
							imageXML = tilesetXML.getElementsByTagName("image")[0]
							longueurTileset, largeurTileset = int(imageXML.getAttribute("width"))/32, int(imageXML.getAttribute("height"))/32
							print(tilesetXML.getAttribute("name"),gidTileset,longueurTileset,largeurTileset)
							idLocal = gid - gidTileset
							proprisTileTileset = tilesetXML.getElementsByTagName("tile")[idLocal].getElementsByTagName("properties")[0]
							proprisTileTileset = proprisTileTileset.getElementsByTagName("property")
							for propri in proprisTileTileset:
								if propri.getAttribute("name") == "Praticabilite" and propri.getAttribute("value") == "True":
									praticabilite = True
								elif propri.getAttribute("name") == "Praticabilite" and propri.getAttribute("value") == "False":
									praticabilite = False
							positionSource = ( int((idLocal%longueurTileset)*32),int((idLocal//longueurTileset)*32), 32, 32)
							self.blocsRef.append((nomTileset,couleurTransparente,praticabilite,positionSource))
							indiceRefBloc = len(self.blocsRef)-1
							self.blocs[x,y,c], self.dicoGeneral[gid] = indiceRefBloc, indiceRefBloc #On ajoute un bloc de ref qu'on utilise de suite
				x += 1
			c += 1
		x,y,c = 0,0,0
		while x < self.longueur: #On détermine la praticabilité des tiles (tout dépend de la couche à laquelle le joueur veut accéder)
			y = 0
			while y < self.largeur:
				c, praticabilite = 0, True
				self.tiles[x,y] = dict()
				while c < self.nombreCouches:
					if self.blocsRef[self.blocs[x,y,c]][2] == False:
						praticabilite = False
					if c == 0 and self.blocs[x,y,c] == 0: #Bloc vide en couche 0
						praticabilite = False
					self.tiles[x,y][c] = praticabilite
					c += 1
				y += 1
			x += 1

	def exporterNouvelleConfig(self):
		self.config = configparser.ConfigParser()
		self.config.add_section("Generalites")
		self.config.set("Generalites","Nom",self.nom)
		self.config.set("Generalites","Description",self.description)
		self.config.set("Generalites","Musique",self.musique)
		self.config.set("Generalites","Longueur",str(self.longueur))
		self.config.set("Generalites","Largeur",str(self.largeur))
		self.config.set("Generalites","Couches",str(self.nombreCouches))
		self.config.set("Generalites","Nombre ref",str(len(self.blocsRef)))
		self.config.add_section("Tiles")
		x,y,c = 0,0,0
		while x < self.longueur: #La section des tiles contient, pour chaque tile, à chaque couche, la praticabilité
			y = 0
			while y < self.largeur:
				c = 0
				while c < self.nombreCouches:
					self.config.set("Tiles", str(x) + "+" + str(y) + "+" + str(c), str(self.tiles[x,y][c]))
					c += 1
				y += 1
			x += 1
		i = 0
		while i < len(self.blocsRef): #Les sections de blocs de référence
			bloc = self.blocsRef[i]
			self.config.add_section("Bloc ref"+str(i))
			self.config.set("Bloc ref"+str(i),"Chemin image",bloc[0])
			self.config.set("Bloc ref"+str(i),"Praticabilite",str(bloc[2]))
			self.config.add_section("Bloc ref" + str(i) + "." + "Position source")
			self.config.set("Bloc ref" + str(i) + "." + "Position source","0",str(bloc[3][0]))
			self.config.set("Bloc ref" + str(i) + "." + "Position source","1",str(bloc[3][1]))
			self.config.set("Bloc ref" + str(i) + "." + "Position source","2",str(bloc[3][2]))
			self.config.set("Bloc ref" + str(i) + "." + "Position source","3",str(bloc[3][3]))
			self.config.add_section("Bloc ref" + str(i) + "." + "Couleur transparente")
			self.config.set("Bloc ref" + str(i) + "." + "Couleur transparente","0",str(bloc[1][0]))
			self.config.set("Bloc ref" + str(i) + "." + "Couleur transparente","1",str(bloc[1][1]))
			self.config.set("Bloc ref" + str(i) + "." + "Couleur transparente","2",str(bloc[1][2]))
			i += 1
		self.config.add_section("Blocs") #La section de bloc contient, pour chaque bloc, un id de bloc de référence
		x,y,c = 0,0,0
		while x < self.longueur:
			y = 0
			while y < self.largeur:
				c = 0
				while c < self.nombreCouches:
					self.config.set("Blocs", str(x) + "+" + str(y) + "+" + str(c), str(self.blocs[x,y,c]))
					c += 1
				y += 1
			x += 1
		nomFichierFinal = self.DOSSIER_RESSOURCES + self.nom + ".narromap"
		with open(nomFichierFinal, "w") as fichierFinal:
			self.config.write(fichierFinal)

	def executer(self):
		self.initialiser()
		self.mapXML = self.configXML.documentElement
		self.obtenirGeneralites()
		self.obtenirTilesEtBlocs()
		self.configXML.unlink()
		self.exporterNouvelleConfig()

if __name__ == "__main__":
	appli = Appli()
	appli.executer()
