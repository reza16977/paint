import numpy as np
import cv2
import tkinter as tk
from tkinter import filedialog

"""Global Variable"""
drawing = False
current_shape = 'line'
drawing = False
current_color = (0, 0, 0)
title = 'Drawing tool'
thickness = 5
palette_size = 50
undo_stack = []
redo_stack = []
icon_s = 100
shapes = ['circle', 'pentagon', 'rectangle', 'star', 'triangle']

colors = [
    (255, 192, 203),  # pink
    (0, 0, 255),  # Red
    (0, 255, 0),  # Green
    (255, 0, 0),  # Blue
    (0, 0, 0),  # black
    (255, 255, 0),  # Yellow
    (255, 0, 255),  # Magenta
    (0, 255, 255),  # Cyan
    (128, 128, 128),  # Gray
    (175, 175, 175)  # light gray

]

images = []
for sh in shapes:
    image = cv2.imread(f"project_images/{sh}.png")
    images.append(cv2.resize(image, (100, 30)))

"""Create a blank canvas image"""
img = np.zeros((500, 500, 3), np.uint8)
img.fill(255)

"""All methods"""

"""undo and redo"""


def undo_redo():
    global img

    if len(undo_stack) > 0:
        redo_stack.append(img.copy())
        img = undo_stack.pop()


"""get current thickness on trackbar"""


def onThickness(thick):
    global thickness
    thickness = thick


"""drawing shapes by help of mouse events"""


def draw_shape(event, X, y, flags, param):
    global drawing, thickness, pre_point, current_color, current_shape, img

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        pre_point = (X, y)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False

    elif event == cv2.EVENT_LBUTTONDBLCLK:
        color_index = X // palette_size
        if 0 <= color_index < len(colors):
            current_color = colors[color_index]
    elif event == cv2.EVENT_RBUTTONDBLCLK:
        shape_index = X // icon_s
        if 0 <= shape_index < len(shapes):
            current_shape = shapes[shape_index]

    elif event == cv2.EVENT_RBUTTONDOWN:
        b, g, r = img[y, X]
        current_color = (int(r), int(g), int(b))

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            if current_shape == 'line':
                cv2.line(img, pre_point, (X, y), current_color, thickness)
                pre_point = (X, y)
                undo_stack.append(img.copy())
            elif current_shape == 'rectangle':
                cv2.rectangle(img, (X, y), (X + 100, y + 50), current_color, thickness)
                pre_point = (X, y)
                undo_stack.append(img.copy())

            elif current_shape == 'circle':
                cv2.circle(img, pre_point, thickness * 5, current_color, 5)
                pre_point = (X, y)
                undo_stack.append(img.copy())

            elif current_shape == 'pentagon':
                center_x, center_y = X, y
                side_length = 50 * (thickness / 10)
                vertices = []
                for side in range(5):
                    angle = 2 * np.pi * side / 5
                    vertex_x = int(center_x + side_length * np.cos(angle))
                    vertex_y = int(center_y + side_length * np.sin(angle))
                    vertices.append((vertex_x, vertex_y))
                cv2.polylines(img, [np.array(vertices)], isClosed=True, color=current_color, thickness=thickness)
                pre_point = (X, y)
                undo_stack.append(img.copy())

            elif current_shape == 'triangle':
                vertices = [(X, y), (X + 50, y), (X + 25, y - 50)]
                cv2.polylines(img, [np.array(vertices)], isClosed=True, color=current_color, thickness=thickness)
                pre_point = (X, y)
                undo_stack.append(img.copy())

            elif current_shape == 'star':
                center_x, center_y = X, y
                radius_outer = 50  # Define the outer radius of the star here
                radius_inner = 25  # Define the inner radius of the star here
                angles = np.linspace(0, 2 * np.pi, 5, endpoint=False) + np.pi / 2
                vertices = []
                for angle in angles:
                    vertex_x_outer = int(center_x + radius_outer * np.cos(angle))
                    vertex_y_outer = int(center_y + radius_outer * np.sin(angle))
                    vertices.append((vertex_x_outer, vertex_y_outer))

                    vertex_x_inner = int(center_x + radius_inner * np.cos(angle + np.pi / 5))
                    vertex_y_inner = int(center_y + radius_inner * np.sin(angle + np.pi / 5))
                    vertices.append((vertex_x_inner, vertex_y_inner))

                cv2.polylines(img, [np.array(vertices)], isClosed=True, color=current_color, thickness=thickness)
                pre_point = (X, y)
                undo_stack.append(img.copy())


"""opening new image for editing"""


def open_image():
    global img
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename()
    if file_path:
        img = cv2.imread(file_path)
        img = cv2.resize(img, (500, 500))


"""open new window for removing select area"""


def delete_selected():
    global img
    img_copy = img.copy()
    mask = np.zeros(img.shape[:2], dtype=np.uint8)

    # Select the region of interest (ROI) by drawing a shape
    roi = cv2.selectROI('Delete Selected', img_copy)
    x, y, w, h = roi

    # Create a binary mask of the selected region
    mask[y:y + h, x:x + w] = 255

    # Apply the mask to delete the selected part
    img[mask == 255] = (255, 255, 255)
    cv2.destroyWindow("Delete Selected")


"""making window , trackbar and mouse call function"""
cv2.namedWindow(title)
cv2.setMouseCallback(title, draw_shape)
cv2.createTrackbar('thickness', title, thickness, 20, onThickness)

"""create color palette to showing colors as icons"""
color_palette = np.zeros((palette_size - 25, len(colors) * palette_size, 3), dtype=np.uint8)


"""handle position of every color 's icon inside the palette"""
for i, color in enumerate(colors):
    icon_x = i * palette_size
    icon_y = 0
    color_palette[icon_y:icon_y + palette_size, icon_x:icon_x + palette_size] = color

"""create shape palette to showing shapes as icons"""
shape_palette = np.zeros((30, len(images) * icon_s, 3), dtype=np.uint8)

"""handle position of every shape 's icon inside the palette"""
for i, im in enumerate(images):
    icon_X = i * icon_s
    icon_y = 0
    shape_palette[icon_y:icon_y + 30, icon_X:icon_X + icon_s] = im

"""main function"""
while True:
    merged_img = np.vstack((color_palette, shape_palette, img))
    cv2.imshow(title, merged_img)

    # restricted to the ASCII range, allowing for easier handling and comparison with specific key values.
    key = cv2.waitKey(1) & 0xFF
    if key == ord('l'):
        current_shape = 'line'

    elif key == ord('c'):
        undo_stack.append(img.copy())
        img[:] = 0
        img.fill(255)

    elif key == ord('u'):
        undo_redo()

    elif key == ord('r'):
        if len(redo_stack) > 0:
            undo_stack.append(img.copy())
            img = redo_stack.pop()

    elif key == ord('s'):
        cv2.imwrite('edited_images/new_img.jpg', img)

    elif key == ord('o'):
        open_image()

    elif key == ord('d'):
        delete_selected()

    elif key == 27:
        break

cv2.destroyAllWindows()
