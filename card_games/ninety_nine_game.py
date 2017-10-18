"""
ninety_nine_game.py

This is the accumulating game, not the trick taking game.

Constants:
CREDITS: The credits for Ninety-Nine. (str)
RULES: The rules of Ninety-Nine.

Classes:
NinetyNine: A game of Ninety-Nine. (game.Game)
Bot99: A bot for Ninety-Nine. (player.Bot)
"""


import random
import re

import tgames.cards as cards
import tgames.game as game
import tgames.player as player


CREDITS = """
Game Design: Traditional (Romani)
Game Programming: Craig "Ichabod" O'Brien
"""

RULES = """
Each turn you play a card, adding it's value to the running total. You must 
correctly state the new total when you play a card. For example, if the total 
to you is 81, and you wanted to play the five of diamonds, you would enter 
'5d 86' If you can't play a card without taking the total over 99, you must 
pass, and lose one of your three tokens. At that point the hands are redealt 
and the total is reset to zero. If you lose all of your tokens, you are out 
of the game. The last player with tokens wins.

Cards are face value with face cards being 10, with the following exceptions:
    A: 1 or 11
    4: 0
    10: -10 or 10
    K: 0

In addition, a 4 reverses the order of play and a 3 skips the next player's 
turn.

The tokens command will show you how many tokens each player has left.
"""


class NinetyNine(game.Game):
    """
    A game of Ninety-Nine. (game.Game)

    Attributes:
    card_values: The possible values for each rank. (dict of str: tuple)
    deck: The deck of cards for the game. (cards.Deck)
    hands: The players hands of cards, keyed by name. (dict of str:cards.Hand)
    reverse_rank: The rank that reverses the order of play. (str)
    skip_rank: The rank that skips over a player. (str)
    total: The current total rank count. (int)

    Methods:
    deal: Deal a new hand of cards. (None)
    do_pass: Pass the turn, lose a token. (bool)
    do_tokens: Show how many tokens are left. (bool)

    Overridden Methods:
    clean_up
    do_quit
    handle_options
    player_turn
    set_up
    """

    aka = ['99']
    aliases = {'p': 'pass'}
    credits = CREDITS
    name = 'Ninety-Nine'
    nn_re = re.compile('([1-9atjqk][cdhs]).*?(-?\d\d?)', re.I)
    rules = RULES

    def clean_up(self):
        """Clean up the game. (None)"""
        self.players.extend(self.out_of_the_game)
        self.out_of_the_game = []

    def deal(self):
        """Deal a new hand of cards. (None)"""
        for hand in self.hands.values():
            hand.discard()
        self.deck.shuffle()
        for card in range(3):
            for hand in self.hands.values():
                hand.draw()

    def do_pass(self, arguments):
        """
        Pass the turn and lose a token. (bool)

        Parameters:
        arguments: The ignored arguments to the command. (None)
        """
        player = self.players[self.player_index]
        self.scores[player.name] -= 1
        message = '{} loses a token. They now have {} tokens.'
        self.human.tell(message.format(player.name, self.scores[player.name]))
        if not self.scores[player.name]:
            for name, value in self.scores.items():
                if value < 1:
                    self.scores[name] = value - 1
            next_player = self.players[(self.player_index + 1) % len(self.players)]
            self.players.remove(player)
            self.out_of_the_game.append(player)
            self.player_index = self.players.index(next_player) - 1
            self.human.tell('{} is out of the game.'.format(player.name))
        self.deal()
        self.total = 0

    def do_tokens(self, arguments):
        """
        Show how many tokens are left. (bool)

        Parameters:
        arguments: The ignored arguments to the command. (None)
        """
        self.human.tell()
        for player in self.players:
            self.human.tell('{} has {} tokens left.'.format(player.name, self.scores[player.name]))
        return True

    def do_quit(self, arguments):
        """
        Quit the game, which counts as a loss. (bool)

        Overridden due to changing self.players over course of the game.

        Parameters:
        arguments: The modifiers to the quit. (str)
        """
        self.flags |= 4
        self.force_end = 'loss'
        self.win_loss_draw = [0, max(len(self.scores) - 1, 1), 0]
        if arguments.lower() in ('!', 'quit', 'q'):
            self.human.held_inputs = ['!']
        return False

    def game_over(self):
        """Check for the game being over. (bool)"""
        if len(self.players) == 1:
            human_score = self.scores[self.human.name]
            for score in self.scores.values():
                if score < human_score:
                    self.win_loss_draw[0] += 1
                elif score > human_score:
                    self.win_loss_draw[1] += 1
            return True
        else:
            return False

    def handle_options(self):
        """Handle the game options(None)"""
        # Set default options.
        self.card_values = {rank: (rank_index,) for rank_index, rank in enumerate(cards.Card.ranks)}
        self.card_values['A'] = (1, 11)
        self.card_values['4'] = (0,)
        self.card_values['9'] = (99,) # go to 99
        self.card_values['T'] = (-10, 10)
        self.card_values['J'] = (10,)
        self.card_values['Q'] = (10,)
        self.card_values['K'] = (0,)
        self.reverse_rank = '4'
        self.skip_rank = '3'
        self.players = [self.human]
        for bot in range(3):
            self.players.append(Bot99([player.name for player in self.players]))

    def player_turn(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        self.human.tell()
        hand = self.hands[player.name]
        player.tell('The total to you is {}.'.format(self.total))
        player.tell('Your hand is: {}'.format(hand))
        move = player.ask('What is your move? ')
        parsed = self.nn_re.search(move)
        if parsed:
            card, new_total = parsed.groups()
            card = card.upper()
            new_total = int(new_total)
            if card in hand.cards:
                values = self.card_values[card[0]]
                valid_add = (new_total < 100) and (new_total - self.total in values)
                if valid_add or (new_total == 99 and 99 in values): 
                    hand.discard(card)
                    self.total = new_total
                    message = '{} played the {}, the total is {}.'
                    self.human.tell(message.format(player.name, card, self.total))
                    if card[0] == self.reverse_rank:
                        self.players.reverse()
                        self.player_index = self.players.index(player)
                        self.human.tell('The order of play is reversed.')
                    if card[0] == self.skip_rank:
                        self.player_index = (self.player_index + 1) % len(self.players)
                        name = self.players[self.player_index].name
                        self.human.tell("{}'s turn is skipped.".format(name))
                    hand.draw()
                    return False
                else:
                    player.tell('Incorrect or invalid total provided.')
            else:
                player.tell('You do not have that card.')
        else:
            return self.handle_cmd(move)
        return True

    def set_up(self):
        """Set up the game. (None)"""
        random.shuffle(self.players)
        self.out_of_the_game = []
        # Hand out tokens.
        self.scores = {player.name: 3 for player in self.players}
        # Set up deck and hands.
        self.deck = cards.Deck()
        self.hands = {player.name: cards.Hand(self.deck) for player in self.players}
        # Deal three cards to each player.
        self.deal()
        # Set the tracking variables
        self.total = 0


class Bot99(player.Bot):
    """
    A bot for Ninety-Nine. (player.Bot)

    Overridden Methods:
    ask
    tell
    """

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The information to get from the player. (str)
        """
        hand = self.game.hands[self.name]
        total = self.game.total
        possibles = []
        for card in hand.cards:
            for value in self.game.card_values[card.rank]:
                if total + value < 100:
                    possibles.append((total + value, card))
                elif value == 99:
                    possibles.append((99, card))
        if possibles:
            possibles.sort()
            return '{1} {0}'.format(*possibles[-1])
        else:
            return 'pass'

    def tell(self, text):
        """
        Give information to the player. (None)

        Parameters:
        text: The inforamtion to give to the player. (str)
        """
        pass