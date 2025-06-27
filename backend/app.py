import io
import json
import cv2
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
from tensorflow.keras.models import load_model

# load digit recognizer
model = load_model("model/cnn_model.h5")
with open("model/labels.json") as f:
    labels = json.load(f)

app = Flask(__name__)
CORS(app)

# Sudoku solver (backtracking)
def find_empty(grid):
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                return i, j
    return None

def is_valid(grid, row, col, num):
    if any(grid[row][j] == num for j in range(9)):
        return False
    if any(grid[i][col] == num for i in range(9)):
        return False
    start_row, start_col = 3*(row//3), 3*(col//3)
    for i in range(start_row, start_row+3):
        for j in range(start_col, start_col+3):
            if grid[i][j] == num:
                return False
    return True

def solve(grid):
    empty = find_empty(grid)
    if not empty:
        return True
    r, c = empty
    for num in range(1,10):
        if is_valid(grid, r, c, num):
            grid[r][c] = num
            if solve(grid):
                return True
            grid[r][c] = 0
    return False

# preprocess, detect grid, extract digits
def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7,7), 3)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)
    return thresh

@app.route('/api/solve', methods=['POST'])
def api_solve():
    file = request.files['file']
    img = Image.open(io.BytesIO(file.read())).convert('RGB')
    open_cv_image = np.array(img)
    open_cv_image = open_cv_image[:, :, ::-1]

    # preprocess & find largest contour (the grid)
    proc = preprocess_image(open_cv_image)
    contours, _ = cv2.findContours(proc, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contour = max(contours, key=cv2.contourArea)
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
    if len(approx) != 4:
        return jsonify({'error': 'Grid not found'})

    # warp perspective
    pts = approx.reshape(4,2)
    # order points (implement ordering function)
    rect = order_points(pts)
    dst = np.array([[0,0],[450,0],[450,450],[0,450]], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    warp = cv2.warpPerspective(open_cv_image, M, (450,450))

    # split into 9x9
    cell_w = cell_h = 50
    puzzle = [[0]*9 for _ in range(9)]
    for i in range(9):
        for j in range(9):
            x, y = j*cell_w, i*cell_h
            cell = warp[y:y+cell_h, x:x+cell_w]
            digit = extract_digit(cell)
            if digit is not None:
                pred = model.predict(digit.reshape(1,28,28,1))
                puzzle[i][j] = int(labels[str(pred.argmax())])

    # solve
    if not solve(puzzle):
        return jsonify({'error': 'Cannot solve'})

    return jsonify({'solution': puzzle})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
