# -*-coding:iso-8859-1 -*
import pygame
from pygame.locals import *

class Horloge:
    """Classe qui permet de gérer le temps."""

    _heureAlarme, _sonnerieActivee, _heureDepartAlarme = dict(), dict(), dict()
    
    def initialiser( idInstance, numeroAlarme, nouvelleHeureAlarme, comptageTempsPasse=False):
        """Modifie l'heure de la prochaine alarme."""
        numeroAlarme = str(idInstance) + "+" + str(numeroAlarme)
        heureActuelle = pygame.time.get_ticks()
        Horloge._heureAlarme[numeroAlarme] = heureActuelle + int(nouvelleHeureAlarme)
        if comptageTempsPasse is True:
            Horloge._heureDepartAlarme[numeroAlarme] = heureActuelle
        Horloge._sonnerieActivee[numeroAlarme] = True

    def sonner(idInstance, numeroAlarme, arretApresSonnerie=True):
        """Retourne <True> si l'alarme <numeroAlarme> de l'horloge a sonné.
        Si <arretApresSonnerie> vaut False et que l'alarme a sonné, elle n'est pas arrêtée pour autant."""
        if Horloge.alarmeExiste(idInstance, numeroAlarme) is True: #Si l'alarme indiquée existe
            numeroAlarme = str(idInstance) + "+" + str(numeroAlarme)
            if Horloge._heureAlarme[numeroAlarme] <= pygame.time.get_ticks() and Horloge._sonnerieActivee[numeroAlarme] is True:
                if arretApresSonnerie is True:
                    Horloge._sonnerieActivee[numeroAlarme] = False
                return True
            else:
                return False
        else:
            return False

    def alarmeExiste(idInstance, numeroAlarme):
        """Retourne <True> si l'alarme <numeroAlarme> existe."""
        numeroAlarme = str(idInstance) + "+" + str(numeroAlarme)
        return numeroAlarme in Horloge._heureAlarme.keys()

    def tempsRestant(idInstance, numeroAlarme):
        """Retourne le temps restant avant que l'alarme <numeroAlarme> ne sonne."""
        numeroAlarme = str(idInstance) + "+" + str(numeroAlarme)
        return Horloge._heureAlarme[numeroAlarme] - pygame.time.get_ticks()

    def tempsPasse(idInstance, numeroAlarme):
        """Retourne le temps passe depuis que l'alarme <numeroAlarme> a été initialisée."""
        numeroAlarme = str(idInstance) + "+" + str(numeroAlarme)
        if numeroAlarme in Horloge._heureDepartAlarme.keys():
            return pygame.time.get_ticks() - Horloge._heureDepartAlarme[numeroAlarme]
        else:
            return False

    def arreterSonnerie(idInstance, numeroAlarme):
        """Arrête l'alarme <numeroAlarme>.
        Retourne <True> si l'alarme a été trouvée et arrêtée,
        et <False> si l'alarme n'a pas été trouvée."""
        if Horloge.alarmeExiste(idInstance, numeroAlarme):
            numeroAlarme = str(idInstance) + "+" + str(numeroAlarme)
            Horloge._sonnerieActivee[numeroAlarme] = False
            return True
        else:
            return False

