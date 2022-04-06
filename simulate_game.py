import csv
from game import SquirdleGame
from auto_game import SquirdleSolver


def play_n_auto_games(secret_mon=None, n=0):
    performance = [None for _ in range(n)]
    for ix in range(n):
        solver = SquirdleSolver(secret_mon)
        performance[ix] = solver.auto_guess()
    return performance


def play_n_seeded_games(secret_mon=None, seed_mon=None, n=0):
    performance = [None for _ in range(n)]
    for ix in range(n):
        solver = SquirdleSolver(secret_mon)
        performance[ix] = solver.seed_auto_guess(seed_mon)
    return performance


def play_n_random_games(secret_mon=None, n=0):
    performance = [None for _ in range(n)]
    for ix in range(n):
        solver = SquirdleSolver(secret_mon)
        performance[ix] = solver.total_random_guess()
    return performance


def play_n_informed_random_games(secret_mon=None, n=0):
    performance = [None for _ in range(n)]
    for ix in range(n):
        solver = SquirdleSolver(secret_mon)
        performance[ix] = solver.informed_random_guess()
    return performance


def auto_play_all_mons(n=0):
    pokemon = SquirdleGame().pokedex
    performance = dict()
    for target_mon in pokemon:
        performance[target_mon] = play_n_auto_games(target_mon, n)

    # list of tuples (target_mon, last_guess, num_guesses, game_id)
    game_to_write = []
    # list of tuples
    # (game_id, guess_ix, guess_mon, gen_feedback, type1_feedback, type2_feedback, height_feedback, weight_feedback)
    guess_to_write = []
    for target, games in performance.items():
        for ix, g in enumerate(games):
            game_id = f'{target}_{str(ix).zfill(3)}'
            game_to_write.append((target, g[0], g[1], game_id))
            guess_ix = 0
            for guess_mon, feedback in g[2].items():
                guess_to_write.append([game_id, guess_ix, guess_mon] + feedback)
                guess_ix += 1

    with open(f'auto_play_games_{str(n).zfill(3)}.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['target_mon', 'last_guess', 'num_guesses', 'game_id'])
        writer.writerows(game_to_write)

    with open(f'auto_play_guesses_{str(n).zfill(3)}.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                'game_id',
                'guess_ix',
                'guess_mon',
                'gen_feedback',
                'type1_feedback',
                'type2_feedback',
                'height_feedback',
                'weight_feedback'
            ]
        )
        writer.writerows(guess_to_write)

    return performance


def seeded_auto_play_all_mons(n=0):
    pokemon = SquirdleGame().pokedex
    performance = dict()
    for target_mon in pokemon:
        for seed_mon in pokemon:
            performance[target_mon] = {seed_mon: play_n_seeded_games(target_mon, seed_mon, n)}

    return performance


def auto_play_all_mons(n=0):
    pokemon = SquirdleGame().pokedex
    auto_performance = dict()
    seeded_auto_performance = dict()
    random_performance = dict()
    informed_random_performance = dict()
    for target_mon in pokemon:
        auto_performance[target_mon] = play_n_auto_games(target_mon, n)
        random_performance[target_mon] = play_n_random_games(target_mon, n)
        informed_random_performance[target_mon] = play_n_informed_random_games(target_mon, n)
        for seed_mon in pokemon:
            seeded_auto_performance[target_mon] = {seed_mon: play_n_seeded_games(target_mon, seed_mon, n)}

    performance = {
        'auto': auto_performance,
        'seeded': seeded_auto_performance,
        'random': random_performance,
        'informed': informed_random_performance
    }

    return performance
