import trueskill as ts
import pandas as pd
from collections import defaultdict
import random
import matplotlib.pyplot as plt

def create_default_ratings(players):
    ratings = {}
    for player in players:
        ratings[player] = ts.Rating()
        ratings[player].name = player
    return ratings

def update_ratings(ratings, dataset):
    df = pd.read_csv(dataset)
    historical_ratings = defaultdict(list)
    for k,v in ratings.items():
        historical_ratings[k].append(v)

    for i in range(len(df)):
        p1_name = df.iloc[i]['P1'].lower()
        p2_name = df.iloc[i]['P2'].lower()
        p3_name = df.iloc[i]['P3'].lower()
        p4_name = df.iloc[i]['P4'].lower()
        p1 = ratings[p1_name]
        p2 = ratings[p2_name]
        p3 = ratings[p3_name]
        p4 = ratings[p4_name]
        team1 = [p1, p2]
        team2 = [p3, p4]
        rank1 = int(df.iloc[i]['Team1'])
        rank2 = int(df.iloc[i]['Team2'])

        team1_ranks, team2_ranks = ts.rate([team1, team2], ranks=[rank1, rank2])
        historical_ratings[p1_name].append(team1_ranks[0])
        historical_ratings[p2_name].append(team1_ranks[1])
        historical_ratings[p3_name].append(team2_ranks[0])
        historical_ratings[p4_name].append(team2_ranks[1])

        ratings[p1_name] = team1_ranks[0]
        ratings[p2_name] = team1_ranks[1]
        ratings[p3_name] = team2_ranks[0]
        ratings[p4_name] = team2_ranks[1]

    return ratings, historical_ratings

def rank_players(ratings):
    ordered = sorted(ratings.items(), key=lambda x: ts.expose(x[1]), reverse=True)
    result = []
    for rank in ordered:
        player, rating = rank
        result.append((player, rating, ts.expose(rating)))
    return result

def get_probability_of_draw(first_pair, second_pair, ratings):
    team1 = [ratings[x] for x in first_pair]
    team2 = [ratings[x] for x in second_pair]
    return ts.quality([team1, team2])

def _get_best_pairing_for_player(first_player, all_players, ratings):
    best_pairs = None
    lowest = 1
    for second_player in (set(all_players) - set([first_player])):
        for third_player in (set(all_players) - set([first_player, second_player])):
            for fourth_player in (set(all_players) - set([first_player, second_player, third_player])):
                first_pair = (first_player, second_player)
                second_pair = (third_player, fourth_player)
                p_draw = get_probability_of_draw(first_pair, second_pair, ratings)
                if p_draw < lowest:
                    best_pairs = ((first_pair, second_pair))
    return best_pairs

def matchmake(all_players, ratings):
    matches = []
    random.shuffle(all_players)
    #randomly shuffle all_players
    while len(all_players) >= 4:
        first_player = list(all_players)[0]
        match = _get_best_pairing_for_player(first_player, all_players, ratings)
        matches.append(match)
        for pair in match:
            all_players = set(all_players) - set(pair)
    return matches

def plot_historical_rankings(historical_ratings):
    fig = plt.figure(figsize=(10,5))
    ax = plt.subplot(111)
    for player, history in historical_ratings.items():
        rating_values = [ts.expose(x) for x in history]
        ax.plot(range(len(rating_values)), rating_values, label=player, marker='x')
    ax.grid()
    ax.set_xlabel("# Games")
    ax.set_ylabel("Rank")
    ax.set_title("Ranking over time")
    # Some fancy stuff to put the legend outside the plot
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
