# -*-coding:iso-8859-1 -*
import pygame
from sys import stderr
from pygame.locals import *

#Contient toutes les constantes de l'application
#
#Les constantes de l'application sont des variables utilisées tout au long du programme, et qui ne doivent pas pouvoir être modifiées par la suite.
#Elles sont regroupées ici pour pouvoir être modifiées facilement.


#Données d'odre général

#Fichier vers lequel sont redirigées les erreurs, mais seulement si cette option est activée (à REDIRECTION_FICHIER_ERREURS)
#Dans ce fichier seront écrites toutes les erreurs d'exécution si REDIRECTION_FICHIER_ERREURS est activée. 
#Le mode d'écriture dans le fichier doit être précisé à MODE_FICHIER_ERREURS
FICHIER_ERREURS = "Erreurs.txt" 

#Mode d'écriture du fichier d'erreurs
#Il y en a plusieurs.
#« w » : Efface les erreurs précedéntes avant d'écrire les nouvelles
#« a » : Ajoute les nouvelles erreurs aux précédentes
MODE_FICHIER_ERREURS ="w" 

#Redirection vers un fichier d'erreurs
#Si True, les erreurs sont redirigées dans un fichier
#Si False, les erreurs sont simplement affichées à l'écran.
REDIRECTION_FICHIER_ERREURS = False 
if REDIRECTION_FICHIER_ERREURS is True:
	sys.stderr = open(FICHIER_ERREURS, MODE_FICHIER_ERREURS)

#Message affiché lorsqu'il y a une pause (terminal)
MESSAGE_PAUSE_PAR_DEFAUT = "Veuillez appuyer sur la touche « Entrée » pour continuer..." 

#Chemin relatif vers le dossier des ressources
DOSSIER_RESSOURCES = "Ressources"

#Si cette constante vaut<True>, une répétition de l'évènement KEYDOWN aura lieu quand une touche est appuyée. Voir la constante suivante pour l'intervalle.
REPETITION_TOUCHES = False

#Intervalle en millisecondes entre deux répétitions de l'évènement KEYDOWN (si et seulement si REPETITION_TOUCHES vaut <True>)
INTERVALLE_REPETITION_TOUCHES = 100

#Liste des évènements utilisateur que le jeu peut capter.
LISTE_EVENTS_AUTORISES = [QUIT, KEYDOWN, KEYUP]

#Le nom de la carte sur laquelle on démarre
NOM_CARTE_LANCEMENT = "LD26-Fin"

#L'extension des fichiers carte
EXTENSION_FICHIER_CARTE = ".narromap"

#Le volume des musiques en boucle, à mettre à 0.0 pour pas se soûler
VOLUME_LONGUE_MUSIQUE = 0.0

##Mobile, PNJ, Joueur
#
#Fichier d'image par défaut du joueur, qui doit être situé dans le dossier des ressources
FICHIER_JOUEUR_PAR_DEFAUT = "Actor1.png"

#La couleur transparente de l'image du joueur par défaut.
COULEUR_TRANSPARENTE_FICHIER_JOUEUR_PAR_DEFAUT = (255,255,255)

#La partie de l'image du joueur lui correspondant.
CHARSET_JOUEUR_PAR_DEFAUT = (0,0)

#Affiche les coordonnées du joueur si <True>
LOG_COORDONNEES_JOUEUR = False

#Le nom qui identifie l'évènement Joueur par défaut
NOM_EVENEMENT_JOUEUR_PAR_DEFAUT = "Joueur"

#La vitesse de déplacement par défaut du joueur en pixels par seconde
VITESSE_DEPLACEMENT_JOUEUR_PAR_DEFAUT = 250

#La vitesse de déplacement par défaut du mobile en pixels par seconde
VITESSE_DEPLACEMENT_MOBILE_PAR_DEFAUT = 120 

#Le nombre de millisecondes, au sein d'un tile ou pas, entre deux animations.
DUREE_ANIMATION_MOBILE_PAR_DEFAUT = 200 #3

#Le nombre de millisecondes, au sein d'un tile ou pas, entre deux animations.
DUREE_ANIMATION_JOUEUR_PAR_DEFAUT = 200 #12

#Temps (exprimé en millisecondes) entre deux animations sur place.
DUREE_ANIMATION_SP_PAR_DEFAUT = 100

#La direction de départ par défaut d'un mobile.
DIRECTION_DEPART_MOBILE_PAR_DEFAUT = "Bas"

#L'intelligence par défaut d'un PNJ. Quand elle vaut <True>, le PNJ débloque lui-même une situation de collision, car il est en A*. 
#Cette variable n'a donc rien de fixe, elle dépend purement du trajet.
#La valeur par défaut devrait toujours être <False>, sauf quand le PNJ débute par A* (ce qui est rare).
INTELLIGENCE_PAR_DEFAUT = False

#Le courage par défaut d'un PNJ. Quand il vaut <False>, le PNJ abandonne tout déplacement en cas de collision.
COURAGE_PAR_DEFAUT = True

#Longueur d'un sprite de mobilepar défaut
LONGUEUR_SPRITE_PAR_DEFAUT = 32

#Largeur d'un sprite de mobile par défaut
LARGEUR_SPRITE_PAR_DEFAUT = 32


##Zone de pensée
#Des infos relatives à la zone de pensée de bas d'écran
#Le nom du fichier de police par défaut (qui doit être situé dans le dossier des ressources)
NOM_FICHIER_POLICE_PAR_DEFAUT = "BookAntiqua.ttf"

#La taille de la police par défaut
TAILLE_POLICE_PAR_DEFAUT = 15

#La vitesse d'affichage d'une pensée par défaut : c'est le temps d'affichage entre deux pensées (en millisecondes)
VITESSE_PENSEE_PAR_DEFAUT = 50

#Le temps par défaut, en millisecondes, que met une pensée avant d'être considérée comme lue
TEMPS_LECTURE_PENSEE = 2000

#La couleur de fond de la zone de pensée
COULEUR_FOND_ZONE_PENSEE = (0,0,0)

#La couleur par défaut dans laquelle sont écrites les pensées
COULEUR_ECRITURE_PENSEE = (255,255,255)


##Fenêtre
#Données utilisées lors de l'initialisation de la fenêtre
FENETRE = dict()
FENETRE["messageErreurInitialisationPygame"]="Une erreur s'est produite durant l'initialisation de Pygame, le programme doit donc se fermer." 
FENETRE["messageErreurInitialisationFenetre"]="Une erreur s'est produite durant l'initialisation de la fenêtre, le programme doit donc se fermer." 
FENETRE["longueurFenetre"] = 512
FENETRE["largeurFenetre"] = 384
FENETRE["largeurFenetreReelle"] = 416
FENETRE["couleurFenetre"] = (0,0,0) ##Couleur de fond de la fenêtre (hors zones spéciales comme tileset, outils...)
FENETRE["titreFenetre"] = "Narro Engine"
FENETRE["flagsFenetre"] = DOUBLEBUF#|FULLSCREEN|HWSURFACE
FENETRE["forceDirectX"] = False

#La taille de la police en splashscreen
TAILLE_POLICE_SPLASH_SCREEN = int(FENETRE["largeurFenetre"] / 4)

#L'intégralité des directions possibles
LISTE_DIRECTIONS = ["Haut", "Bas", "Gauche", "Droite", "Aucune"]

#Le nombre maximal de frames par seconde
NOMBRE_MAX_DE_FPS = 120#2000

#<True> si la limite doit être appliquée
LIMITER_FPS = True

#Volume par défaut (compris entre 0 et 1
VOLUME_MUSIQUE = 0.7 #0.0007

#La durée d'une pause lors d'une balade (un trajet aléatoire) exprimée en millisecondes
DUREE_PAUSE_BALADE = 300

#Le nombre de blocs entre deux pauses lors d'une balade
FREQUENCE_PAUSE_BALADE = 2

#Le fait d'être en session de debug. Si <True>, un Debugger/Memory profiler sera initialisé (Pympler). 
SESSION_DEBUG = False

#Le fichier qui doit servir d'icône, à placer dans le dossier de ressources. 
#S'il n'y en a aucun (<False>), Pygame tentera de mettre l'icône par défaut, mais cela ne fonctionne pas sur tous les systèmes/avec cx_Freeze (du moins on dirait).
FICHIER_ICONE = False

##Messages d'erreurs
##
##

#Messages d'erreur de mutation ou d'accès
#
MESSAGE_ERREUR_MUTATION_CHANGEMENT_CARTE = "<jeu.changementCarte> doit être un booléen."
MESSAGE_ERREUR_MUTATION_EN_MARCHE = "<Bloc.enMarche> doit être un booléen."
MESSAGE_ERREUR_MUTATION_CARTE_A_EXECUTER = "<jeu.carteAExecuter> doit être un <str>."
MESSAGE_ERREUR_CHARGEMENT_TILESET = "Le fichier {0}, qui doit servir de tileset, n'a pas pu être chargé : "
MESSAGE_ERREUR_ACCES_CONSTANTE = "La constante d'indice {0} n'existe pas."
MESSAGE_ERREUR_MUTATION_POSITION_SOURCE = "La nouvelle <positionSource> doit être un tuple de quatre entiers naturels."
MESSAGE_ERREUR_MUTATION_COULEUR_TRANSPARENTE = "La couleur {0} n'est pas valide."
MESSAGE_ERREUR_TILE_INEXISTANT = "Le tile aux coordonnées {0},{1} n'existe pas."
MESSAGE_ERREUR_MUTATION_DIRECTION1 = "La direction {0} doit être un <str>."
MESSAGE_ERREUR_MUTATION_DIRECTION2 = "La direction doit faire partie de la liste des directions possibles."

#Messages d'erreur divers
#
MESSAGE_ERREUR_UTILISATION_INTERRUPTEUR_INVERSE = "Il est impossible d'activer, désactiver, inverser ou changer l'état d'un interrupteur inversé : son état est indexé sur celui de l'interrupteur source."
MESSAGE_ERREUR_TILES_NON_ADJACENTS = "Les tiles {0} et {1} doivent être adjacents, et ce horizontalement ou verticalement uniquement (pas en diagonale)."
MESSAGE_ERREUR_INITIALISATION_ICONE = "L'icône {0} n'a pas pu être chargée. Pygame tentera d'utiliser l'icône par défaut."
from constantes import * #Import des constantes du projet, pour écraser celles du Narro Engine en cas de redéfinition
