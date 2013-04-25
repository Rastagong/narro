# -*-coding:iso-8859-1 -*
from constantes import *

class Observateur:
	"""Interface repr�sentant l'Observateur du design pattern du m�me nom."""

	def __init__(self):
		pass

	def obsOnNouvelleObservation(self, instance, nomAttribut, info):
		"""Fonction appel�e quand un <Observable> est mis � jour.
		<instance> d�signe l'instance de l'observable mais doit seulement servir � d�terminer la classe d'appartenance.
		Cela permet � un observateur de surveiller plusieurs observables tout en les traitant de mani�re diff�renci�e.
		<nomAttribut> est une cha�ne qui d�signe l'attribut qui a �t� mis � jour. Il s'agit de son nom. Les attributs cens�s �tre priv�s,
		c'est-�-dire ceux avec deux tirets du bas ne peuvent pas �tre surveill�s. L'utilisation de cette cha�ne permet � un observateur 
		de surveiller plusieurs attributs d'un observateur tout en les traitant de mani�re diff�renci�e.
		<info> est l'attribut mis � jour en lui-m�me."""
