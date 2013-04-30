# -*-coding:iso-8859-1 -*
import configparser,os,pygame,xml.dom.minidom
from pygame.locals import *
from interacteur import *

class Appli:
    def executer(self):
        """Exécute le script"""
        interacteur = Interacteur()
        listeTilesets = os.listdir("../Ressources/") #Liste des images tilesets
        message = "Quel tileset choisissez-vous ?\n" 
        i, choixPossibles = 0,list()
        listeTilesets = [tileset for tileset in listeTilesets if ".tsx" not in tileset and ".sqtileset" not in tileset and ".png" in tileset]
        while i < len(listeTilesets):
            message += str(i+1) + ". " + listeTilesets[i] + "\n" #Ajout du nom de chaque image au message qui sera affiché
            choixPossibles.append(i+1) #Ajout du chiffre d'un tileset à la liste des choix possibles
            i += 1
        choix = interacteur.recupererChoixDuJoueur(choixPossibles,message) #Récupération du choix
        nomTileset = listeTilesets[choix-1] 
        nomFichier = "../Ressources/" + nomTileset[:nomTileset.find(".png")] + ".tsx"
        if os.path.lexists(nomFichier) is True:
            print("Un tileset correspondant existe déjà.")
            raise SystemExit
        nomImage = "../Ressources/" + nomTileset
        try:
            surfaceTileset = pygame.image.load(nomImage)
        except:
            print("Impossible de charger {0}".format(nomImage))
            raise SystemExit
        orgaXML = xml.dom.minidom.getDOMImplementation().createDocument(None,"tileset",None)
        tilesetXML = orgaXML.documentElement
        tilesetXML.setAttribute("name",nomTileset)
        tilesetXML.setAttribute("tilewidth","32")
        tilesetXML.setAttribute("tileheight","32")
        tilesetXML.appendChild(orgaXML.createElement("image"))
        imageXML = tilesetXML.getElementsByTagName("image")[0]
        imageXML.setAttribute("source", nomTileset )
        imageXML.setAttribute("trans","ffffff")
        longueur,largeur = surfaceTileset.get_width(), surfaceTileset.get_height()
        imageXML.setAttribute("width", str(longueur) )
        imageXML.setAttribute("height", str(largeur) )
        nombreTiles = int(longueur / 32) * int(largeur / 32)
        print(nombreTiles)
        i = 0
        while i < nombreTiles:
            tile = orgaXML.createElement("tile")
            tile.setAttribute("id",str(i))
            tilesetXML.appendChild(tile)
            propris = orgaXML.createElement("properties")
            tile.appendChild(propris)
            propri = orgaXML.createElement("property")
            propri.setAttribute("name","Praticabilite")
            propri.setAttribute("value","True")
            propris.appendChild(propri)
            i += 1
        with open(nomFichier,"w") as fichier:
            orgaXML.writexml(fichier, addindent="   ", newl="\n", encoding="UTF-8")
        orgaXML.unlink()

if __name__ == "__main__":
    appli = Appli()
    appli.executer()
