import os
import cv2
import shutil
import numpy as np
from PyQt5.QtGui import QImage, QPixmap

class LoadImage:
    def __init__(self, image_files, image_label, label, remaining_label, completed_label):
        self.image_files = image_files
        self.image_label = image_label
        self.label = label
        self.remaining_label = remaining_label
        self.completed_label = completed_label
        self.magnifier = None
        
        self.image_pairs = self.find_image_pairs()
        self.current_pair_index = 0
        self.current_image_path_1 = None
        self.current_image_path_2 = None
        self.completed_count = 0
        self.create_combined_image = None
        self.prev_combined_image = None

    def find_image_pairs(self):
        files = os.listdir(self.image_files)
        base_files = set(f.replace("_debug", "") for f in files if "_debug" not in f)
        pairs = [(os.path.join(self.image_files, f), os.path.join(self.image_files, f.replace(".jpg", "_debug.jpg")))
                 for f in base_files if f.replace(".jpg", "_debug.jpg") in files]
        return pairs

    def load_next_image_pair(self):
        if self.current_pair_index < len(self.image_pairs):
            self.current_image_path_1, self.current_image_path_2 = self.image_pairs[self.current_pair_index]
            print(f"Loading images: {self.current_image_path_1}, {self.current_image_path_2}")
        
            # Load first image
            image_1 = cv2.imread(self.current_image_path_1)
            if image_1 is not None:
                image_1 = cv2.cvtColor(image_1, cv2.COLOR_BGR2RGB)
                print(f"Loaded first image with shape: {image_1.shape}")
            else:
                print(f"Failed to load image: {self.current_image_path_1}")
                image_1 = np.zeros((100, 100, 3), dtype=np.uint8)  # Placeholder for missing image
            
            # Load second image
            image_2 = cv2.imread(self.current_image_path_2)
            if image_2 is not None:
                image_2 = cv2.cvtColor(image_2, cv2.COLOR_BGR2RGB)
                print(f"Loaded second image with shape: {image_2.shape}")
            else:
                print(f"Failed to load image: {self.current_image_path_2}")
                image_2 = np.zeros((100, 100, 3), dtype=np.uint8)  # Placeholder for missing image
            
            # Resize images to the same height
            height = max(image_1.shape[0], image_2.shape[0])
            image_1 = cv2.resize(image_1, (int(image_1.shape[1] * height / image_1.shape[0]), height))
            image_2 = cv2.resize(image_2, (int(image_2.shape[1] * height / image_2.shape[0]), height))
            
            # Combine images side by side
            combined_image = np.hstack((image_2, image_1))

            # Resize combined image to fit within 1920x1080 while maintaining aspect ratio
            max_height = 1080
            max_width = 1900
            h, w, _ = combined_image.shape
            if h > max_height or w > max_width:
                scaling_factor = min(max_width / w, max_height / h)
                new_size = (int(w * scaling_factor), int(h * scaling_factor))
                combined_image = cv2.resize(combined_image, new_size)

            # Combine current image with previous combined image, if it exists
            # if self.prev_combined_image is not None:
            #     # Resize current combined image to match the previous combined image width
            #     prev_h, prev_w, _ = self.prev_combined_image.shape
            #     if prev_w != combined_image.shape[1]:
            #         combined_image = cv2.resize(combined_image, (prev_w, combined_image.shape[0]))
            #     combined_image = np.vstack((combined_image, self.prev_combined_image))

            self.create_combined_image = combined_image.copy()  # Ensure it's copied to avoid reference issues

            height, width, channel = combined_image.shape
            bytesPerLine = 3 * width
            qImg = QImage(combined_image.data, width, height, bytesPerLine, QImage.Format_RGB888)
            
            self.image_label.setPixmap(QPixmap.fromImage(qImg))
        
            # Update label to show current image name
            self.label.setText(os.path.basename(self.current_image_path_1))
            
            # Store the current combined image as the previous one for the next iteration
            self.prev_combined_image = self.create_combined_image

            self.current_pair_index += 1
            if self.magnifier:
                self.magnifier.update_image_display()
            self.update_counts()
        else:
            self.label.setText("No More Images")

    def move_image(self, category, new_name):
        '''
        Move image pairs into normal and debug respectively
        '''
        if self.current_image_path_1:
            dest_dir_normal = os.path.join(self.image_files, category, "normal")
            dest_dir_debug = os.path.join(self.image_files, category, "debug")
            if not os.path.exists(dest_dir_normal):
                os.makedirs(dest_dir_normal)
            if not os.path.exists(dest_dir_debug):
                os.makedirs(dest_dir_debug)
            
            normal_new_path = os.path.join(dest_dir_normal, (new_name + '.jpg') if new_name else os.path.basename(self.current_image_path_1))
            debug_new_path = os.path.join(dest_dir_debug, (new_name + '_debug.jpg') if new_name else os.path.basename(self.current_image_path_2))
            
            shutil.move(self.current_image_path_1, normal_new_path)
            if os.path.exists(self.current_image_path_2):
                shutil.move(self.current_image_path_2, debug_new_path)
            
            self.completed_count += 1
            self.load_next_image_pair()

    def move_image_without_creating_folders(self, category, new_name):
        '''
        Moves correct images without creating folders
        Deletes the wrong images
        '''
        dest_dir = os.path.join(self.image_files, category)  # Parent directory where 'normal' would be
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)  # Ensure the directory exists

        normal_new_path = os.path.join(dest_dir, (new_name + '.jpg') if new_name else os.path.basename(self.current_image_path_1))
        shutil.move(self.current_image_path_1, normal_new_path)
        if os.path.exists(self.current_image_path_2):  # Check if the debug image exists
            os.remove(self.current_image_path_2)  # Delete the debug image  
        self.completed_count += 1
        self.load_next_image_pair()

    def move_image_without_creating_folders_both(self, category, new_name):
        '''
        Moves image pairs into a common folder
        '''
        dest_dir = os.path.join(self.image_files, category)  # Parent directory where 'normal' would be
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)  # Ensure the directory exists

        # Generate unique paths for both images
        normal_new_path_1 = os.path.join(dest_dir, (new_name + '.jpg') if new_name else os.path.basename(self.current_image_path_1))
        normal_new_path_2 = os.path.join(dest_dir, (new_name + '_debug.jpg') if new_name else os.path.basename(self.current_image_path_2))

        # Move both images
        shutil.move(self.current_image_path_1, normal_new_path_1)
        if os.path.exists(self.current_image_path_2):  # Check if the debug image exists
            shutil.move(self.current_image_path_2, normal_new_path_2)
        
        self.completed_count += 1
        self.load_next_image_pair()

    def update_counts(self):
        remaining_count = len(self.image_pairs) - self.current_pair_index
        self.remaining_label.setText(f'Remaining: {remaining_count}')
        self.completed_label.setText(f'Completed: {self.completed_count}')
