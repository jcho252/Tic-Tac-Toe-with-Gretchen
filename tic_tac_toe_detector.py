import cv2
import numpy as np
import imutils

class TicTacToeBoardDetector:
    # Class constructor
    def __init__(self):
        # Parameters for edge detection
        self.blur_kernel_size = (5, 5)
        self.canny_threshold1 = 50
        self.canny_threshold2 = 150

    # Class method that detects a Tic Tac Toe board and returns its center
    def detect(self, frame):
        # Convert frame from RGB to Grayscale color space
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply GaussianBlur to reduce noise and improve edge detection
        blurred = cv2.GaussianBlur(gray, self.blur_kernel_size, 0)

        # Use Canny edge detection
        edges = cv2.Canny(blurred, self.canny_threshold1, self.canny_threshold2)

        # Use Hough Line Transform to detect lines
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)

        if lines is None:
            return None

        # Create a blank image to draw the detected lines
        line_image = np.zeros_like(frame)

        # Draw the detected lines on the blank image
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(line_image, (x1, y1), (x2, y2), (255, 255, 255), 2)

        # Use findContours to detect the grid pattern of the tic-tac-toe board
        contours, _ = cv2.findContours(cv2.cvtColor(line_image, cv2.COLOR_BGR2GRAY), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Look for a large contour with multiple lines crossing
        board_contour = None
        for cnt in contours:
            # Approximate the contour to a polygon
            epsilon = 0.02 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)

            # Check if the contour has a large area and is approximately square
            if len(approx) >= 4:
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = w / float(h)

                if 0.8 < aspect_ratio < 1.2 and 100 < w < 500 and 100 < h < 500:
                    # Check for the presence of multiple horizontal and vertical lines
                    num_horizontal_lines = sum(1 for line in lines if abs(line[0][1] - line[0][3]) < 10)
                    num_vertical_lines = sum(1 for line in lines if abs(line[0][0] - line[0][2]) < 10)

                    if num_horizontal_lines >= 2 and num_vertical_lines >= 2:
                        board_contour = approx
                        break

        if board_contour is not None:
            # Calculate the center of the board
            M = cv2.moments(board_contour)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        else:
            center = None

        return center

# Test the detector (pseudo-code, the actual main function will be part of the complete program)
def main():
    # Initialize camera
    ROSEnvironment()
    camera = Camera()
    camera.start()

    # Initialize Tic Tac Toe board detector
    board_detector = TicTacToeBoardDetector()

    # Loop until board is detected
    while True:
        # Get image from camera
        img = camera.getImage()

        # Run Tic Tac Toe board detector on image
        center = board_detector.detect(img)

        # Print center if board is detected
        if center is not None:
            print(f"Tic Tac Toe board detected at center: {center}")
            break
        else:
            print("No Tic Tac Toe board detected.")

    # Stop camera
    camera.stop()

if __name__ == '__main__':
    main()
