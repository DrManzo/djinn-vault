---
subject: cs/gaming/programming-tutorials
tags:
  - cs/game-development
  - cs/algorithms
  - cs/basic-programming
created: 2026-05-23
source: Perplexity export
---

# Python Game Development: Placing a Ship on a 10x10 Grid

## Summary
This note provides an introduction to placing a ship on a 10x10 grid using Python, focusing on basic programming concepts and game development.

## Key Points
- Initialize a 10x10 grid.
- Place a 1x5 ship diagonally from the top-left to bottom-right corner.
- Implement a function to print the board state.
- Handle player input for coordinates.
- Check if the move hits the ship or is a miss.
- Update and display the game board.

## Details
The provided Python code demonstrates how to set up a simple 10x10 grid-based game where a player can place a 1x5 ship diagonally. The game checks whether the player's input coordinates hit the ship, updates the board state accordingly, and prints the updated board after each move.

### Step-by-Step Explanation

1. **Initialize the Game Board:**
   ```python
   # Initialize the game board as a 10x10 grid of zeros
   board = [[0] * 10 for _ in range(10)]
   ```

2. **Place the Ship Diagonally:**
   The ship is placed diagonally from the top-left to bottom-right corner.
   ```python
   # Place the 1x5 ship diagonally from top-left to bottom-right
   ship_x, ship_y = 0, 4
   for i in range(5):
       board[ship_x + i][ship_y + i] = 'S'
   ```

3. **Print the Game Board:**
   A function is defined to print the game board.
   ```python
   def print_board():
       print(' ', end='')
       for i in range(10):
           print(i, end=' ')
       print()
       for i in range(10):
           print(i, end=' ')
           for j in range(10):
               if board[i][j] == 'S':
                   print('S', end=' ')
               elif board[i][j] == 1:
                   print('X', end=' ')
               else:
                   print(' ', end=' ')
           print()
   ```

4. **Main Game Loop:**
   The game loop handles player input and updates the board state.
   ```python
   while True:
       # Ask the player for their move (x, y coordinates)
       x = int(input("Enter x coordinate: "))
       y = int(input("Enter y coordinate: "))

       # Check if the move is within the board boundaries
       if x < 0 or x >= 10 or y < 0 or y >= 10:
           print("Invalid move! Try again.")
           continue

       # Check if the move hits the ship
       if board[x][y] == 'S':
           print("Hit!")
           board[x][y] = 1
       else:
           print("Miss!")

       # Print the updated game board
       print_board()
   ```

### References
- No specific sources or URLs are mentioned in this content.

## Related
- [[Building-A-Tetris-Game-In-Python]] — grid-based-game
