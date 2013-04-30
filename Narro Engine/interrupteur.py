# -*-coding:iso-8859-1 -*
from constantes import *

class Interrupteur:
	"""Classe représentant un interrupteur"""

	def __init__(self, etat, inverser=False):
		"""Initialise un interrupteur d'état <etat>. Si <inverser> vaut <True>, prend l'état inverse."""
		self.majSelonBooleen(etat, inverser=inverser, initialisation=True)

	def _etatInverse(self, etatAInverser):
		"""Retourne l'inverse du booléen <etatAInverser>. Retourne -1 en cas d'erreur (l'état n'est pas un booléen)."""
		if isinstance(etatAInverser, bool) is True:
			if etatAInverser is False:
				return True
			elif etatAInverser is True:
				return False
		else:
			return -1

	def majSelonBooleen(self, booleen, inverser=False, initialisation=False):
		"""Prend l'état du booléen <booleen> et retourne <True> si l'opération a réussi. 
		Si <inverser> vaut <True>, l'interrupteur prend l'état inverse.
		<initialisation> vaut <True> quand la fonction est appelée lors de l'initialisation."""
		if isinstance(booleen, bool) is True and inverser is False: #Si l'état est bien un booléen et qu'on associe sans inverser
			self._etat = booleen
			return True
		elif isinstance(booleen, bool) is True and inverser is True:
			self._etat = self._etatInverse(booleen)
			return True
		else:
			return False

	def activer(self):
		"""Active l'interrupteur"""
		self._etat = True
	
	def desactiver(self):
		"""Désactive l'interrupteur"""
		self._etat = False
	
	def inverser(self):
		"""Inverse l'état de l'interrupteur"""
		self._etat = self._etatInverse(self._etat)
	
	def voir(self, inverser=False):
		"""Retourne l'état de l'interrupteur, inversé si <inverser> vaut <True>."""
		etatRetour = self._etat
		if inverser is True:
			etatRetour = self._etatInverse(etatRetour)
		return etatRetour

class InterrupteurInverse(Interrupteur):

	def __init__(self, interrupteur):
		super().__init__(interrupteur._etat, inverser=True)
		self._interrupteurSource = interrupteur
	
	def inverser(self):
		raise Exception(MESSAGE_ERREUR_UTILISATION_INTERRUPTEUR_INVERSE)

	def activer(self):
		raise Exception(MESSAGE_ERREUR_UTILISATION_INTERRUPTEUR_INVERSE)

	def desactiver(self):
		raise Exception(MESSAGE_ERREUR_UTILISATION_INTERRUPTEUR_INVERSE)

	def majSelonBooleen(self, booleen, inverser=False, initialisation=False):
		if initialisation is False:
			raise Exception(MESSAGE_ERREUR_UTILISATION_INTERRUPTEUR_INVERSE)

	def voir(self):
		self._etat = self._interrupteurSource.voir(inverser=True)
		return super().voir()

