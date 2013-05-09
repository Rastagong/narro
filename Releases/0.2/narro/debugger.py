import pygame
from pygame.locals import *
from constantes import *
from evenement import *
import pdb, pympler.summary, pympler.muppy, pympler.tracker, pympler.refbrowser 
from pympler.classtracker import ClassTracker

class Debugger(Evenement):
    def __init__(self, jeu, gestionnaire, methode=False):
        print("start")
        super().__init__(jeu, gestionnaire)
        self._debugFait, self._methode = 0, methode
        if self._methode is not False:
            if self._methode == "Instance":
                self._tracker = ClassTracker()
                self._tracker.track_class(Evenement)
                self._tracker.create_snapshot("Initialisation")
            elif self._methode == "Fuites":
                self._tracker = pympler.tracker.SummaryTracker()
                self._tracker.print_diff()
            Horloge.initialiser(id(self), 1, 3000)

    def cmp(self, obj):
        return str(type(obj))

    def traiter(self):
        if Horloge.sonner(id(self), 1) is True:
            if self._methode == "Instance":
                if self._debugFait < 3:
                    self._tracker.create_snapshot("Etape n°" + str(self._debugFait))
                    self._debugFait += 1
                    Horloge.initialiser(id(self), 1, 3000)
                else:
                    self._tracker.stats.print_summary()
            elif self._methode == "Fuites":
                self._tracker.print_diff()
                Horloge.initialiser(id(self), 1, 3000)
