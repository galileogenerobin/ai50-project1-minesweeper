import itertools
import random
import copy


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # If the number of current cells equals the count of mines in the set and count is not 0, then all cells in the set are mines
        if len(self.cells) == self.count and self.count != 0:
            return self.cells
        return None
        # raise NotImplementedError

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # If the count of mines in the set = 0 and the number of cells is not 0, then all cells in the set are safe
        if self.count == 0 and len(self.cells) != 0:
            return self.cells
        return None
        
        # raise NotImplementedError

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # We will only update if the cell exists in the sentence
        if cell in self.cells:
            # Remove from the set of cells and reduce count by 1
            self.cells.remove(cell)
            self.count = self.count - 1
        # raise NotImplementedError

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # We will only update if the cell exists in the sentence
        if cell in self.cells:
            # Remove from the set of cells (count remains the same)
            self.cells.remove(cell)
        # raise NotImplementedError


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # 1) mark the cell as a move that has been made
        self.moves_made.add(cell)

        # 2) mark the cell as safe, both in self.safes and in the knowledge base
        self.mark_safe(cell)

        # 3) add a new sentence to the AI's knowledge base based on the value of `cell` and `count`
        # First we identify the neighboring cells
        neighbor_cells = set()
        # Add valid neighboring cells (i.e. -1 or +1 from current cell that are not out of bounds)
        for i in range(max(0, cell[0] - 1), min(self.width, cell[0] + 2)):
            for j in range(max(0, cell[1] - 1), min(self.height, cell[1] + 2)):
                # The neighbor cell cannot be the current cell
                if not (i, j) == cell:
                    if (i, j) in self.mines:
                        # If the neighbor cell is a known mine, we don't add it to the sentence and we should reduce the count of mines by 1
                        count = count - 1
                    elif (i, j) not in self.safes:
                        # Also, if the neighbor cell is a known safe, no need to add it to the sentence; all other neighbor cells we add to the sentence
                        neighbor_cells.add((i, j))
        # Add the new sentence to the knowledge base
        self.knowledge.append(Sentence(neighbor_cells, count))

        # 4) mark any additional cells as safe or as mines if it can be concluded based on the AI's knowledge base
        # 5) add any new sentences to the AI's knowledge base if they can be inferred from existing knowledge
        # See function definition below
        self.update_knowledge()
        # raise NotImplementedError

    def update_knowledge(self):
        """Additional function to update knowledge
        """
        # We will create a flag to identify if the knowledge base changed during this update, in which case we will call this function again
        knowledge_changed = False
        
        # Now we loop through the updated knowledge base and mark cells
        # 4) mark any additional cells as safe or as mines if it can be concluded based on the AI's knowledge base
        for sentence in self.knowledge:
            # Check if the sentence resolves to known safes or known mines, in which case we make updates
            # In each, we create copies of the known_safes and known_mines so we can iterate through them
            if sentence.known_safes() is not None:
                known_safes = copy.deepcopy(sentence.known_safes())
                # Mark safe each cell which is known to be safe (i.e. if sentence.count == 0)
                for cell in known_safes:
                    self.mark_safe(cell)
                    sentence.mark_safe(cell)
                knowledge_changed = True
            if sentence.known_mines() is not None:
                known_mines = copy.deepcopy(sentence.known_mines())
                # Mark mine each cell which is known to be a mine (i.e. if sentence.count == len(sentence.cells))
                for cell in known_mines:
                    self.mark_mine(cell)
                    sentence.mark_mine(cell)
                knowledge_changed = True

        # Before we do Step 5, let's clean up our knowledge base by removing empty sets
        # Create a copy of the current knowledge base so we can iterate through it
        knowledge_copy = copy.deepcopy(self.knowledge)
        for sentence in knowledge_copy:
            # If cells are an empty set (i.e. as a result of all its cells having previously been marked safe), let's remove the sentence
            if len(sentence.cells) == 0:
                self.knowledge.remove(sentence)
                break

        # Update the copy of the current knowledge base
        knowledge_copy = copy.deepcopy(self.knowledge)
        for sentence1 in knowledge_copy:
            # We check for subsets with other sentences
            for sentence2 in knowledge_copy:
                # 5) add any new sentences to the AI's knowledge base if they can be inferred from existing knowledge
                if not sentence1 == sentence2:
                    # Check if one sentence's cells is a subset of the other
                    # Note, we are not checking sentence2 < sentence1, since that will be processed later in the loop
                    if sentence1.cells < sentence2.cells:
                        # If so, add the inferred subset to the original knowledge base, only if the sentence does not exist yet
                        new_sentence = Sentence(sentence2.cells - sentence1.cells, sentence2.count - sentence1.count)
                        if new_sentence not in self.knowledge:
                            self.knowledge.append(new_sentence)
                            knowledge_changed = True

        # Check if the knowledge base updated
        if knowledge_changed:
            self.update_knowledge()

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # Loop through all cells
        for i in range(self.width):
            for j in range(self.height):
                # The cell must not be an existing move
                if (i, j) not in self.moves_made and (i, j) in self.safes:
                    return (i, j)
                    
        return None
        # raise NotImplementedError

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        # List of unknown cells (i.e. not moves made and not known mines), from which we will choose randomly
        unknown_cells = []
        # Loop through all cells
        for i in range(self.width):
            for j in range(self.height):
                # The cell must not be an existing move and is not a known mine
                # Since, from specification, this move will be called when there are no safe moves, we will no longer check for self.safes
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    unknown_cells.append((i, j))

        if len(unknown_cells) > 0:
            return random.choice(unknown_cells)
        # If no unknown cells
        return None

        # raise NotImplementedError
