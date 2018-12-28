"""
mate_game.py

A game of Mate.

Constants:
CREDITS: The credits for Mate. (str)
RULES: The rules of Mate. (str)

Classes:
Mate: A game of mate. (game.Game)
"""


import random

import t_games.dice as dice
import t_games.game as game
import t_games.player as player


CREDITS = """
Game Design: Craig "Ichabod" O'Brien
Game Programming: Craig "Ichabod" O'Brien
"""

RULES = """
Mate is a dice game using special dice that have Chess pieces as sides. Each
player has five dice which are rolled at the beginning of the game, and set in
a row opposite the other player's dice. Each 'piece' has a different point
value, and a differnt way to capture:

    * Queen: Queens can capture any opposing piece and are worth 5 points.
    * Rooks: Rooks can capture any opposing piece in the same or an adjacent
      column, and they are worth 3 points.
    * Bishops: Bishops can capture any opposing piece in an adjacent column,
      and they are worth 2 points.
    * Knights: Knights can capture any opposing piece two or three columns away
      from them, and they are worth 2 points.
    * Pawns: Pawns can capture the other piece in their column, and they are
      worth one point.

Players alternate turns. On their turn a play choses the column of one of their
own pieces (the attacker) and the column of an opponent's piece (the captured
piece). If the entry is valid, the player scores points equal to the opponent's
piece, and both dice are rerolled.

The first player to 64 points wins the game. If the score is tied at 64 or
higher, two more turns are played.
"""


class Mate(game.Game):
    """
    A game of Mate. (game.Game)

    Attributes:
    dice: The dice for each player, keyed by player name. (dict of str: dice.Pool)
    turns_left: The number of turns left after a winning tie. (int)

    Methods:
    dice_line: Show a player's dice with their columns. (str)
    get_moves: Determine the valid moves for a given player. (self)

    Overridden Methods:
    __str__
    game_over
    player_action
    set_up
    """

    aliases = {'t': 'take', 'x': 'take', 'takes': 'take'}
    attacks = {'Pawn': (0,), 'Knight': (-3, -2, 2, 3), 'Bishop': (-1, 1),
        'Rook': (-1, 0, 1), 'Queen': tuple(range(-5, 6))}
    categories = ['Dice Games']
    name = 'Mate'
    sides = ('Pawn', 'Pawn', 'Knight', 'Bishop', 'Rook', 'Queen')
    piece_aliases = {'p': 'pawn', 'n': 'knight', 'k': 'knight', 'b': 'bishop', 'r': 'rook', 'q': 'queen'}
    points = {'Pawn': 1, 'Knight': 2, 'Bishop': 2, 'Rook': 3, 'Queen': 5}

    def __str__(self):
        """Human readable text representation. (str)"""
        if self.players[self.player_index] == self.human:
            bot = self.players[1 - self.player_index]
        else:
            bot = self.players[self.player_index]
        lines = ['']
        lines.append('{}: {}'.format(bot.name, self.scores[bot.name]))
        lines.append(self.dice_line(self.dice[bot.name]))
        lines.append('-' * 53)
        lines.append(self.dice_line(self.dice[self.human.name]))
        lines.append('{}: {}'.format(self.human.name, self.scores[self.human.name]))
        return '\n'.join(lines)

    def dice_line(self, pool):
        """
        Show a player's dice with their columns. (str)

        Parameters:
        pool: The dice to show. (dice.Pool)
        """
        text = ['{}: {:<8}'.format(column, die.value) for column, die in enumerate(pool)]
        return ''.join(text)

    def default(self, text):
        """
        Handle unrecognized commands. (bool)

        Parameters:
        text: The raw text input by the user. (str)
        """
        words = text.replace('the', '').replace('teh', '').split()
        if len(words) == 2:
            return self.do_take('{} {}'.format(*words))
        else:
            self.players[self.player_index].error('I do not understand the move {!r}.'.format(text))
            return False

    def do_take(self, arguments):
        """
        Take an opponent's piece. (takes, t, x)

        This can be done as 'take defender with attacker', or as 'attacker takes
        defender'. Attacker and defender can be column names or piece names. If you use
        piece names that are ambiguous, you will be asked to clarify which columns
        those pieces are in.
        """
        # Get the players
        attacker = self.players[self.player_index]
        defender = self.players[1 - self.player_index]
        # Clean the arguments.
        words = [word for word in arguments.split() if word not in ('with', 'w', 'w/', 'the', 'teh', 'a')]
        arguments = ' '.join(words)
        # Parse out the two pieces
        try:
            target_piece, attack_piece = arguments.split()
        except ValueError:
            attacker.error('Invalid arguments to the take command: {!r}.'.format(arguments))
            return True
        # Identify the two pieces
        attack_indexes = self.piece_indexes(attack_piece, self.dice[attacker.name].values)
        if not attack_indexes:
            attacker.error('Invalid attack piece specification: {!r}'.format(attack_piece))
            return True
        target_indexes = self.piece_indexes(target_piece, self.dice[defender.name].values)
        if not target_indexes:
            attacker.error('Invalid target piece specification: {!r}'.format(target_piece))
            return True
        # Confirm valid move.
        moves = self.get_moves(attacker)
        possible = [move for move in moves if move[0] in attack_indexes and move[1] in target_indexes]
        if not possible:
            attacker.error('There is no legal move matching {!r}.'.format(arguments))
            return True
        # Narrow the move as needed.
        if len(possible) > 1:
            valid_attackers = set([move[0] for move in possible])
            if len(valid_attackers) > 1:
                query = 'Which {} did you mean to attack with? '.format(attack_piece)
                narrow = attacker.ask_int(query, valid = valid_attackers, cmd = False)
                possible = [move for move in possible if move[0] == narrow]
            if len(possible) > 1:
                valid_targets = set([move[1] for move in possible])
                query = 'Which {} did you mean to target? '.format(target_piece)
                narrow = attacker.ask_int(query, valid = valid_targets, cmd = False)
                possible = [move for move in possible if move[1] == narrow]
        # Score the move.
        attack_index, target_index = possible[0]
        self.scores[attacker.name] += self.points[self.dice[defender.name].values[target_index]]
        # Reroll the dice.
        self.dice[attacker.name].roll(attack_index)
        self.dice[defender.name].roll(target_index)

    def game_over(self):
        """Check for the end of the game. (bool)"""
        if self.players[self.player_index] == self.human:
            bot = self.players[1 - self.player_index]
        else:
            bot = self.players[self.player_index]
        bot_score = self.scores[bot.name]
        human_score = self.scores[self.human.name]
        if bot_score == human_score and bot_score >= 64:
            self.turns_left = 2
            return False
        elif bot_score < 64 and human_score < 64:
            return False
        elif bot_score > human_score:
            self.human.tell('You lose, {} to {}. :('.format(human_score, bot_score))
            self.win_loss_draw = [0, 1, 0]
        else:
            self.human.tell('You win! {} to {}!'.format(human_score, bot_score))
            self.win_loss_draw = [1, 0, 0]
        return True

    def get_moves(self, player):
        """
        Determine the valid moves for a given player. (self)

        Parameters:
        player: The current player. (player.Player)
        """
        valid = []
        targets = range(5)
        for attacker in range(5):
            for attack in self.attacks[self.dice[player.name].values[attacker]]:
                if attacker + attack in targets:
                    valid.append([attacker, attacker + attack])
        return valid

    def handle_options(self):
        """Handle the option settings for the game. (None)"""
        self.players = [self.human, MateDefendBot(taken_names = [self.human.name])]

    def piece_indexes(self, piece, values):
        """
        Determine where a user specified piece could be. (list of int)

        Parameters:
        piece: The user's piece specification. (str)
        values: The values of the appropriate dice. (list of str)
        """
        if piece.isdigit():
            return [int(piece)]
        else:
            name = self.piece_aliases.get(piece.lower(), piece.lower())
            return [index for index, value in enumerate(values) if value.lower() == name]

    def player_action(self, player):
        """
        Handle a player's turn or other player actions. (bool)

        Parameters:
        player: The player whose turn it is. (Player)
        """
        player.tell(self)
        # Get the player's move.
        move = player.ask('\nWhat is your move? ')
        words = move.lower().split()
        # Handle the alternate syntax.
        if words[1] in ('take', 'takes', 't', 'x'):
            words = words[2:] + words[:1]
            return self.do_take(' '.join(words))
        elif words[0] in ('the', 'teh') and words[2] in ('take', 'takes', 't', 'x'):
            words = words[3:] + words[:2]
            return self.do_take(' '.join(words))
        else:
            return self.handle_cmd(move)

    def set_up(self):
        """Set up the game. (None)"""
        for player in self.players:
            player.game = self
        self.dice = {}
        for player in self.players:
            self.dice[player.name] = dice.Pool([self.sides for die in range(5)])


class MateBot(player.Bot):
    """
    A bot player for the game of Mate. (player.Bot)

    The base MateBot just plays randomly.

    Methods:
    choose_attacker: Choose the column to attack with. (int)
    choose_target: Choose the column to attack. (int)

    Overridden Methods:
    ask_int
    """

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question being asked of the player. (str)
        """
        if prompt == '\nWhat is your move? ':
            attacker = self.choose_attacker()
            moves = self.game.get_moves(self)
            valid_targets = [move[1] for move in moves if move[0] == attacker]
            target = self.choose_target(valid_targets)
            return 'take {} {}'.format(target, attacker)
        else:
            raise BotError('Unexpected question asked of {}: {!r}.'.format(self.__class__.name, prompt))

    def choose_attacker(self):
        """Choose the column to attack with. (int)"""
        self.attacker = random.randrange(5)
        return self.attacker

    def choose_target(self, valid):
        """
        Choose the column to attack. (int)

        Parameters:
        valid: The columns that can be attacked. (list of int)
        """
        return random.choice(valid)


class MateAttackBot(MateBot):
    """
    A bot that goes after the biggest target. (MateBot)

    Overridden Methods:
    choose_attacker
    choose_target
    """

    def choose_attacker(self):
        """Choose the column to attack with. (int)"""
        valued_moves = self.value_moves()
        valued_moves.sort(reverse = True)
        max_valued = [move for value, move in valued_moves if value == valued_moves[0][0]]
        self.target, self.attacker = max_valued[0]
        return self.attacker

    def choose_target(self, valid):
        """
        Choose the column to attack. (int)

        Parameters:
        valid: The columns that can be attacked. (list of int)
        """
        return self.target

    def value_moves(self):
        moves = self.game.get_moves(self)
        moves = [(target, attacker) for attacker, target in moves]
        human_values = self.game.dice[self.game.human.name].values
        my_values = self.game.dice[self.name].values
        pieces = [(human_values[target], my_values[attacker]) for target, attacker in moves]
        values = [(self.game.points[target], self.game.points[attacker]) for target, attacker in pieces]
        return list(zip(values, moves))


class MateDefendBot(MateAttackBot):
    """
    A bot that removes it's biggest piece. (MateAttackBot)

    Overridden Methods:
    value_moves
    """

    def value_moves(self):
        """Determine a value for each possible move. (list of tuple)"""
        attacker_moves = super(MateDefendBot, self).value_moves()
        valued_moves = [((points[1], points[0]), move) for points, move in attacker_moves]
        return valued_moves
