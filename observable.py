# -*-coding:iso-8859-1 -*
from constantes import *
from observateur import *

class Observable:
	"""Interface repr�sentant un objet observable dans le design pattern Observateur."""

	def __init__(self, *nomsAttributs):
		"""Cr�� le dictionnaire des observateurs � partir des cha�nes fournies. Il s'agit des noms des attributs qui peuvent �tre surveill�s."""
		self._obsObservateurs = dict()
		for nomAttribut in nomsAttributs:
			self._obsObservateurs[nomAttribut] = list()

	def obsAjouterObservateur(self, observateur, nomAttribut):
		"""Ajoute <observateur> � la liste des observateurs.
		<nomAttribut> est une cha�ne qui d�signe l'attribut qui est surveill�. Il s'agit de son nom. Les attributs cens�s �tre priv�s,
		c'est-�-dire ceux avec deux tirets du bas ne peuvent pas �tre surveill�s. L'utilisation de cette cha�ne permet � un observateur 
		de surveiller plusieurs attributs d'un observateur tout en les traitant de mani�re diff�renci�e.
		<False> est retourn� lorsque : 
			<observateur> n'impl�mente pas l'interface <Observateur>,
			<nomAttribut> n'est pas le nom d'un attribut qui peut �tre surveill�"""
		if isinstance(observateur, Observateur) is True and nomAttribut in self._obsObservateurs.keys():
			self._obsObservateurs[nomAttribut].append(observateur)
			return True
		else:
			return False

	def obsSupprimerObservateur(self, observateur, nomAttribut):
		"""Supprime <observateur> de la liste des observateurs.
		<nomAttribut> est une cha�ne qui d�signe l'attribut qui est surveill�. Il s'agit de son nom. Les attributs cens�s �tre priv�s,
		c'est-�-dire ceux avec deux tirets du bas ne peuvent pas �tre surveill�s. L'utilisation de cette cha�ne permet � un observateur 
		de surveiller plusieurs attributs d'un observateur tout en les traitant de mani�re diff�renci�e.
		<False> est retourn� lorsque : 
			<observateur> n'impl�mente pas l'interface <Observateur>,
			<nomAttribut> n'est pas le nom d'un attribut qui peut �tre surveill�,
			<observateur> n'est pas r�pertori� comme un observateur de <nomAttribut>"""
		if isinstance(observateur, Observateur) is True and nomAttribut in self._obsObservateurs.keys():
			if observateur in self._obsObservateurs[nomAttribut]:
				self._obsObservateurs[nomAttribut].remove(observateur)
			else:
				return False
		else:
			return False

	def obsOnMiseAJour(self, nomAttribut, valeur):
		"""Lors d'une mise � jour d'un attribut surveill� <nomAttribut> avec <valeur> pour nouvelle valeur, pr�vient tous les observateurs
		cet attribut du changement. <False> est retourn� lorsque <nomAttribut> n'est pas le nom d'un attribut qui peut �tre surveill�."""
		if nomAttribut in self._obsObservateurs.keys():
			for observateur in self._obsObservateurs[nomAttribut]:
				observateur.obsOnNouvelleObservation(self, nomAttribut, valeur)
			return True
		else:
			return False
