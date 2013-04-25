# -*-coding:iso-8859-1 -*
import pygame
from pygame.locals import *
from interactionConsole import *
from carte import *

class Tileset:
	def __init__(self, carte, fenetre, positionSourceBlocSelectionneParDefaut, couleurZone, hauteurTile, positionCollage, couleurLigne):
		self.positionCollage = pygame.Rect(positionCollage) 
		self.positionSource = pygame.Rect(self.positionCollage) #La position source(rectangle dans le tileset entier) est la même que celle de collage : en haut à gauche
		self.carte = carte
		self.surface = self.carte.getSurfaceTileset().subsurface(self.positionSource)
		self.fenetre = fenetre
		self.couleurZone = couleurZone
		self.hauteurTile = hauteurTile
		self.couleurLigne = couleurLigne
		self.partieTilesetAffichee, self.besoinReaffichage, self.blocSelectionne = 0, True, Bloc(positionSourceBlocSelectionneParDefaut)

	def getBlocSelectionne(self):
		return self.blocSelectionne
	
	def afficherGrille(self):
		positionTileset, hauteurTile = self.positionCollage, self.hauteurTile
		nombreLignesVerticales = (positionTileset.width / hauteurTile) - 1
		nombreLignesHorizontales = (positionTileset.height / hauteurTile) - 1
		i = 1
		while i <= nombreLignesVerticales:
			pointDebutLigne = ((hauteurTile * i),0)
			pointFinLigne = ((hauteurTile * i), positionTileset.height)
			positionInutile = pygame.draw.line(self.surface, self.couleurLigne, pointDebutLigne, pointFinLigne)
			i += 1
		i = 1
		while i <= nombreLignesHorizontales:
			pointDebutLigne = (0,hauteurTile * i)
			pointFinLigne = (positionTileset.width,hauteurTile * i)
			positionInutile = pygame.draw.line(self.surface, self.couleurLigne, pointDebutLigne, pointFinLigne)
			i += 1

	def selectionnerTile(self, evenement):
		"""Enregistre le bloc sélectionné par l'utilisateur (s'il en a sélectionné un)"""
		conditionSelection = evenement.type == MOUSEBUTTONUP and evenement.dict["button"] == 1 and evenement.dict["pos"][0] >= self.positionCollage.left and evenement.dict["pos"][0] <= self.positionCollage.left + self.positionCollage.width and evenement.dict["pos"][0] >= self.positionCollage.top and evenement.dict["pos"][1] <= self.positionCollage.top + self.positionCollage.height and self.carte.getPoseDeTilesEnCours() == False
		hauteurTile = self.hauteurTile
		if conditionSelection is True:
			abscisseSourceBlocSelectionne = evenement.dict["pos"][0] // hauteurTile * hauteurTile
			ordonneeSourceBlocSelectionne = (evenement.dict["pos"][1] // self.hauteurTile * hauteurTile) + (hauteurTile * self.partieTilesetAffichee)
			positionSourceBlocSelectionne = pygame.Rect(abscisseSourceBlocSelectionne, ordonneeSourceBlocSelectionne, hauteurTile, hauteurTile)
			self.blocSelectionne = Bloc(positionSourceBlocSelectionne)
	
	def changerPartieTileset(self, evenement):
		"""Gère le scrolling du tileset"""
		hauteurTile = self.hauteurTile
		if evenement.type == KEYDOWN and evenement.dict["key"] == K_a: #Si le joueur a appuyé sur la lettre Q
			self.partieTilesetAffichee -= 1	#On bouge d'une ligne la partie à afficher
			self.besoinReaffichage = True
		elif evenement.type == KEYDOWN and evenement.dict["key"] == K_z: #Si le joueur a appuyé sur la lettre W
			self.partieTilesetAffichee += 1	
			self.besoinReaffichage = True
		self.positionSource.top = hauteurTile * self.partieTilesetAffichee #Modification (ou non) de la partie à afficher
		if self.positionSource.top + self.positionSource.height >= self.surface.get_parent().get_height(): #Recadrement de la partie à afficher dans le tileset
			self.partieTilesetAffichee -= 1
			self.positionSource.top = hauteurTile * self.partieTilesetAffichee
		elif self.positionSource.top < 0:
			self.partieTilesetAffichee += 1
			self.positionSource.top = hauteurTile * self.partieTilesetAffichee
		self.surface = self.surface.get_parent().subsurface(self.positionSource) #Actualisation de la surface correspondant à la partie à afficher
		if self.besoinReaffichage is True: #Si et seulement si on a changé la partie à afficher, alors on affiche des changements à l'écran
			self.fenetre.fill(self.couleurZone,self.positionCollage)
			self.afficherGrille()
			self.positionCollage = self.fenetre.blit(self.surface, self.positionCollage)
			self.besoinReaffichage = False
	
	def gerer(self, evenement):
		"""Gère le tileset et retourne le bloc sélectionné par le joueur (None s'il n'y en a aucun)"""
		self.selectionnerTile(evenement)
		self.changerPartieTileset(evenement)

