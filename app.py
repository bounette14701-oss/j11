import streamlit as st
import numpy as np
import random

# --- Configuration ---
st.set_page_config(page_title="Matrix Repair - Fast Mode", page_icon="⚡", layout="centered")

# --- CSS ---
st.markdown("""
    <style>
    .matrix-val {
        font-size: 30px;
        font-weight: bold;
        text-align: center;
        padding: 15px;
        background-color: #2ecc71;
        border: 2px solid #27ae60;
        border-radius: 8px;
        color: white;
    }
    .locked-row-btn {
        width: 100%;
        background-color: #e74c3c;
        color: white;
        font-weight: bold;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
    }
    .stButton button {
        width: 100%;
        font-size: 18px;
        height: 60px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Données ---
FIXED_MATRIX = np.array([
    [1, 6],
    [9, 14],
    [7, 4],
    [3, 8],
    [7, 15],
    [4, 5],
    [12, 5]
])

NUM_ROWS = len(FIXED_MATRIX)

# --- Session State ---
if 'unlocked_rows' not in st.session_state:
    # Tableau de booléens : une valeur par LIGNE
    st.session_state.unlocked_rows = [False] * NUM_ROWS

if 'active_row_index' not in st.session_state:
    st.session_state.active_row_index = None

if 'mini_game_state' not in st.session_state:
    st.session_state.mini_game_state = {}

# --- Logique de Victoire ---
def reset_game_state():
    st.session_state.mini_game_state = {}

def win_row():
    idx = st.session_state.active_row_index
    st.session_state.unlocked_rows[idx] = True
    st.session_state.active_row_index = None
    reset_game_state()
    st.balloons()
    st.rerun()

# --- LES JEUX ---

def game_rps():
    st.info("Duel rapide : Battez l'ordinateur.")
    col1, col2, col3 = st.columns(3)
    
    u = None
    if col1.button("👊"): u = "P"
    if col2.button("✋"): u = "F"
    if col3.button("✌️"): u = "C"
    
    if u:
        bot = random.choice(["P", "F", "C"])
        mapping = {"P": "Pierre", "F": "Papier", "C": "Ciseaux"}
        st.write(f"Ordi joue : {mapping[bot]}")
        
        # Victoire si : P>C, F>P, C>F
        if (u == "P" and bot == "C") or (u == "F" and bot == "P") or (u == "C" and bot == "F"):
            st.success("Gagné !")
            win_row()
        elif u == bot:
            st.warning("Égalité, réessayez !")
        else:
            st.error("Perdu !")

def game_hangman(target_word):
    st.info(f"Devinez le mot ({len(target_word)} lettres).")
    
    if 'word' not in st.session_state.mini_game_state:
        st.session_state.mini_game_state['word'] = target_word
        st.session_state.mini_game_state['guesses'] = set()
        st.session_state.mini_game_state['errors'] = 0
        
    word = st.session_state.mini_game_state['word']
    guesses = st.session_state.mini_game_state['guesses']
    
    # Affichage
    display = " ".join([l if l in guesses else "_" for l in word])
    st.markdown(f"## {display}")
    
    # Clavier
    alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    cols = st.columns(9)
    for i, char in enumerate(alpha):
        if char not in guesses:
            if cols[i%9].button(char):
                st.session_state.mini_game_state['guesses'].add(char)
                if char not in word:
                    st.session_state.mini_game_state['errors'] += 1
                st.rerun()
                
    # Check Fin
    if set(word).issubset(guesses):
        st.success(f"Mot : {word}")
        win_row()
    elif st.session_state.mini_game_state['errors'] >= 6:
        st.error("Perdu ! Recommencez.")
        reset_game_state()
        st.rerun()

def game_math_simple():
    st.info("Calcul mental rapide.")
    if 'math_q' not in st.session_state.mini_game_state:
        a, b = random.randint(5, 15), random.randint(5, 15)
        st.session_state.mini_game_state['math_q'] = (a, b)
        
    a, b = st.session_state.mini_game_state['math_q']
    ans = st.number_input(f"{a} x {b} = ?", step=1)
    if st.button("Valider"):
        if ans == (a * b):
            win_row()
        else:
            st.error("Faux.")

def game_guess_symbol():
    st.info("Logique : 🔼 = 3, ⏹️ = 4. Combien vaut 🔼 + ⏹️ x 2 ?")
    ans = st.number_input("Réponse", step=1)
    if st.button("Valider la logique"):
        # 3 + (4 * 2) = 11
        if ans == 11:
            win_row()
        else:
            st.error("Non. Priorité des opérations !")

# --- ROUTEUR DE JEU ---
def launch_level(row_index):
    st.markdown(f"### 🛡️ Sécurité Ligne {row_index + 1}")
    
    col_l, col_r = st.columns([1, 4])
    with col_l:
        if st.button("🔙"):
            st.session_state.active_row_index = None
            reset_game_state()
            st.rerun()

    with col_r:
        # SCÉNARIO DES NIVEAUX
        if row_index == 0:
            st.subheader("Niveau 1 : Réflexes")
            game_rps()
            
        elif row_index == 1:
            st.subheader("Niveau 2 : Décryptage")
            # Mot spécifique demandé
            game_hangman("SILENCE")
            
        elif row_index == 2:
            st.subheader("Niveau 3 : Arithmétique")
            game_math_simple()
            
        elif row_index == 3:
            st.subheader("Niveau 4 : Code Source")
            # Mot différent
            game_hangman("MATRIX")
            
        elif row_index == 4:
            st.subheader("Niveau 5 : Symboles")
            game_guess_symbol()
            
        elif row_index == 5:
            st.subheader("Niveau 6 : Langage")
            # Encore un mot différent
            game_hangman("PYTHON")
            
        elif row_index == 6:
            st.subheader("Niveau 7 : Boss Final")
            game_rps() # Ou un autre jeu

# --- INTERFACE PRINCIPALE ---

st.title("⚡ Matrix Repair : Fast Track")
st.write("Déverrouillez chaque ligne complète en réussissant le défi associé.")

if st.session_state.active_row_index is None:
    
    # Vérif Victoire Totale
    if all(st.session_state.unlocked_rows):
        st.success("🏆 SYSTÈME ENTIÈREMENT RESTAURÉ !")
        st.balloons()
        if st.button("Reset"):
            st.session_state.unlocked_rows = [False] * NUM_ROWS
            st.rerun()

    # Affichage Grille Ligne par Ligne
    for r in range(NUM_ROWS):
        is_open = st.session_state.unlocked_rows[r]
        val1, val2 = FIXED_MATRIX[r]
        
        if is_open:
            # Ligne ouverte : on affiche les deux nombres
            c1, c2 = st.columns(2)
            c1.markdown(f'<div class="matrix-val">{val1}</div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="matrix-val">{val2}</div>', unsafe_allow_html=True)
        else:
            # Ligne fermée : un gros bouton
            if st.button(f"🔒 DÉVERROUILLER LIGNE {r+1} (Défi requis)", key=f"row_{r}"):
                st.session_state.active_row_index = r
                reset_game_state()
                st.rerun()
        
        st.write("") # Petit espace entre les lignes

else:
    # Mode Jeu
    launch_level(st.session_state.active_row_index)
