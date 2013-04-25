# -*-coding:iso-8859-1 -*
from constantes import *

class Interrupteur:
	"""Classe repr�sentant un interrupteur"""

	def __init__(self, etat, inverser=False):
		"""Initialise un interrupteur d'�tat <etat>. Si <inverser> vaut <True>, prend l'�tat inverse."""
		self.majSelonBooleen(etat, inverser=inverser, initialisation=True)

	def _etatInverse(self, etatAInverser):
		"""Retourne l'inverse du bool�en <etatAInverser>. Retourne -1 en cas d'erreur (l'�tat n'est pas un bool�en)."""
		if isinstance(etatAInverser, bool) is True:
			if etatAInverser is False:
				return True
			elif etatAInverser is True:
				return False
		else:
			return -1

	def majSelonBooleen(self, booleen, inverser=False, initialisation=False):
		"""Prend l'�tat du bool�en <booleen> et retourne <True> si l'op�ration a r�ussi. 
		Si <inverser> vaut <True>, l'interrupteur prend l'�tat inverse.
		<initialisation> vaut <True> quand la fonction est appel�e lors de l'initialisation."""
		if isinstance(booleen, bool) is True and inverser is False: #Si l'�tat est bien un bool�en et qu'on associe sans inverser
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
		"""D�sactive l'interrupteur"""
		self._etat = False
	
	def inverser(self):
		"""Inverse l'�tat de l'interrupteur"""
		self._etat = self._etatInverse(self._etat)
	
	def voir(self, inverser=False):
		"""Retourne l'�tat de l'interrupteur, invers� si <inverser> vaut <True>."""
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

