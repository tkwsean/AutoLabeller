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
        self.previous_states = []
        self.remaining_count = len(self.image_pairs) - self.current_pair_index

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

    def undo_load_next_image_pair(self):
        '''
        Undo the loading of the next image pair by reverting to the previous state
        '''
        if self.previous_states:
            # Revert to the previous state
            self.current_pair_index, self.current_image_path_1, self.current_image_path_2, self.prev_combined_image = self.previous_states.pop()
        
            # Load the previous combined image
            if self.prev_combined_image is not None:
                height, width, channel = self.prev_combined_image.shape
                bytesPerLine = 3 * width
                qImg = QImage(self.prev_combined_image.data, width, height, bytesPerLine, QImage.Format_RGB888)
                self.image_label.setPixmap(QPixmap.fromImage(qImg))
                self.label.setText(os.path.basename(self.current_image_path_1))
        
            # Update the counts
            self.update_counts()
        else:
            self.label.setText("No Previous Image to Undo")


    def move_image(self, category, new_name):
        '''
        Move image pairs into normal and debug respectively
        Not currently used
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
    
    def undo_move_image(self, category, new_name):
        '''
        Undo the move operation by moving image pairs back to their original location
        Meant for keypointerror
        '''
        if self.current_image_path_1:
            dest_dir_normal = os.path.join(self.image_files, category, "normal")
            dest_dir_debug = os.path.join(self.image_files, category, "debug")
        
            normal_new_path = os.path.join(dest_dir_normal, (new_name + '.jpg') if new_name else os.path.basename(self.current_image_path_1))
            debug_new_path = os.path.join(dest_dir_debug, (new_name + '_debug.jpg') if new_name else os.path.basename(self.current_image_path_2))
        
            # Paths to move the images back to
            original_normal_path = os.path.join(self.image_files, os.path.basename(normal_new_path))
            original_debug_path = os.path.join(self.image_files, os.path.basename(debug_new_path))
        
            # Move images back to original locations
            if os.path.exists(normal_new_path):
                shutil.move(normal_new_path, original_normal_path)
            if os.path.exists(debug_new_path):
                shutil.move(debug_new_path, original_debug_path)
        
            self.completed_count -= 1
            self.remaining_count += 1
            self.current_pair_index -= 1
        
            # Reload the previous image pair
            if self.current_pair_index >= 0:
                self.current_image_path_1, self.current_image_path_2 = self.image_pairs[self.current_pair_index]
                self.load_next_image_pair()
            else:
                self.label.setText("No More Images to Undo")
                self.current_pair_index = 0  # Reset to the first image pair
        
            self.update_counts()
        
    def move_image_without_creating_folders(self, category, new_name):
        '''
        Moves correct images without creating folders
        Transfers the wrong images to a folder called to_be_deleted
        Meant for imageblur, correct, wrong
        '''
        dest_dir = os.path.join(self.image_files, category)  # Parent directory where 'normal' would be
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)  # Ensure the directory exists

        normal_new_path = os.path.join(dest_dir, (new_name + '.jpg') if new_name else os.path.basename(self.current_image_path_1))

        print(f"Moving normal image from {self.current_image_path_1} to {normal_new_path}")
        shutil.move(self.current_image_path_1, normal_new_path)

        to_be_deleted_dir = os.path.join(self.image_files, 'to_be_deleted')
        if not os.path.exists(to_be_deleted_dir):
            os.makedirs(to_be_deleted_dir)

        if os.path.exists(self.current_image_path_2):  # Check if the debug image exists
            debug_new_path = os.path.join(to_be_deleted_dir, os.path.basename(self.current_image_path_2))
            print(f"Transferring debug image {self.current_image_path_2} to {debug_new_path}")
            shutil.move(self.current_image_path_2, debug_new_path)  # Move the debug image to to_be_deleted folder
        else:
            print(f"Debug image not found: {self.current_image_path_2}")

        self.completed_count += 1
        self.load_next_image_pair()

        
    def undo_move_image_without_creating_folders(self, category, new_name):
        '''
        Undo the move operation by moving the image back to its original location
        Restores the debug image from to_be_deleted folder if it existed
        '''
        dest_dir = os.path.join(self.image_files, category)
        normal_new_path = os.path.join(dest_dir, (new_name + '.jpg') if new_name else os.path.basename(self.current_image_path_1))
        original_normal_path = os.path.join(self.image_files, os.path.basename(normal_new_path))

        to_be_deleted_dir = os.path.join(self.image_files, 'to_be_deleted')
        debug_new_path = os.path.join(to_be_deleted_dir, os.path.basename(original_normal_path).replace('.jpg', '_debug.jpg'))
        original_debug_path = os.path.join(self.image_files, os.path.basename(debug_new_path))

        try:
            # Debug information
            print(f"Undo move: category={category}, new_name={new_name}")
            print(f"Normal image paths: {normal_new_path} -> {original_normal_path}")
            print(f"Debug image paths: {debug_new_path} -> {original_debug_path}")

            # Delete the old normal image if it exists in the new folder
            if os.path.exists(normal_new_path):
                print(f"Deleting old normal image path: {normal_new_path}")
                os.remove(normal_new_path)

            # Move normal image back
            if os.path.exists(original_normal_path):
                print(f"Normal image successfully moved back to {original_normal_path}")
            else:
                print(f"Failed to move normal image back to {original_normal_path}")

            # Delete the old debug image if it exists in the new folder
            if os.path.exists(debug_new_path):
                print(f"Deleting old debug image path: {debug_new_path}")
                os.remove(debug_new_path)

            # Move debug image back
            if os.path.exists(original_debug_path):
                print(f"Debug image successfully moved back to {original_debug_path}")
            else:
                print(f"Failed to move debug image back to {original_debug_path}")

            self.completed_count -= 1
            self.remaining_count += 1
            self.current_pair_index -= 1

            if self.current_pair_index >= 0:
                self.current_image_path_1, self.current_image_path_2 = self.image_pairs[self.current_pair_index]
                self.load_next_image_pair()
            else:
                self.label.setText("No More Images to Undo")
                self.current_pair_index = 0  # Reset to the first image pair

            self.update_counts()
        except Exception as e:
            print(f"Error undoing move: {e}")


    
    def move_image_without_creating_folders_both(self, category, new_name):
        '''
        Moves image pairs into a common folder
        For keypointerror
        '''
        dest_dir = os.path.join(self.image_files, category)  # Parent directory where 'normal' would be
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)  # Ensure the directory exists

        # Generate unique paths for both images
        normal_new_path_1 = os.path.join(dest_dir, (new_name + '.jpg') if new_name else os.path.basename(self.current_image_path_1))
        normal_new_path_2 = os.path.join(dest_dir, (new_name + '_debug.jpg') if new_name else os.path.basename(self.current_image_path_2))

        try:
            # Move both images
            shutil.move(self.current_image_path_1, normal_new_path_1)
            if os.path.exists(self.current_image_path_2):  # Check if the debug image exists
                shutil.move(self.current_image_path_2, normal_new_path_2)
            else:
                print(f"Debug image not found: {self.current_image_path_2}")
        
            self.completed_count += 1
            self.load_next_image_pair()
        except Exception as e:
            print(f"Error moving images: {e}")


    def undo_move_image_without_creating_folders_both(self, category, new_name):
        '''
        Undo the move operation by moving the image pairs back to their original location
        For keypointerror
        '''
        dest_dir = os.path.join(self.image_files, category)
    
        # Paths to the moved images
        normal_new_path_1 = os.path.join(dest_dir, (new_name + '.jpg') if new_name else os.path.basename(self.current_image_path_1))
        normal_new_path_2 = os.path.join(dest_dir, (new_name + '_debug.jpg') if new_name else os.path.basename(self.current_image_path_2))
    
        # Original paths to move the images back to
        original_normal_path_1 = os.path.join(self.image_files, os.path.basename(normal_new_path_1))
        original_debug_path_2 = os.path.join(self.image_files, os.path.basename(normal_new_path_2))
    
        try:
            # Debug information
            print(f"Undo move: category={category}, new_name={new_name}")
            print(f"Normal image paths: {normal_new_path_1} -> {original_normal_path_1}")
            print(f"Debug image paths: {normal_new_path_2} -> {original_debug_path_2}")

            # Delete the old normal image if it exists in the new folder
            if os.path.exists(normal_new_path_1):
                print(f"Deleting old normal image path: {normal_new_path_1}")
                os.remove(normal_new_path_1)

            # Move normal image back
            if os.path.exists(original_normal_path_1):
                print(f"Normal image successfully moved back to {original_normal_path_1}")
            else:
                print(f"Failed to move normal image back to {original_normal_path_1}")

            # Delete the old debug image if it exists in the new folder
            if os.path.exists(normal_new_path_2):
                print(f"Deleting old debug image path: {normal_new_path_2}")
                os.remove(normal_new_path_2)

            # Move debug image back
            if os.path.exists(original_debug_path_2):
                print(f"Debug image successfully moved back to {original_debug_path_2}")
            else:
                print(f"Failed to move debug image back to {original_debug_path_2}")

            self.completed_count -= 1
            self.current_pair_index -= 1

            if self.current_pair_index >= 0:
                self.current_image_path_1, self.current_image_path_2 = self.image_pairs[self.current_pair_index]
                self.load_next_image_pair()
            else:
                self.label.setText("No More Images to Undo")
                self.current_pair_index = 0  # Reset to the first image pair

            self.update_counts()
        except Exception as e:
            print(f"Error undoing move: {e}")



    def update_counts(self):
        self.remaining_label.setText(f'Remaining: {self.remaining_count}')
        self.completed_label.setText(f'Completed: {self.completed_count}')
