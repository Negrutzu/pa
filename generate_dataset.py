import os
import cv2
import numpy as np

OUTPUT = "data/raw/"
CLASSES = ["usa_stanga", "usa_dreapta", "aripa", "capota", "portbagaj"]
IMG_SIZE = 256

def draw_usa_stanga(img):
    # contur usă stânga
    pts = np.array([
        [60, 60],
        [180, 60],
        [170, 200],
        [70, 200]
    ], dtype=np.int32)
    cv2.fillPoly(img, [pts], (255, 255, 255))
    # mâner
    cv2.rectangle(img, (150, 120), (165, 135), (0, 0, 0), -1)
    return img

def draw_usa_dreapta(img):
    # contur usă dreaptă (oglindire logică)
    pts = np.array([
        [80, 60],
        [200, 60],
        [190, 200],
        [90, 200]
    ], dtype=np.int32)
    cv2.fillPoly(img, [pts], (255, 255, 255))
    # mâner
    cv2.rectangle(img, (95, 120), (110, 135), (0, 0, 0), -1)
    return img

def draw_aripa(img):
    pts = np.array([
        [40, 180],
        [210, 180],
        [190, 120],
        [70, 100]
    ], dtype=np.int32)
    cv2.fillPoly(img, [pts], (255, 255, 255))
    return img

def draw_capota(img):
    cv2.ellipse(img, (IMG_SIZE // 2, 150), (100, 70), 0, 0, 180, (255, 255, 255), -1)
    return img

def draw_portbagaj(img):
    cv2.rectangle(img, (70, 150), (190, 220), (255, 255, 255), -1)
    cv2.line(img, (70, 150), (190, 150), (0, 0, 0), 3)
    return img

def draw_shape(cls_name):
    img = np.zeros((IMG_SIZE, IMG_SIZE, 3), dtype=np.uint8)

    if cls_name == "usa_stanga":
        return draw_usa_stanga(img)
    elif cls_name == "usa_dreapta":
        return draw_usa_dreapta(img)
    elif cls_name == "aripa":
        return draw_aripa(img)
    elif cls_name == "capota":
        return draw_capota(img)
    elif cls_name == "portbagaj":
        return draw_portbagaj(img)

    return img

def generate_images():
    for cls in CLASSES:
        cls_folder = os.path.join(OUTPUT, cls)
        os.makedirs(cls_folder, exist_ok=True)

        print(f"Generating images for {cls}...")
        for i in range(40):
            img = draw_shape(cls)

            # random small shift
            dx = np.random.randint(-5, 6)
            dy = np.random.randint(-5, 6)
            M = np.float32([[1, 0, dx], [0, 1, dy]])
            img = cv2.warpAffine(img, M, (IMG_SIZE, IMG_SIZE))

            cv2.imwrite(os.path.join(cls_folder, f"{cls}_{i}.png"), img)

    print("Dataset generated successfully!")

if __name__ == "__main__":
    generate_images()
