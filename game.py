import json
import random


class SquirdleGame:
    def __init__(self, secret_mon=None):
        # start with set of all possible pokemon
        with open('pokedex.json') as f:
            pokedex = json.load(f)

        # simplify names with non-standard characters
        pokedex["Nidoran-F"] = pokedex["Nidoran♀"]
        pokedex.pop("Nidoran♀")
        pokedex["Nidoran-M"] = pokedex["Nidoran♂"]
        pokedex.pop("Nidoran♂")
        pokedex["Flabebe"] = pokedex["Flabébé"]
        pokedex.pop("Flabébé")

        # reset pokemon names to all lower case for checking
        self._pokedex = {key.lower(): [str(i) for i in val] for key, val in pokedex.items()}

        # set target pokemon
        if not secret_mon:
            self._secret_mon = random.choice(sorted(self._pokedex))
            self._secret_mon_attr = self._pokedex[self._secret_mon]
        elif secret_mon.lower() not in self._pokedex:
            raise ValueError(f'{secret_mon} is not a valid pokemon, check spelling')
        else:
            self._secret_mon = secret_mon.lower()
            self._secret_mon_attr = self._pokedex[self._secret_mon]

        # initialize game tracking attributes
        self._guess_ix = 0
        self._win_status = False
        self._already_guessed = dict()

    def _check_guess(self, guess_mon):
        if guess_mon == self._secret_mon:
            self._win_status = True
        else:
            guess_feedback = []
            guess_mon_attr = self._pokedex[guess_mon]

            # check generation
            if guess_mon_attr[0] < self._secret_mon_attr[0]:
                guess_feedback.append('+')
            elif guess_mon_attr[0] > self._secret_mon_attr[0]:
                guess_feedback.append('-')
            else:
                guess_feedback.append('=')

            # check type 1
            if guess_mon_attr[1] == self._secret_mon_attr[1]:
                guess_feedback.append('=')
            elif guess_mon_attr[1] == self._secret_mon_attr[2]:
                guess_feedback.append('<>')
            else:
                guess_feedback.append('x')

            # check type 2
            if guess_mon_attr[2] == self._secret_mon_attr[2]:
                guess_feedback.append('=')
            elif guess_mon_attr[2] == self._secret_mon_attr[1]:
                guess_feedback.append('<>')
            else:
                guess_feedback.append('x')

            # check height
            if guess_mon_attr[3] < self._secret_mon_attr[3]:
                guess_feedback.append('+')
            elif guess_mon_attr[3] > self._secret_mon_attr[3]:
                guess_feedback.append('-')
            else:
                guess_feedback.append('=')

            # check weight
            if guess_mon_attr[4] < self._secret_mon_attr[4]:
                guess_feedback.append('+')
            elif guess_mon_attr[4] > self._secret_mon_attr[4]:
                guess_feedback.append('-')
            else:
                guess_feedback.append('=')

            self._already_guessed[guess_mon] = guess_feedback

        self._guess_ix += 1

    def _make_guess(self):
        guess = input("What's your guess? ")
        guess_lower = guess.lower()
        if guess_lower not in self._already_guessed:
            if guess_lower not in self._pokedex:
                print(f"I don't recognize {guess.title()}, try another pokémon")
            else:
                self._check_guess(guess)
        else:
            reminder = self._pokedex[guess]
            print(f"You've already guessed {guess.title()}, here's a reminder of its stats")
            print(f"gen: {reminder[0]} | type1: {reminder[1]} | type2: {reminder[2]}")
            print(f"height: {reminder[3]} | weight: {reminder[4]}")
            print("Try another pokémon")

    def play(self):
        while self._guess_ix < 9:
            self._make_guess()
            if not self._win_status:
                print(" gen | type1 | type2 |   h   |   w   | Pokémon")
                for pokemon, stats in self._already_guessed.items():
                    print(f" {'   |   '.join(stats)}   | {pokemon.title()}")
            else:
                print(f'Congratulations! You guessed the secret pokémon in {self._guess_ix} turns')
                break

        if not self._win_status:
            print(f"The secret pokémon was {self._secret_mon}")
            print("Better luck next time!")


if __name__ == '__main__':
    play_state = "y"
    while play_state == 'y':
        game = SquirdleGame()
        game.play()
        play_state = input("Play again? [y/n] ").lower()
