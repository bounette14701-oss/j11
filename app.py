import streamlit as st
import numpy as np
import time
import random

# --- Configurations et Initialisation des États ---

SESSION_KEYS = [
    'niveau_actuel', 'score', 'C_solution', 'D_defectueuse', 'T_cible', 
    'C_joueur_finale', 'C_joueur_display', 'i_curseur', 'j_curseur', 
    'temps_debut', 'jeu_actif', 'messages'
]

def initialiser_session():
    """Initialise ou réinitialise les variables de session du jeu."""
    if 'jeu_actif' not in st.session_state or not st.session_state.jeu_actif:
        for key in SESSION_KEYS:
            if key not in st.session_state:
                st.session_state[key] = None
        
        st.session_state.niveau_actuel = 1
        st.session_state.score = 0
        st.session_state.jeu_actif = True
        st.session_state.messages = []
        initialiser_niveau()

def initialiser_niveau():
    """Crée les matrices pour le niveau actuel, en utilisant les données fixes pour le Niveau 1."""
    niveau = st.session_state.niveau_actuel
    
    parametres_niveaux = {
        1: {'taille': 3, 'min_val': -5, 'max_val': 15, 'temps_limite': 90}, # Niveau 1 ajusté à 3x3 et 90s
        2: {'taille': 4, 'min_val': -8, 'max_val': 8, 'temps_limite': 150},
        3: {'taille': 5, 'min_val': -10, 'max_val': 10, 'temps_limite': 200},
    }

    if niveau not in parametres_niveaux:
        st.session_state.jeu_actif = False
        return

    params = parametres_niveaux[niveau]
    taille = params['taille']
    
    st.session_state.temps_limite = params['temps_limite']
    st.session_state.temps_debut = time.time()
    st.session_state.i_curseur = 0
    st.session_state.j_curseur = 0
    
    # --- DÉFINITION DES MATRICES POUR LE NIVEAU 1 FIXE ---
    if niveau == 1:
        # Données de l'utilisateur (7 éléments par colonne)
        col1_data = [1, 9, 7, 3, 7, 4, 12]
        col2_data = [6, 14, 4, 8, 15, 5, 5]
        
        # Compléter avec 2 valeurs aléatoires pour la taille 3x3 (9 éléments)
        random_filler_T = [random.randint(5, 15) for _ in range(2)]
        random_filler_D = [random.randint(1, 10) for _ in range(2)]
        
        # Créer les matrices 3x3
        D_defectueuse = np.array(col1_data + random_filler_D).reshape(3, 3)
        T_cible = np.array(col2_data + random_filler_T).reshape(3, 3)
        
        # Calculer la solution C = T - D
        C_solution = T_cible - D_defectueuse
        
    # --- DÉFINITION DES MATRICES POUR LES AUTRES NIVEAUX (ALÉATOIRES) ---
    else:
        D_defectueuse = np.random.randint(params['min_val'], params['max_val'] + 1, size=(taille, taille))
        C_solution = np.random.randint(params['min_val'], params['max_val'] + 1, size=(taille, taille))
        T_cible = D_defectueuse + C_solution # T = D + C

    st.session_state.C_solution = C_solution
    st.session_state.D_defectueuse = D_defectueuse
    st.session_state.T_cible = T_cible
    
    # Matrice du joueur, initialisée avec des ? pour l'affichage
    st.session_state.C_joueur_display = np.full((taille, taille), "?", dtype=object)
    st.session_state.C_joueur_finale = np.zeros((taille, taille), dtype=int)
    st.session_state.messages = [f"Niveau {niveau} démarré. Trouvez les {taille*taille} corrections!"]


# --- Fonctions d'Affichage et Mini-Jeu (Même logique que le code précédent) ---

def afficher_matrice_html(nom, matrice, i_curseur=-1, j_curseur=-1):
    """Affiche une matrice en utilisant le HTML/Markdown de Streamlit."""
    taille = matrice.shape[0]
    
    st.markdown(f"### {nom}")
    
    # Construction du tableau HTML
    html_content = f'<table style="width:100%; text-align:center; border: 1px solid #ccc; border-collapse: collapse;">'
    
    for i in range(taille):
        html_content += '<tr>'
        for j in range(taille):
            val = matrice[i, j]
            style = 'padding: 8px; border: 1px solid #ccc;'
            
            # Mise en évidence de la cellule active
            if i == i_curseur and j == j_curseur:
                style += ' background-color: #ffe0b2; font-weight: bold; border: 2px solid orange;' 
            
            html_content += f'<td style="{style}">{val}</td>'
        html_content += '</tr>'
        
    html_content += '</table>'
    st.markdown(html_content, unsafe_allow_html=True)

def generer_mini_jeu(valeur_cible):
    """Génère le texte du mini-jeu pour la valeur_cible."""
    op = random.choice(['+', '-']) 
    n1 = random.randint(5, 15)
    
    if op == '+':
        n2 = valeur_cible - n1
        question = f"Quel nombre (X) faut-il ajouter à {n1} pour obtenir {valeur_cible} ?"
        equation = f"({n1} + X = {valeur_cible})"
    elif op == '-':
        n2 = n1 - valeur_cible
        question = f"Quel nombre (X) faut-il soustraire de {n1} pour obtenir {valeur_cible} ?"
        equation = f"({n1} - X = {valeur_cible})"
    
    return question, equation

def soumettre_reponse():
    """Gère la soumission de la réponse du mini-jeu."""
    if 'mini_jeu_input' not in st.session_state or st.session_state.mini_jeu_input is None:
        st.session_state.messages.append("⚠️ Veuillez entrer une réponse.")
        return

    try:
        reponse_joueur = int(st.session_state.mini_jeu_input)
    except ValueError:
        st.session_state.messages.append("❌ Erreur : Votre réponse doit être un nombre entier.")
        return

    i, j = st.session_state.i_curseur, st.session_state.j_curseur
    valeur_attendue = st.session_state.C_solution[i, j]
    taille = st.session_state.C_solution.shape[0]
    
    if reponse_joueur == valeur_attendue:
        st.session_state.messages.append(f"✅ Position [{i+1},{j+1}] corrigée avec succès : {valeur_attendue}")
        
        st.session_state.C_joueur_display[i, j] = str(valeur_attendue)
        st.session_state.C_joueur_finale[i, j] = valeur_attendue
        st.session_state.score += 100 * st.session_state.niveau_actuel
        
        st.session_state.j_curseur += 1
        if st.session_state.j_curseur >= taille:
            st.session_state.j_curseur = 0
            st.session_state.i_curseur += 1
        
        st.session_state.mini_jeu_input = ''

    else:
        st.session_state.messages.append(f"❌ Erreur de correction à la position [{i+1},{j+1}].")
        st.session_state.score = max(0, st.session_state.score - 50)
        st.session_state.mini_jeu_input = ''


# --- Affichage Streamlit (Code principal) ---

st.set_page_config(layout="wide", page_title="Streamlit Matrix Repair")
initialiser_session()

st.title("🤖 Streamlit Matrix Repair : Défi Personnalisé")

if not st.session_state.jeu_actif:
    st.success(f"🎉 FÉLICITATIONS ! Vous avez terminé toutes les missions avec un score final de {st.session_state.score}!")
    st.button("Recommencer le jeu", on_click=initialiser_session)
else:
    # Colonnes pour les informations de statut et le chrono
    col_statut, col_chrono = st.columns([1, 1])
    col_statut.metric("Niveau Actuel", st.session_state.niveau_actuel)
    col_statut.metric("Score", st.session_state.score)

    # Chronomètre
    temps_ecoule = time.time() - st.session_state.temps_debut
    temps_restant = st.session_state.temps_limite - temps_ecoule
    
    if temps_restant <= 0:
        st.error("🚨 TEMPS ÉCOULÉ ! Mission échouée.")
        st.session_state.jeu_actif = False
        st.button("Réessayer la mission", on_click=initialiser_session)
        st.stop()
    else:
        col_chrono.metric("Temps Restant", f"{int(temps_restant)}s", delta=-1)
        time.sleep(1) 
        st.experimental_rerun()
    
    # Affichage des matrices
    col_T, col_D, col_C = st.columns(3)
    
    with col_T:
        afficher_matrice_html("Matrice Cible (T)", st.session_state.T_cible)
        
    with col_D:
        afficher_matrice_html("Matrice Défectueuse (D)", st.session_state.D_defectueuse)

    with col_C:
        afficher_matrice_html("Matrice de Correction (C)", st.session_state.C_joueur_display, 
                              st.session_state.i_curseur, st.session_state.j_curseur)


    # --- Mini-Jeu & Logique ---
    
    i, j = st.session_state.i_curseur, st.session_state.j_curseur
    taille = st.session_state.C_solution.shape[0]

    if i < taille: 
        st.markdown("---")
        
        valeur_attendue = st.session_state.C_solution[i, j]
        T_val = st.session_state.T_cible[i, j]
        D_val = st.session_state.D_defectueuse[i, j]
        
        st.subheader(f"🛠️ Mini-Jeu : Correction C[{i+1},{j+1}]")
        st.info(f"Rappel : C[{i+1},{j+1}] = T[{i+1},{j+1}] ({T_val}) - D[{i+1},{j+1}] ({D_val}) = ?")
        
        question, equation = generer_mini_jeu(valeur_attendue)
        
        st.markdown(f"**Problème logique :** {question}")
        st.caption(f"Indices : {equation}")
        
        st.text_input("Votre Correction (X)", key='mini_jeu_input', on_change=soumettre_reponse)
        
        if st.session_state.messages:
            st.sidebar.markdown("---")
            st.sidebar.subheader("Historique des Actions")
            for msg in reversed(st.session_state.messages[-5:]):
                st.sidebar.text(msg)
                
    else:
        # La matrice est complète, validation finale
        st.markdown("---")
        st.success("✅ Matrice de Correction complète ! Vérification finale...")
        
        if np.array_equal(st.session_state.C_joueur_finale, st.session_state.C_solution):
            st.session_state.messages.append(f"Mission {st.session_state.niveau_actuel} réussie en {round(temps_ecoule)}s!")
            st.session_state.niveau_actuel += 1
            st.balloons()
            st.button("Démarrer la Mission Suivante", on_click=initialiser_niveau)
        else:
             st.error("❌ Erreur de validation finale.")
             st.button("Réessayer la mission", on_click=initialiser_session)
