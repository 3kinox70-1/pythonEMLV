from flask import Flask, render_template, request, jsonify, session
from combattant import Guerrier, Mage, Archer
import sqlite3
import random
from sauvegarde import sauvegarder

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
    nom_joueur = request.form.get('nom', '').strip()

    if not nom_joueur:
        return jsonify({'error': "Le nom du joueur est requis."}), 400

    if classe_nom not in classes_combattants:
        return jsonify({'error': "Classe invalide"}), 400

    # Créer le joueur avec le nom saisi
    joueur = classes_combattants[classe_nom](nom_joueur)
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

    return jsonify({'message': f"Bienvenue {nom_joueur}, vous avez choisi la classe {classe_nom}", 'classe': classe_nom})

@app.route('/rejouer', methods=['POST'])
def rejouer():
    session.clear()  # Réinitialiser la session
    return '', 204  # Réponse vide pour indiquer que tout est bon

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

    # Trouver la cible
    cible = next((adv for adv in adversaires if adv['nom'] == cible_nom), None)
    if not cible:
        return jsonify({'error': "Cible invalide"}), 400

    # Le joueur attaque la cible
    cible['vie'] -= joueur['attaque']
    message = f"{attaquant_nom} attaque {cible_nom} et inflige {joueur['attaque']} dégâts !"

    if cible['vie'] <= 0:
        message += f" {cible_nom} est vaincu !"
        adversaires.remove(cible)
        if len(adversaires) == 0:
            # Création de l'objet avec attribut 'pseudo' pour la sauvegarde
            class Gagnant:
                def __init__(self, pseudo):
                    self.pseudo = pseudo

            gagnant = Gagnant(joueur['nom'])
            sauvegarder(gagnant)  # Appel vers sauvegarde.py
            return jsonify({'message': f"{joueur['nom']} a gagné !", 'gagnant': True})
    # Contre-attaque de la cible (50% de chance de rater)
    contre_attaque_msg = ""
    if cible and cible['vie'] > 0:
        if random.choice([True, False]):  # 50% de chances de réussir
            joueur['vie'] -= cible['attaque']
            contre_attaque_msg = f"{cible_nom} riposte et inflige {cible['attaque']} dégâts à {attaquant_nom} !"
        else:
            contre_attaque_msg = f"{cible_nom} tente de riposter mais rate son attaque !"

    # Vérifier si le joueur est mort après la contre-attaque
    if joueur['vie'] <= 0:
        return jsonify({
            'message': message,
            'contre_attaque': contre_attaque_msg,
            'joueur_vie': joueur['vie'],
            'perdu_message': f"{joueur['nom']} a été vaincu. Game Over.",
            'pv_cible': cible['vie'] if cible else 0
        })

    # Sauvegarder les modifications dans la session
    session['joueur'] = joueur
    session['adversaires'] = adversaires

    # Retourner les informations mises à jour
    return jsonify({
        'message': message,
        'contre_attaque': contre_attaque_msg,
        'joueur_vie': joueur['vie'],
        'pv_cible': cible['vie'] if cible else 0
    })


def sauvegarder_vainqueur(nom):
    con = sqlite3.connect("jeu.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS vainqueurs(nom TEXT)")
    cur.execute("INSERT INTO vainqueurs(nom) VALUES (?)", (nom,))
    con.commit()
    con.close()

if __name__ == '__main__':
    app.run(debug=True)