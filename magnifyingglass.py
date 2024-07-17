# magnifyingglass.py
import cv2
import numpy as np
from PyQt5.QtGui import QImage, QPixmap

class MagnifyingGlass:
    def __init__(self, loader, magnifying_glass_size=100, magnifying_glass_zoom=2):
        self.loader = loader
        self.magnifying_glass_size = magnifying_glass_size
        self.magnifying_glass_zoom = magnifying_glass_zoom
        self.magnifying_glass_pos = None

    def draw_magnifying_glass(self, image, pos):
        if pos is None:
            return image

        x, y = pos
        h, w, _ = image.shape
        size = self.magnifying_glass_size
        zoom = self.magnifying_glass_zoom

        # Determine the region to magnify
        x1 = max(0, x - size // (2 * zoom))
        y1 = max(0, y - size // (2 * zoom))
        x2 = min(w, x + size // (2 * zoom))
        y2 = min(h, y + size // (2 * zoom))

        if x2 <= x1 or y2 <= y1:
            return image  # Return original image if invalid region

        # Extract and resize the region
        region = image[y1:y2, x1:x2]
        magnified_region = cv2.resize(region, (size, size), interpolation=cv2.INTER_LINEAR)

        # Calculate the placement position
        place_x1 = max(0, x - size // 2)
        place_y1 = max(0, y - size // 2)
        place_x2 = min(w, place_x1 + size)
        place_y2 = min(h, place_y1 + size)

        magnified_region = magnified_region[:place_y2-place_y1, :place_x2-place_x1]

        # Create a mask for the magnifying glass
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.circle(mask, (x, y), size // 2, 255, -1)

        # Combine the original image with the magnified region using the mask
        result = image.copy()
        result[place_y1:place_y2, place_x1:place_x2] = magnified_region

        result = cv2.bitwise_and(result, result, mask=mask) + cv2.bitwise_and(image, image, mask=cv2.bitwise_not(mask))

        return result

    def mouseMoveEvent(self, event):
        if self.loader.image_label.pixmap() is not None:
            self.magnifying_glass_pos = (event.x(), event.y())
            self.update_image_display()

    def update_image_display(self):
        if self.loader.current_image_path_1 and self.loader.current_image_path_2:
            combined_image = self.loader.create_combined_image
            magnified_image = self.draw_magnifying_glass(combined_image, self.magnifying_glass_pos)
            height, width, channel = magnified_image.shape
            bytesPerLine = 3 * width
            qImg = QImage(magnified_image.data, width, height, bytesPerLine, QImage.Format_RGB888)
            self.loader.image_label.setPixmap(QPixmap.fromImage(qImg))
