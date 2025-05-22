import random
import streamlit as st
from utils import word_dict  # Ensure utils.py contains the word_dict dictionary.
class HangmanGame:
    def __init__(self, word_dict, max_incorrect_guesses=6):
        self.word_dict = word_dict
        self.max_incorrect_guesses = max_incorrect_guesses
        self.word, self.hint = self.select_random_word_and_hint()
        self.guessed_letters = set()
        self.incorrect_guesses = 0

    def select_random_word_and_hint(self):
        word, hint = random.choice(list(self.word_dict.items()))
        return word.lower(), hint

    def display_current_state(self):
        return ''.join([letter if letter in self.guessed_letters else '_' for letter in self.word])

    def is_game_won(self):
        return all(letter in self.guessed_letters for letter in self.word)

    def is_game_lost(self):
        return self.incorrect_guesses >= self.max_incorrect_guesses
    
    

# Main Streamlit app
def main():
    st.title("🎮 Hangman Game with Streamlit")
    st.markdown(
        "Guess the word letter by letter. You have a limited number of incorrect guesses. Good luck!"
    )

    # Initialize game state in session_state
    if "game" not in st.session_state:
        st.session_state.game = HangmanGame(word_dict)
        st.session_state.message = ""
        st.session_state.game_over = False

    game = st.session_state.game

    if not st.session_state.game_over:
        # Display game information
        st.write(f"**Hint:** {game.hint}")
        st.write("**Word:** " + " ".join(game.display_current_state()))
        st.write(f"**Incorrect guesses left:** {game.max_incorrect_guesses - game.incorrect_guesses}")
        st.write(f"**Guessed letters:** {', '.join(game.guessed_letters) if game.guessed_letters else 'None'}")
        st.write(st.session_state.message)

        # Input for guessing
        guess = st.text_input("Enter your guess (a single letter):", key="guess_input").lower()

        if st.button("Submit Guess"):
            if len(guess) != 1 or not guess.isalpha():
                st.session_state.message = "⚠️ Invalid input. Please enter a single letter."
            elif guess in game.guessed_letters:
                st.session_state.message = f"⚠️ You already guessed '{guess}'. Try another letter."
            else:
                game.guessed_letters.add(guess)

                if guess in game.word:
                    st.session_state.message = f"✅ Good guess! '{guess}' is in the word."
                    if game.is_game_won():
                        st.session_state.message = f"🎉 Congratulations! You guessed the word: {game.word}"
                        st.session_state.game_over = True
                else:
                    game.incorrect_guesses += 1
                    st.session_state.message = f"❌ Incorrect guess. '{guess}' is not in the word."
                    if game.is_game_lost():
                        st.session_state.message = f"😢 You lost! The word was: {game.word}"
                        st.session_state.game_over = True
    else:
        # Game over state
        st.write(st.session_state.message)
        if st.button("Play Again"):
            # Reset the game state
            st.session_state.game = HangmanGame(word_dict)
            st.session_state.message = ""
            st.session_state.game_over = False


if __name__ == "__main__":
    main()
