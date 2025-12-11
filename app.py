import streamlit as st
import numpy as np
import random

# --- Configuration de la page ---
st.set_page_config(page_title="Matrix Repair", page_icon="🧩", layout="centered")

# --- Styles CSS personnalisés ---
st.markdown("""
    <style>
    .matrix-cell {
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        padding: 20px;
        border-radius: 10px;
        margin: 5px;
        color: white;
    }
    .locked {
        background-color: #e74c3c;
        border: 2px dashed #c0392b;
        cursor: pointer;
    }
    .unlocked {
        background-color: #2ecc71;
        border: 2px solid #27ae60;
        color: white;
    }
    .stButton button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# --- Initialisation de l'état (Session State) ---
if 'matrix_size' not in st.session_state:
    st.session_state.matrix_size = 3  # Grille 3x3

if 'target_matrix' not in st.session_state:
    # La matrice finale (C) remplie de nombres aléatoires
    st.session_state.target_matrix = np.random.randint(1, 99, size=(3, 3))

if 'unlocked_mask' not in st.session_state:
    # Masque booléen : False = Verrouillé, True = Déverrouillé
    st.session_state.unlocked_mask = np.full((3, 3), False)

if 'current_active_cell' not in st.session_state:
    # Quelle case le joueur essaie-t-il de réparer ? (None ou (row, col))
    st.session_state.current_active_cell = None

if 'mini_game_state' not in st.session_state:
    # Stockage temporaire pour les jeux (ex: mot du pendu, score RPS)
    st.session_state.mini_game_state = {}

# --- Fonctions des Mini-Jeux ---

def reset_mini_game():
    st.session_state.mini_game_state = {}

def win_cell():
    r, c = st.session_state.current_active_cell
    st.session_state.unlocked_mask[r, c] = True
    st.session_state.current_active_cell = None
    reset_mini_game()
    st.balloons()
    st.rerun()

# 1. JEU : Pierre-Papier-Ciseaux
def game_rps():
    st.subheader("👊 ✋ ✌️ Duel : Pierre-Papier-Ciseaux")
    st.info("Battez l'ordinateur pour réparer ce secteur de la matrice.")
    
    choices = ["Pierre", "Papier", "Ciseaux"]
    
    col1, col2, col3 = st.columns(3)
    user_choice = None
    
    if col1.button("👊 Pierre"): user_choice = "Pierre"
    if col2.button("✋ Papier"): user_choice = "Papier"
    if col3.button("✌️ Ciseaux"): user_choice = "Ciseaux"

    if user_choice:
        bot_choice = random.choice(choices)
        st.write(f"Vous: **{user_choice}** | Ordi: **{bot_choice}**")
        
        if user_choice == bot_choice:
            st.warning("Égalité ! Rejouez.")
        elif (user_choice == "Pierre" and bot_choice == "Ciseaux") or \
             (user_choice == "Papier" and bot_choice == "Pierre") or \
             (user_choice == "Ciseaux" and bot_choice == "Papier"):
            st.success("Gagné !")
            win_cell()
        else:
            st.error("Perdu ! Essayez encore.")

# 2. JEU : Le Pendu
def game_hangman():
    st.subheader("🔤 Le Pendu du Hacker")
    st.info("Trouvez le mot de passe pour déchiffrer la donnée.")
    
    words = ["PYTHON", "MATRIX", "DATA", "LOGIC", "CODE", "ROBOT", "STREAM"]
    
    # Init pendu
    if 'word' not in st.session_state.mini_game_state:
        st.session_state.mini_game_state['word'] = random.choice(words)
        st.session_state.mini_game_state['guesses'] = set()
        st.session_state.mini_game_state['errors'] = 0
    
    word = st.session_state.mini_game_state['word']
    guesses = st.session_state.mini_game_state['guesses']
    
    # Affichage du mot masqué
    display_word = " ".join([letter if letter in guesses else "_" for letter in word])
    st.markdown(f"## `{display_word}`")
    
    # Clavier virtuel
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    cols = st.columns(9)
    for i, letter in enumerate(alphabet):
        if letter not in guesses:
            if cols[i % 9].button(letter):
                st.session_state.mini_game_state['guesses'].add(letter)
                if letter not in word:
                    st.session_state.mini_game_state['errors'] += 1
                st.rerun()
    
    # Vérification victoire/défaite
    if set(word).issubset(guesses):
        st.success(f"Mot trouvé : {word}")
        win_cell()
    elif st.session_state.mini_game_state['errors'] >= 5:
        st.error(f"Trop d'erreurs ! Le mot était {word}. Réinitialisation...")
        reset_mini_game() # On recommence le jeu avec un nouveau mot
        st.rerun()
    else:
        st.write(f"Erreurs : {st.session_state.mini_game_state['errors']} / 5")

# 3. JEU : Logique Émoji (Algèbre Visuelle)
def game_visual_logic():
    st.subheader("🍎 Logique Visuelle")
    st.info("Déduisez la valeur du dernier symbole.")
    
    # Génération simple d'énigme
    if 'logic_vals' not in st.session_state.mini_game_state:
        val_a = random.randint(2, 10)
        val_b = random.randint(1, 5)
        st.session_state.mini_game_state['logic_vals'] = (val_a, val_b)
    
    val_a, val_b = st.session_state.mini_game_state['logic_vals']
    res_1 = val_a * 2
    res_2 = val_a + val_b
    final_res = val_b + val_a
    
    st.markdown(f"""
    1. 🍎 + 🍎 = **{res_1}**
    2. 🍎 + 🍌 = **{res_2}**
    3. 🍌 + 🍎 = **?**
    """)
    
    ans = st.number_input("Quelle est la valeur ?", step=1)
    
    if st.button("Valider"):
        if ans == final_res:
            st.success("Correct !")
            win_cell()
        else:
            st.error("Faux calcul. Réessayez.")

# 4. JEU : Quiz Géométrique
def game_geometry():
    st.subheader("📐 Géométrie Matrixienne")
    
    questions = [
        {"q": "Combien de côtés a un Hexagone ?", "a": 6},
        {"q": "Combien d'angles droits a un carré ?", "a": 4},
        {"q": "Somme des angles d'un triangle (degrés) ?", "a": 180},
        {"q": "Combien de faces a un cube ?", "a": 6}
    ]
    
    if 'geo_q' not in st.session_state.mini_game_state:
        st.session_state.mini_game_state['geo_q'] = random.choice(questions)
    
    q_data = st.session_state.mini_game_state['geo_q']
    
    st.write(f"**Question :** {q_data['q']}")
    user_ans = st.number_input("Votre réponse :", step=1)
    
    if st.button("Vérifier"):
        if user_ans == q_data['a']:
            st.success("Géométrie validée.")
            win_cell()
        else:
            st.error("Mauvaise réponse.")

# --- Dispatcher de Jeux ---
def play_mini_game(row, col):
    # On choisit le jeu en fonction de la position pour varier (cycle)
    game_index = (row * 3 + col) % 4
    
    st.markdown("---")
    col_left, col_right = st.columns([1, 3])
    
    with col_left:
        if st.button("🔙 Retour à la grille"):
            st.session_state.current_active_cell = None
            reset_mini_game()
            st.rerun()
            
    with col_right:
        if game_index == 0:
            game_rps()
        elif game_index == 1:
            game_hangman()
        elif game_index == 2:
            game_visual_logic()
        elif game_index == 3:
            game_geometry()

# --- Interface Principale ---

st.title("📟 Matrix Repair")
st.markdown("""
    **Votre mission :** La Matrice $C$ est corrompue. Les valeurs sont cachées derrière des firewalls.
    Cliquez sur une case verrouillée 🔒 et gagnez le mini-jeu pour révéler le nombre !
""")

# Affichage de la grille ou du jeu
if st.session_state.current_active_cell is None:
    # --- VUE GRILLE ---
    
    # Vérification si tout est gagné
    if np.all(st.session_state.unlocked_mask):
        st.success("🎉 FÉLICITATIONS ! LA MATRICE EST ENTIÈREMENT RÉPARÉE ! 🎉")
        if st.button("Générer une nouvelle Matrice"):
            st.session_state.target_matrix = np.random.randint(1, 99, size=(3, 3))
            st.session_state.unlocked_mask = np.full((3, 3), False)
            st.rerun()
    
    # Affichage grille
    for r in range(3):
        cols = st.columns(3)
        for c in range(3):
            is_unlocked = st.session_state.unlocked_mask[r, c]
            value = st.session_state.target_matrix[r, c]
            
            with cols[c]:
                if is_unlocked:
                    st.markdown(f'<div class="matrix-cell unlocked">{value}</div>', unsafe_allow_html=True)
                else:
                    # Bouton pour lancer le jeu
                    if st.button("🔒 Locked", key=f"btn_{r}_{c}"):
                        st.session_state.current_active_cell = (r, c)
                        reset_mini_game()
                        st.rerun()

else:
    # --- VUE MINI-JEU ---
    r, c = st.session_state.current_active_cell
    st.markdown(f"### Réparation du Secteur [{r}, {c}]")
    play_mini_game(r, c)
