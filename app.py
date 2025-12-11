import streamlit as st
import numpy as np
import time
import random

# --- Configurations et Initialisation des États ---

SESSION_KEYS = [
    'niveau_actuel', 'score', 'C_solution', 'D_defectueuse', 'T_cible', 
    'C_joueur_finale', 'C_joueur_display', 'i_curseur', 'j_curseur', 
    'temps_debut', 'jeu_actif', 'messages', 'temps_limite',
    'ppc_player_choice', 'ppc_ai_choice', 'ppc_result', 'ppc_game_won',
    'hangman_word', 'hangman_display', 'hangman_guesses', 'hangman_misses', 'hangman_game_won', 'hangman_max_misses',
    'current_game_type', 'puzzle_data'
]

# Le cycle des jeux : Pendu -> PPC -> Géométrique -> Lumineuse
GAME_TYPES = ["HANGMAN", "PPC", "GEOMETRIC", "LOGIC_SWITCH"] 

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

def reset_ppc_state():
    """Réinitialise l'état du jeu Pierre-Papier-Ciseaux."""
    st.session_state.ppc_player_choice = None
    st.session_state.ppc_ai_choice = None
    st.session_state.ppc_result = "Jouez pour déverrouiller la correction !"
    st.session_state.ppc_game_won = False

def reset_hangman_state(valeur_cible):
    """Réinitialise l'état du jeu Le Pendu."""
    # Le mot à deviner sera un mot simple ou un indice lié à la valeur cible
    # Pour simplifier, les mots seront des indices liés à la correction (ex: PLUS, MOINS, DEUX, DIX)
    mots = {
        0: 'ZERO', 1: 'UN', 2: 'DEUX', 3: 'TROIS', 4: 'QUATRE', 5: 'CINQ',
        6: 'SIX', 7: 'SEPT', 8: 'HUIT', 9: 'NEUF', 10: 'DIX', -1: 'NEGATIF'
    }
    
    # Nous utilisons la valeur absolue pour le mot, ou 'NEGATIF' si négatif
    mot_cle = mots.get(valeur_cible) if valeur_cible >= 0 else mots.get(-1)
    
    st.session_state.hangman_word = mot_cle
    st.session_state.hangman_display = ["_" if l.isalpha() else l for l in mot_cle]
    st.session_state.hangman_guesses = set()
    st.session_state.hangman_misses = 0
    st.session_state.hangman_max_misses = 7
    st.session_state.hangman_game_won = False


def initialiser_niveau():
    """Crée les matrices pour le niveau actuel."""
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
    
    # Initialisation du type de jeu et des états
    st.session_state.current_game_type = GAME_TYPES[0] 
    st.session_state.puzzle_data = None
    reset_ppc_state()
    # Le Pendu sera initialisé lors de la première itération du main loop
    
# --- Fonctions d'Affichage et des Mini-Jeux (identiques à la réponse précédente) ---
# ... (omises pour la concision, mais elles sont conservées)

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

# --- Logique PPC (Jeu Classique) ---

def play_ppc(player_choice):
    """Joue une manche de Pierre-Papier-Ciseaux."""
    choices = {'Pierre': '✊', 'Feuille': '✋', 'Ciseaux': '✌️'}
    ai_choice_name = random.choice(list(choices.keys()))
    
    st.session_state.ppc_player_choice = player_choice
    st.session_state.ppc_ai_choice = ai_choice_name
    
    result_msg = f"Joueur: {choices[player_choice]} vs IA: {choices[ai_choice_name]} "
    
    if player_choice == ai_choice_name:
        st.session_state.ppc_result = result_msg + "-> Égalité ! Rejouez."
        st.session_state.ppc_game_won = False
    elif (
        (player_choice == 'Pierre' and ai_choice_name == 'Ciseaux') or
        (player_choice == 'Feuille' and ai_choice_name == 'Pierre') or
        (player_choice == 'Ciseaux' and ai_choice_name == 'Feuille')
    ):
        st.session_state.ppc_result = result_msg + "-> Victoire ! La correction est déverrouillée."
        st.session_state.ppc_game_won = True
    else:
        st.session_state.ppc_result = result_msg + "-> Défaite. Rejouez pour déverrouiller."
        st.session_state.ppc_game_won = False
    
    st.session_state.messages.append(f"PPC: {st.session_state.ppc_result}")

# --- Logique Le Pendu (Jeu de Lettres) ---

def submit_hangman_guess():
    """Gère la soumission d'une lettre pour le jeu Le Pendu."""
    if 'hangman_input' not in st.session_state or not st.session_state.hangman_input:
        return

    guess = st.session_state.hangman_input.upper().strip()
    st.session_state.hangman_input = '' # Effacer l'entrée immédiatement

    if len(guess) != 1 or not guess.isalpha():
        st.session_state.messages.append("⚠️ Pendu : Veuillez entrer une seule lettre valide.")
        return

    if guess in st.session_state.hangman_guesses:
        st.session_state.messages.append(f"⚠️ Pendu : Vous avez déjà essayé la lettre '{guess}'.")
        return

    st.session_state.hangman_guesses.add(guess)
    word = st.session_state.hangman_word

    if guess in word:
        st.session_state.messages.append(f"✅ Pendu : La lettre '{guess}' est correcte !")
        new_display = list(st.session_state.hangman_display)
        for i, letter in enumerate(word):
            if letter == guess:
                new_display[i] = guess
        st.session_state.hangman_display = new_display
        
        if "_" not in st.session_state.hangman_display:
            st.session_state.hangman_game_won = True
            st.session_state.messages.append("🎉 Pendu : MOT TROUVÉ ! La correction est déverrouillée.")
    else:
        st.session_state.hangman_misses += 1
        st.session_state.messages.append(f"❌ Pendu : La lettre '{guess}' est fausse. Erreurs : {st.session_state.hangman_misses}/{st.session_state.hangman_max_misses}")
        
        if st.session_state.hangman_misses >= st.session_state.hangman_max_misses:
            st.session_state.hangman_game_won = False
            st.session_state.messages.append(f"💀 Pendu : PENDU ! Le mot était '{word}'. Correction échouée, réessayez la cellule.")

# --- Logique Logique Géométrique (Jeu de Déduction) ---

def generer_geometric_puzzle(valeur_cible):
    """Génère un problème de séquence de formes non-scolaire."""
    symboles_disponibles = {
        '🔴': random.randint(1, 5),    # Cercle rouge
        '🟦': random.randint(-5, 0),   # Carré bleu
        '⭐': random.randint(6, 10),   # Étoile
        '🔺': random.randint(-10, -6), # Triangle
        '🔸': valeur_cible,            # Losange (Symbole cible)
    }
    
    clés_enigme = list(symboles_disponibles.keys())[:-1] 
    symbole_A = random.choice(clés_enigme)
    symbole_B = random.choice([s for s in clés_enigme if s != symbole_A])
    valeur_A = symboles_disponibles[symbole_A]
    valeur_B = symboles_disponibles[symbole_B]

    puzzle_description = f"""
    <div style='border: 1px solid #ddd; padding: 10px; background-color: #f9f9f9;'>
    <h3>Puzzle de Réparation Géométrique</h3>
    <p>Chaque symbole a une valeur fixe. Déduisez la valeur du symbole 🔸.</p>
    
    **Règles de valeur :**
    <ul style='list-style-type: none; padding-left: 0;'>
        <li>{symbole_A} + {symbole_B} = {valeur_A + valeur_B}</li>
        <li>{symbole_B} + {symbole_A} + {symbole_A} = {valeur_B + 2*valeur_A}</li>
    </ul>
    
    **Question :** Quelle est la valeur de {symboles_disponibles['🔸']} ?
    </div>
    """
    return puzzle_description

# --- Logique Lumineuse (Jeu Logique Booléenne) ---

def generer_logic_switch_puzzle(valeur_cible):
    """Génère un problème de Logique Lumineuse."""
    
    target_is_true = valeur_cible >= 0
    amplitude = abs(valeur_cible)
    
    A = random.choice([0, 1]); B = random.choice([0, 1]); C = random.choice([0, 1]); D = random.choice([0, 1])
    
    result_R1 = A & B
    result_R2 = C | D
    final_logic_result = result_R1 ^ result_R2
    
    target_value_logic = 1 if target_is_true else 0 # La réponse logique attendue (1 ou 0)

    if final_logic_result != target_value_logic:
        target_formula = f"NOT ( (A AND B) XOR (C OR D) )"
    else:
        target_formula = f"( (A AND B) XOR (C OR D) )"

    puzzle_description = f"""
    <div style='border: 1px solid #ddd; padding: 10px; background-color: #f9f9f9;'>
    <h3>💡 Logique Lumineuse : Déterminez l'état final (0 ou 1)</h3>
    <p>L'état final (L) détermine le signe de la correction (1=Positif, 0=Négatif).</p>
    
    **États de départ :** A={A}, B={B}, C={C}, D={D}
    
    **Règle de Logique Appliquée à L :**
    <p style='font-family: monospace; font-weight: bold; font-size: 1.1em;'>L = {target_formula}</p>
    
    **Amplitude :** La valeur absolue de la correction est **|{amplitude}|**.
    </div>
    """
    return puzzle_description

# --- Fonction principale de génération de mini-jeu ---

def generer_mini_jeu(i, j):
    """Détermine et génère le mini-jeu pour la position (i, j)."""
    
    valeur_cible = st.session_state.C_solution[i, j]
    
    # L'indice de jeu est basé sur la position absolue dans la matrice
    current_cell_index = i * st.session_state.C_solution.shape[0] + j
    game_index = current_cell_index % len(GAME_TYPES)
    game_type = GAME_TYPES[game_index]
    st.session_state.current_game_type = game_type
    
    st.session_state.puzzle_data = None # Réinitialiser les données du puzzle

    if game_type == "HANGMAN":
        reset_hangman_state(valeur_cible)
        st.session_state.puzzle_data = {"requires_win": True}
        return {"type": "HANGMAN"}

    elif game_type == "PPC":
        reset_ppc_state()
        st.session_state.puzzle_data = {"requires_win": True}
        return {"type": "PPC"}

    elif game_type == "GEOMETRIC":
        puzzle_html = generer_geometric_puzzle(valeur_cible)
        st.session_state.puzzle_data = {"requires_win": False, "html": puzzle_html}
        return {"type": "GEOMETRIC", "html": puzzle_html}

    elif game_type == "LOGIC_SWITCH":
        puzzle_html = generer_logic_switch_puzzle(valeur_cible)
        st.session_state.puzzle_data = {"requires_win": False, "html": puzzle_html}
        return {"type": "LOGIC_SWITCH", "html": puzzle_html}

# --- Logique de Soumission de la Correction ---

def soumettre_correction():
    """Vérifie le statut et soumet la correction finale."""
    
    game_type = st.session_state.current_game_type
    can_submit = True
    
    # 1. Vérification des conditions de victoire (si applicable)
    if game_type == "PPC" and not st.session_state.ppc_game_won:
        st.session_state.messages.append("❌ Vous devez gagner à Pierre-Papier-Ciseaux avant de soumettre la correction.")
        return
    elif game_type == "HANGMAN" and st.session_state.hangman_misses >= st.session_state.hangman_max_misses:
        st.session_state.messages.append(f"❌ Pendu : Échec critique (pendu !). Vous devez recommencer la cellule.")
        st.session_state.current_game_type = "PPC" # Passage forcé à PPC pour la prochaine tentative
        st.rerun()
        return
    elif game_type == "HANGMAN" and not st.session_state.hangman_game_won:
        st.session_state.messages.append("❌ Pendu : Vous devez trouver le mot avant de soumettre la correction.")
        return

    # 2. Vérification de l'entrée finale
    if 'mini_jeu_input_finale' not in st.session_state or st.session_state.mini_jeu_input_finale == '':
        st.session_state.messages.append("⚠️ Veuillez entrer la correction finale.")
        return

    try:
        reponse_finale = int(st.session_state.mini_jeu_input_finale)
    except ValueError:
        st.session_state.messages.append("❌ Erreur : La correction finale doit être un nombre entier.")
        return

    i, j = st.session_state.i_curseur, st.session_state.j_curseur
    valeur_attendue = st.session_state.C_solution[i, j]
    taille = st.session_state.C_solution.shape[0]

    # 3. Validation
    if reponse_finale == valeur_attendue:
        st.session_state.messages.append(f"✅ Position [{i+1},{j+1}] corrigée et validée avec succès : {valeur_attendue}")
        
        st.session_state.C_joueur_display[i, j] = str(valeur_attendue)
        st.session_state.C_joueur_finale[i, j] = valeur_attendue
        st.session_state.score += 100 * st.session_state.niveau_actuel
        
        # Passage au prochain élément
        st.session_state.j_curseur += 1
        if st.session_state.j_curseur >= taille:
            st.session_state.j_curseur = 0
            st.session_state.i_curseur += 1
        
        # Réinitialisation et Rerun
        st.session_state.mini_jeu_input_finale = ''
        st.session_state.puzzle_data = None
        st.rerun() 

    else:
        st.session_state.messages.append(f"❌ Erreur de correction à la position [{i+1},{j+1}]. La correction est fausse. Réessayez la cellule (le mini-jeu reste actif).")
        st.session_state.score = max(0, st.session_state.score - 50)
        st.session_state.mini_jeu_input_finale = ''
        if game_type in ["PPC", "HANGMAN"]:
            st.session_state.current_game_type = GAME_TYPES[(GAME_TYPES.index(game_type) + 1) % len(GAME_TYPES)]
            st.session_state.puzzle_data = None
            st.rerun() # Recommence le cycle de jeu pour cette cellule

# --- Affichage Streamlit (Code principal) ---

st.set_page_config(layout="wide", page_title="Streamlit Matrix Repair - Multi-Jeux")
initialiser_session()

st.title("🤖 Streamlit Matrix Repair : Défi Classique & Logique")

if not st.session_state.jeu_actif:
    st.success(f"🎉 FÉLICITATIONS ! Vous avez terminé toutes les missions avec un score final de {st.session_state.score}!")
    st.button("Recommencer le jeu", on_click=initialiser_session)
else:
    # 1. Barre de Statut
    col_statut, col_chrono = st.columns([1, 1])
    col_statut.metric("Niveau Actuel", st.session_state.niveau_actuel)
    col_statut.metric("Score", st.session_state.score)

    temps_ecoule = time.time() - st.session_state.temps_debut
    temps_restant = st.session_state.temps_limite - temps_ecoule
    
    pourcentage_temps_ecoule = min(1.0, temps_ecoule / st.session_state.temps_limite)
    
    col_chrono.metric("Temps Restant (s)", f"{int(temps_restant)}", delta=0)
    st.progress(pourcentage_temps_ecoule, text="Progression du temps")

    if temps_restant <= 0:
        st.error("🚨 TEMPS ÉCOULÉ ! Mission échouée.")
        st.session_state.jeu_actif = False
        st.button("Réessayer la mission", on_click=initialiser_session)
    
    # 2. Affichage des matrices
    col_T, col_D, col_C = st.columns(3)
    
    with col_T:
        afficher_matrice_html("Matrice Cible (T)", st.session_state.T_cible)
        
    with col_D:
        afficher_matrice_html("Matrice Défectueuse (D)", st.session_state.D_defectueuse)

    with col_C:
        afficher_matrice_html("Matrice de Correction (C)", st.session_state.C_joueur_display, 
                              st.session_state.i_curseur, st.session_state.j_curseur)


    # 3. Mini-Jeu & Logique
    
    i, j = st.session_state.i_curseur, st.session_state.j_curseur
    taille = st.session_state.C_solution.shape[0]

    if i < taille: 
        st.markdown("---")
        
        if st.session_state.puzzle_data is None:
            puzzle_info = generer_mini_jeu(i, j)
        else:
            puzzle_info = {"type": st.session_state.current_game_type, "html": None} 

        valeur_attendue = st.session_state.C_solution[i, j]
        T_val = st.session_state.T_cible[i, j]
        D_val = st.session_state.D_defectueuse[i, j]
        
        st.subheader(f"🛠️ Étape de Correction C[{i+1},{j+1}] ({puzzle_info['type']})")
        st.info(f"**Calcul :** C[{i+1},{j+1}] = T[{i+1},{j+1}] ({T_val}) - D[{i+1},{j+1}] ({D_val})")
        
        game_type = puzzle_info['type']
        
        # --- Affichage du Jeu actuel ---
        
        if game_type == "HANGMAN":
            st.markdown("### 💀 Mini-Jeu : Le Pendu")
            
            if st.session_state.hangman_misses >= st.session_state.hangman_max_misses:
                 st.error(f"Pendu ! Le mot était '{st.session_state.hangman_word}'. Échec de la cellule.")
            elif st.session_state.hangman_game_won:
                 st.success(f"Mot trouvé : {st.session_state.hangman_word} ! Correction déverrouillée.")
            else:
                st.markdown(f"Mot à deviner : **{' '.join(st.session_state.hangman_display)}**")
                st.write(f"Erreurs restantes : {st.session_state.hangman_max_misses - st.session_state.hangman_misses}")
                st.write(f"Lettres essayées : {', '.join(sorted(st.session_state.hangman_guesses))}")
                
                st.text_input("Proposer une lettre", key='hangman_input', max_chars=1, on_change=submit_hangman_guess)
                
            can_submit_game = st.session_state.hangman_game_won
            
        elif game_type == "PPC":
            st.markdown("### 🔑 Mini-Jeu : Pierre-Papier-Ciseaux")
            
            col_ppc_pierre, col_ppc_feuille, col_ppc_ciseaux, col_ppc_result = st.columns([1, 1, 1, 2])
            
            with col_ppc_pierre: st.button("Pierre ✊", on_click=play_ppc, args=('Pierre',))
            with col_ppc_feuille: st.button("Feuille ✋", on_click=play_ppc, args=('Feuille',))
            with col_ppc_ciseaux: st.button("Ciseaux ✌️", on_click=play_ppc, args=('Ciseaux',))
                
            with col_ppc_result:
                if st.session_state.ppc_game_won: st.success(st.session_state.ppc_result)
                elif st.session_state.ppc_player_choice: st.warning(st.session_state.ppc_result)
                else: st.caption(st.session_state.ppc_result)

            can_submit_game = st.session_state.ppc_game_won
            
        elif game_type == "GEOMETRIC":
            st.markdown("### 🧩 Mini-Jeu : Logique Géométrique")
            st.markdown(st.session_state.puzzle_data['html'], unsafe_allow_html=True)
            can_submit_game = True # Logique/Géométrique n'a pas besoin de victoire, juste de la réponse
            
        elif game_type == "LOGIC_SWITCH":
            st.markdown("### 💡 Mini-Jeu : Logique Lumineuse")
            st.markdown(st.session_state.puzzle_data['html'], unsafe_allow_html=True)
            can_submit_game = True # Logique/Géométrique n'a pas besoin de victoire, juste de la réponse


        # --- Interface de Soumission Finale ---
        
        st.markdown("---")
        
        if not can_submit_game:
            st.error("🔒 Correction verrouillée. Vous devez réussir le mini-jeu actif.")
        
        st.text_input(
            "Correction Finale (Résultat du calcul/puzzle)", 
            key='mini_jeu_input_finale', 
            on_change=soumettre_correction,
            disabled=not can_submit_game
        )
        
        if st.session_state.messages:
            st.sidebar.markdown("---")
            st.sidebar.subheader("Historique des Actions")
            for msg in reversed(st.session_state.messages[-5:]):
                st.sidebar.text(msg)
                
    else:
        # Fin de la matrice
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
