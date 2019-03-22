
# coding: utf-8

# <div style="text-align:right">Peter Norvig<br>21 March 2018</div>
# 
# # `xkcd` Name Dominoes
# 
# The March 21, 2018 `xkcd` comic (#1970) was [Name Dominoes](https://xkcd.com/1970/): domino tiles laid out as if in a game, but the tiles contain names of famous people rather than numbers. 
# In [dominoes](https://en.wikipedia.org/wiki/Dominoes) each tile has two halves, and a tile can be legally placed only if  one half is adjacent to another tile half with the same number/name, and neither half is adjacent to a tile half with a different number/name. (Exception: the very first tile can be placed anywhere.) 
# 
# I will write a function to lay out tiles in a random, legal array.  First, the key data structures:
# 
# - **`Tile`**: a tile is a 2-element tuple of names, like `('TIM', 'COOK')`.
# The tile `('FRANK LLOYD', 'WRIGHT')` has a space in the first name.
# - **`Name`**: a name (first name or last name) is a string.
# - **`Board(width, height)`**: a `Board` represents
# a width × height array of squares, initially `empty`, but  when we put a tile on the board,
# the first name covers one location and the last name covers an adjacent location, e.g. `board[0, 0], board[0, 1] = ('TIM', 'COOK')`. Implemented as a subtype of `dict` that keeps track of `width` and `height`.
# - **`Location`**: a location is an `(x, y)` pair of coordinates for a square on the board.
# 
# Now I need a strategy to fill the board with tiles.  I will randomly place tiles one at a time, and to make things easier I will *not* consider removing a tile from the board and backtracking. Some more concepts and functions:
# 
# - **`frontier`**: I'll maintain a *frontier*, a set of locations that are adjacent to tiles on the board, and thus are candidates for placing new tiles.
# - **`dominoes(tiles)`**: makes a board and places tiles on it, one at a time, until no more can be placed. Chooses a random tile for the first tile, then repeatedly calls `try_one` to legally place an additional tile, stopping when either there is no `frontier` left (meaning no place to legally place a tile) or no `tiles` left to place.
# - **`try_one(tiles, board, frontier)`**: pop a location off the frontier, and try to find some tile that can legally put one of its halves there; when found, `put` the tile there, and remove it from `tiles`.
# - **`legal(name, loc, board)`**: a name can be placed if the location is empty, and there are no conflicts with any neighboring location.
# - **`neighbors(loc, board)`**: returns the (up to 4) neighbors of a location that are on the board.
# - **`put_tile(board, loc0, loc1, tile, frontier)`**: places a tile on the board across `loc0` and `loc1`; update the `frontier` to say that the just-covered locations are no longer in the frontier, but the empty neighbors of the tile are.
# - **`shuffle(items)`**: used to randomize lists; calls `random.shuffle` and returns the result.
# 
# # The Code

# In[8]:


import random

empty = None # An empty square

class Board(dict):
    "A mapping from location to name."
    def __init__(self, width, height): self.width, self.height = width, height
    def __missing__(self, loc): return empty

def dominoes(tiles, width=16, height=24):
    "Place as many tiles on board as possible (legally and randomly)."
    tiles    = shuffle(list(tiles))
    board    = Board(width, height)
    frontier = set()
    m        = min(width, height) // 2
    put_tile(board, (m, m), (m, m + 1), tiles.pop(), frontier) # Place first tile
    while tiles and frontier:
        try_one(tiles, board, frontier)
    return board
          
def try_one(tiles, board, frontier):
    "Pop a frontier location, and try to place a tile on that location."
    loc0 = frontier.pop()
    for tile in shuffle(tiles):
        for (name0, name1) in [tile, tile[::-1]]:
            if legal(name0, loc0, board):
                for loc1 in shuffle(neighbors(loc0, board)):
                    if legal(name1, loc1, board):
                        put_tile(board, loc0, loc1, (name0, name1), frontier)
                        tiles.remove(tile)
                        return tile
                        
def legal(name, loc, board):
    "Is it legal to place this name on this location on board?"
    return (board[loc] is empty and
            all(board[nbr] is empty or board[nbr] == name
                for nbr in neighbors(loc, board)))

def neighbors(loc, board):
    "Neighbors of this location on the board."
    x, y = loc
    return [(x+dx, y+dy) for (dx, dy) in ((0, 1), (1, 0), (0, -1), (-1, 0))
            if 0 <= x+dx < board.width and 0 <= y+dy < board.height]

def put_tile(board, loc0, loc1, tile, frontier): 
    "Place the tile across the two locations, and update frontier."
    board[loc0], board[loc1] = tile
    frontier -= {loc0, loc1}
    frontier |= {loc for loc in neighbors(loc0, board) + neighbors(loc1, board)
                 if board[loc] is empty}
                            
def shuffle(items): random.shuffle(items); return items


# In[9]:


tiles8 = [('BO', 'JA'), ('JA', 'PO'), ('JA', 'RY'), ('RY', 'KE'), 
          ('GR', 'KE'), ('GR', 'JO'), ('JA', 'KE'), ('KE', 'JO')]

dominoes(tiles8, 6, 6)


# # Pretty Output
# 
# Technically, this is a legal solution, but there are two problems with it: One, it is not visual. Two, it doesn't say where each tile is: when three names come together, which of the outside names goes with the middle name?  To fix those two problems I will:
# 
# - Define `plot_board(board)` to use `matplotlib` to plot the board, the names, and the tiles.
# - Modify the `Board` class and the `put` function so that the board maintains a list of `boxes` that surround each two-location rectangle that a tile occupies: `[loc0, loc1]`. The constant e is the distance between two adjacent tiles; we want them to not-quite touch (as in the xkcd comic).

# In[10]:

import matplotlib.pyplot as plt
import matplotlib
plt.switch_backend('agg')
matplotlib.use('agg')
# from IPython import get_ipython
# get_ipython().run_line_magic('matplotlib', 'qt5')


e = 0.06 # A small amount; the space between adjacent lines

class Board(dict):
    "A mapping from location to name."
    def __init__(self, width=16, height=24): 
        self.width, self.height, self.boxes = width, height, []
    def __missing__(self, loc): return empty
    
def plot_board(board):
    "Plot the box and name for every tile, plus a big box around the board."
    plt.figure(figsize=(board.width, board.height))
    plt.subplots_adjust(left=e, right=1-e, top=1-e, bottom=e)
    plt.axis('off')  
    plt.axis('equal')
    for box in board.boxes:
        plot_box(box)
    plot_box([(-2*e, -2*e), (board.width - 1 + 2*e, board.height - 1 + 2*e)])
    for (x, y) in board:
        plt.text(x + 0.5, y + 0.5, board[x, y], 
                 va='center', ha='center', fontsize=8)
    plt.savefig('visualization')

def plot_box(box):
    "Plot a box, which is a [loc0, loc1] pair."
    Xs, Ys = {loc[0] for loc in box}, {loc[1] for loc in box}
    x0, x1 = min(Xs), max(Xs) + 1 - e
    y0, y1 = min(Ys), max(Ys) + 1 - e
    plt.plot([x0, x1, x1, x0, x0], 
             [y0, y0, y1, y1, y0], 'k-')
#    plt.savefig('visualization')

def put_tile(board, loc0, loc1, tile, frontier): 
    "Place the tile across the two locations, and update frontier and boxes."
    board[loc0], board[loc1] = tile
    frontier -= {loc0, loc1}
    frontier |= {loc for loc in neighbors(loc0, board) + neighbors(loc1, board)
                 if board[loc] is empty}
    board.boxes.append([loc0, loc1])       


# In[11]:


#plot_board(dominoes(tiles8, 6, 6))


# # All the Names
# 
# Now let's try all the names from the comic, courtesy of 
#  [explainxkcd](http://www.explainxkcd.com/wiki/index.php/1970:_Name_Dominoes), with a few typos corrected:

# In[13]:


def name_tiles(text):
    "For each line of text, create a tile of ('First Name(s)', 'Lastname')."
    return [name.strip().rpartition(' ')[0::2]
            for name in text.upper().split('\n')]
#Change output file path according to cluster
f= open("peoples_names_list.txt",encoding="utf8") 
names = f.read()
           
xkcdtiles = name_tiles(names)


# In[15]:


len(xkcdtiles)


# In[16]:


# xkcd_tiles_og= xkcdtiles
# xkcdtiles= random.sample(xkcd_tiles_og, 25000)
# xkcdtiles


# # Approximate and Partial Matches
# 
# Two tile halves match if they are an exact match, like "ADAMS" and "ADAMS", or if they are an **approximate match**, like "AMY" and "AIMEE". To accomodate this, you can manually define allowable approximate matches by making the global variable `synsets` (synonym sets) be a mapping from a name to the set of approximate matches it should match, which can be done like this:
# 
#      synsets = synonyms("AMY=AIMEE, COOK=COOKE=COOKIE=COKIE, ...")
# 
# Another issue is  a **partial match**: in the comic, some tiles, like "FRANK LLOYD WRIGHT" are 3 squares wide, and some, like "PRINCE" are only one square wide. For simplicity, I chose to have all my tiles be 2 squares wide, but I still want `'LLOYD'` to match the first name of `('FRANK LLOYD', 'WRIGHT')`. To accomplish this, the second argument to `synonyms` is a list of tiles; the function will go through these and add synset entries for parts of first names,
# so that both `'FRANK'` and `'LLOYD'` will match `'FRANK LLOYD'`. As for "PRINCE", he gets represented as the tile `('', 'PRINCE')`. 

# In[17]:


import collections

def synonyms(text='', tiles=()): 
    "synonyms('AMY=AIMEE') => dict(AMY={'AMY', 'AIMEE'}, AIMEE={'AMY', 'AIMEE'})"
    synsets = collections.defaultdict(set)
    # Process `text`
    for text1 in text.upper().split(','):
        synset = set(text1.strip().split('='))
        for s in synset:
            synsets[s] |= synset
    # Process `tiles`
    for (first, last) in tiles:
        for part in first.split():
            synsets[part].add(first)
            synsets[first].add(part)
    return synsets
                
#synsets = synonyms("""AMY=AIMEE, COOK=COOKE=COOKIE=COKIE, ALASTAIR=ALISTAIR, 
 # COLUMBO=COLUMBUS, SAFIRE=SAPPHIRE=GARNET, GARNET=RUBY, CHARLIE=CHARLES, SEAN=SHAWN,
  #JIMMY=JAMES, MAN=MANN, JACK=JOHN, TOM=TOMMY, WILL=WILLIAM=WILLIAMS, ROBERT=ROBERTS=BOB, 
  #CAM=CAMERON, OLIVER=OLIVIA, EDWARD=EDWARDS, RICH=RICHARD, CHRIS=CHRISTOPHER=TOPHER, 
  #FAT=FATS=FATTY, WALT=WALTER, HANK=HANKS, CROW=CROWE, COLBERT=KOLBERT""", xkcdtiles)

synsets = synonyms("""DANIEL=DANIELS=DANIELSSEN=DANIELLE, MCDONALD= MCDONALD, CHARLES=CHARLES, 
  GEORGE=GEORGES=GEORG=GEORGIA, ABDUL=ABDULLA=ABDULA, WILLIAM=WILLIAMS, THOMPSON=THOMP, JOHN=JOH,
  SARAH=SARA, MARTIN=MARTINEZ=MARTI, IAN=IAN, JAKE=JAKE, WILL=WILLIAM=WILLIAMS, HENRY=HENRYS, ROBERT=ROBERTS=BOB, 
  CAM=CAMERON, OLIVER=OLIVIA, EDWARD=EDWARDS, RICH=RICHARD, CHRIS=CHRISTOPHER=TOPHER=CHRISTYL,KENNEDY=KENNARD
  """, xkcdtiles)


# In[18]:


def get_synset_dict():
    synsets_dict = {}
    linked_indexes_fn = []
    linked_indexes_ln = []
    linked_indexes_fn_ln = []
    check_similarity_in_name = 5
    for (idx,name) in enumerate(xkcdtiles) :
        if idx % 1000 == 0:
           (f'Words Iterated : {idx}')
        for (inner_idx, inner_name) in enumerate(xkcdtiles[idx:]) :
            if inner_idx not in linked_indexes_fn :
                if name[0][:check_similarity_in_name] == inner_name[0][:check_similarity_in_name]:
                    found_name = name[0]
                    linked_indexes_fn.append(inner_idx)
                    if found_name in synsets_dict :
                        synsets_dict[found_name].append(inner_name[0])
                    else :
                        synsets_dict[found_name] = [inner_name[0]]
                if inner_idx not in linked_indexes_ln :
                    if name[1][:check_similarity_in_name] == inner_name[1][:check_similarity_in_name]:
                        found_name = name[1]
                        linked_indexes_ln.append(inner_idx)
                        if found_name in synsets_dict :
                            synsets_dict[found_name].append(inner_name[1])
                        else :
                            synsets_dict[found_name] = [inner_name[1]]
                if inner_idx not in linked_indexes_fn_ln :
                    if name[1][:check_similarity_in_name] == inner_name[0][:check_similarity_in_name] :
                        found_name = name[1]
                        linked_indexes_fn_ln.append(inner_idx)
                        if found_name in synsets_dict :
                            synsets_dict[found_name].append(inner_name[0])
                        else :
                            synsets_dict[found_name] = [inner_name[0]]
    return synsets_dict


# In[24]:


# get_synset_dict()


# In[25]:


f = open('synstring.txt',encoding="utf8")
synset = f.read()

# print('Generated synonyms')

# In[26]:


synsets = synonyms(synset, xkcdtiles)


# To make this work, I update `legal` to consult the `synsets` global variable for an approximate or partial matches, and while I'm changing `legal`, I'll also disallow a match between the empty first name of "PRINCE" with the empty first name of "DRAKE".

# In[27]:


def legal(name, loc, board):
    "Is it legal to place this value on this location on board?"
    return (board[loc] is empty and 
            all(board[nbr] is empty 
                or board[nbr] == name != '' 
                or board[nbr] in synsets[name]
                for nbr in neighbors(loc, board)))


# # Final Result (with Random Restart)
# 
# The program sometimes gets stuck after placing relatively few tiles. I could modify the program to *back up* in this case, but it will be easier to just *give up* and restart with an empty board. I can restart multiple times, and accept the best board (the one on which the most tiles were placed):

# In[29]:


def best(boards): return max(boards, key=lambda board: len(board.boxes))
#plot_board(dominoes(xkcdtiles,15,15))
print('Generating domino board please wait...............')
plot_board(best(dominoes(xkcdtiles) for _ in range(200)))
print('Generated !! Stored in visualization.png')


# *Note:* I used a 16×24 square board while the xkcd comic used 27×35, but if I tried to fit 27 squares across then each tile would be smaller, and many names would overflow the sides of the dominoes too much. Here is the original xkcd comic:
# 
# [![](https://imgs.xkcd.com/comics/name_dominoes_2x.png)](https://xkcd.com/1970/)
# 
# # What's Next?
# 
# I'm happy with the results, but here are some ideas for improvements, if you want something to work on:
# - Allow tiles that are 1 or 3 squares wide, like `('PRINCE',)` or `('FRANK', 'LLOYD', 'WRIGHT')`.
# - Print names vertically in tiles that are placed vertically, and upside down for tiles that are placed horizontally, but with the first name on the right.
# - Print shorter names with a bigger font and longer names with a smaller font.
# - Download a bunch of names from Wikipedia and fill a 200 × 300 board.
# - If you like xkcd try [regex golf](https://github.com/norvig/pytudes/blob/master/ipynb/xkcd1313.ipynb), and [part 2](https://github.com/norvig/pytudes/blob/master/ipynb/xkcd1313-part2.ipynb).
# 
