# -*-coding:iso-8859-1 -*
import configparser,os,pygame,math,xml.dom.minidom
from pygame.locals import *
from interacteur import *

class Appli:

	def _initialiserAffichage(self, longueurFenetre, largeurFenetre, couleurFenetre, titreFenetre, flagsFenetre=0):
		try:
			pygame.init()
		except pygame.error:
			print("messageErreurInitialisationPygame")
			interacteur.mettreEnPause()
			raise SytemExit
		try:
			fenetre = pygame.display.set_mode((longueurFenetre,largeurFenetre), flagsFenetre)
		except pygame.error:
			print("messageErreurInitialisationFenetre")
			pygame.quit()
			raise SystemExit
		fenetre.fill(couleurFenetre)
		pygame.display.set_caption(titreFenetre)
		return fenetre
 
	def _initialiserTout(self):
		"""Initialise le script"""
		interacteur = Interacteur()
		listeTilesets = os.listdir("../Ressources/") #Liste des images tilesets
		listeTilesets = [tileset for tileset in listeTilesets if ".swp" not in tileset and ".tsx~" not in tileset and ".tsx" in tileset]
		message = "Quel tileset (image) choisissez-vous ?\n"
		i, choixPossibles = 0,list()
		while i < len(listeTilesets): 
			message += str(i+1) + ". " + listeTilesets[i] + "\n" #Ajout du nom de chaque image au message qui sera affiché
			choixPossibles.append(i+1) #Ajout du chiffre d'un tileset à la liste des choix possibles
			i += 1
		choix = interacteur.recupererChoixDuJoueur(choixPossibles,message) #Récupération du choix
		self.cheminTileset = "../Ressources/" + listeTilesets[choix-1]
		self.documentXML = xml.dom.minidom.parse(self.cheminTileset)
		self.cheminImage = self.documentXML.documentElement.getElementsByTagName("image")[0].getAttribute("source")
		self.image = pygame.image.load("../Ressources/" + self.cheminImage)
		longueurFenetre, largeurFenetre = 256, 640
		if self.image.get_width() < longueurFenetre:
			longueurFenetre = self.image.get_width()
		if self.image.get_height() < largeurFenetre:
			largeurFenetre = self.image.get_height()
		self.fenetre = self._initialiserAffichage(longueurFenetre,largeurFenetre,(255,255,255),"Narro Tileset Editor",pygame.DOUBLEBUF)
		pygame.key.set_repeat(10,10)

	def _quitterLeJeu(self, evenement):
		return (evenement.type == QUIT) or (evenement.type == KEYDOWN and evenement.dict["key"] == K_ESCAPE)

	def _gererScrolling(self, evenement):
		ancienPixelY, ancienPixelX = self.pixelDepartY, self.pixelDepartX
		if evenement.type == KEYDOWN and evenement.dict["key"] == K_q:  #Touche A : on remonte
			self.pixelDepartY -= 32
		if evenement.type == KEYDOWN and evenement.dict["key"] == K_z: #Touche W : on descend
			self.pixelDepartY += 32
		if self.pixelDepartY > self.image.get_height() - self.fenetre.get_height():
			self.pixelDepartY = math.floor( (self.image.get_height() - self.fenetre.get_height() ) / 32) * 32
		if self.pixelDepartY < 0:
			self.pixelDepartY = 0
		if evenement.type == KEYDOWN and evenement.dict["key"] == K_s: 
			self.pixelDepartX -= 32
		if evenement.type == KEYDOWN and evenement.dict["key"] == K_d:
			self.pixelDepartX += 32
		if self.pixelDepartX < 0:
			self.pixelDepartX = 0
		if self.pixelDepartX > self.image.get_width() - self.fenetre.get_width():
			self.pixelDepartX = math.floor( (self.image.get_width() - self.fenetre.get_width() ) / 32) * 32
		if self.pixelDepartY != ancienPixelY or self.pixelDepartX != ancienPixelX:
			self.tileset = self.image.subsurface((self.pixelDepartX,self.pixelDepartY, self.longueurTileset, self.largeurTileset)).copy()
			self._afficherTileset()
	
	def _afficherTileset(self):
		x = int(self.pixelDepartX / 32)
		xMax = x + int( (self.fenetre.get_width()+32) / 32)
		y = int(self.pixelDepartY / 32) 
		yMax = y + int( (self.fenetre.get_height()+32) / 32)
		self.fenetre.fill((255,255,255))
		while x < xMax and x < len(self.praticabilites):
			y = int(self.pixelDepartY / 32)
			while y < yMax and y < len(self.praticabilites[x]):
				xCollage = (x * 32) - self.pixelDepartX
				yCollage = (y * 32) - self.pixelDepartY
				if self.praticabilites[x][y] is True and self.modeEdition is True:
					pygame.draw.rect(self.tileset,(0,0,255),(xCollage,yCollage,32,32),2)
				elif self.praticabilites[x][y] is False and self.modeEdition is True:
					pygame.draw.ellipse(self.tileset,(255,0,0),(xCollage,yCollage,32,32),2)
				y += 1
			x += 1
		self.fenetre.blit(self.tileset,(0,0))
		pygame.display.flip()

	def _sauvegarder(self, evenement):
		if evenement.type == KEYUP and evenement.dict["key"] == K_n:
			print("Sauvegarde")
			xActuel, yActuel, longueurLigne, longueurColonne = 0, 0, int(self.image.get_width()/32), int(self.image.get_height()/32)
			tilesXML = self.documentXML.documentElement.getElementsByTagName("tile")
			while xActuel < longueurLigne:
				yActuel = 0
				while yActuel < longueurColonne:
					indice = (yActuel * longueurLigne) + xActuel
					praticaActuelle = str(self.praticabilites[xActuel][yActuel])
					tilesXML[indice].getElementsByTagName("properties")[0].getElementsByTagName("property")[0].setAttribute("value",praticaActuelle)
					yActuel += 1
				xActuel += 1
			with open(self.cheminTileset,"w") as fichier:
				self.documentXML.writexml(fichier, indent="", addindent="	", newl="", encoding="UTF-8")

	def _gererClic(self, evenement):
		if evenement.type == MOUSEBUTTONUP:
			posX,posY = evenement.dict["pos"][0],evenement.dict["pos"][1]
			x = int(posX / 32) + int(self.pixelDepartX / 32)
			y = int(posY / 32) + int(self.pixelDepartY / 32)
			if self.praticabilites[x][y] is True:
				self.praticabilites[x][y] = False
			elif self.praticabilites[x][y] is False:
				self.praticabilites[x][y] = True
			self.tileset = self.image.subsurface((self.pixelDepartX,self.pixelDepartY,self.longueurTileset, self.largeurTileset)).copy()
			self._afficherTileset()

	def _chargerPraticabilites(self):
		xActuel, yActuel, longueurLigne, longueurColonne = 0, 0, int(self.image.get_width() / 32), int(self.image.get_height() / 32)
		self.praticabilites = list()
		tilesXML = self.documentXML.documentElement.getElementsByTagName("tile")
		while xActuel < longueurLigne:
			self.praticabilites.append( list() )
			yActuel = 0
			while yActuel < longueurColonne:
				indice = (yActuel * longueurLigne) + xActuel
				print("Indices",indice,xActuel,yActuel)
				praticabiliteActuelle = tilesXML[indice].getElementsByTagName("properties")[0].getElementsByTagName("property")[0].getAttribute("value")
				praticabiliteActuelle = praticabiliteActuelle == "True"
				self.praticabilites[xActuel].append(praticabiliteActuelle)
				yActuel += 1
			xActuel += 1
	
	def _gererModeEdition(self, evenement):
		if evenement.type == KEYUP and evenement.dict["key"] == K_p:
			if self.modeEdition is True:
				self.modeEdition = False
			elif self.modeEdition is False:
				self.modeEdition = True
			self.tileset = self.image.subsurface((self.pixelDepartX,self.pixelDepartY,self.longueurTileset, self.largeurTileset)).copy()
			self._afficherTileset()

	def executer(self):
		self._initialiserTout()
		self.pixelDepartX, self.pixelDepartY, self.modeEdition = 0, 0, True
		if self.image.get_width() > self.fenetre.get_width():
			self.longueurTileset = self.fenetre.get_width()
		else:
			self.longueurTileset = self.image.get_width()
		if self.image.get_height() > self.fenetre.get_height():
			self.largeurTileset = self.fenetre.get_height()
		else:
			self.largeurTileset = self.image.get_height()
		self.tileset = self.image.subsurface((self.pixelDepartX,self.pixelDepartY,self.longueurTileset, self.largeurTileset)).copy()
		self._chargerPraticabilites()
		self._afficherTileset()
		jeuFini = False
		while jeuFini is not True:
			evenement = pygame.event.poll()
			self._gererModeEdition(evenement)
			self._gererScrolling(evenement)
			self._gererClic(evenement)
			self._sauvegarder(evenement)
			jeuFini = self._quitterLeJeu(evenement)
		self.documentXML.unlink()


if __name__ == "__main__":
	appli = Appli()
	appli.executer()
