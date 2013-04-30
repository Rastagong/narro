# -*-coding:iso-8859-1 -*
from constantes import *

class Observateur:
	"""Interface représentant l'Observateur du design pattern du même nom."""

	def __init__(self):
		pass

	def obsOnNouvelleObservation(self, instance, nomAttribut, info):
		"""Fonction appelée quand un <Observable> est mis à jour.
		<instance> désigne l'instance de l'observable mais doit seulement servir à déterminer la classe d'appartenance.
		Cela permet à un observateur de surveiller plusieurs observables tout en les traitant de manière différenciée.
		<nomAttribut> est une chaîne qui désigne l'attribut qui a été mis à jour. Il s'agit de son nom. Les attributs censés être privés,
		c'est-à-dire ceux avec deux tirets du bas ne peuvent pas être surveillés. L'utilisation de cette chaîne permet à un observateur 
		de surveiller plusieurs attributs d'un observateur tout en les traitant de manière différenciée.
		<info> est l'attribut mis à jour en lui-même."""
