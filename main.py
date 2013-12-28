# -*-coding:utf-8 -*
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
        self._zonePensee, self._modificationsCarte = ZonePensee(self), dict()

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
        #pygame.mixer.init(44100, -16, 2, 2048)
        pygame.mixer.set_num_channels(NOMBRE_CANAUX_SONS)

    def ajouterModificationCarte(self, nomCarte, nomModif, *args, **argv):
        """Ajoute une modification permanente de la carte <nomCarte>. Dès son initialisation, les arguments <args> et <argv> seront transmis à la méthode <changerBloc>."""
        if nomCarte not in self._modificationsCarte.keys():
            self._modificationsCarte[nomCarte] = dict()
        self._modificationsCarte[nomCarte][nomModif] = args,argv

    def retirerModificationCarte(self, nomCarte, nomModif):
        if nomCarte in self._modificationsCarte.keys():
            if nomModif in self._modificationsCarte[nomCarte].keys():
                self._modificationsCarte[nomCarte].pop(nomModif)

    def _chargerCarteAExecuter(self):
        """Charge en mémoire la carte à exécuter"""
        transformationsPermanentes = dict()
        if self._premiereCarteChargee is True: #Il y a une carte précédente, on la supprime proprement : sons fixes, obsertvation par la zone de pensée, etc
            self._zonePensee.obsSupprimerObservateur(self._carteActuelle, "_surface")
            self._zonePensee.obsSupprimerObservateur(self._carteActuelle, "_positionSurface")
            self._zonePensee.obsSupprimerObservateur(self._carteActuelle, "_faceActuelle")
            self._boiteOutils.viderSonsFixes(self._carteActuelle.nom)
            self._gestionnaireEvenements.prevenirEvenementsChangementCarte(self._carteActuelle.nom, self._carteAExecuter)
            self._gestionnaireEvenements.evenements["concrets"][self._carteActuelle.nom].pop("Joueur") #Le joueur ne doit plus être traité sur l'ancienne carte
            self._gestionnaireEvenements.tuerEvenementsATuer()
            self._gestionnaireEvenements.registerPositionInitialeJoueur(self._carteAExecuter)
            for transformation in self._carteActuelle.transformationsGlobales+self._carteActuelle.transformationsParties: #On sauvegarde les transformations permanentes
                if transformation in self._carteActuelle.parametresTransformations.keys():
                    if "permanente" in self._carteActuelle.parametresTransformations[transformation].keys():
                        transformationsPermanentes[transformation] = transformation in self._carteActuelle.transformationsGlobales, self._carteActuelle.parametresTransformations[transformation]
            del self._carteActuelle
        self._carteActuelle = Carte(self._carteAExecuter, self)
        if self._carteActuelle.nom in self._modificationsCarte.keys():
            for (args,argv) in self._modificationsCarte[self._carteActuelle.nom].values():
                self._carteActuelle.changerBloc(*args, **argv)
        for (transformation, (globale, parametres)) in transformationsPermanentes.items():
            if globale:
                self._carteActuelle.transformationsGlobales.append(transformation)
            else:
                self._carteActuelle.transformationsParties.append(transformation)
            self._carteActuelle.parametresTransformations[transformation] = parametres
        self._premiereCarteChargee = True
        self._carteActuelle.initialiserScrolling(self._joueur.x, self._joueur.y) 
        self._carteActuelle.initialiserScrollingBackground(self._joueur.x, self._joueur.y) 
        self._zonePensee.obsAjouterObservateur(self._carteActuelle, "_surface", transmissionImmediate=True)
        self._zonePensee.obsAjouterObservateur(self._carteActuelle, "_positionSurface", transmissionImmediate=True)
        self._zonePensee.obsAjouterObservateur(self._carteActuelle, "_faceActuelle", transmissionImmediate=True)
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
