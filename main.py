from flask import Flask, render_template, request, jsonify, session
from combattant import Guerrier, Mage, Archer
import sqlite3

app = Flask(__name__)
app.secret_key = "secret_key"

# Création des classes disponibles
classes_combattants = {
    "Guerrier": Guerrier,
    "Mage": Mage,
    "Archer": Archer
}

# Liste des adversaires
def generer_adversaires():
    return [
        Guerrier("Maximus"),
        Mage("Comode"),
        Archer("Lagerta")
    ]

@app.route('/')
def index():
    return render_template('choix_classe.html')

@app.route('/choisir_classe', methods=['POST'])
def choisir_classe():
    classe_nom = request.form.get('classe')
    if classe_nom not in classes_combattants:
        return jsonify({'error': "Classe invalide"}), 400

    joueur = classes_combattants[classe_nom]("Joueur")
    session['joueur'] = {
        'nom': joueur.nom,
        'classe': classe_nom,
        'vie': joueur.vie,
        'attaque': joueur.attaque
    }
    session['adversaires'] = [{
        'nom': adv.nom,
        'vie': adv.vie,
        'attaque': adv.attaque
    } for adv in generer_adversaires()]

    return jsonify({'message': f"Vous avez choisi la classe {classe_nom}", 'classe': classe_nom})

@app.route('/jeu')
def jeu():
    if 'joueur' not in session:
        return "Choisissez d'abord une classe.", 400

    joueur = session['joueur']
    adversaires = session['adversaires']
    return render_template('jeu.html', joueur=joueur, adversaires=adversaires)

@app.route('/attaque', methods=['POST'])
def attaque():
    joueur = session['joueur']
    adversaires = session['adversaires']

    attaquant_nom = joueur['nom']
    cible_nom = request.form.get('cible')

    cible = next((adv for adv in adversaires if adv['nom'] == cible_nom), None)
    if not cible:
        return jsonify({'error': "Cible invalide"}), 400

    cible['vie'] -= joueur['attaque']

    if cible['vie'] <= 0:
        adversaires.remove(cible)
        if len(adversaires) == 0:
            sauvegarder_vainqueur(joueur['nom'])
            return jsonify({'message': f"{joueur['nom']} a gagné !", 'gagnant': True})

    session['adversaires'] = adversaires
    return jsonify({'message': f"{attaquant_nom} attaque {cible_nom}!", 'pv_cible': cible['vie']})

def sauvegarder_vainqueur(nom):
    con = sqlite3.connect("jeu.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS vainqueurs(nom TEXT)")
    cur.execute("INSERT INTO vainqueurs(nom) VALUES (?)", (nom,))
    con.commit()
    con.close()

if __name__ == '__main__':
    app.run(debug=True)