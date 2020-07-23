# chessNaturalSelection
Uses pygame to display chess board, then has different methods of trying to build a chess engine. Attempts below:
- Natural Selection: randomly initializes neural nets, has them play against themselves, the winners are rewarded and the losers are killed off. Winners reproduce by copying themselves, random mutations occur, and process repeats.
- Minimax Algorithm: Scores every board by material and positions of pieces, and then makes the moves to get to the highest scoring positions. Looks 3 moves ahead to be fast, 5 moves ahead to be slower but more accurate.
