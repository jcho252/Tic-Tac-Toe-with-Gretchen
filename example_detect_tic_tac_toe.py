import cv2
import numpy as np
import random
from tic_tac_toe_detector import TicTacToeBoardDetector  # Replace with your actual detector
import sys
sys.path.append('..')
from lib.camera_v2 import Camera  # Replace with your actual camera module
from lib.ros_environment import ROSEnvironment  # Replace with your actual ROS environment module

# Define RGB color ranges for blue, red, and white
blue_lower = np.array([0, 0, 100])
blue_upper = np.array([100, 100, 255])

red_lower = np.array([0, 0, 100])
red_upper = np.array([100, 100, 255])

white_lower = np.array([200, 200, 200])
white_upper = np.array([255, 255, 255])

def get_color_name(rgb):
    if np.all((blue_lower <= rgb) & (rgb <= blue_upper)):
        return "Blue"
    elif np.all((red_lower <= rgb) & (rgb <= red_upper)):
        return "Red"
    elif np.all((white_lower <= rgb) & (rgb <= white_upper)):
        return "White"
    else:
        return "Unknown"

def calculate_grid_points():
    grid_points = [
        (120, 80), (320, 80), (500, 80),
        (120, 240), (320, 240), (500, 240),
        (120, 400), (320, 400), (500, 400)
    ]
    return grid_points

def mark_spot(img, index, color):
    grid_points = calculate_grid_points()
    x, y = grid_points[index]
    if color == "Blue":
        cv2.circle(img, (x, y), 20, (255, 0, 0), -1)  # Blue in RGB (BGR in OpenCV)
    elif color == "Red":
        cv2.circle(img, (x, y), 20, (0, 0, 255), -1)  # Red in RGB (BGR in OpenCV)

    # Draw box number
    cv2.putText(img, str(index + 1), (x - 10, y + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

def draw_box_numbers(img):
    grid_points = calculate_grid_points()
    for idx, (x, y) in enumerate(grid_points):
        # Draw box number
        cv2.putText(img, str(idx + 1), (x - 10, y + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

def check_for_winner(board):
    # Define winning combinations (indexes)
    winning_combinations = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Rows
        (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Columns
        (0, 4, 8), (2, 4, 6)              # Diagonals
    ]

    # Check for three consecutive same colors
    for combo in winning_combinations:
        marks = [board[idx] for idx in combo]
        if marks == ["Blue", "Blue", "Blue"]:
            return "Blue"
        elif marks == ["Red", "Red", "Red"]:
            return "Red"

    return None

def find_best_move(board, player_color):
    # Define winning combinations (indexes)
    winning_combinations = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Rows
        (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Columns
        (0, 4, 8), (2, 4, 6)              # Diagonals
    ]

    # Check for winning or blocking opportunities
    def check_for_two_in_a_row(color):
        for combo in winning_combinations:
            marks = [board[idx] for idx in combo]
            if marks.count(color) == 2 and marks.count("White") == 1:
                return combo[marks.index("White")]
        return None

    # Prioritize winning
    move = check_for_two_in_a_row(player_color)
    if move is not None:
        return move

    # Block opponent's winning move
    opponent_color = "Blue" if player_color == "Red" else "Red"
    move = check_for_two_in_a_row(opponent_color)
    if move is not None:
        return move

    # Otherwise, choose a random move
    empty_indices = [idx for idx, mark in enumerate(board) if mark == "White"]
    if empty_indices:
        return random.choice(empty_indices)
    else:
        return None

def detect_board_state(rgb_img, grid_points):
    board_state = []
    for point in grid_points:
        x, y = point
        rgb_color = rgb_img[y, x]
        color_name = get_color_name(rgb_color)
        board_state.append(color_name)
    return board_state

def main():
    ROSEnvironment()  # Initialize your ROS environment

    # Initialize Tic Tac Toe board detector
    board_detector = TicTacToeBoardDetector()  # Initialize your board detector

    camera = Camera()  # Initialize camera
    camera.start()  # Start camera capture

    while True:
        # Initialize game variables
        board = ["White"] * 9
        user_turn = True
        num_moves = 0

        while True:
            if user_turn:
                # User's turn: Wait for user to place a blue box
                input("Your turn! Place a blue box on one of the white spots and press Enter when ready: ").strip().lower()

                # Capture initial image
                initial_img = camera.getImage()
                cv2.imshow("Initial Image", initial_img)
                cv2.waitKey(1000)  # Display the image for a short period

                img = initial_img.copy()
                grid_points = calculate_grid_points()
                draw_box_numbers(img)  # Draw box numbers

                user_index = None
                for idx, point in enumerate(grid_points):
                    x, y = point
                    rgb_color = img[y, x]
                    color_name = get_color_name(rgb_color)

                    if color_name == "Blue" and board[idx] == "White":
                        user_index = idx
                        break

                if user_index is not None:
                    # Update board and display
                    board[user_index] = "Blue"
                    mark_spot(img, user_index, "Blue")
                    cv2.imshow("Tic Tac Toe Board", img)
                    cv2.waitKey(1000)

                    # Output where the user placed the blue box
                    print(f"User placed blue at Box {user_index + 1}")

                    # Check for winner or draw after user's move
                    winner = check_for_winner(board)
                    if winner:
                        print(f"{winner} wins!")
                        break
                    elif all(mark != "White" for mark in board):
                        print("It's a draw!")
                        break

                    # Switch turns to robot
                    user_turn = False
                    num_moves += 1
                else:
                    print("No valid move detected. Press Enter to try again.")
                    cv2.destroyAllWindows()
                    continue  # Restart the user's turn

            else:
                # Robot's turn: Analyze the board and decide its move
                print("Robot's turn!")

                img = camera.getImage()
                cv2.imshow("Robot's Initial Image", img)
                cv2.waitKey(1000)  # Display the image for a short period

                grid_points = calculate_grid_points()
                draw_box_numbers(img)  # Draw box numbers

                for idx, point in enumerate(grid_points):
                    x, y = point
                    rgb_color = img[y, x]
                    color_name = get_color_name(rgb_color)
                    if color_name == "Blue" and board[idx] == "White":
                        board[idx] = "Blue"  # Update board state with user's move

                # Robot's move decision
                robot_index = find_best_move(board, "Red")
                if robot_index is not None:
                    # Output where the robot wants to place the red box
                    print(f"Robot wants to place red at Box {robot_index + 1}")

                    # Wait for user to place the red box and press Enter
                    input("Place the red box at the specified location then press Enter to continue: ").strip().lower()

                    # Capture new image after robot's decision
                    new_img = camera.getImage()
                    cv2.imshow("Robot's New Image", new_img)
                    cv2.waitKey(1000)  # Display the image for a short period

                    # Update board and display
                    board[robot_index] = "Red"
                    mark_spot(new_img, robot_index, "Red")
                    cv2.imshow("Tic Tac Toe Board", new_img)
                    cv2.waitKey(1000)

                    # Output where the robot placed the red box
                    print(f"Robot placed red at Box {robot_index + 1}")

                    # Check for winner or draw after robot's move
                    winner = check_for_winner(board)
                    if winner:
                        print(f"{winner} wins!")
                        break
                    elif all(mark != "White" for mark in board):
                        print("It's a draw!")
                        break

                    # Switch turns to user
                    user_turn = True
                    num_moves += 1

                else:
                    print("No empty white spot available for robot to move. Press Enter to continue.")
                    cv2.destroyAllWindows()
                    continue  # Restart the robot's turn

            # Clean up camera for this move
            cv2.destroyAllWindows()

        # Clean up (not expected to reach here in normal game flow)
        cv2.destroyAllWindows()

        # Ask if the user wants to play again
        play_again = input("Do you want to play again? (Y/N): ").strip().lower()
        if play_again != 'y':
            break

    # Stop the camera at the end
    camera.stop()

if __name__ == '__main__':
    main()
