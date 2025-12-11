import streamlit as st
import numpy as np
import time
import random

# --- Configurations et Initialisation des États ---

SESSION_KEYS = [
    'niveau_actuel', 'score', 'C_solution', 'D_defectueuse', 'T_cible', 
    'C_joueur_finale', 'C_joueur_display', 'i_curseur', 'j_curseur', 
    'temps_debut', 'jeu_actif', 'messages', 'temps_limite'
]

def initialiser_session():
    """Initialise ou réinitialise les variables de session du jeu."""
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
        1: {'taille': 3, 'min_val': -5, 'max_val': 15, 'temps_limite': 90}, 
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
    
    # --- DÉFINITION DES MATRICES POUR LE NIVEAU 1 FIXE (3x3) ---
    if niveau == 1:
        col1_data = [1, 9, 7, 3, 7, 4, 12]
        col2_data = [6, 14, 4, 8, 15, 5, 5]
        
        random_filler_T = [random.randint(5, 15) for _ in range(2)]
        random_filler_D = [random.randint(1, 10) for _ in range(2)]
        
        D_defectueuse = np.array(col1_data + random_filler_D).reshape(3, 3)
        T_cible = np.array(col2_data + random_filler_T).reshape(3, 3)
        
        C_solution = T_cible - D_defectueuse
        
    # --- DÉFINITION DES MATRICES POUR LES AUTRES NIVEAUX (ALÉATOIRES) ---
    else:
        D_defectueuse = np.random.randint(params['min_val'], params['max_val'] + 1, size=(taille, taille))
        C_solution = np.random.randint(params['min_val'], params['max_val'] + 1, size=(taille, taille))
        T_cible = D_defectueuse + C_solution

    st.session_state.C_solution = C_solution
    st.session_state.D_defectueuse = D_defectueuse
    st.session_state.T_cible = T_cible
    
    st.session_state.C_joueur_display = np.full((taille, taille), "?", dtype=object)
    st.session_state.C_joueur_finale = np.zeros((taille, taille), dtype=int)
    st.session_state.messages = [f"Niveau {niveau} démarré. Trouvez les {taille*taille} corrections!"]

# --- Fonctions d'Affichage ---

def afficher_matrice_html(nom, matrice, i_curseur=-1, j_curseur=-1):
    """Affiche une matrice joliment encadrée en HTML."""
    taille = matrice.shape[0]
    st.markdown(f"### {nom}")
    html_content = f'<table style="width:100%; text-align:center; border: 1px solid #ccc; border-collapse: collapse;">'
    for i in range(taille):
        html_content += '<tr>'
        for j in range(taille):
            val = matrice[i, j]
            style = 'padding: 8px; border: 1px solid #ccc;'
            if i == i_curseur and j == j_curseur:
                style += ' background-color: #ffe0b2; font-weight: bold; border: 2px solid orange;'
            html_content += f'<td style="{style}">{val}</td>'
        html_content += '</tr>'
    html_content += '</table>'
    st.markdown(html_content, unsafe_allow_html=True)

# --- NOUVEAU MINI-JEU LOGIQUE LUMINEUSE ---

def generer_mini_jeu(valeur_cible):
    """
    Génère un problème de Logique Lumineuse.
    Le signe de la valeur_cible est déterminé par un puzzle VRAI/FAUX.
    """
    
    # Déterminer si la valeur cible est POSITIVE (True) ou NÉGATIVE (False)
    target_is_true = valeur_cible >= 0
    target_value = 1 if target_is_true else 0 # La réponse logique attendue (1 ou 0)
    amplitude = abs(valeur_cible)
    
    # Générer une simple grille 2x2 de VRAI (T)/FAUX (F) ou 1/0
    A = random.choice([0, 1])
    B = random.choice([0, 1])
    C = random.choice([0, 1])
    D = random.choice([0, 1])
    
    # Définir deux règles logiques pour cacher la valeur cible
    # Règle 1: Résultat de (A AND B)
    result_R1 = A & B
    # Règle 2: Résultat de (C OR D)
    result_R2 = C | D
    
    # La valeur finale (target_value) est le résultat de (R1 XOR R2)
    # Note: Ceci assure que la réponse logique est bien cachée par la formule
    final_logic_result = result_R1 ^ result_R2
    
    # Si le résultat logique ne correspond pas à la cible (target_value), nous ajustons la formule
    # Nous allons simplement forcer la réponse attendue à être le résultat de (R1 XOR R2) ou son inverse
    if final_logic_result != target_value:
        # Si le résultat logique est l'inverse de la cible, nous utilisons (R1 XOR R2) + NOT(R3)
        # Mais pour la simplicité, nous allons dire que la lumière finale L est le NOT(R1 XOR R2)
        target_formula = f"NOT ( (A AND B) XOR (C OR D) )"
        final_logic_result = 1 - final_logic_result # Inverse pour correspondre à target_value
    else:
        target_formula = f"( (A AND B) XOR (C OR D) )"

    # Affichage du puzzle
    puzzle_description = f"""
    <div style='border: 1px solid #ddd; padding: 10px; background-color: #f9f9f9;'>
    <h3>💡 Logique Lumineuse : Déterminez l'état final</h3>
    <p>La correction est déterminée par l'état final de la lumière L.</p>
    
    **États de départ :**
    <ul style='list-style-type: none; padding-left: 0; display:flex; gap: 20px;'>
        <li>A : **{A}** (FAUX/0 ou VRAI/1)</li>
        <li>B : **{B}** (FAUX/0 ou VRAI/1)</li>
        <li>C : **{C}** (FAUX/0 ou VRAI/1)</li>
        <li>D : **{D}** (FAUX/0 ou VRAI/1)</li>
    </ul>
    
    **Règles de Logique Appliquées à L :**
    <p style='font-family: monospace; font-weight: bold; font-size: 1.1em;'>L = {target_formula}</p>
    
    **Indice d'Amplitude :** La valeur absolue de la correction est **|{amplitude}|**.
    </div>
    """
    
    return puzzle_description, target_value, amplitude

# --- Logique de Soumission ---

def soumettre_reponse():
    """Gère la soumission de la réponse du mini-jeu."""
    
    # Nous avons besoin de DEUX champs de saisie pour ce jeu (valeur du mini-jeu et valeur finale)
    
    # 1. Vérifier la réponse logique (signe)
    try:
        reponse_logique = int(st.session_state.mini_jeu_input_logique)
    except ValueError:
        st.session_state.messages.append("❌ Erreur : La réponse logique doit être 0 (FAUX) ou 1 (VRAI).")
        return
    
    # 2. Vérifier la réponse finale (valeur complète)
    try:
        reponse_finale = int(st.session_state.mini_jeu_input_finale)
    except ValueError:
        st.session_state.messages.append("❌ Erreur : La correction finale doit être un nombre entier.")
        return

    i, j = st.session_state.i_curseur, st.session_state.j_curseur
    valeur_attendue = st.session_state.C_solution[i, j]
    taille = st.session_state.C_solution.shape[0]

    # Vérification complète
    if reponse_finale == valeur_attendue:
        # Vérification du signe (réponse logique)
        expected_logic = 1 if valeur_attendue >= 0 else 0
        
        if reponse_logique != expected_logic:
            st.session_state.messages.append(f"⚠️ Correction correcte ({valeur_attendue}), mais votre réponse logique ({reponse_logique}) est incorrecte. Attention aux signes !")
        
        st.session_state.messages.append(f"✅ Position [{i+1},{j+1}] corrigée avec succès : {valeur_attendue}")
        
        st.session_state.C_joueur_display[i, j] = str(valeur_attendue)
        st.session_state.C_joueur_finale[i, j] = valeur_attendue
        st.session_state.score += 100 * st.session_state.niveau_actuel
        
        st.session_state.j_curseur += 1
        if st.session_state.j_curseur >= taille:
            st.session_state.j_curseur = 0
            st.session_state.i_curseur += 1
        
        # Effacer les entrées
        st.session_state.mini_jeu_input_logique = ''
        st.session_state.mini_jeu_input_finale = ''

    else:
        st.session_state.messages.append(f"❌ Erreur de correction à la position [{i+1},{j+1}].")
        st.session_state.score = max(0, st.session_state.score - 50)
        # Effacer uniquement les entrées finales pour réessayer le mini-jeu
        st.session_state.mini_jeu_input_finale = ''


# --- Affichage Streamlit (Code principal) ---

st.set_page_config(layout="wide", page_title="Streamlit Matrix Repair - Logique Booléenne")
initialiser_session()

st.title("🤖 Streamlit Matrix Repair : Logique Lumineuse")

if not st.session_state.jeu_actif:
    st.success(f"🎉 FÉLICITATIONS ! Vous avez terminé toutes les missions avec un score final de {st.session_state.score}!")
    st.button("Recommencer le jeu", on_click=initialiser_session)
else:
    # Colonnes pour les informations de statut et le chrono
    col_statut, col_chrono = st.columns([1, 1])
    col_statut.metric("Niveau Actuel", st.session_state.niveau_actuel)
    col_statut.metric("Score", st.session_state.score)

    # Chronomètre et vérification du temps (méthode stable)
    temps_ecoule = time.time() - st.session_state.temps_debut
    temps_restant = st.session_state.temps_limite - temps_ecoule
    
    pourcentage_temps_ecoule = min(1.0, temps_ecoule / st.session_state.temps_limite)
    
    col_chrono.metric("Temps Restant (s)", f"{int(temps_restant)}", delta=0)
    st.progress(pourcentage_temps_ecoule, text="Progression du temps")

    if temps_restant <= 0:
        st.error("🚨 TEMPS ÉCOULÉ ! Mission échouée.")
        st.session_state.jeu_actif = False
        st.button("Réessayer la mission", on_click=initialiser_session)
    
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
        st.info(f"Rappel : C[{i+1},{j+1}] = T[{i+1},{j+1}] ({T_val}) - D[{i+1},{j+1}] ({D_val}) = {valeur_attendue}")
        
        puzzle_html, valeur_attendue_puzzle, amplitude = generer_mini_jeu(valeur_attendue)
        
        st.markdown(puzzle_html, unsafe_allow_html=True) # Affichage du puzzle
        
        # Deux inputs pour le nouveau jeu
        col_logique, col_finale = st.columns(2)
        
        with col_logique:
             st.text_input("Réponse Logique (L) [0 ou 1]", key='mini_jeu_input_logique')
        
        with col_finale:
             st.text_input("Correction Finale (C)", key='mini_jeu_input_finale', on_change=soumettre_reponse)

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
