import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
import cv2
from pathlib import Path
import shutil
from ultralytics import YOLO

class SortPicturesTab:
    """Tab for sorting pictures with/without people"""

    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.input_folder = tk.StringVar()
        self.with_people_folder = tk.StringVar()
        self.without_people_folder = tk.StringVar()
        self.is_sorting = False
        self.detection_method = tk.StringVar(value="yolo")  # Default to YOLO
        self.yolo_model = None

        self.create_widgets()

    def create_widgets(self):
        # Main container
        main_container = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Info section
        info_frame = ctk.CTkFrame(main_container)
        info_frame.pack(fill=tk.X, pady=(0, 20))

        info_label = ctk.CTkLabel(
            info_frame,
            text="📸 Sort Pictures by People Detection\n\n"
                 "This tool automatically sorts your pictures into two folders:\n"
                 "• Pictures WITH people detected\n"
                 "• Pictures WITHOUT people\n\n"
                 "Select the folders below and click 'Start Sorting'",
            font=ctk.CTkFont(size=13),
            justify="left"
        )
        info_label.pack(padx=20, pady=15)

        # Detection method selection
        method_frame = ctk.CTkFrame(main_container)
        method_frame.pack(fill=tk.X, pady=(0, 20))

        method_label = ctk.CTkLabel(
            method_frame,
            text="Detection Method:",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        method_label.pack(side=tk.LEFT, padx=(10, 20))

        yolo_radio = ctk.CTkRadioButton(
            method_frame,
            text="YOLO (More Accurate)",
            variable=self.detection_method,
            value="yolo",
            font=ctk.CTkFont(size=12)
        )
        yolo_radio.pack(side=tk.LEFT, padx=(0, 20))

        haar_radio = ctk.CTkRadioButton(
            method_frame,
            text="Haar Cascade (Faster)",
            variable=self.detection_method,
            value="haar",
            font=ctk.CTkFont(size=12)
        )
        haar_radio.pack(side=tk.LEFT)

        # File picker section
        picker_frame = ctk.CTkFrame(main_container)
        picker_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Input folder
        self.create_folder_picker(
            picker_frame,
            "Input Folder:",
            "Select folder containing pictures to sort",
            self.input_folder,
            0
        )

        # With people folder
        self.create_folder_picker(
            picker_frame,
            "With People Folder:",
            "Select destination for pictures with people",
            self.with_people_folder,
            1
        )

        # Without people folder
        self.create_folder_picker(
            picker_frame,
            "Without People Folder:",
            "Select destination for pictures without people",
            self.without_people_folder,
            2
        )

        # Start button
        self.start_button = ctk.CTkButton(
            main_container,
            text="Start Sorting",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            command=self.start_sorting
        )
        self.start_button.pack(fill=tk.X, pady=(0, 15))

        # Status area
        status_frame = ctk.CTkFrame(main_container)
        status_frame.pack(fill=tk.BOTH, expand=True)

        status_label = ctk.CTkLabel(
            status_frame,
            text="Status Log:",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        status_label.pack(fill=tk.X, padx=10, pady=(10, 5))

        self.status_text = ctk.CTkTextbox(status_frame, height=150)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.status_text.insert("1.0", "Ready to sort pictures...\n")
        self.status_text.configure(state="disabled")

    def create_folder_picker(self, parent, label_text, placeholder, variable, row):
        """Create a folder picker row"""
        row_frame = ctk.CTkFrame(parent, fg_color="transparent")
        row_frame.pack(fill=tk.X, padx=10, pady=8)

        label = ctk.CTkLabel(
            row_frame,
            text=label_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            width=150,
            anchor="w"
        )
        label.pack(side=tk.LEFT, padx=(0, 10))

        entry = ctk.CTkEntry(
            row_frame,
            textvariable=variable,
            placeholder_text=placeholder,
            height=35
        )
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        browse_btn = ctk.CTkButton(
            row_frame,
            text="Browse",
            width=100,
            height=35,
            command=lambda: self.browse_folder(variable)
        )
        browse_btn.pack(side=tk.LEFT)

    @staticmethod
    def browse_folder(variable):
        """Open folder selection dialog"""
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            variable.set(folder)

    def log_status(self, message):
        """Add a message to status log"""
        self.status_text.configure(state="normal")
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.status_text.configure(state="disabled")

    def start_sorting(self):
        """Start the sorting process"""
        if self.is_sorting:
            return

        # Validate inputs
        if not self.input_folder.get():
            messagebox.showwarning("Warning", "Please select an input folder")
            return
        if not self.with_people_folder.get():
            messagebox.showwarning("Warning", "Please select a folder for pictures with people")
            return
        if not self.without_people_folder.get():
            messagebox.showwarning("Warning", "Please select a folder for pictures without people")
            return

        if not os.path.exists(self.input_folder.get()):
            messagebox.showerror("Error", "Input folder does not exist")
            return

        # Create output folders if they don't exist
        os.makedirs(self.with_people_folder.get(), exist_ok=True)
        os.makedirs(self.without_people_folder.get(), exist_ok=True)

        self.is_sorting = True
        self.start_button.configure(state="disabled", text="Sorting...")

        # Clear status
        self.status_text.configure(state="normal")
        self.status_text.delete("1.0", tk.END)
        self.status_text.configure(state="disabled")

        # Run in thread
        threading.Thread(target=self.sort_pictures, daemon=True).start()

    def has_people_yolo(self, image_path: str) -> tuple[bool, int]:
        """
        Check if people are in the picture using YOLO

        :param image_path: path to the image
        :return: tuple (has_people: bool, count: int)
        """
        if self.yolo_model is None:
            self.yolo_model = YOLO('../../yolov8n.pt')

        results = self.yolo_model(image_path, verbose=False)

        # class 0 in COCO dataset = person
        person_count = 0
        for result in results:
            for box in result.boxes:
                if int(box.cls) == 0:
                    person_count += 1

        return person_count > 0, person_count

    def sort_pictures(self):
        """Sort pictures using selected detection method"""
        try:
            method = self.detection_method.get()
            self.log_status(f"Starting picture sorting using {method.upper()} detection...")

            # Initialize detection model
            if method == "haar":
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                face_cascade = cv2.CascadeClassifier(cascade_path)

                if face_cascade.empty():
                    self.log_status("Error: Could not load face detection model")
                    self.finish_sorting()
                    return
            else:  # YOLO
                try:
                    self.log_status("Loading YOLO model (this may take a moment)...")
                    self.yolo_model = YOLO('../../yolov8n.pt')
                    self.log_status("YOLO model loaded successfully")
                except Exception as e:
                    self.log_status(f"Error loading YOLO: {str(e)}")
                    self.log_status("Please install ultralytics: pip install ultralytics")
                    self.finish_sorting()
                    return

            # Get all image files
            input_path = Path(self.input_folder.get())
            image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.heic'}
            image_files = [f for f in input_path.iterdir()
                           if f.suffix.lower() in image_extensions]

            self.log_status(f"Found {len(image_files)} images to process")

            with_people_count = 0
            without_people_count = 0
            error_count = 0

            for i, image_file in enumerate(image_files, 1):
                try:
                    has_people = False
                    people_count = 0

                    if method == "yolo":
                        # Use YOLO detection
                        has_people, people_count = self.has_people_yolo(str(image_file))
                    else:
                        # Use Haar Cascade detection
                        img = cv2.imread(str(image_file))
                        if img is None:
                            self.log_status(f"⚠️ Could not read: {image_file.name}")
                            error_count += 1
                            continue

                        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        faces = face_cascade.detectMultiScale(
                            gray,
                            scaleFactor=1.1,
                            minNeighbors=5,
                            minSize=(30, 30)
                        )
                        has_people = len(faces) > 0
                        people_count = len(faces)

                    # Determine destination
                    if has_people:
                        dest_folder = self.with_people_folder.get()
                        with_people_count += 1
                        status = f"✓ [{i}/{len(image_files)}] {image_file.name} → WITH people ({people_count} detected)"
                    else:
                        dest_folder = self.without_people_folder.get()
                        without_people_count += 1
                        status = f"✓ [{i}/{len(image_files)}] {image_file.name} → WITHOUT people"

                    # Copy file
                    dest_path = Path(dest_folder) / image_file.name

                    # Handle duplicate names
                    counter = 1
                    while dest_path.exists():
                        dest_path = Path(dest_folder) / f"{image_file.stem}_{counter}{image_file.suffix}"
                        counter += 1

                    # Copy the file
                    shutil.copy2(image_file, dest_path)

                    self.log_status(status)

                except Exception as e:
                    self.log_status(f"❌ Error processing {image_file.name}: {str(e)}")
                    error_count += 1

            # Summary
            self.log_status("\n" + "=" * 50)
            self.log_status("SORTING COMPLETE!")
            self.log_status(f"Detection method: {method.upper()}")
            self.log_status(f"Pictures with people: {with_people_count}")
            self.log_status(f"Pictures without people: {without_people_count}")
            if error_count > 0:
                self.log_status(f"Errors: {error_count}")
            self.log_status("=" * 50)

            messagebox.showinfo(
                "Success",
                f"Sorting complete!\n\n"
                f"Method: {method.upper()}\n"
                f"With people: {with_people_count}\n"
                f"Without people: {without_people_count}\n"
                f"Errors: {error_count}"
            )

        except Exception as e:
            self.log_status(f"❌ Fatal error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

        finally:
            self.finish_sorting()

    def finish_sorting(self):
        """Reset UI after sorting"""
        self.is_sorting = False
        self.start_button.configure(state="normal", text="Start Sorting")