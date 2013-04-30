# -*-coding:iso-8859-1 -*
import pygame, sys 
from pygame.locals import *

##@package constantes
#Contient toutes les constantes de l'application
#
#Les constantes de l'application sont des variables utilis�es tout au long du programme, et qui ne doivent pas pouvoir �tre modifi�es par la suite.
#Elles sont regroup�es ici pour pouvoir �tre modifi�es facilement.


#Donn�es d'odre g�n�ral

##@var FICHIER_ERREURS
#Fichier vers lequel sont redirig�es les erreurs, mais seulement si cette option est activ�e (� REDIRECTION_FICHIER_ERREURS)
#
#Dans ce fichier seront �crites toutes les erreurs d'ex�cution si REDIRECTION_FICHIER_ERREURS est activ�e. 
#Le mode d'�criture dans le fichier doit �tre pr�cis� � MODE_FICHIER_ERREURS
FICHIER_ERREURS = "Erreurs.txt" 

##@var MODE_FICHIER_ERREURS
#Mode d'�criture du fichier d'erreurs
#
#Il y en a plusieurs.
#@par 
#� w � : Efface les erreurs pr�ced�ntes avant d'�crire les nouvelles
#@par
#� a � : Ajoute les nouvelles erreurs aux pr�c�dentes
MODE_FICHIER_ERREURS ="w" 

#Si True, les erreurs sont redirig�es dans un fichier
#
#Si False, les erreurs sont simplement affich�es � l'�cran.
REDIRECTION_FICHIER_ERREURS = False 
if REDIRECTION_FICHIER_ERREURS is True:
	sys.stderr = open(FICHIER_ERREURS, MODE_FICHIER_ERREURS)

#Message affich� lorsqu'il y a une pause (terminal)
MESSAGE_PAUSE_PAR_DEFAUT = "Veuillez appuyer sur la touche � Entr�e � pour continuer..." 

#Chemin relatif vers le dossier des ressources
DOSSIER_RESSOURCES = "../Ressources/"

#Si cette constante vaut<True>, une r�p�tition de l'�v�nement KEYDOWN aura lieu quand une touche est appuy�e. Voir la constante suivante pour l'intervalle.
REPETITION_TOUCHES = False

#Intervalle en millisecondes entre deux r�p�titions de l'�v�nement KEYDOWN (si et seulement si REPETITION_TOUCHES vaut <True>)
INTERVALLE_REPETITION_TOUCHES = 100

#Liste des �v�nements utilisateur que le jeu peut capter.
LISTE_EVENTS_AUTORISES = [QUIT, KEYDOWN, KEYUP]

#Le nom de la carte sur laquelle on d�marre
NOM_CARTE_LANCEMENT = "LD26-Fin"

#L'extension des fichiers carte
EXTENSION_FICHIER_CARTE = ".narromap"

#Le volume des musiques en boucle, � mettre � 0.0 pour pas se so�ler
VOLUME_LONGUE_MUSIQUE = 0.0

#Le nom du projet actuel
PROJET = "LD26"


##Mobile, PNJ, Joueur
#
#Fichier d'image par d�faut du joueur, qui doit �tre situ� dans le dossier des ressources
FICHIER_JOUEUR_PAR_DEFAUT = "Actor1.png"

#La couleur transparente de l'image du joueur par d�faut.
COULEUR_TRANSPARENTE_FICHIER_JOUEUR_PAR_DEFAUT = (255,255,255)

#La partie de l'image du joueur lui correspondant.
CHARSET_JOUEUR_PAR_DEFAUT = (0,0)

#Affiche les coordonn�es du joueur si <True>
LOG_COORDONNEES_JOUEUR = False

#Le nom qui identifie l'�v�nement Joueur par d�faut
NOM_EVENEMENT_JOUEUR_PAR_DEFAUT = "Joueur"

#La dur�e de d�placement du joueur (d'un tile � un autre) par d�faut, exprim�e en millisecondes.
DUREE_DEPLACEMENT_JOUEUR_PAR_DEFAUT = 250#250

#La dur�e par d�faut, exprim�e en millisecondes, d'un d�placement de mobile d'un tile vers un autre.
DUREE_DEPLACEMENT_MOBILE_PAR_DEFAUT = 200 #250

#Le nombre de d�placements d'un mobile au sein d'un tile, sans qu'il y ait animation pour autant.
FREQUENCE_DEPLACEMENT_MOBILE_PAR_DEFAUT = 16 #3

#Le nombre de d�placements du joueur au sein d'un tile, sans qu'il y ait animation pour autant.
FREQUENCE_DEPLACEMENT_JOUEUR_PAR_DEFAUT =  32#16#32 #20

#Le nombre de millisecondes, au sein d'un tile ou pas, entre deux animations.
FREQUENCE_ANIMATION_MOBILE_PAR_DEFAUT = 200 #3

#Le nombre de millisecondes, au sein d'un tile ou pas, entre deux animations.
FREQUENCE_ANIMATION_JOUEUR_PAR_DEFAUT = 200 #12

#Temps (exprim� en millisecondes) entre deux animations sur place.
DUREE_ANIMATION_SP_PAR_DEFAUT = 125

#La direction de d�part par d�faut d'un mobile.
DIRECTION_DEPART_MOBILE_PAR_DEFAUT = "Bas"

#L'intelligence par d�faut d'un PNJ. Quand elle vaut <True>, le PNJ d�bloque lui-m�me une situation de collision, car il est en A*. 
#Cette variable n'a donc rien de fixe, elle d�pend purement du trajet.
#La valeur par d�faut devrait toujours �tre <False>, sauf quand le PNJ d�bute par A* (ce qui est rare).
INTELLIGENCE_PAR_DEFAUT = False

#Le courage par d�faut d'un PNJ. Quand il vaut <False>, le PNJ abandonne tout d�placement en cas de collision.
COURAGE_PAR_DEFAUT = True

#Longueur d'un sprite de mobilepar d�faut
LONGUEUR_SPRITE_PAR_DEFAUT = 32

#Largeur d'un sprite de mobile par d�faut
LARGEUR_SPRITE_PAR_DEFAUT = 32


##Zone de pens�e
#Des infos relatives � la zone de pens�e de bas d'�cran
#Le nom du fichier de police par d�faut (qui doit �tre situ� dans le dossier des ressources)
NOM_FICHIER_POLICE_PAR_DEFAUT = "BookAntiqua.ttf"

#La taille de la police par d�faut
TAILLE_POLICE_PAR_DEFAUT = 15

#La vitesse d'affichage d'une pens�e par d�faut : c'est le temps d'affichage entre deux pens�es (en millisecondes)
VITESSE_PENSEE_PAR_DEFAUT = 50

#Le temps par d�faut, en millisecondes, que met une pens�e avant d'�tre consid�r�e comme lue
TEMPS_LECTURE_PENSEE = 2000

#La couleur de fond de la zone de pens�e
COULEUR_FOND_ZONE_PENSEE = (0,0,0)

#La couleur par d�faut dans laquelle sont �crites les pens�es
COULEUR_ECRITURE_PENSEE = (255,255,255)


##Fen�tre
#Donn�es utilis�es lors de l'initialisation de la fen�tre
FENETRE = dict()
FENETRE["messageErreurInitialisationPygame"]="Une erreur s'est produite durant l'initialisation de Pygame, le programme doit donc se fermer." 
FENETRE["messageErreurInitialisationFenetre"]="Une erreur s'est produite durant l'initialisation de la fen�tre, le programme doit donc se fermer." 
FENETRE["longueurFenetre"] = 512
FENETRE["largeurFenetre"] = 384
FENETRE["largeurFenetreReelle"] = 416
FENETRE["couleurFenetre"] = (0,0,0) ##Couleur de fond de la fen�tre (hors zones sp�ciales comme tileset, outils...)
FENETRE["titreFenetre"] = "Narro Engine"
FENETRE["flagsFenetre"] = pygame.DOUBLEBUF#|pygame.FULLSCREEN|pygame.HWSURFACE

#La taille de la police en splashscreen
TAILLE_POLICE_SPLASH_SCREEN = int(FENETRE["largeurFenetre"] / 4)

#L'int�gralit� des directions possibles
LISTE_DIRECTIONS = ["Haut", "Bas", "Gauche", "Droite", "Aucune"]

#Le nombre maximal de frames par seconde
NOMBRE_MAX_DE_FPS = 60#2000

#Volume par d�faut (compris entre 0 et 1
VOLUME_MUSIQUE = 0.7 #0.0007

#La dur�e d'une pause lors d'une balade (un trajet al�atoire) exprim�e en millisecondes
DUREE_PAUSE_BALADE = 300

#Le nombre de blocs entre deux pauses lors d'une balade
FREQUENCE_PAUSE_BALADE = 2

#Le fait d'�tre en session de debug. Si <True>, un Debugger/Memory profiler sera initialis� (Pympler). 
SESSION_DEBUG = False

##Messages d'erreurs
##
##

#Messages d'erreur de mutation ou d'acc�s
#
MESSAGE_ERREUR_MUTATION_CHANGEMENT_CARTE = "<jeu.changementCarte> doit �tre un bool�en."
MESSAGE_ERREUR_MUTATION_EN_MARCHE = "<Bloc.enMarche> doit �tre un bool�en."
MESSAGE_ERREUR_MUTATION_CARTE_A_EXECUTER = "<jeu.carteAExecuter> doit �tre un <str>."
MESSAGE_ERREUR_CHARGEMENT_TILESET = "Le fichier {0}, qui doit servir de tileset, n'a pas pu �tre charg� : "
MESSAGE_ERREUR_ACCES_CONSTANTE = "La constante d'indice {0} n'existe pas."
MESSAGE_ERREUR_MUTATION_POSITION_SOURCE = "La nouvelle <positionSource> doit �tre un tuple de quatre entiers naturels."
MESSAGE_ERREUR_MUTATION_COULEUR_TRANSPARENTE = "La couleur {0} n'est pas valide."
MESSAGE_ERREUR_TILE_INEXISTANT = "Le tile aux coordonn�es {0},{1} n'existe pas."
MESSAGE_ERREUR_MUTATION_DIRECTION1 = "La direction {0} doit �tre un <str>."
MESSAGE_ERREUR_MUTATION_DIRECTION2 = "La direction doit faire partie de la liste des directions possibles."

#Messages d'erreur divers
#
MESSAGE_ERREUR_UTILISATION_INTERRUPTEUR_INVERSE = "Il est impossible d'activer, d�sactiver, inverser ou changer l'�tat d'un interrupteur invers� : son �tat est index� sur celui de l'interrupteur source."
MESSAGE_ERREUR_TILES_NON_ADJACENTS = "Les tiles {0} et {1} doivent �tre adjacents, et ce horizontalement ou verticalement uniquement (pas en diagonale)."

