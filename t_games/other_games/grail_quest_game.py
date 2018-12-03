"""
grail_quest_game.py

An Oregon Trail style game based on Monty Python and the Holy Grail.

4902  REM A = AMOUNT SPENT ON ANIMALS
4904  REM B = AMOUNT SPENT ON AMMUNITION
4906  REM B1 = ACTUAL RESPONSE TIME FOR INPUTING 'BANG'
4908  REM B2 = MAXIMUM RESPONSE TIME FOR INPUTING 'BANG'
4910  REM C = AMOUNT SPENT ON CLOTHING
4912  REM C1 = FLAG FOR INSUFFICIENT CLOTHING IN COLD WEATHER
4914  REM C$ = YES/NO RESPONSE TO QUESTIONS
4916  REM D1 = COUNTER IN GENERATING EVENTS
4918  REM D3 = TURN NUMBER FOR SETTING DATE
4920  REM D4 = CURRENT DATE
4922  REM E = CHOICE OF EATING
4924  REM F = AMOUNT SPENT ON FOOD
4926  REM F1 = FLAG FOR CLEARING SOUTH PASS
4928  REM F2 = FLAG FOR CLEARING BLUE MOUNTAINS
4930  REM F9 = FRACTION OF 2 WEEKS TRAVELED ON FINAL TURN
4932  REM K8 = FLAG FOR INJURY
4934  REM L1 = FLAG FOR BLIZZARD
4936  REM M = TOTAL MILEAGE WHOLE TRIP
4938  REM M1 = AMOUNT SPENT ON MISCELLANEOUS SUPPLIES
4940  REM M2 = TOTAL MILEAGE UP THROUGH PREVIOUS TURN
4942  REM M9 = FLAG FOR CLEARING SOUTH PASS IN SETTING MILEAGE
4944  REM P = AMOUNT SPENT ON ITEMS AT FORT
4946  REM R1 = RANDOM NUMBER IN CHOOSING EVENTS
4948  REM S4 = FLAG FOR ILLNESS
4950  REM S5 = 'HOSTILITY OF RIDERS' FACTOR
4952  REM T = CASH LEFT OVER AFTER INITIAL PURCHASES
4954  REM T1 = CHOICE OF TACTICS WHEN ATTACKED
4956  REM X = CHOICE OF ACTION FOR EACH TURN
4958  REM X1 = FLAG FOR FORT OPTION

Constants:
CREDITS: The credits for the game. (str)
FINAL_CREDITS: You know, the staff need time to clean the place. (str)
INITIAL_PURCHASES: The text shown before making the initial purchases. (str)
LLAMA_CREDITS: Ay yai yai yipee! (str)
MOOSE_CREDITS: Moose bits can be very serious. (str)
MOOSER_CREDITS: My sister was bitten by a moose once. (str)
RULES: The rules of the game. (str)
SACKED_CREDITS: It's hard to find good people these days. (str)
SACKER_CREDITS: But it's really easy to sack people. (str)
SACKEST_CREDITS: It's also pretty easy to make up new words. (str)

Classes:
GrailQuest: A game of Quest for the Grail. (game.Game)
"""


import datetime
import random

import t_games.game as game
import t_games.utility as utility


CREDITS = """
Original Program and Design: Don Rawitsch, Bill Heinemann, and
    Paul Dillenberger with the Minnesota Educational Computing Consortium.
Python Programming: Craig "Ichabod" O'Brien
Arthurian Content: Monty Python
"""

FINAL_CREDITS = """
You're one of those guys who stays in the theatre until the final credits
are completely done, aren't you?
"""

INITIAL_PURCHASES = """
You have 700 pieces of gold to spend on the following items:

    * Trusty steeds: You can spend 180 to 270 gold on your steeds. The more
      you spend, the faster you'll go, because you have better animals.
    * Coconuts: You can spend 20 to 30 gold on coconuts. Higher quality
      coconuts allow your steeds to travel faster, more dramatically, and in
      the correct idiom.
    * Spam: The more you have, the less chance there is of getting sick.
    * Arrows: 1 gold buys a sheaf of 50 arrows. You will need arrows for
      attacks by animals and bandits, and for hunting food.
    * Clothing: This is especially important for the cold weather you will
      face in the frozen land of Nador.
    * Miscellaneous Supplies: This includes medicine and other things you
      will need for sickness and emergency repairs.
"""

LLAMA_CREDITS = """
Original Program and Design: Don Llamaitsch, Bill Heinellama, and
    Paul Llamaberger with 40 specially trained Ecaudorian mountain llamas.
Python Programming: Craig "Llamabod" O'Llama and 6 Venzeaulan blue llamas.
Arthurian Content: Llama Python and the Red Llama of Brixton.
"""

MOOSE_CREDITS = """
Original Program and Design: Don Rawik, Bill Heinemik, and Paul Dillenbik
    wik the Moose Educational Computing Consortium.
Python Programming: Craig "Moosabod" O'Brien
Arthurian Content: Moosey Python

No moose were harmed in the making of this game. A few of the programmers might
have gotten bit a little, though.
"""

MOOSER_CREDITS = """
Original Moose Coreography: Don Rawitsch, Bill Heinemann, and
    Paul Dillenberger with the Minnesota Educational Computing Consortium.
Moose Training: Craig "Ichabod" O'Brien
Moose Handlers: Monty Python
"""

RULES = """
This program simulates a quest over England from Camelot to the Castle
Aaaaarrrrrrggghhh. You team of five knights will complete the quest in five to
six months -- if you make it alive.

At the beginning you will need to provision for the trip. You can spend all of
your money at the start of the quest, or you can save some of your gold to
spend at castles along the way when you run low on supplies. However, items
cost more at the castles. You can also go hunting along the way to get more
food.

Whenever you have to use your trusty bow and arrow along the way you will see
the words 'type twang'. The faster you type 'twang' and hit the return key, the
better luck you'll have with your bow and arrow.

Signed,
Richard M. Nixon
"""

SACKED_CREDITS = """
We apologize for the problems with the credits. The people responsible have
been sacked.

And don't forget to try a loveli holiday in Sweden.
"""

SACKER_CREDITS = """
We apologize again for the problems with the credits. The people responsible
for sacking the people who have just been sacked, have just been sacked.
"""

SACKEST_CREDITS = """
The programmers of the firm hired to continue the credits after the other
people had be sacked, wish it to be known that they have just been sacked.

The credits have been completed in an entirely different style at great
expense and at the last minute.
"""


class GrailQuest(game.Game):
    """
    A game of Quest for the Grail. (game.Game)

    Note: the film starts in 932 AD

    Class Attributes:
    credits_order: The various credits texts in the order to show them. (list of str)

    Attributes:
    arrows: The number of arrows left. (int)
    clothes: The quality of the clothing. (int)
    coconuts: The quality of the coconuts. (int)
    credits_index: The index of the next credits text to show. (int)
    gold: How much money the player has left. (int)
    mileage: The total miles travelled. (int)
    miscellaneous: The quality of the miscellaneous goods. (int)
    spam: The amount of spam left. (int)
    steeds: The quality of the steeds. (int)

    Overridden Methods:
    do_credits
    set_up
    """

    aka = ['I seek the Holy Grail!', 'qftg']
    aliases = {'castle': 'stop', 's': 'stop'}
    categories = ['Adventure Games']
    diseases = ['measles', 'dysentery', 'typhoid', 'cholera', 'spamitis']
    credits = CREDITS
    credits_order = [CREDITS, MOOSE_CREDITS, SACKED_CREDITS, SACKER_CREDITS, MOOSER_CREDITS,
        SACKEST_CREDITS, LLAMA_CREDITS, FINAL_CREDITS]
    forts = ['Castle of Camelot', 'Swamp Castle', 'Castle Anthrax', 'Spam Castle', 'Catapult Castle']
    name = 'Quest for the Grail'

    def do_credits(self):
        """
        Show the credits for the game.
        """
        try:
            print(self.credits_order[self.credits_index].rstrip())
            self.credits_index += 1
            return True
        except IndexError:
            print("Sorry, sir. The movie's over. You'll have to leave.")
            self.force_end = 'loss'
            return False

    def do_stop(self):
        """
        Stop at a castle to buy things. (s, castle)
        """
        if not self.fort_option:
            self.human.tell('The castle you thought you could get to turned out to only be a model.')
            return True
        else:
            self.human.tell('\nWelcome to {}!'.format(self.castles))
            modifier = random.random() / 2 + 0.5
            self.purchases(modifier)
            self.mileage -= 45
            return False

    def purchases(self, modifier = None):
        """Make purchases. (None)"""
        if modifier is None:
            self.human.tell(INITIAL_PURCHASES)
            modifier = 1
            # Purchase steeds.
            query = 'How much would you like to spend on steeds? '
            self.steeds = self.human.ask_int(query, min = 180, max = 270, cmd = False)
            self.gold -= self.steeds
        # Purchase coconuts.
        query = 'How much would you like to spend on coconuts? '
        new_coconuts = self.human.ask_int(query, min = 20, max = 30, cmd = False)
        self.gold -= new_coconuts
        self.coconuts += int(new_coconuts * modifier)
        # Purchase spam.
        query = 'How much would you like to spend on spam? '
        new_spam = self.human.ask_int(query, min = 0, max = self.gold, cmd = False)
        self.gold -= new_spam
        self.spam += int(new_spam * modifier)
        # Purchase arrows.
        query = 'How much would you like to spend on arrows? '
        new_arrows = self.human.ask_int(query, min = 0, max = self.gold, cmd = False)
        self.gold -= new_arrows
        self.arrows += int(new_arrows * modifier * 50)
        # Purchase clothing.
        query = 'How much would you like to spend on clothing? '
        new_clothing = self.human.ask_int(query, min = 0, max = self.gold, cmd = False)
        self.gold -= new_clothing
        self.clothing += int(new_clothing * modifier)
        # Purchase miscellaneous supplies.
        query = 'How much would you like to spend on miscellaneous supplies? '
        new_miscellaneous = self.human.ask_int(query, min = 0, max = self.gold, cmd = False)
        self.gold -= new_miscellaneous
        self.miscellaneous = int(new_miscellaneous * modifier)
        # Inform the player of the balance.
        self.human.tell('After all of your purchases, you have {} pieces of gold left.'.format(self.gold))

    def player_action(self, player):
        """
        Handle a player's action during a turn. (bool)

        Parameters:
        player: The player whose turn it is. (player.Player)
        """
        # Check for initial purchases.
        if not self.turns:
            self.purchases()
        # Update the date.
        self.human.tell('\n{}'.format(self.date).replace(' 0', ' '))
        # Update the user.
        if self.spam < 12:
            self.human.tell('You better do some hunting or buy food soon!')
        if self.coconuts < 11:
            self.human.tell('Your steeds have just about beaten those coconuts to death.')
        if self.fort_option:
            self.human.tell('You can see a castle in the distance.')
        self.show_status()
        # Check for medical issues.
        if self.illness and self.injury:
            bill = 40
        elif self.illness or self.injury:
            bill = 20
        if bill:
            warnings.append("The apothecary's bill is {} gold.".format(bill))
            self.injury = False
            self.illness = False
        if warnings:
            self.human.tell('', '\n'.join(warnings))
        if bill > self.gold:
            if self.illness:
                self.death = 'illness'
            else:
                self.death = 'injury'
            return False
        else:
            self.gold -= bill
        # Get the player's action.
        action = self.human.ask('\nWhat would you like to do? ')
        go = self.handle_cmd(action)
        if not go and not self.force_end:
            self.fort_option = not self.fort_option

    def set_up(self):
        """Set up the game. (None)"""
        self.credits_index = 0
        # Set purchasables.
        self.arrows = 0
        self.clothes = 0
        self.coconuts = 0
        self.miscellaneous = 0
        self.spam = 0
        self.steeds = 0
        # Set tracking variables.
        self.date = datetime.date(932, 4, 12)
        self.fortnight = datetime.timedelta(days = 14)
        self.fort_option = True
        self.fort_index = 0
        self.gold = 700
        self.mileage = 0
        self.illness = False
        self.injury = False
        self.death = ''
        self.felt_better = False

    def show_status(self):
        """Show the current consumables. (None)"""
        self.human.tell('\nToday is {}.'.format(self.date))
        self.human.tell('\nYou have travelled {} miles.'.format(self.mileage))
        self.human.tell('You have:')
        self.human.tell('{} cans of spam,'.format(self.spam))
        self.human.tell('{} arrows,'.format(self.arrows))
        self.human.tell('{} gold pieces worth of clothing,'.format(self.clothing))
        self.human.tell('{} gold pieces worth of miscellaneous supplies,'.format(self.miscellaneous))
        self.human.tell('{} coconuts, and'.format(self.coconuts))
        self.huamn.tell('{} pieces of gold.'.format(self.gold))
