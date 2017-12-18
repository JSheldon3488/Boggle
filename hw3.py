import random
from tkinter import *
import string


class Boggle():
    def __init__(self, file='words.dat'):
        '''Initializes all the data structes we need as well as creates and shows the board'''
        self.file = file
        self.freq_dict, self.trie = self.readData(file)
        self.size = 5
        self.scale = 50  # Allows me to easily change the scale of the window
        self.soln = []
        self.board = [random.choices(list(self.freq_dict.keys()), list(
            self.freq_dict.values()), k=5) for j in range(self.size)]
        self.initTK()  # Build the board
        self.window.mainloop()  # Show the board

    # This function handles initializing the TKinter winow and everything that goes with that
    def initTK(self):
        ''' Initializes the TKinter Window with grid and letters also binds the buttons'''
        self.window = Tk()
        self.window.title('Boggle')
        # Create a canvas within the window to draw on
        self.canvas = Canvas(self.window, width=self.size * self.scale,
                             height=self.size * self.scale, bg='white')
        self.canvas.pack()
        # Draw the grid on the canvas, and place the letters
        self.drawBoard()
        # Bind buttons
        self.canvas.bind("<Button-1>", self.extend)
        self.canvas.bind("<Button-2>", self.new)
        self.canvas.bind("<Button-3>", self.reset)
    # Created this as a seperate function so that I can use it later in reset and new without calling all of init

    def drawBoard(self):
        '''Draws the board'''
        for i in range(self.size):
            for j in range(self.size):
                self.canvas.create_rectangle(
                    i * self.scale, j * self.scale, (i + 1) * self.scale, (j + 1) * self.scale)
                self.canvas.create_text(i * self.scale + (self.scale / 2), j * self.scale +
                                        (self.scale / 2), text=self.board[j][i].upper(), font=('Purisa', 20))


# The next three functions are for reading in the data and creating the frequency and trie data structues
# Input: a file of words
# Output: frequency and trie data structures
    def readData(self, file):
        '''Read in a file and create the frequency and trie data structures'''
        # Read in the file and create a list of all the words
        self.infile = open(file, 'r')
        self.word_list = self.infile.read().split()
        self.infile.close()
        return(self.freqs(self.word_list), self.buildTrie(self.word_list))

    def freqs(self, words):
        '''Builds a frequency data structure for each letter in a list of words'''
        freq_dict = {}
        # Create Dictionary of counts for each letter. key=letter value=count
        for word in words:
            for letter in word:
                if letter in freq_dict.keys():
                    freq_dict[letter] += 1
                else:
                    freq_dict[letter] = 1
        # Turn each letters count into frequencies (% chance this letter is picked at random)
        print(freq_dict.keys())
        for letter in freq_dict.keys():
            freq_dict[letter] /= len(words) * 5
        return(freq_dict)

    def buildTrie(self, words):
        '''Builds a trie data structure from a list of words'''
        trie = {}
        for word in words:
            current_dict = trie
            for letter in word[:-1]:
                current_dict = current_dict.setdefault(letter, {})
            current_dict[word[-1]] = word
        return(trie)

# The next two functions are used to check if a solution is viable
# Input is a list of tuples, where each corresponds to a (row,col) location on the baord.
# Returns False if not viable. If viable returns value of the trie at this state in the game, or the found word.
    def ckSoln(self, soln):
        '''Checks that the solution input is a viable solution'''
        # Deals with the first letter selection (dont need to check if neighbor)
        if len(soln) == 1:
            return(self.chktrie(soln, self.trie))

        # All picks after first pick
        # Check that row or column only differ by one (neighbor in cardinal directions)
        elif (abs(soln[-2][0] - soln[-1][0]) + abs(soln[-2][1] - soln[-1][1])) == 1:
            # Check if viable options still in trie
            return(self.chktrie(soln, self.trie))
        else:
            return(False)

    def chktrie(self, soln, trie):
        '''Check if Viable option in trie, return state of trie after check'''
        # Loop threw the solution updating the trie as you go.
        # If key not in trie will throw key error and return False
        for l in soln:
            try:
                trie = trie[self.board[l[0]][l[1]]]
            except:
                return(False)
        return(trie)

# extend function is the driver for our game. Will update the board visually and our working solution
# Also handles the found word message
# Input: Click which will be a row,col location on the board.
    def extend(self, event):
        '''Checks if move is viable, if it is turns space green, if it is not turns space red.
            Also prints a message if word is found and resets the game'''
        # Store the clicks (row,col)
        row = event.y // self.scale
        col = event.x // self.scale
        # Make sure Tile not already used
        if (row, col) not in self.soln:
            self.soln.append((row, col))
        else:
            print("You already used this letter, pick again!")
            return(None)

        # Check if click is viable using ckSoln
        move = self.ckSoln(self.soln)
        if move != False:
            # Found a word, print message and reset the game
            if type(move) == str:
                self.canvas.create_oval(self.soln[-1][1] * self.scale + 1, self.soln[-1][0] * self.scale + 1,
                                        (self.soln[-1][1] + 1) * self.scale - 1, (self.soln[-1][0] + 1) * self.scale - 1, fill='green2')
                print("Congratulations! You found: {}!".format(move))
                self.reset("<Button-3>")

            # Still a viable solution
            else:
                self.canvas.create_oval(self.soln[-1][1] * self.scale + 1, self.soln[-1][0] * self.scale + 1,
                                        (self.soln[-1][1] + 1) * self.scale - 1, (self.soln[-1][0] + 1) * self.scale - 1, fill='green2')

        # Not a viable move, turn red and remove it from solution variable
        else:
            self.canvas.create_oval(self.soln[-1][1] * self.scale + 1, self.soln[-1][0] * self.scale + 1,
                                    (self.soln[-1][1] + 1) * self.scale - 1, (self.soln[-1][0] + 1) * self.scale - 1, fill='red')
            del self.soln[-1]

        # Redraw the baord over the color ovals so you can see the letters still
        self.drawBoard()

# New and reset are simple functions that do exactly what they sound like they would do
    def new(self, event):
        '''Creates a new boggle puzzle and overwrites the old puzzle data structures'''
        self.soln = []
        self.board = [random.choices(list(self.freq_dict.keys()), list(
            self.freq_dict.values()), k=5) for j in range(self.size)]
        self.canvas.create_rectangle(0, 0, self.size * self.scale,
                                     self.size * self.scale, fill='white')
        self.drawBoard()

    def reset(self, event):
        ''' Resets the board visually and resets the current solution self.soln'''
        # Redisplay current board with nothing on it, and reset self.soln
        self.soln = []
        self.canvas.create_rectangle(0, 0, self.size * self.scale,
                                     self.size * self.scale, fill='white')
        self.drawBoard()

# The rest of this code is for the solver. Makes use of recursion to find all possible words in the board
# Had trouble with the search function, remember to think about how scopeing works!
    def solve(self):
        '''Returns a list of all words found in the current puzzle'''
        # Container for the found words
        l = []
        # Loops over all the possible starting squares in the grid and calls the recursive step
        for x in range(self.size):
            for y in range(self.size):
                l.extend(self.search(x, y, self.trie[self.board[x][y]], [(x, y)]))
        return(l)

    def search(self, x, y, trie, path):
        '''Recursively searches all possible viable paths from the start point (x,y)'''
        # Container for the found words
        l = []
        # Base Case: We found a word, append it to the list
        if type(trie) == str:
            l.append(trie)
        # Recursive Step: Look in every direction 1 by 1, recursively calling deeper until move is not valid or we find a word
        # I beleive this will work in a deapth first fashion
        for d in [(0, 1), (0, -1), (-1, 0), (1, 0)]:
            if self.legal(x + d[0], y + d[1], trie) and (x + d[0], y + d[1]) not in path:
                l.extend(self.search(
                    x + d[0], y + d[1], trie[self.board[x + d[0]][y + d[1]]], path + [(x + d[0], y + d[1])]))
        return(l)

    def legal(self, x, y, trie):
        ''' Checks if new move is still on the board and checks if still a viable solution in the trie'''
        # The trie being passed in will be a modified trie from the search recursive calls
        # Check if move still on the board, if not return false and end this path
        if 0 <= x < self.size and 0 <= y < self.size:
            # Check if still move still a viable path in trie, if throws key error or error because trie = str return false
            # and end this path
            try:
                return(self.board[x][y] in trie.keys())
            except:
                return(False)
        return(False)


# def main():
#    B = Boggle()
# if __name__ == '__main__':
#    main()
