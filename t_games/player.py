"""
player.py

Base player classes for tgames.

!! reorganize this so the human stuff is in Human.

Copyright (C) 2018 by Craig O'Brien and the t_game contributors.
See the top level __init__.py file for details on the t_games license.

Classes:
BotError: An invalid play by a bot. (ValueError)
Player: The base player class. (object)
Bot: A computer player. (Player)
AlphaBetaBot: A robot player using alpha-beta pruning. (Bot)
Human: A human being, with stored data. (Player)
Tester: A preset test account. (Human)
"""


from __future__ import print_function

import os
import random
import re
import string

import t_games.utility as utility


try:
    input = raw_input
except NameError:
    pass


class BotError(ValueError):
    pass
    

class Player(object):
    """
    The base player class. (object)

    Attributes:
    game: The game the player is playing. (game.Game)
    name: The name of the player. (str)

    Methods:
    ask: Get information from the player. (str)
    ask_int: Get an integer response from the human. (int)
    ask_int_list: Get a multiple integer response from the human. (int)
    ask_valid: Get and validate responses from the user. (str)
    error: Warn the player about an invalid play. (None)
    clean_up: Do any necessary post-game processing. (None)
    set_up: Do any necessary pre-game processing. (None)
    store_results: Store a game result. (None)
    tell: Give information to the player. (None)

    Overridden Methods:
    __init__
    """

    int_re = re.compile('[, \t]?(-?\d+)')

    def __init__(self, name):
        """
        Save the player's name. (None)

        Parameters:
        name: The name of the player. (str)
        """
        self.name = name
        self.game = None
        self.held_inputs = []
        self.shortcuts = {}

    def __repr__(self):
        """Debugging text representation. (str)"""
        return '<{} {}>'.format(self.__class__.__name__, self.name)

    def __str__(self):
        """Human readable representation. (str)"""
        return self.name

    def ask(self, prompt):
        """
        Get information from the player. (str)

        Parameters:
        prompt: The question being asked of the player. (str)
        """
        if not self.held_inputs:
            answer = input(prompt).strip()
            if ';' in answer:
                self.held_inputs = [part.strip() for part in answer.split(';')]
        if self.held_inputs:
            answer = self.held_inputs.pop(0)
        first, space, rest = answer.partition(' ')
        first = self.shortcuts.get(first, first)
        return '{} {}'.format(first, rest).strip()

    def ask_int(self, prompt, low = None, high = None, valid = [], default = None, cmd = True):
        """
        Get an integer response from the human. (int)

        Parameters:
        prompt: The question asking for the interger. (str)
        low: The lowest acceptable value for the integer. (int or None)
        high: The highest acceptable value for the integer. (int or None)
        valid: The valid values for the integer. (container of int)
        default: The default choice. (int or None)
        cmd: A flag for returning commands for processing. (bool)
        """
        if cmd and self.game.force_end:
            return [x for x in valid + [low, high, default, 0] if x is not None][0]
        while True:
            response = self.ask(prompt).strip()
            if not response and default is not None:
                return default
            try:
                response = int(response)
            except ValueError:
                if cmd:
                    break
                else:
                    self.error('Integers only please.')
            else:
                if low is not None and response < low:
                    self.error('That number is too low. The lowest valid response is {}.'.format(low))
                elif high is not None and response > high:
                    self.error('That number is too high. The highest valid response is {}'.format(high))
                elif valid and response not in valid:
                    self.error('{} is not a valid choice.'.format(response))
                    self.error('You must choose one of {}.'.format(', '.join([str(x) for x in valid])))
                else:
                    break
        return response

    def ask_int_list(self, prompt, low = None, high = None, valid = [], valid_lens = [], default = None,
        cmd = True):
        """
        Get a multiple integer response from the human. (int)

        Parameters:
        prompt: The question asking for the interger. (str)
        low: The lowest acceptable value for the integer. (list or None)
        high: The highest acceptable value for the integer. (laist or None)
        valid: The valid values for the integer. (list of int)
        valid_lens: The valid numbers of values. (list of int)
        default: The default choice. (list or None)
        cmd: A flag for returning commands for processing. (bool)
        """
        if cmd and self.game.force_end:
            return [x for x in valid + [[low], [high], default, [0]] if x is not None][0]
        while True:
            response = self.ask(prompt).strip()
            if not response and default is not None:
                return default
            elif not response and not cmd and (0 in valid_lens or not valid_lens):
                return []
            if self.int_re.match(response):
                response = [int(num) for num in self.int_re.findall(response)]
                if low is not None and min(response) < low:
                    self.error('{} is too low. The lowest valid response is {}.'.format(min(response), low))
                elif high is not None and max(response) > high:
                    highest = max(response)
                    self.error('{} is too high. The highest valid response is {}'.format(highest, high))
                elif valid:
                    for number in set(response):
                        if response.count(number) > valid.count(number):
                            self.error("You have more {}'s than allowed".format(number))
                            self.error("You must choose from:", ', '.join(valid))
                            break
                    else:
                        break
                elif valid_lens and len(response) not in valid_lens:
                    self.error('That is an invalid number of integers.')
                    if len(valid_lens) == 1:
                        plural = 's' if valid_lens[0] > 1 else ''
                        self.error('Please enter {} integer{}.'.format(str(valid_lens[0]), plural))
                    else:
                        message = 'Please enter {}, or {} integers.'
                        len_text = [str(x) for x in valid_lens[:-1]]
                        self.error(message.format(', '.join(len_text), valid_lens[-1]))
                else:
                    break
            else:
                if cmd:
                    break
                else: 
                    self.error('Please enter the requested integers.')
        return response

    def ask_valid(self, prompt, valid, default = '', lower = True):
        """
        Get and validate responses from the user. (str)

        Note that default must be in valid.

        Parameters:
        prompt: The question to ask the user. (str)
        valid: The valid responses from the user. (container of str)
        default: The default value for the response. (str)
        lower: A flag for case insensitive matching. (bool)
        """
        while True:
            # Get the response.
            response = self.ask(prompt)
            if lower:
                response = response.lower()
            # Check the response.
            if not response and default:
                response = default
            if response in valid:
                return response
            # Warn the user on invalid responses.
            self.error('That is not a valid response.')
            self.error('Please choose one of: {}.'.format(', '.join(valid)))

    def clean_up(self):
        """Do any necessary post-game processing. (None)"""
        pass

    def error(self, *args, **kwargs):
        """
        Warn the player about an invalid play. (None)

        Parameters:
        The parameters are as teh built-in print function.
        """
        print(*args, **kwargs)

    def set_up(self):
        """Do any necessary pre-game processing. (None)"""
        pass

    def store_results(self, game_name, result):
        """
        Store game results. (None)

        Parameters:
        game_name: The name of the game the result is from. (str)
        results: The results of playing the game. (list of int)
        """
        pass

    def tell(self, *args, **kwargs):
        """
        Give information to the player. (None)

        Parameters:
        The parameters are as per the built-in print function.
        """
        print(*args, **kwargs)


class Cyborg(Player):
    """
    A bot that is run by the human for testing. (Player)

    Overridden Methods:
    __init__
    """

    def __init__(self, taken_names = [], initial = ''):
        """
        Set the bot's name. (None)

        If initial is empty, the bot's name can start with any letter.

        Parameters:
        taken_names: Names already used by a player. (list of str)
        initial: The first letter of the bot's name. (str)
        """
        while True:
            if initial:
                self.name = random.choice(BOT_NAMES[initial].split('/'))
            else:
                self.name = random.choice(BOT_NAMES[random.choice(string.ascii_lowercase)].split('/'))
            if self.name not in taken_names:
                break
        self.held_inputs = []
        self.shortcuts = {}


class Bot(Cyborg):
    """
    A full computer player. (Player)

    Overridden Methods:
    error
    tell
    """

    def error(self, *args, **kwargs):
        """
        Stop play due to a bot malfunction. (None)

        Parameters:
        The parameters are the same as the built-in bot function.
        """
        kwargs['sep'] = kwargs.get('sep', ' ')
        kwargs['end'] = kwargs.get('end', '\n')
        text = kwargs['sep'].join([str(arg) for arg in args]) + kwargs['end']
        raise BotError(text.strip())

    def tell(self, *args, **kwargs):
        """
        Give information to the player. (None)

        Parameters:
        The parameters are as per the built-in print function.
        """
        kwargs['sep'] = kwargs.get('sep', ' ')
        kwargs['end'] = kwargs.get('end', '\n')
        text = kwargs['sep'].join([str(arg) for arg in args]) + kwargs['end']
        possessive = self.name + "'s"
        pairs = (('Your', possessive), ('your', possessive), ('You', self.name), ('you', self.name), 
            ('have', 'has'))
        for pronoun, name in pairs:
            text = text.replace(pronoun, name)
        del kwargs['sep']
        del kwargs['end']
        print(text, **kwargs)

class AlphaBetaBot(Bot):
    """
    A robot player using alpha-beta pruning. (Bot)

    The AlphaBetaBot assumes you have a board game, and the board has a get_moves
    method which returns all legal moves, a copy method which returns an 
    indepent copy of the board, and a check_win method that returns 'game on'
    until the game is over.

    Attributes:
    depth: The depth of the search. (int)
    fudge: A fudge factor to avoid early capitulation. (int or float)

    Methods:
    alpha_beta: Tree search with alpha-beta pruning. (tuple)
    eval_board: Evaluate the board. (int)

    Overridden Methods:
    __init__
    """

    def __init__(self, depth, fudge, taken_names = [], initial = ''):
        """
        Set up the bot. (None)

        Parameters:
        depth: The depth of the search. (int)
        fudge: A fudge factor to avoid early capitulation. (int or float)
        taken_names: Names already used by a player. (list of str)
        initial: The first letter of the bot's name. (str)
        """
        # parent initialization
        super(AlphaBetaBot, self).__init__(taken_names, initial)
        # attribute initialization
        self.depth = depth
        self.fudge = fudge

    def alpha_beta(self, board, depth, alpha, beta, max_player):
        """
        Tree search with alpha-beta pruning. (tuple)

        The return value is a tuple of the best move found and the estimated board
        value for that move.

        Parameters:
        board: The board position at this point in the tree. (ConnectFourBoard)
        depth: How many more iterations of the search there should be. (int)
        alpha: The best score for the maximizing player. (int)
        beta: The best score for the minimizing player. (int)
        max_player: Flag for evaluating the maximizing player. (int)
        """
        # get the correct player index ?? not used
        if max_player:
            player_index = self.game.players.index(self)
        else:
            player_index = 1 - self.game.players.index(self)
        # initialize loops
        best_move = None
        # check for terminal node
        if depth == 0 or board.check_win() != 'game on':
            #print()
            value = self.eval_board(board)
            fudge = self.fudge * (self.depth - depth)
            # ?? this is meant to prevent giving up in a forced win situation. Not sure it works.
            value -= fudge
            return None, value
        elif max_player:
            # maximize loop
            board_value = -utility.MAX_INT
            for move in board.get_moves():
                # evaluate the move
                clone = board.copy()
                clone.make_move(move)
                sub_move, move_value = self.alpha_beta(clone, depth - 1, alpha, beta, False)
                # check for better move
                if move_value > board_value:
                    board_value = move_value
                    best_move = move
                # adjust and check alpha
                alpha = max(alpha, board_value)
                if beta <= alpha:
                    break
        else:
            # minimize loop
            board_value = utility.MAX_INT
            for move in board.get_moves():
                # evaluate the move
                clone = board.copy()
                clone.make_move(move)
                sub_move, move_value = self.alpha_beta(clone, depth - 1, alpha, beta, True)
                # check for worse move
                if move_value < board_value:
                    board_value = move_value
                    best_move = move
                # adjust and check beta
                beta = min(beta, board_value)
                if beta <= alpha:
                    break
        # return best move found with board value
        return best_move, board_value

    def eval_board(self, board):
        """
        Evaluate the board. (int)

        Parameters:
        board: The board to evaluate. (board.GridBoard)
        """
        return NotImplemented


class Human(Player):
    """
    A human being, with stored data. (Player)

    Attributes:
    color: The player's favorite color. (str)
    folder_name: The local file with the player's data. (str)
    quest: The player's quest. (str)

    Overridden Methods:
    __init__
    store_results
    """

    def __init__(self):
        """Get a login from a human. (None)"""
        while True:
            # Get the user's name.
            self.name = input('What is your name? ')
            # Allow for single or multiple entry of quest and color.
            if ';' in self.name:
                self.name, self.quest, self.color = [word.strip() for word in self.name.split(';')]
            else:
                self.quest = input('What is your quest? ')
                self.color = input('What is your favorite color? ')
            # Check for previous log in.
            base_name = '{}-{}-{}'.format(self.name, self.quest, self.color).lower()
            self.folder_name = os.path.join(utility.LOC, base_name)
            if not os.path.exists(self.folder_name):
                new_player = input('I have not heard of you. Are you a new player? ')
                if new_player.lower() in utility.YES:
                    os.mkdir(self.folder_name)
                    with open(os.path.join(self.folder_name, 'results.txt'), 'w') as player_data:
                        player_data.write('')
                    with open(os.path.join(self.folder_name, 'shortcuts.txt'), 'w') as player_data:
                        player_data.write('')
                    break
                print()
            else:
                break
        self.load_results()
        self.load_shortcuts()
        self.held_inputs = []

    def load_results(self):
        """Load the player's history of play. (None)"""
        self.results = []
        with open(os.path.join(self.folder_name, 'results.txt')) as player_data:
            for line in player_data:
                results = line.strip().split(',')
                self.results.append(results[:1] + [int(x) for x in results[1:-1]] + results[-1:])

    def load_shortcuts(self):
        """Load the player's interface shortcuts. (None)"""
        self.shortcuts = {}
        with open(os.path.join(self.folder_name, 'shortcuts.txt')) as player_data:
            for line in player_data:
                shortcut, text = line.strip().split('\t')
                self.shortcuts[shortcut] = text

    def store_results(self, game_name, results):
        """
        Store game results. (None)

        Parameters:
        game_name: The name of the game the result is from. (str)
        results: The results of playing the game. (list of int)
        """
        # Store locally.
        self.results.append([game_name] + results)
        # Store in the player's file.
        results_text = ','.join([str(x) for x in results])
        with open(os.path.join(self.folder_name, 'results.txt'), 'a') as player_data:
            player_data.write('{},{}\n'.format(game_name, results_text))

    def store_shortcut(self, shortcut, text):
        """
        Store new shortcuts. (None)

        Parameters:
        shortcut: The word that is the short cut. (str)
        text: The text the shortcut expands into. (str)
        """
        # Store locally
        self.shortcuts[shortcut] = text
        # Store in the player's file.
        with open(os.path.join(self.folder_name, 'shortcuts.txt'), 'a') as player_data:
            player_data.write('{}\t{}\n'.format(shortcut, text))

class Tester(Human):
    """
    A preset test account. (Human)

    Overridden Methods:
    __init__
    """

    def __init__(self, name = 'Buckaroo', quest = 'testing', color = 'black'):
        """Auto setup a Human. (None)"""
        self.name = name
        self.quest = quest
        self.color = color
        base_name = '{}-{}-{}'.format(self.name, self.quest, self.color).lower()
        self.folder_name = os.path.join(utility.LOC, base_name)
        if not os.path.exists(self.folder_name):
            os.mkdir(self.folder_name)
            with open(os.path.join(self.folder_name, 'results.txt'), 'w') as player_data:
                player_data.write('')
        self.load_results()
        self.load_shortcuts()
        self.held_inputs = []


BOT_NAMES = {'a': 'Ash/Abby/Adam/Alan/Alice/Ada/Adele/Alonzo/Angus/Astro',
    'b': 'Bender/Barbara/Blue/Bella/Buckaroo/Beth/Bob/Bishop/Betty/Brooke',
    'c': 'Caitlyn/Calvin/Candice/Carl/Carol/Carsen/Cassandra/Cecilia/Chance/Craig',
    'd': 'Data/Deckard/Dahlia/Dana/Daphne/Damon/Debby/David/Darryl/Denise',
    'e': 'Edith/Eve/Ed/Elliot/Elizabeth/Edgar/Enzo/Emelia/Erin/Ernest',
    'f': 'Felicity/Futura/Fatima/Felix/Felipe/Finn/Fiona/Frances/Frank/Fletcher',
    'g': 'Gort/Guido/Geneva/Gia/Gerty/Gilberto/Grace/Gloria/Garry/Grover',
    'h': 'Hymie/Hobbes/Hiro/Homer/Hugo/Haladay/Harriet/Heidi/Hope/Haven',
    'i': 'Ida/Indira/Ines/Inga/Ivy/Ian/Igor/Isaac/Ichabod/Ivan',
    'j': 'Judith/Jade/Jane/Jodie/Julia/John/Jaque/Joshua/Johan/Jerome',
    'k': 'Kitt/Karen/Kay/Kelly/Kyoko/Kareem/Kurt/Kronos/Klaus/Kirk',
    'l': 'Lore/Lee/Lars/Leon/Laszlo/Limor/Laverne/Leelu/Lola/Lois',
    'm': 'Marvin/Mr. Roboto/MechaCraig/Maximillian/Mordecai/Maria/Mary Lou/Marlyn/Monique/Mika',
    'n': 'Nellodee/Nancy/Naomi/Norma/Natalie/Nathan/Ned/Nero/Nick/Nigel',
    'o': 'Otis/Ogden/Omar/Oscar/Otto/Olga/Olivia/Oksana/Octavia/Oriana',
    'p': 'Pris/Patience/Patty/Phoebe/Pru/Patrick/Phillip/Parker/Paul/Pavel',
    'q': 'Queenie/Quenby/Quiana/Quinn/Qadir/Qasim/Quincy/Quang/Quest',
    'r': 'Robby/Roy/Rachel/Risana/Rita/Rosie/River/Reiner/Rick/Rusty',
    's': 'Sam/Shroud/Santiago/Steve/Sonny/Sarina/Susan/Sylvia/Shirley/Sheba',
    't': 'Tabitha/Theresa/Tracy/Trinity/Tamala/Tanner/Tariq/Ted/Tyler/Tyrone',
    'u': 'Ulla/Uma/Ursula/Ursuline/Uta/Ulric/Umberto/Uriah/Usher/Urban',
    'v': 'Vincent/Valerie/Venus/Vivian/Vera/Veronica/Victor/Viggo/Vikram/Vladimir',
    'w': 'Wally/Wednesday/Wana/Wendy/Willow/Winnie/Waylon/Wayne/William/Wolfgang',
    'x': 'Xander/Xavier/Xena/Xhosa/Ximena/Xiang/Xaria/Xanthus/Xenon/Xerxes',
    'y': 'Yamina/Yasmin/Yoland/Yvette/Yadira/Yaakov/Yitzhak/Yves/Yannick/Yaron',
    'z': 'Zahara/Zelda/Zoe/Zuma/Zenaida/Zachary/Zafar/Zane/Zebulon/Zen'}