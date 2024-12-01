Gretchen plays Tic Tac Toe by analyzing the board with image processing, identifying color-coded positions, and making moves based on game logic. The robot and user take turns, and Gretchen processes each move to determine the winner, and then prompts the user to play again.

Code Functionality:
Board Detection: The board detection algorithm (using OpenCV) detects the Tic Tac Toe grid based on edge detection and contour finding. It uses the Hough Line Transform to identify the grid lines and then calculates the grid points representing each of the 9 cells.

Color Detection: Once the grid points are established, the system detects cell colors—blue for the user, red for Gretchen, and white for unoccupied—using predefined RGB ranges.

Game Logic: After each move, the board state is checked with the winning combinations algorithm to determine if either the user or Gretchen has won; if no winner is found, Gretchen uses the optimal move finder to select the best move for its turn.

User Interaction: The user is prompted to place a blue marker and then press "Enter" after each move. Gretchen takes its turn and updates the board accordingly.

Coding Concepts:
OpenCV: For image processing tasks like color detection, grid point analysis, and board state management, functions such as cv2.Canny and cv2.HoughLinesP were used to detect edges and lines, while cv2.circle and cv2.putText were used for marking spots and labeling grid points.

Python: The entire project was coded in Python, and we leveraged various libraries such as NumPy for array handling, and random for generating Gretchen’s fallback moves when no immediate win or block was possible.

ROS (Robot Operating System): This was essential for managing the camera input and handling interactions between the camera and the image processing algorithms.

Algorithms: The winning combination check and optimal move-finding algorithms were coded to enhance Gretchen’s ability to play Tic Tac Toe intelligently.
