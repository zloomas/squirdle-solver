from random import choice
from game import SquirdleGame


def pseudo_median(lst):
    if len(set(lst)) == 1:
        upper_ix = lower_ix = 0
    else:
        upper_ix = len(lst) // 2
        if len(lst) % 2 == 0:
            lower_ix = upper_ix - 1
        else:
            lower_ix = upper_ix
    return lst[lower_ix], lst[upper_ix]


class SquirdleSolver:
    def __init__(self, secret_mon=None):
        self.game = SquirdleGame(secret_mon)
        self.possible_pokemon = self.game.pokedex
        self.current_guess = None
        self.current_guess_attr = None
        self.feedback = None
        self._find_best_picks()

    def _update_gen_feedback(self):
        change = self.feedback[0]
        gen = int(self.current_guess_attr[0])
        updated = self.possible_pokemon.copy()
        if change == '=':
            updated = {key: val for key, val in updated.items() if int(val[0]) == gen}
        elif change == '+':
            updated = {key: val for key, val in updated.items() if int(val[0]) > gen}
        elif change == '-':
            updated = {key: val for key, val in updated.items() if int(val[0]) < gen}
        else:
            raise ValueError(f"cannot update generation feedback {change}")

        self.possible_pokemon = updated

    def _update_type1_feedback(self):
        change = self.feedback[1]
        type1 = self.current_guess_attr[1]
        updated = self.possible_pokemon.copy()
        if change == '=':
            updated = {key: val for key, val in updated.items() if val[1] == type1}
        elif change == '<>':
            updated = {key: val for key, val in updated.items() if val[2] == type1}
        elif change == 'x':
            updated = {key: val for key, val in updated.items() if val[1] != type1}
        else:
            raise ValueError(f"cannot update type 1 feedback {change}")

        self.possible_pokemon = updated

    def _update_type2_feedback(self):
        change = self.feedback[2]
        type2 = self.current_guess_attr[2]
        updated = self.possible_pokemon.copy()
        if change == '=':
            updated = {key: val for key, val in updated.items() if val[2] == type2}
        elif change == '<>':
            updated = {key: val for key, val in updated.items() if val[1] == type2}
        elif change == 'x':
            updated = {key: val for key, val in updated.items() if val[2] != type2}
        else:
            raise ValueError(f"cannot update type 2 feedback {change}")

        self.possible_pokemon = updated

    def _update_height_feedback(self):
        change = self.feedback[3]
        height = float(self.current_guess_attr[3])
        updated = self.possible_pokemon.copy()
        if change == '=':
            updated = {key: val for key, val in updated.items() if float(val[3]) == height}
        elif change == '+':
            updated = {key: val for key, val in updated.items() if float(val[3]) > height}
        elif change == '-':
            updated = {key: val for key, val in updated.items() if float(val[3]) < height}
        else:
            raise ValueError(f"cannot update height feedback {change}")

        self.possible_pokemon = updated

    def _update_weight_feedback(self):
        change = self.feedback[4]
        weight = float(self.current_guess_attr[4])
        updated = self.possible_pokemon.copy()
        if change == '=':
            updated = {key: val for key, val in updated.items() if float(val[4]) == weight}
        elif change == '+':
            updated = {key: val for key, val in updated.items() if float(val[4]) > weight}
        elif change == '-':
            updated = {key: val for key, val in updated.items() if float(val[4]) < weight}
        else:
            raise ValueError(f"cannot update weight feedback {change}")

        self.possible_pokemon = updated

    def _update_possible(self):
        if not self.feedback or not self.current_guess_attr:
            return

        self._update_gen_feedback()
        self._update_type1_feedback()
        self._update_type2_feedback()
        self._update_height_feedback()
        self._update_weight_feedback()

    def _update_references(self):
        self._update_possible()

        self.gen_list = []
        self.height_list = []
        self.weight_list = []

        type1_dict = dict()
        type2_dict = dict()

        for pokemon, stats in self.possible_pokemon.items():

            self.gen_list.append(int(stats[0]))
            self.height_list.append(float(stats[3]))
            self.weight_list.append(float(stats[4]))

            t1 = stats[1]
            t2 = stats[2]

            if t1 not in type1_dict:
                type1_dict[t1] = 1
            else:
                type1_dict[t1] += 1

            if t2 not in type2_dict:
                type2_dict[t2] = 1
            else:
                type2_dict[t2] += 1

        self.gen_list.sort()
        self.height_list.sort()
        self.weight_list.sort()

        self.type1_freq = [(key, val) for key, val in type1_dict.items()]
        self.type1_freq.sort(key=lambda x: x[-1], reverse=True)
        self.type2_freq = [(key, val) for key, val in type2_dict.items()]
        self.type2_freq.sort(key=lambda x: x[-1], reverse=True)

    def _find_best_picks(self):
        # update possible pokemon
        self._update_references()

        # start by trying to eliminate generations
        gen_guess = pseudo_median(self.gen_list)
        if self.gen_list.count(gen_guess[0]) > self.gen_list.count(gen_guess[1]):
            gen_guess = gen_guess[0]
        else:
            gen_guess = gen_guess[1]

        best_picks = {key: val for key, val in self.possible_pokemon.items() if int(val[0]) == gen_guess}

        # try to pick most frequent component type available among this generation's pokemon
        primary_ix = 0
        secondary_ix = 0
        best_type = []
        while not len(best_type):
            type1_guess = self.type1_freq[primary_ix][0]
            type2_guess = self.type2_freq[secondary_ix][0]
            best_type = [key for key, val in best_picks.items() if val[1] == type1_guess and val[2] == type2_guess]

            if secondary_ix < len(self.type2_freq)-1:
                secondary_ix += 1
            elif primary_ix < len(self.type1_freq)-1:
                secondary_ix = 0
                primary_ix += 1
            else:
                break

        # if still no selection, type is not more informative than generation...somehow
        # make sure to not clobber existing best picks
        if len(best_type):
            best_picks = {key: val for key, val in best_picks.items() if key in best_type}

        best_height = []
        temp_height_list = self.height_list.copy()
        while not len(best_height) and len(temp_height_list):
            height_guess = pseudo_median(temp_height_list)
            best_height = [key for key, val in best_picks.items() if float(val[3]) in height_guess]
            temp_height_list = list(filter(lambda x: x not in height_guess, temp_height_list))

        if len(best_height):
            best_picks = {key: val for key, val in best_picks.items() if key in best_height}

        best_weight = []
        temp_weight_list = self.weight_list.copy()
        while not len(best_weight) and len(temp_weight_list):
            weight_guess = pseudo_median(temp_weight_list)
            best_weight = [key for key, val in best_picks.items() if float(val[4]) in weight_guess]
            temp_weight_list = list(filter(lambda x: x not in weight_guess, temp_weight_list))

        if len(best_weight):
            best_picks = {key: val for key, val in best_picks.items() if key in best_weight}

        self.best_picks = list(best_picks.keys())

    def auto_guess(self):
        while self.game.guess_ix < 9:
            self.current_guess = choice(self.best_picks)
            self.current_guess_attr = self.possible_pokemon[self.current_guess]
            self.feedback = self.game.check_guess(self.current_guess)
            if self.game.win_status:
                print(f"found {self.current_guess} on guess {self.game.guess_ix} using best picks")
                break
            self._find_best_picks()

        return self.current_guess, self.game.guess_ix, self.game.already_guessed

    def total_random_guess(self):
        while not self.game.win_status:
            self.current_guess = choice(sorted(self.possible_pokemon))
            self.game.check_guess(self.current_guess)
            self.possible_pokemon.pop(self.current_guess)
        print(f"found {self.current_guess} on guess {self.game.guess_ix} using total random guesses")

        return self.current_guess, self.game.guess_ix, self.game.already_guessed

    def informed_random_guess(self):
        while not self.game.win_status:
            self.current_guess = choice(sorted(self.possible_pokemon))
            self.current_guess_attr = self.possible_pokemon[self.current_guess]
            self.feedback = self.game.check_guess(self.current_guess)
            self._update_possible()
        print(f"found {self.current_guess} on guess {self.game.guess_ix} using informed random guesses")
        return self.current_guess, self.game.guess_ix, self.game.already_guessed

    def seed_auto_guess(self, seed_mon=None):
        if seed_mon in self.possible_pokemon:
            self.current_guess = seed_mon
            self.current_guess_attr = self.possible_pokemon[self.current_guess]
            self.feedback = self.game.check_guess(self.current_guess)
            self._find_best_picks()
        if self.game.win_status:
            print(f"found {self.current_guess} on guess {self.game.guess_ix} using seeded best picks")
            return
        return self.auto_guess()


if __name__ == '__main__':
    play_state = "y"
    while play_state == 'y':
        game = SquirdleSolver()
        game.auto_guess()
        rando_game = SquirdleSolver()
        rando_game.total_random_guess()
        better_rando_game = SquirdleSolver()
        better_rando_game.informed_random_guess()
        seeded_game = SquirdleSolver()
        seeded_game.seed_auto_guess("bulbasaur")
        play_state = input("Play again? [y/n] ").lower()
