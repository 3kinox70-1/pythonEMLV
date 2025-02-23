# -*- coding: utf-8 -*-


class Combattant:
    def __init__(self, nom, vie, attaque):
        self.nom = nom
        self.vie = vie
        self.attaque = attaque
    
    def blesser(self, degats):
        self.vie -= degats
        return f"{self.nom} perd {degats} PV et a maintenant {self.vie} PV."

class Guerrier(Combattant):
    def __init__(self, nom):
        super().__init__(nom, vie=50, attaque=7)
    
    def capacite_speciale(self):
        return "Rien de spécial juste un mec chill."

class Mage(Combattant):
    def __init__(self, nom):
        super().__init__(nom, vie=30, attaque=12)
    
    def capacite_speciale(self):
        return "Attaque plus puissante : 12 de dégâts."

class Archer(Combattant):
    def __init__(self, nom):
        super().__init__(nom, vie=70, attaque=5)
    
    def capacite_speciale(self):
        return "Plein de vie : nul en attaque mais 70 PV."
