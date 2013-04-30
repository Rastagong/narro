# -*-coding:iso-8859-1 -*
from constantes import *
from observateur import *

class Observable:
	"""Interface représentant un objet observable dans le design pattern Observateur."""

	def __init__(self, *nomsAttributs):
		"""Créé le dictionnaire des observateurs à partir des chaînes fournies. Il s'agit des noms des attributs qui peuvent être surveillés."""
		self._obsObservateurs = dict()
		for nomAttribut in nomsAttributs:
			self._obsObservateurs[nomAttribut] = list()

	def obsAjouterObservateur(self, observateur, nomAttribut):
		"""Ajoute <observateur> à la liste des observateurs.
		<nomAttribut> est une chaîne qui désigne l'attribut qui est surveillé. Il s'agit de son nom. Les attributs censés être privés,
		c'est-à-dire ceux avec deux tirets du bas ne peuvent pas être surveillés. L'utilisation de cette chaîne permet à un observateur 
		de surveiller plusieurs attributs d'un observateur tout en les traitant de manière différenciée.
		<False> est retourné lorsque : 
			<observateur> n'implémente pas l'interface <Observateur>,
			<nomAttribut> n'est pas le nom d'un attribut qui peut être surveillé"""
		if isinstance(observateur, Observateur) is True and nomAttribut in self._obsObservateurs.keys():
			self._obsObservateurs[nomAttribut].append(observateur)
			return True
		else:
			return False

	def obsSupprimerObservateur(self, observateur, nomAttribut):
		"""Supprime <observateur> de la liste des observateurs.
		<nomAttribut> est une chaîne qui désigne l'attribut qui est surveillé. Il s'agit de son nom. Les attributs censés être privés,
		c'est-à-dire ceux avec deux tirets du bas ne peuvent pas être surveillés. L'utilisation de cette chaîne permet à un observateur 
		de surveiller plusieurs attributs d'un observateur tout en les traitant de manière différenciée.
		<False> est retourné lorsque : 
			<observateur> n'implémente pas l'interface <Observateur>,
			<nomAttribut> n'est pas le nom d'un attribut qui peut être surveillé,
			<observateur> n'est pas répertorié comme un observateur de <nomAttribut>"""
		if isinstance(observateur, Observateur) is True and nomAttribut in self._obsObservateurs.keys():
			if observateur in self._obsObservateurs[nomAttribut]:
				self._obsObservateurs[nomAttribut].remove(observateur)
			else:
				return False
		else:
			return False

	def obsOnMiseAJour(self, nomAttribut, valeur):
		"""Lors d'une mise à jour d'un attribut surveillé <nomAttribut> avec <valeur> pour nouvelle valeur, prévient tous les observateurs
		cet attribut du changement. <False> est retourné lorsque <nomAttribut> n'est pas le nom d'un attribut qui peut être surveillé."""
		if nomAttribut in self._obsObservateurs.keys():
			for observateur in self._obsObservateurs[nomAttribut]:
				observateur.obsOnNouvelleObservation(self, nomAttribut, valeur)
			return True
		else:
			return False
