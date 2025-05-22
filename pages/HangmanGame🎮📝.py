import streamlit as st
from game import HangmanGame
from utils import word_dict
from utils2 import translate_text  # Import translation function
import os

# ✅ Ensure `selected_language` is initialized
if "selected_language" not in st.session_state:
    st.session_state.selected_language = "en"

# Load Custom CSS
def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# **Main Hangman Game Logic**
def hangman_game():
    st.markdown(f"<h3 style='text-align: center;'>{translate_text('🎯 Guess the Word & Win!')}</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 16px;'>{translate_text('Guess the word letter by letter. You have a limited number of incorrect guesses. Good luck! 🤞')}</p>", unsafe_allow_html=True)

    # **Check if game exists in session state**
    if "game" not in st.session_state:
        st.session_state.game = HangmanGame(word_dict)
        st.session_state.message = ""
        st.session_state.game_over = False

    game = st.session_state.game

    # **Display Game State with Image Beside the Subheading/Game**
    col1, col2 = st.columns([3, 1])  # Adjust column width
    with col1:
        st.write(f"**{translate_text('Hint')}:** {translate_text(game.hint)}")
        st.write(f"**{translate_text('Word')}:** " + " ".join(game.display_current_state()))
        st.write(f"**{translate_text('Incorrect guesses left')}:** {game.max_incorrect_guesses - game.incorrect_guesses}")
        st.write(f"**{translate_text('Guessed letters')}:** {', '.join(game.guessed_letters) if game.guessed_letters else translate_text('None')}")
        st.write(translate_text(st.session_state.message))

    with col2:
        st.image("img/hangman.jpg", width=180)  # Adjust the image size

    # **Generate a Unique Key for Text Input**
    unique_key = f"guess_input_{game.incorrect_guesses}"  # Unique key based on incorrect guesses

    # **User Input for Guessing**
    guess = st.text_input(translate_text("🔤 Enter your guess (a single letter):"), key=unique_key).lower()
    
    if st.button(translate_text("Submit Guess")):
        if len(guess) != 1 or not guess.isalpha():
            st.session_state.message = translate_text("⚠ Invalid input. Please enter a single letter.")
        elif guess in game.guessed_letters:
            st.session_state.message = translate_text(f"⚠ You already guessed '{guess}'. Try another letter.")
        else:
            if guess in game.word:
                st.session_state.message = translate_text(f"✅ Good guess! '{guess}' is in the word.")
                game.guessed_letters.add(guess)
                if game.is_game_won():
                    st.session_state.message = translate_text(f"🎉 Congratulations! You guessed the word: {game.word}")
                    st.session_state.game_over = True
            else:
                game.incorrect_guesses += 1
                game.guessed_letters.add(guess)
                st.session_state.message = translate_text(f"❌ Incorrect guess. '{guess}' is not in the word.")
                if game.is_game_lost():
                    st.session_state.message = translate_text(f"😢 You lost! The word was: {game.word}")
                    st.session_state.game_over = True

    if st.session_state.game_over:
        st.write(translate_text(st.session_state.message))
        if st.button(translate_text("🔄 Play Again")):
            st.session_state.game = HangmanGame(word_dict)
            st.session_state.message = ""
            st.session_state.game_over = False

# **Main Game Page**
def game():
    st.markdown(f"<h1 style='text-align: center;'>{translate_text('🎮 Play AI-Powered Hangman!')}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 18px;'>{translate_text('Can you guess the word before running out of chances? Test your vocabulary skills and have fun with AI-powered Hangman! 🚀')}</p>", unsafe_allow_html=True)
    st.write("---")
    
    # Start the Game
    hangman_game()

if __name__ == "__main__":
    game()
