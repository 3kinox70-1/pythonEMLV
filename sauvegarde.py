# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 17:08:08 2025

@author: romai
"""
import sqlite3

def sauvegarder(gagnant):
    con = sqlite3.connect("jeu.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS vainqueurs_partie2(nom_vainqueur TEXT)")
    
    # Utilisez des paramètres pour éviter les injections SQL
    cur.execute(f"INSERT INTO vainqueurs_partie2(nom_vainqueur) VALUES (?)", [gagnant.pseudo])
    
    con.commit()
    con.close()