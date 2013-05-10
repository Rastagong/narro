# -*-coding:iso-8859-1 -*
import pygame,pdb,math
from pygame.locals import *
from .constantes import *
from .observateur import *
from .zonePensee import * 
from .joueur import *
from .interrupteur import *


class BoiteOutils():
    """Classe permettant aux évènements d'accéder à des méthodes diverses pour réaliser des actions."""

    def __init__(self, jeu, INTERRUPTEURS, VARIABLES):
        self._jeu, self._interrupteurs, self._variables = jeu, dict(), dict()
        self._penseeAGerer = self._jeu.zonePensee.penseeAGerer
        for nomInterrupteur in INTERRUPTEURS: #Initialisation des interrupteurs
            self._interrupteurs[nomInterrupteur] = Interrupteur(False)
        for (nom, valeur) in VARIABLES:
            self._variables[nom] = valeur
        self._sons = dict()
        self._canauxSons, self._sonsFixes, self._volumesFixes, self._sourcesSonsFixes = dict(), dict(), dict(), dict()
        self._joueurLibre = Interrupteur(True)

    def initialiser(self):
        Horloge.initialiser(id(self), "DEBUG", 1000)
        self._gestionnaire = self._jeu.gestionnaireEvenements

    def getMotPenseeActuelle(self):
        return self._jeu.zonePensee.getMotActuel()

    def getNomPensee(self):
        return self._jeu.zonePensee.getNomPensee()

    def ajouterPensee(self, message, **parametres):
        """Actualise le message de la zone de pensée"""
        self._jeu.zonePensee.ajouterPensee(message, **parametres)

    def mettreToutAChanger(self):
        """Prévient la carte que tout est à changer."""
        self._jeu.carteActuelle.mettreToutAChanger()

    def changerPraticabilite(self, x, y, c, nouvellePraticabilite):
        """Change la praticabilité d'un bloc"""
        self._jeu.carteActuelle.tiles[x][y].modifierPraticabilite(c, nouvellePraticabilite)

    def changerBloc(self, x, y, c, nomTileset, positionSource, couleurTransparente, praticabilite, **argsv):
        """Change le tile d'un bloc."""
        self._jeu.carteActuelle.changerBloc(x, y, c, nomTileset, positionSource, couleurTransparente, praticabilite, **argsv)

    def determinerPresenceTilesSurCarte(self, c, nomTileset, positionSource):
        """Retourne les coordonnées de tous les tiles de la couche <c> présents sur la carte qui viennent du tileset <nomTileset> en <positionSource>, sous forme d'une liste."""
        tilesTrouves, carte, x, y, nomTileset = [], self._jeu.carteActuelle, 0, 0, nomTileset
        while x < carte.longueur:
            y = 0
            while y < carte.largeur:
                if carte.tiles[x][y].bloc[c].vide == False:
                    if carte.tiles[x][y].bloc[c].nomTileset == nomTileset and carte._tiles[x][y].bloc[c].positionSource == positionSource:
                        tilesTrouves.append((x,y))
                y += 1
            x += 1
        return tilesTrouves

    def ajouterTransformation(self, globalite, nomTransformation, **parametres):
        """Ordonne à la carte d'appliquer, à chaque frame, la transformation <nomTransformation> avec les <parametres> (un dictionnaire).
        Si <globalite> vaut <True>, il s'agit d'une transformation globale."""
        if globalite is True and nomTransformation not in self._jeu.carteActuelle.transformationsGlobales:
            self._jeu.carteActuelle.transformationsGlobales.append(nomTransformation)
        elif globalite is False and nomTransformation not in self._jeu.carteActuelle.transformationsParties:
            self._jeu.carteActuelle.transformationsParties.append(nomTransformation)
        self._jeu.carteActuelle.parametresTransformations[nomTransformation] = parametres

    def retirerTransformation(self, globalite, nomTransformation):
        """Ordonne à la carte de ne plus appliquer la transformation <nomTransformation>, globale si <globalite> vaut <True>."""
        if globalite is True and nomTransformation in self._jeu.carteActuelle.transformationsGlobales:
            self._jeu.carteActuelle.transformationsGlobales.remove(nomTransformation)
        if globalite is False and nomTransformation in self._jeu.carteActuelle.transformationsParties:
            self._jeu.carteActuelle.transformationsParties.remove(nomTransformation)
        if nomTransformation in self._jeu.carteActuelle.parametresTransformations.keys():
            self._jeu.carteActuelle.parametresTransformations[nomTransformation] = dict()

    def jouerSon(self, nomSon, instance, duree=0, nombreEcoutes=1, fixe=False, xFixe=-1, yFixe=-1, evenementFixe=-1, volume=VOLUME_MUSIQUE):
        """Joue le son nommé <nomSon> en une instance nommée <instance>. 
        Le son peut s'arrêter au bout d'un certain temps <duree> (en millisecondes).
        <nombreEcoutes> désigne le nombre de fois où le son est joué.
        <fixe> est un booléen. 
           Quand il vaut <True>, le son est localisé dans l'espace, càd que son volume décrôit quand le joueur s'en éloigne (position à préciser dans <gérerVolumeSonsFixes>.
           La position du son peut être désignée soit par <xFixe><yFixe>, soit par le nom d'un évènement <evenementFixe) (un PNJ qui chante par exemple).
           <evenementFixe> est le nom de l'évènement auquel le son est alors attaché.
        <volume> désigne le volume du son (compris entre 0.0 et 1.0)."""
        if nomSon not in self._sons.keys():
            self._sons[nomSon] = pygame.mixer.Sound(os.path.join(DOSSIER_RESSOURCES, nomSon + ".wav"))
        self._canauxSons[instance] = pygame.mixer.find_channel()
        self._canauxSons[instance].play(self._sons[nomSon], loops=nombreEcoutes-1, maxtime=duree)
        self._canauxSons[instance].set_volume(volume)
        if fixe is True:
            if self._jeu.carteAExecuter not in self._sonsFixes.keys():
                self._sonsFixes[self._jeu.carteAExecuter] = list()
            self._sonsFixes[self._jeu.carteAExecuter].append(instance)
            self._volumesFixes[instance] = volume
            if duree == 0:
                duree = self._sons[nomSon].get_length() * 1000
            if nombreEcoutes >= 1:
                Horloge.initialiser(id(self), instance, duree * nombreEcoutes)
            if xFixe != -1 and yFixe != -1:
                sourceSon = (xFixe, yFixe)
            else:
                sourceSon = evenementFixe
            self._sourcesSonsFixes[instance] = sourceSon
            self.gererVolumeSonsFixes(self._gestionnaire.xJoueur, self._gestionnaire.yJoueur)
    
    def viderSonsFixes(self, nomCarte):
        """Quand on change de cartes, on vide les sons fixes"""
        if nomCarte in self._sonsFixes.keys():
            for instance in self._sonsFixes[nomCarte]:
                self._canauxSons[instance].fadeout(3000)
                Horloge.arreterSonnerie(id(self), instance)
            self._sonsFixes.pop(nomCarte)

    def actualiserSonsFixes(self):
        """Fonction exécutée à chaque boucle du jeu. Maintient la liste des sons fixes à jour."""
        if self._jeu.carteAExecuter in self._sonsFixes.keys():
            nouveauxSonsFixes = list(self._sonsFixes[self._jeu.carteAExecuter])
            for instance in self._sonsFixes[self._jeu.carteAExecuter]:
                if Horloge.sonner(id(self), instance) is True:
                    nouveauxSonsFixes.remove(instance)
            self._sonsFixes[self._jeu.carteAExecuter] = nouveauxSonsFixes
    
    def gererVolumeSonsFixes(self, xJoueur, yJoueur):
        """Fonction appelée par l'évènement abstrait modulateur de musique dès que le joueur a bougé. 
        Sert à mettre à jour le volume des sons fixes en fonction de sa position."""
        if self._jeu.carteAExecuter in self._sonsFixes.keys():
            for instance in self._sonsFixes[self._jeu.carteAExecuter]:
                if isinstance(self._sourcesSonsFixes[instance], str): #Si la source du son fixe est un évènement (désigné par une chaîne)
                    (xFixe, yFixe) = self.getCoordonneesEvenement(self._sourcesSonsFixes[instance])
                else: #Sinon, la source donne directement les coordonnées
                    (xFixe, yFixe) = self._sourcesSonsFixes[instance]
                estimationEloignement = abs(xJoueur - xFixe) + abs(yJoueur - yFixe) - 1 #On soustrait 1 car le joueur ne peut pas être SUR la source
                nouveauVolume = self._volumesFixes[instance] - (estimationEloignement / 50) #Plus on est éloigné, plus le volume est diminué. 1 bloc d'éloignement = 0,02 ua en moins sur le volume
                if nouveauVolume < 0:
                    nouveauVolume = 0
                self._canauxSons[instance].set_volume(nouveauVolume)

    def supprimerPNJ(self, nomPNJ, couche):
        self._jeu.carteActuelle.supprimerPNJ(nomPNJ, couche)

    def teleporterSurPosition(self, positionCarte, c, positionSource, nomTileset, couleurTransparente, nomPNJ):
        """Téléporte un mobile à une autre position de la carte actuelle.""" 
        deplacementPossible = self._jeu.carteActuelle.deplacementPossible(positionCarte, c, nomPNJ) 
        if deplacementPossible is True:
            self._jeu.carteActuelle.poserPNJ(positionCarte, c, positionSource, nomTileset, couleurTransparente, nomPNJ)

    def teleporterJoueurSurPosition(self, xTile, yTile, direction, couche=-1):
        self._jeu.joueur.teleporterSurPosition(xTile, yTile, direction, couche=couche)

    def teleporterSurCarte(self, nomCarte, x, y, c, direction):
        """Téléporte le joueur sur la carte <nomCarte> en <x>,<y>,<c> avec un regard en <direction>."""
        jeu = self._jeu
        jeu.carteAExecuter, jeu.changementCarte = nomCarte, True
        self._gestionnaire.evenements["concrets"][self._gestionnaire.nomCarte].pop("Joueur") #Le joueur ne doit plus être traité sur l'ancienne carte
        self._gestionnaire.evenements["concrets"][nomCarte]["Joueur"] = [jeu.joueur, (x,y), direction]
        self._gestionnaire.evenements["concrets"][nomCarte].move_to_end("Joueur", last=False)
        jeu.joueur.transfertCarte(x, y, c, direction)

    def getJoueurMouvement(self):
        return self._jeu.joueur.mouvement

    def positionProcheEvenement(self, x, y, nomEvenement):
        """Retourne <True> si <x><y> est à une case de l'évènement nommé <nomEvenement>."""
        (xEvenement,yEvenement) = self.getCoordonneesEvenement(nomEvenement)
        if (x == xEvenement + 1 or x == xEvenement - 1 or x == xEvenement) and (y == yEvenement + 1 or y == yEvenement - 1 or y == yEvenement) and not (x == xEvenement and y == yEvenement):
            return True
        else:
            return False

    def _positionsAdjacentes(self, position, positionArrivee, blocsExclus, typeTile, c):
        """Retourne les positions adjacentes (pas en diagonale) à <position>."""
        positionsAdjacentes = [ (position[0]+1, position[1]), (position[0]-1, position[1]), (position[0], position[1]+1), (position[0], position[1]-1) ]
        positionsCorrectes, i = list(), 0
        if blocsExclus is None:
            blocsExclus = []
        while i < len(positionsAdjacentes):
            positionAdjacente = positionsAdjacentes[i]
            x, y = positionAdjacente[0], positionAdjacente[1]
            if self._jeu.carteActuelle.tileExistant(x, y) is True and ((self._jeu.carteActuelle.tilePraticable(x, y, c) is True) or (positionAdjacente == positionArrivee)) and ((x,y) not in blocsExclus or positionAdjacente == positionArrivee):
                if typeTile is False:
                    positionsCorrectes.append(positionAdjacente)
                else: #Vérification du type de tile : on n'ajoute aux positions correctes que ceux faisant partie de la liste fournie
                    bloc = self._jeu.carteActuelle.tiles[x][y].bloc[c]
                    while bloc.vide == True and c > 0:
                        c -= 1
                        bloc = self._jeu.carteActuelle.tiles[x][y].bloc[c]
                    if (bloc.nomTileset, bloc.positionSource) in typeTile: #La liste fournie est composée de tuples (<nomTileset>,<positionSource>) des tiles autorisés
                        positionsCorrectes.append(positionAdjacente)
            i += 1
        return positionsCorrectes

    def _estimationDistanceRestante(self, positionActuelle, destination):
        """Donne, en utilisant la méthode de Manhattan, une estimation heuristique entre <positionActuelle> et <destination>. 
        Cette estimation donne, avec le nombre de positions déjà parcourues, un coût <score> à chaque position.
        La position ayant le moindre côut est analysée prioritairement à chaque fois (algorithme A*)."""
        return abs(destination[0]-positionActuelle[0]) + abs(destination[1]-positionActuelle[0])

    def _determinerChemin(self, parents, position, positionDepart, chemin):
        """Détermine le chemin pour un mobile à partir de <position>, l'arrivée, et de la chaîne de parents <parents>. Le chemin est la liste de positions <chemin>."""
        if parents[position] != positionDepart:
            chemin.append(parents[position])
            self._determinerChemin(parents, parents[position], positionDepart, chemin)
        else:
            chemin.append(positionDepart)

    def _determinerDirectionDeplacement(self, positionDepart, positionArrivee):
        """Détermine la direction correspondant au déplacement entre <positionDepart> et <positionArrivee>, qui sont deux tiles adjacents (pas en diagonale)."""
        x1, y1, x2, y2 = positionDepart[0], positionDepart[1], positionArrivee[0], positionArrivee[1]
        if x2 == x1 + 1:
            return "Droite"
        elif x2 == x1 - 1:
            return "Gauche"
        elif y2 == y1 + 1:
            return "Bas"
        elif y2 == y1 - 1:
            return "Haut"
        else:
            raise Exception(MESSAGE_ERREUR_TILES_NON_ADJACENTS.format(positionDepart, positionArrivee))

    def _transformerPositionsCheminEnDirections(self, cheminPositions):
        """Transforme un chemin en positions <cheminPositions> en chemin de directions."""
        cheminDirections, i = list(), 0
        cheminPositions.reverse()
        while i < len(cheminPositions) - 1:
            positionActuelle, positionSuivante = cheminPositions[i], cheminPositions[i+1]
            cheminDirections.append( self._determinerDirectionDeplacement(positionActuelle, positionSuivante) )
            i += 1
        return cheminDirections

    def cheminVersJoueur(self, x, y, c, blocsExclus=None):
        """Retourne un chemin (une liste de directions) pour un mobile en <x><y><c> vers le joueur ne passant par aucun bloc de <blocsExclus>.
        Le chemin fait se tourner le mobile vers le joueur une fois à proximité (par une direction de regard)."""
        (xJoueur, yJoueur) = (self._gestionnaire.xJoueur, self._gestionnaire.yJoueur)
        return self.cheminVersPosition(x, y, c, xJoueur, yJoueur, arretAvant=True, regardAvant=True, blocsExclus=blocsExclus)

    def cheminVersPosition(self, x, y, c, xArrivee, yArrivee, arretAvant=False, regardAvant=False, regardFinal=False, blocsExclus=None, balade=False, dureePauseBalade=DUREE_PAUSE_BALADE, frequencePauseBalade=FREQUENCE_PAUSE_BALADE, typeTile=False):
        """Retourne un chemin (une liste de directions) pour un mobile en <x><y><c> vers <xArrivee><yArrivee> ne passant par aucun bloc de <blocsExclus>.
        Si <arretAvant> vaut <True>, le chemin s'arrêt une case avant la destination. 
        Si <regardAvant> vaut <True>, le PNJ regarde la position d'arrivée à la fin.
        Si <regardFinal> est fourni, le PNJ regarde dans la direction en question à l'arrivée.
        Si <typeTile> est fourni, le PNJ n'empruntera que les tiles définis dans cette liste de tuples (<nomTileset>,<positionSource>)."""
        positionArrivee, positionDepart = (xArrivee, yArrivee), (int(x), int(y))
        positionsVues, positionsLibres = list(), [positionDepart]
        if positionArrivee == positionDepart:
            return ["Aucune"]
        scores, scoresPositions, parents = {positionDepart:self._estimationDistanceRestante(positionDepart, positionArrivee)}, {positionDepart:0}, {positionDepart:positionDepart}
        positionsLibres = sorted(positionsLibres, key=lambda position: scores[position]) #Positions à examiner
        if blocsExclus is not None:
            for (xExclu,yExclu) in blocsExclus:
                if xArrivee == xExclu and yArrivee == yExclu: #Si le bloc d'arrivée a été exclu
                    blocsExclus.remove((xExclu,yExclu))
        while len(positionsLibres) > 0:
            position = positionsLibres[0]
            positionsLibres.remove(position)
            positionsVues.append(position)
            if position == positionArrivee: 
                chemin = [position]
                self._determinerChemin(parents, position, positionDepart, chemin)
                chemin = self._transformerPositionsCheminEnDirections(chemin)
                if arretAvant and regardAvant: #S'il faut regarder la position de fin à l'arrivée...
                    chemin[len(chemin)-1] = "R" + chemin[len(chemin)-1] #On rajoute R à la direction pour qu'il y ait un regard
                elif arretAvant:
                    del chemin[len(chemin)-1]
                if regardFinal is not False:
                    chemin.append("R" + regardFinal)
                if balade:
                    nombrePauses, i = math.floor(len(chemin) / frequencePauseBalade), 0
                    while i < nombrePauses:
                        chemin.insert(i*frequencePauseBalade, dureePauseBalade)
                        i += 1
                return chemin
            voisins = self._positionsAdjacentes(position, positionArrivee, blocsExclus, typeTile, c)
            i = 0
            while i < len(voisins):
                voisin = voisins[i]
                if positionsVues.count(voisin) == 0: #Si la position n'est pas définitivement vérifiée
                    score = scoresPositions[parents[position]] + 1 + self._estimationDistanceRestante(voisin, positionArrivee) 
                    if positionsLibres.count(voisin) == 0: #Si on ne l'a même pas examinée
                        positionsLibres.append(voisin)
                        meilleurChemin = True
                        parents[voisin] = position
                    elif score < scores[voisin]: #Si on l'a déjà examinée mais qu'elle permet d'arriver plus vite
                        meilleurChemin = True
                    else:
                        meilleurChemin = False
                    if meilleurChemin: #Si, en définitive, le score est meilleur (ou nouveau) -> Màj du score et du parent
                        scores[voisin] = score
                        scoresPositions[voisin] = scoresPositions[parents[voisin]] + 1
                        parents[voisin] = position
                i += 1
            positionsLibres = sorted(positionsLibres, key=lambda position: scores[position]) #On trie les positions à examiner pour avoir la meilleure en premier
        return ["RelanceEtoile"]

    def getCoordonneesJoueur(self):
        """Retourne un tuple contenant les coordonnées du joueur."""
        return (self._gestionnaire.xJoueur, self._gestionnaire.yJoueur)

    def getCoordonneesEvenement(self, nomEvenement):
        """Retourne les coordonnées de l'évènement nommé <nomEvenement> sur la carte actuelle. S'il n'existe pas, retourne <False>."""
        if nomEvenement in self._gestionnaire.evenements["concrets"][self._gestionnaire.nomCarte].keys():
            return self._gestionnaire.evenements["concrets"][self._gestionnaire.nomCarte][nomEvenement][1]
        else:
            return False
    
    def deplacementVersPnj(self, nomEvenement, x, y):
        """Retourne une instruction de déplacement vers le PNJ nommé <nomEvenement> situé à côté."""
        if nomEvenement in self._gestionnaire.evenements["concrets"][self._gestionnaire.nomCarte].keys():
            (xEvenement, yEvenement) = self._gestionnaire.evenements["concrets"][self._gestionnaire.nomCarte][nomEvenement][1]
            if xEvenement == x - 1:
                return ["Gauche"]
            elif xEvenement == x + 1:
                return ["Droite"]
            elif yEvenement == y - 1:
                return ["Haut"]
            elif yEvenement == y + 1:
                return ["Bas"]
            else:
                return False
        else:
            return False

    def regardVersPnj(self, nomEvenement, x, y):
        """Retourne une instruction de regard vers le PNJ nommé <nomEvenement> situé à côté."""
        direction = self.deplacementVersPnj(nomEvenement, x, y) 
        if direction is not False:
            return ["R" + direction[0]]
        else:
            return False

    def deplacementSPVersPnj(self, nomEvenement, tempsDeplacement, x, y):
        """Retourne une instruction de déplacement sur place en direction du PNJ nommé <nomEvenement> situé à côté."""
        direction = self.deplacementVersPnj(nomEvenement, x, y) 
        if direction is not False:
            return ["V" + direction[0] + str(tempsDeplacement)]
        else:
            return False

    ##Accesseurs et mutateurs
    def _getPenseeAGerer(self):
        return self._penseeAGerer

    def _getNomCarte(self):
        return self._jeu.carteActuelle.nom

    def _getInterrupteurs(self):
        return self._interrupteurs
    
    def _setInterrupteurs(self, nouveauxInterrupteurs):
        self._interrupteurs = nouveauxInterrupteurs

    def _getJoueurLibre(self):
        return self._joueurLibre

    def _setJoueurLibre(self, val):
        self._joueurLibre = val

    def _getVariables(self):
        return self._variables
    
    def _setVariables(self, nouvellesVariables):
        self._variables = nouvellesVariables

    penseeAGerer = property(_getPenseeAGerer)
    nomCarte = property(_getNomCarte)
    interrupteurs = property(fget=_getInterrupteurs, fset=_setInterrupteurs)
    variables = property(_getVariables, _setVariables)
    joueurLibre = property(_getJoueurLibre, _setJoueurLibre)

