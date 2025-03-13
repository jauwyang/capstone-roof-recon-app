import cv2
import numpy as np
import os

def stitch_images(images):
    # Initialize OpenCV stitcher
    stitcher = cv2.Stitcher_create()
    
    # Stitch images together
    status, stitched = stitcher.stitch(images)
    
    if status == cv2.Stitcher_OK:
        return stitched
    else:
        print("Stitching failed with status:", status)
        return None

    

def load_images_from_folder(folder):
    """Loads all images from a given folder, regardless of type, without using glob."""
    valid_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}
    
    # Get all file names in the folder
    files = os.listdir(folder)

    # Filter and load images
    images = []
    for file in sorted(files):  # Sorting to maintain order
        ext = os.path.splitext(file)[1].lower()  # Extract file extension
        if ext in valid_extensions:
            img_path = os.path.join(folder, file)
            img = cv2.imread(img_path)
            if img is not None:
                images.append(img)

    print(f"Loaded {len(images)} images.")
    return images

images = load_images_from_folder("./top_roof")

stitch = stitch_images(images)


if stitch is not None:
    cv2.imshow("Stitched Roof", stitch)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imwrite("stitched_roof.jpg", stitch)