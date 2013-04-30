import pygame,sys
from pygame.locals import *

class Appli:
    def __init__(self):
        pygame.init()
        self._fenetre = pygame.display.set_mode((640,480))
        pygame.display.set_caption("Subsurfacer")
        self._fenetre.fill((0,0,0))

    def exporterTiles(self, nomScreenshot, xDepart, yDepart, longueur, largeur, nomSortie):
        surfaceTiles = pygame.image.load(nomScreenshot).subsurface((xDepart, yDepart, longueur, largeur)).convert_alpha()
        pygame.image.save(surfaceTiles, nomSortie)
        pygame.quit()

if __name__ == "__main__":
    appli = Appli()
    if len(sys.argv)  == 7:
        nomScreenshot, xDepart, yDepart, longueur, largeur, nomSortie = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
        appli.exporterTiles(nomScreenshot, xDepart, yDepart, longueur, largeur, nomSortie)
