# -*-coding:iso-8859-1 -*
import pygame, os, sys
from pygame.locals import *
from .constantes import *
from .zonePensee import *
from .gestionnairevenements import *
from .carte import *
if SESSION_DEBUG:
    import pdb

class Narro:
    """Classe contenant l'intégralité du jeu"""
    
    ##Méthodes privées
    ##Classées par ordre d'appel dans le code

    def __init__(self):
        self._initialiserAffichage(**FENETRE)
        self._zonePensee = ZonePensee(self)

    def inclureGestionnaire(self, gestionnaireEvenements):
        self._gestionnaireEvenements = gestionnaireEvenements
        self._boiteOutils = self._gestionnaireEvenements.initialiserBoiteOutils()

    def _initialiserAffichage(self, messageErreurInitialisationPygame, messageErreurInitialisationFenetre, longueurFenetre, largeurFenetre, largeurFenetreReelle, couleurFenetre, titreFenetre, flagsFenetre=0, forceDirectX=False):
        """Initialise Pygame et la fenêtre"""
        if sys.platform == "win32" and forceDirectX is True:
            os.environ["SDL_VIDEODRIVER"] = "directx"
        try:
            pygame.init()
        except pygame.error:
            print(messageErreurInitialisationPygame)
            raise SystemExit
        try:
            self._fenetre = pygame.display.set_mode((longueurFenetre, largeurFenetreReelle), flagsFenetre)
        except pygame.error:
            print(messageErreurInitialisationFenetre)
            pygame.quit()
            raise SystemExit
        pygame.display.set_caption(titreFenetre)
        if FICHIER_ICONE is not False:
            try:
                surfaceIcone = pygame.image.load(os.path.join(DOSSIER_RESSOURCES, FICHIER_ICONE)).convert_alpha()
                pygame.display.set_icon(surfaceIcone)
            except Exception as e:
                print(MESSAGE_ERREUR_INITIALISATION_ICONE.format(FICHIER_ICONE), e)
        self._fenetre.fill(couleurFenetre)
        if REPETITION_TOUCHES is True:
            pygame.key.set_repeat(1,INTERVALLE_REPETITION_TOUCHES)
        pygame.event.set_allowed(None)
        pygame.event.set_allowed(LISTE_EVENTS_AUTORISES)
        pygame.mixer.init()

    def _chargerCarteAExecuter(self):
        """Charge en mémoire la carte à exécuter"""
        """if self._carteAExecuter not in self._cartes.keys(): #Si la carte n'a pas encore été initialisée, on l'initialise
            cheminFichierCarte = DOSSIER_RESSOURCES + self._carteAExecuter + EXTENSION_FICHIER_CARTE
            config = configparser.ConfigParser()
            config.read(cheminFichierCarte)
            self._cartes[self._carteAExecuter] = Carte(config, self)"""
        if self._premiereCarteChargee is True: #Il y a une carte précédente, on enlève toutes ses transformations (dont les transitions) 
            """del self._carteActuelle.transformationsGlobales[:]
            del self._carteActuelle.transformationsParties[:]
            self._carteActuelle.mettreToutAChanger()"""
            self._zonePensee.obsSupprimerObservateur(self._carteActuelle, "_surface")
            self._zonePensee.obsSupprimerObservateur(self._carteActuelle, "_positionSurface")
            self._gestionnaireEvenements.evenements["concrets"][self._carteActuelle.nom].clear()
            self._boiteOutils.viderSonsFixes(self._carteActuelle.nom)
            del self._carteActuelle
        self._carteActuelle = Carte(self._carteAExecuter, self)
        self._premiereCarteChargee = True
        self._carteActuelle.initialiserScrolling(self._joueur.x, self._joueur.y) 
        self._zonePensee.obsAjouterObservateur(self._carteActuelle, "_surface")
        self._zonePensee.obsAjouterObservateur(self._carteActuelle, "_positionSurface")
        self._gestionnaireEvenements.chargerEvenements(self._carteActuelle.nom)
        if self._zonePensee.auMoinsUnePenseeGeree is True:
            self._zonePensee.redonnerPositionSurface()

    def _verifierSiLeJeuEstFini(self):
        return (self._event.type == QUIT) or (self._event.type == KEYDOWN and self._event.dict["key"] == K_ESCAPE)

    ##Méthodes publiques
    #
    def executer(self):
        """Exécute le jeu"""
        self._jeuFini, self._carteAExecuter, self._changementCarte, self._cartes = False, str(NOM_CARTE_LANCEMENT), False, dict()
        self._horlogeFps, self._premiereCarteChargee = pygame.time.Clock(), False
        self._haut, self._gauche, UNITE = 0, 0, 2
        while self._jeuFini is not True: #Tant que le joueur ne veut pas quitter
            self._changementCarte = False #Si on veut changer de carte, il faut pouvoir rentrer dans la boucle ci-dessous pour la nouvelle carte
            self._chargerCarteAExecuter()
            while self._changementCarte is not True and self._jeuFini is not True: #Tant que le joueur ne veut pas quitter ou changer de carte
                self._event = pygame.event.poll()
                self._jeuFini = self._verifierSiLeJeuEstFini()
                """if self._event.type == KEYDOWN:
                    if self._event.key == K_LEFT:
                        self._gauche = -UNITE
                    if self._event.key == K_RIGHT:
                        self._gauche = +UNITE
                    if self._event.key == K_UP:
                        self._haut = -UNITE
                    if self._event.key == K_DOWN:
                        self._haut = +UNITE
                elif self._event.type == KEYUP:
                    if self._event.key == K_LEFT or self._event.key == K_RIGHT:
                        self._gauche = 0
                    if self._event.key == K_UP or self._event.key == K_DOWN:
                        self._haut = 0
                self._carteActuelle._ecranVisible.move_ip(self._gauche, self._haut)"""
                self._gestionnaireEvenements.gererEvenements(self._carteActuelle.nom)
                self._gestionnaireEvenements.traiterPositions()
                self._gestionnaireEvenements.actualiserSonsFixes()
                self._zonePensee.gererSurfacePensee()
                self._carteActuelle.afficher()
        pygame.mixer.quit()
        pygame.quit()

    ##Accesseurs et mutateurs 
    ##
    ##
    def _getEvent(self):
        """Accesseur retournant <event>, qui est le dernier event produit par le joueur"""
        return self._event
    
    def _getFenetre(self):
        return self._fenetre

    def _getJeuFini(self):
        """Accesseur retournant le booléen <jeuFini>, qui vaut True si le joueur veut quitter le jeu"""
        return self._jeuFini

    def _getCarteActuelle(self):
        """Accesseur retournant la carte actuelle"""
        return self._carteActuelle

    def _getCarteAExecuter(self):
        """Accesseur retournant le <str> <carteAExecuter>, qui contient le nom de la carte en cours d'exécution"""
        return self._carteAExecuter

    def _getZonePensee(self):
        return self._zonePensee

    def _getGestionnaireEvenements(self):
        return self._gestionnaireEvenements

    def _getJoueur(self):
        return self._joueur

    def _setJoueur(self, nouveauJoueur):
        self._joueur = nouveauJoueur

    def _getHorlogeFps(self):
        return self._horlogeFps

    def _setCarteAExecuter(self,nouvelleCarteAExecuter):
        try:
            nouvelleCarteAExecuter = str(nouvelleCarteAExecuter)
        except:
            print(MESSAGE_ERREUR_MUTATION_CARTE_A_EXECUTER)
            raise SystemExit
        else:
            self._carteAExecuter = nouvelleCarteAExecuter

    def _setChangementCarte(self, nouveauChangementCarte):
        if nouveauChangementCarte is True or nouveauChangementCarte is False: #Si <nouveauChangementCarte> est bien un booléen
            self._changementCarte = nouveauChangementCarte
        else:
            print(MESSAGE_ERREUR_MUTATION_CHANGEMENT_CARTE)
            raise SystemExit
    
    event = property(_getEvent)
    fenetre = property(_getFenetre)
    jeuFini = property(_getJeuFini)
    carteAExecuter = property(_getCarteAExecuter, _setCarteAExecuter)
    changementCarte = property(fset=_setChangementCarte)
    carteActuelle = property(_getCarteActuelle)
    zonePensee = property(_getZonePensee)
    joueur = property(fget=_getJoueur, fset=_setJoueur)
    horlogeFps = property(fget=_getHorlogeFps)
    gestionnaireEvenements = property(_getGestionnaireEvenements)
