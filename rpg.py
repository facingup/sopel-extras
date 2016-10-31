import sopel.module

from threading import Timer
import random

'''
RPG States
'''
RPG_REGISTER = 1
RPG_RUNNING = 2
RPG_OFF = 3

'''
game states
'''
IN_BATTLE = 1
ROAMING = 2

'''
Base class for character classes

All character classes must inherit from this class.
Sets defaults and standards, holds information about the character.
'''
class base_class():
    def __init__(self):
        self.name = name
        self.hp = 50
        self.mana = 0
        self.ac = 10

        self.load()

    '''
    class loader. Overload this function to customize the character
    '''
    def load(self):
        pass

    '''
    tryhit: see if this character is hit. Returns boolean, true if hit,
    false if not.
    DnD style, the attack roll is input
    Special character classes like thief override this, adding dodge
    TODO: Add attack type?
    '''
    def tryhit(self, attackroll):
        return attackroll >= self.ac


class figher_class(base_class):
    def load():
        self.hp = 60
        self.ac = 13

'''
Player class

Holds information about this player.
- who it is
- what class they are playing
- more?
'''
class player():
    def __init__(self, name):
        self.name = name
        self.char = None

'''
Map classes

The game's core is an n by m map that is being explored
This is implemented with an array of arrays. Each array element
is a MapCell class
'''
class Map():
    def __init__(self, n, m):
        self.grid = []
        self.n = n
        self.m = m
        # choose random start and end points
        start = (random.randint(0, n-1),
            random.randint(0, m-1))
        self.current_cell = start
        end = (random.randint(0, n-1),
            random.randint(0, m-1))
        while (start[0] == end[0] and start[1] == end[1]):
            end = (random.randint(0, n-1),
                random.randint(0, m-1))
        for i in range(0, n):
            self.grid.append([])
            for j in range(0, m):
                self.grid[i].append(MapCell(i, j))
        self.grid[start[0]][start[1]].start = True
        self.grid[end[0]][end[1]].end = True
        # Make random door. Check if the map is possible
        # repeat until the map is possible
        while not self.check_possible():
            self.make_random_door()

    '''
    make_random_door

    make a random door somewhere in the map.
    '''
    def make_random_door(self):
        # key on a cell, then choose a random wall
        # yes, the doors on a corner/wall cell have a higher probability
        # whatever.
        # deal with it.
        cell = (random.randint(0, self.n - 1),
                random.randint(0, self.m - 1))
        # 0 = north
        # 1 = east
        # 2 = south
        # 3 = west
        d = random.randint(0, 3)
        c = self.grid[cell[0]][cell[1]]
        if d == 0 and c.x - 1 >= 0:
            c.doorNorth = True
            self.grid[cell[0] - 1][cell[1]].doorSouth = True
        if d == 1 and c.y + 1 < self.m:
            c.doorEast = True
            self.grid[cell[0]][cell[1] + 1].doorWest = True
        if d == 2 and c.x + 1 < self.n:
            c.doorSouth = True
            self.grid[cell[0] + 1][cell[1]].doorNorth = True
        if d == 3 and c.y - 1 >= 0:
            c.doorWest = True
            self.grid[cell[0]][cell[1] - 1].doorEast = True

    '''
    Visit a cell, check neighbours.

    Mark neighbours as known, this cell as visited
    '''
    def visit_cell(self, x, y):
        self.grid[x][y].visited = True
        if self.grid[x][y].doorNorth:
            self.grid[x-1][y].known = True
        if self.grid[x][y].doorSouth:
            self.grid[x+1][y].known = True
        if self.grid[x][y].doorEast:
            self.grid[x][y+1].known = True
        if self.grid[x][y].doorWest:
            self.grid[x][y-1].known = True

    def get_current_cell(self):
        return self.grid[self.current_cell[0]][self.current_cell[1]]

    '''
    try move

    Try a move, don't move and print error on failure
    '''
    def try_move(self, bot, direction):
        d = direction.lower()
        c = self.get_current_cell()
        if d == 'south' and c.doorSouth:
            self.current_cell = (c.x + 1, c.y)
        elif d == 'north' and c.doorNorth:
            self.current_cell = (c.y - 1, c.y)
        elif d == 'east' and c.doorEast:
            self.current_cell = (c.x, c.y + 1)
        elif d == 'west' and c.doorWest:
            self.current_cell = (c.x, c.y - 1)
        else:
            bot.say("Can't move " + direction + ".")
        self.visit_cell(self.current_cell[0], self.current_cell[1])
        c = self.get_current_cell()
        bot.say(c.get_exits())

    '''
    check_possible - ensure map has path from start to finish

    Use a backtracking algorithm to make sure that there is a clear map
    from start to finish.
    '''
    def check_possible(self):
        # start from the start
        # add all possible moves, that have not been visited
        # pop the stack, add all possible moves...
        c = self.get_current_cell()
        seen = []
        todo = [c]
        success = False
        while len(todo) > 0 and not success:
            cur = todo.pop()
            seen.append(cur)
            if cur.end:
                success = True
                print seen
            if cur.doorNorth:
                t = (self.grid[cur.x-1][cur.y])
                if not t in seen and not t in todo:
                    todo.append(t)
            if cur.doorSouth:
                t = (self.grid[cur.x+1][cur.y])
                if not t in seen and not t in todo:
                    todo.append(t)
            if cur.doorEast:
                t = (self.grid[cur.x][cur.y+1])
                if not t in seen and not t in todo:
                    todo.append(t)
            if cur.doorWest:
                t = (self.grid[cur.x][cur.y-1])
                if not t in seen and not t in todo:
                    todo.append(t)
        return success

    '''
    print the map
    '''
    def print_map(self, bot):

        def mapline():
           s = "+"
           for _ in range(0, self.n):
                s+= "-"
           s += '+'
           return s

        line = mapline()
        bot.say(line)
        for row in self.grid:
            s = '|'
            for col in row:
                if (col.x == self.current_cell[0] and
                        col.y == self.current_cell[1]):
                    s += 'C'
                else:
                    s += col.get_icon()
            s += '|'
            bot.say(s)
        bot.say(line)

class MapCell():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.visitable = True
        self.visited = False
        self.start = False
        self.end = False
        self.known = False
        self.doorNorth = False
        self.doorEast = False
        self.doorSouth = False
        self.doorWest = False
        self.occupants = []
    def get_icon(self):
        if self.start:
            return 's'
        if self.end and self.visited:
            return 'e'
        if self.visited:
            return '.'
        if self.known:
            return '?'
        return ' '

    def get_exits(self):
        exits = []
        if self.doorNorth:
            exits.append('North')
        if self.doorEast:
            exits.append('East')
        if self.doorSouth:
            exits.append('South')
        if self.doorWest:
            exits.append('West')
        if len(exits) == 1:
            return 'You see an exit to the ' + ', '.join(exits) + '.'
        if len(exits) > 1:
            return 'You see exits to the ' + ', '.join(exits) + '.'

@sopel.module.commands('startrpg')
def startrpg(bot, trigger):
    if ((bot.memory.contains('rpgstate') and bot.memory['rpgstate'] == RPG_OFF)
            or not bot.memory.contains('rpgstate')):
        bot.memory['rpgstate'] = RPG_REGISTER
        # make a new player list
        bot.memory['players'] = {}
        # gs is game state
        bot.memory['gs'] = ROAMING
        # make an nxm grid. n and m are configurable (TODO)
        bot.memory['x'] = 10
        bot.memory['y'] = 10
        bot.memory['map'] = Map(10, 10)
        bot.say('RPG now starting! Type .register to register for this game!')
        # end registration after a timeout (in seconds)
        t = Timer(20, registration_end, args=[bot])
        t.start()
    else:
        # game is running... reply, or is that spammy?
        pass

def registration_end(bot):
    if len(bot.memory['players']) == 0:
        bot.say('No one registered. Good bye')
        bot.memory['rpgstate'] = RPG_OFF
    else:
        bot.say('Registration is now closed. Welcome, '
                + ', '.join(bot.memory['players'].keys()) + '.')
        bot.memory['rpgstate'] = RPG_RUNNING
        c = bot.memory['map'].get_current_cell()
        bot.memory['map'].visit_cell(c.x, c.y)
        bot.say(c.get_exits())

@sopel.module.commands('register')
def register(bot, trigger):
    if not bot.memory.contains('rpgstate')\
            or bot.memory['rpgstate'] != RPG_REGISTER:
        return
    # see if they are already registered
    if trigger.nick not in bot.memory['players']:
        bot.memory['players'][trigger.nick] = None
        bot.say(trigger.nick + ' is now registered.')

'''
isrunning helper function

Tells us if the game is running.
'''
def isrunning(bot):
    if bot.memory.contains('rpgstate'):
        if bot.memory['rpgstate'] == RPG_RUNNING:
            return True
    return False

@sopel.module.commands('map')
def showmap(bot, trigger):
    if isrunning(bot):
        bot.memory['map'].print_map(bot)

@sopel.module.commands('bail')
def bail(bot, trigger):
    if isrunning(bot):
        if trigger.nick in bot.memory['players']:
            del bot.memory['players'][trigger.nick]
            if len(bot.memory['players']) == 0:
                bot.say('Everyone quit!')
                bot.memory['rpgstate'] == RPG_OFF

@sopel.module.commands('move')
def move(bot, trigger):
    if isrunning(bot) and bot.memory['gs'] == ROAMING:
        bot.memory['map'].try_move(bot, trigger.group(2))
    # check to see if there is enemies in this room.
    # if so, go into BATTLE status
    c = bot.memory['map'].get_current_cell()
    if len(c.occupants) > 0:
        bot.memory['gs'] = IN_BATTLE
    else:
        # if we escaped from a room, we may have to move from battle to roam
        bot.memory['gs'] = ROAMING
    # currently possible end state - you got to the end of the map, no
    # monsters to fight.
    # future, this might be possible if you can beat the end boss and leave
    # the room? Probably impossible in the future.
    if c.end and bot.memory['gs'] == ROAMING:
        bot.say('You win! The end!')
        bot.memory['rpgstate'] = RPG_OFF



@sopel.module.commands('info')
def info(bot, trigger):
    bot.say(bot.memory['map'].get_current_cell().get_exits())
