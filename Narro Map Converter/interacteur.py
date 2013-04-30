# -*-coding:iso-8859-1 -*
import os,sys



class Interacteur:
	"""Cette classe gère l'interaction avec l'utilisateur en mode console."""
	def __init__(self,messagePauseParDefaut=""):
		self.messagePauseParDefaut = messagePauseParDefaut

	def mettreEnPause(self, chaine=""):
		"""Fonction permettant la mise en pause du programme"""
		if chaine == "":
			chaine = self.messagePauseParDefaut
		print(chaine)
		try:
			variableInutile = input()
			return True
		except:
			print("Une erreur s'est produite ; le programme va se fermer.")
			raise SystemExit
			return False
	
	def annoncer(self, message):
		"""Affiche un message puis met le programme en pause"""
		try:
			message = str(message)
		except ValueError:
			print("Une erreur s'est produite car vous devez entrer une chaîne de caractères à afficher. Le programme va se fermer.")
			raise SystemExit
		else:
			print(message)
			self.mettreEnPause()

	def recupererChoixDuJoueur(self, choixPossibles, messageMenu):
		""" recupererChoixDuJoueur (tupleDeChoixPossibles,messageMenuAAfficher) -> int
		Affiche un menu (avec comme message messageMenu) et demande au joueur de faire un choix (un chiffre). Retourne ce chiffre."""
		choixBienFait = False
		while choixBienFait is not True:
			print(messageMenu)
			choix = input()
			try:
				choix = int(choix)
			except ValueError:
				print("Vous devez entrer un chiffre.\n")
				choix = 0
				self.mettreEnPause()
			else:
				if choix in choixPossibles:
					print("Très bien !")
					choixBienFait = True
				else:
					print("Le chiffre que vous avez entré ne correspond à aucun choix.")
					self.mettreEnPause()
		return choix

	def recupererNombre(self, message):
		"""recupererNombre(message) -> int
		Après avoir affiché message à l'écran, demande à l'utilisateur de rentrer un entier et le retourne retourne."""
		nombreBienEntre = False
		while nombreBienEntre is not True:
			print(message)
			nombre = input()
			try:
				nombre = int(nombre)
			except:
				print("Vous n'avez pas entré de nombre.")
				nombre = 0
			else:
				nombreBienEntre = True
		return nombre

	def recupererChaine(self, message):
		"""recupererChaine(message) -> str
		Après avoir affiché message à l'écran, demande à l'utilisateur de rentrer une chaîne de caractères et la retourne."""
		chaineBienEntree = False
		while chaineBienEntree is not True:
			print(message)
			chaine = input()
			try:
				chaine = str(chaine)
			except:
				print("Vous n'avez pas entré de texte.")
				chaine = ""
			else:
				chaineBienEntree = True
		return chaine

	def listerNombres(self, min=1, max=100):
		""" listerNombres(intMin,intMax) -> list
		Retourne une liste de nombres allant de intMin à intMax
		Remarque : intMin < intMax """
		if min > max:
			min, max = max, min #Maintenant min <= max
		listeNombres = []
		while min <= max:
			listeNombres.append(min)
			min += 1
		return listeNombres

	def demanderInfosCarte(self,listeMessages, tileset, couleurTransparente, messageErreurChargementTileset, positionSourceBlocVide, positionSourceBlocRempli, nombreCouches):
		"""demanderInfosCarte(listeMessages) -> dict
		Demande à l'utilisateur les infos nécessaires pour la création d'une carte et les retourne dans un dictionnaire. 
		Lors de la demande, affiche pour chaque info le message correspondant contenu dans listeMessages."""
		infosCarte = dict()
		infosCarte["nom"] = self.recupererChaine(listeMessages[0])
		infosCarte["description"] = self.recupererChaine(listeMessages[1])
		infosCarte["longueur"] = self.recupererNombre(listeMessages[2])
		infosCarte["largeur"] = self.recupererNombre(listeMessages[3])
		infosCarte["musique"] = self.recupererChaine(listeMessages[4])
		infosCarte["tileset"] = tileset
		infosCarte["messageErreurChargementTileset"] = messageErreurChargementTileset
		infosCarte["positionSourceBlocVide"] = positionSourceBlocVide
		infosCarte["positionSourceBlocRempli"] = positionSourceBlocRempli
		infosCarte["couleurTransparente"] = couleurTransparente
		infosCarte["nombreCouches"] = nombreCouches
		return infosCarte

if __name__ == "__main__": #Simple test de fonctionnement ; ne réalise rien pour le programme
	interacteur = Interacteur("Appuyez sur Entrée") 
	menuDeMidi = interacteur.recupererChoixDuJoueur((1,2),"Que voulez-vous manger aujourd'hui ? \n1.Poulet frites\n2.Lapin aux pruneaux")
	interacteur.mettreEnPause()
	if menuDeMidi is 1:
		print("Poulet frites ? Beurk !")
	elif menuDeMidi is 2:
		print("Du lapin aux pruneaux ? Excellent choix !")
	interacteur.mettreEnPause()
	print(interacteur.listerNombres(1,100))
	interacteur.mettreEnPause()
