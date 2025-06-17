import random
from collections import deque, defaultdict
from prettytable import PrettyTable

# Define deck and orders
deck = [
    r + s for s in ['♠', '♥', '♦', '♣']
    for r in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
]

rank_order = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
              '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}

trump_suit = '♠'  # Spades
n = 0

def get_suit(card):
    return card[-1]

def get_value(card):
    return rank_order[card[:-1]]

def card_greater(c1, c2, lead_suit):
    s1, s2 = get_suit(c1), get_suit(c2)
    v1, v2 = get_value(c1), get_value(c2)
    if s1 == trump_suit and s2 != trump_suit:
        return True
    if s1 != trump_suit and s2 == trump_suit:
        return False
    if s1 == s2:
        return v1 > v2
    if s1 == lead_suit and s2 != lead_suit:
        return True
    return False

def group_hand(hand):
    grouped = defaultdict(list)
    for card in sorted(hand, key=get_value):
        grouped[get_suit(card)].append(card)
    return grouped

def display_user_hand(grouped_hand):
    idx = 0
    index_map = {}
    for suit in ['♠', '♥', '♦', '♣']:
        if grouped_hand[suit]:
            print(f"\n{suit} suit:")
            for card in grouped_hand[suit]:
                print(f"{idx}: {card}", end='  ')
                index_map[idx] = card
                idx += 1
    print()
    return index_map

def computer_play(lead_suit, prev_cards, hand, memory):
    same_suit_cards = [card for card in hand if get_suit(card) == lead_suit] if lead_suit else []
    trump_cards = [card for card in hand if get_suit(card) == trump_suit]
    other_cards = [card for card in hand if get_suit(card) != trump_suit and get_suit(card) != lead_suit]

    current_winner = prev_cards[0][1] if prev_cards else None
    for _, card in prev_cards[1:]:
        if card_greater(card, current_winner, lead_suit):
            current_winner = card

    if lead_suit and same_suit_cards:
        higher_cards = [c for c in same_suit_cards if not current_winner or card_greater(c, current_winner, lead_suit)]
        play = min(higher_cards, key=get_value) if higher_cards else min(same_suit_cards, key=get_value)
    elif trump_cards:
        higher_trumps = [c for c in trump_cards if not current_winner or card_greater(c, current_winner, lead_suit)]
        play = min(higher_trumps, key=get_value) if higher_trumps else min(trump_cards, key=get_value)
    else:
        play = min(other_cards, key=get_value) if other_cards else min(hand, key=get_value)

    hand.remove(play)
    memory['played'].append(play)
    return play

def rotate_to_winner(winner):
    while player_order[0] != winner:
        player_order.rotate(-1)

round_scores = []
scores = {name: 0.0 for name in ['You', 'Comp1', 'Comp2', 'Comp3']}
bids = {}

for round_no in range(1, 3):
    print(f"\n--- Round {round_no} ---")
    round_score = {name: 0 for name in scores}

    random.shuffle(deck)
    comp1 = deck[:13]
    comp2 = deck[13:26]
    comp3 = deck[26:39]
    user_hand = deck[39:]

    hands = {'You': user_hand, 'Comp1': comp1, 'Comp2': comp2, 'Comp3': comp3}
    ai_memory = {'Comp1': {'played': []}, 'Comp2': {'played': []}, 'Comp3': {'played': []}}

    player_order = deque(['You', 'Comp1', 'Comp2', 'Comp3'])
    player_order.rotate(n)

    grouped_hand = group_hand(user_hand)
    index_map = display_user_hand(grouped_hand)

    for player in player_order:
        if player == 'You':
            while True:
                try:
                    bid = int(input("Enter your bid (1-13): "))
                    if 1 <= bid <= 13:
                        bids[player] = bid
                        break
                    else:
                        print("Bid must be between 1 and 13.")
                except ValueError:
                    print("Enter a valid number.")
        else:
            bids[player] = random.randint(1, 5)
            print(f"{player} bids: {bids[player]}")

    for _ in range(13):
        cards_played = []
        for player in player_order:
            if player == 'You':
                grouped_hand = group_hand(hands['You'])
                index_map = display_user_hand(grouped_hand)

                while True:
                    try:
                        idx = int(input("Choose a card index to play: "))
                        if idx in index_map:
                            selected_card = index_map[idx]
                            lead_suit = get_suit(cards_played[0][1]) if cards_played else None
                            if lead_suit:
                                if get_suit(selected_card) == lead_suit:
                                    highest_played = max([get_value(c) for _, c in cards_played if get_suit(c) == lead_suit], default=0)
                                    if get_value(selected_card) <= highest_played and any(get_value(c) > highest_played and get_suit(c) == lead_suit for c in hands['You']):
                                        print("You must play a higher card of the same suit if you have it.")
                                        continue
                                    break
                                elif any(get_suit(c) == lead_suit for c in hands['You']):
                                    print(f"Must follow lead suit: {lead_suit}.")
                                    continue
                                elif get_suit(selected_card) == trump_suit or all(get_suit(c) not in [lead_suit, trump_suit] for c in hands['You']):
                                    break
                                else:
                                    print("Invalid card. Try again.")
                            else:
                                break
                        else:
                            print("Invalid index.")
                    except ValueError:
                        print("Invalid input.")
                card = selected_card
                hands['You'].remove(card)
                print(f"You played: {card}")
            else:
                card = computer_play(get_suit(cards_played[0][1]) if cards_played else None,
                                     cards_played,
                                     hands[player],
                                     ai_memory[player])
                print(f"{player} played: {card}")
            cards_played.append((player, card))

        lead_suit = get_suit(cards_played[0][1])
        winner, winning_card = cards_played[0]
        for player, card in cards_played[1:]:
            if card_greater(card, winning_card, lead_suit):
                winner, winning_card = player, card

        round_score[winner] += 1
        print(f"{winner} won the hand with {winning_card}\n")
        rotate_to_winner(winner)

    round_scores.append(round_score)
    print(f"\n--- Round {round_no} Scores ---")
    table = PrettyTable()
    table.field_names = ["Player", "Hands Won"]
    for player in round_score:
        bid = bids[player]
        won = round_score[player]
        score = float(f"{bid}.{(won - bid) % 10}") if won >= bid else -float(bid)
        table.add_row([player, score])
        scores[player] += score
    print(table)
    n -= 1

print("\n--- Final Scores ---")
table = PrettyTable()
table.field_names = ["Player", "Score"]
for player in scores:
    table.add_row([player, round(scores[player], 2)])
print(table)

winner = max(scores.items(), key=lambda x: x[1])[0]
print(f"\nWinner: {winner}")
