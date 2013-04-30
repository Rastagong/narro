# -*-coding:iso-8859-1 -*
from constantes import *

def ajusterCoordonneesLorsDeplacement(coor, direction, enTile=False):
	"""Selon la direction, donne les coordonnées au tile suivant. Si <enTile> est vrai, les coordonnées seront exprimées non pas en valeurs de pixels,
	mais en indices de tiles."""
	if enTile is True:
		coor = coor * 32
	if direction == "Haut":
		coor -= 32
	elif direction == "Bas":
		coor += 32
	elif direction == "Gauche":
		coor -= 32
	elif direction == "Droite":
		coor += 32
	if enTile is True:
		coor = int(coor / 32)
	return coor

def ajusterCoupleCoordonneesLorsDeplacement(x, y, direction, enTile=False):
	xFutur, yFutur = x, y
	if direction == "Haut" or direction == "Bas":
		yFutur = ajusterCoordonneesLorsDeplacement(y, direction, enTile=enTile)
	elif direction == "Gauche" or direction == "Droite":
		xFutur = ajusterCoordonneesLorsDeplacement(x, direction, enTile=enTile)
	return (xFutur,yFutur)

def directionContraire(direction):
	dicoDirectionsContraires = dict(Haut="Bas", Bas="Haut", Gauche="Droite", Droite="Gauche")
	if direction in dicoDirectionsContraires.keys():
		return dicoDirectionsContraires[direction]
	else:
		return "Aucune"
