# This function helps to sort pictures on your PC by presence of people
# It iterates over the pictures in input folder and moves them to one of the folders: with or without people accordingly
from ultralytics import YOLO
import os
from pathlib import Path

model = YOLO('yolov8n.pt')


def has_people_yolo(image_path: str) -> bool:
    """
    Function checks if people are on the picture

    :param image_path: path to the image
    :return: Bool: true or false
    """
    results = model(image_path, verbose=False)

    # class 0 in COCO dataset = person
    for result in results:
        for box in result.boxes:
            if int(box.cls) == 0: # poeple found
                return True
    return False

def sort_photos_yolo(source_folder: str,
                     with_people_folder: str,
                     without_people_folder: str):
    """
    Function moves pictures with people from source folder to with_people_folder and
    pictures with no people to without_people_folder

    :param source_folder: input folder with pictures
    :param with_people_folder: folder where the pictures with people will be moved
    :param without_people_folder: folder for pictures without people
    :return: Nothing
    """
    os.makedirs(with_people_folder, exist_ok=True)
    os.makedirs(without_people_folder, exist_ok=True)

    photos = list(Path(source_folder).glob('*'))
    total = len([p for p in photos if p.suffix.lower() in ['.jpg', '.jpeg', '.png', '.heic']])

    processed = 0
    for image_file in photos:
        if image_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.heic']:
            try:
                if has_people_yolo(str(image_file)):
                    destination = Path(with_people_folder) / image_file.name
                else:
                    destination = Path(without_people_folder) / image_file.name

                # shutil.copy2(image_file, destination)
                image_file.rename(destination)
                processed += 1
                print(f"[{processed}/{total}] ✓ {image_file.name}")
            except Exception as e:
                print(f"✗ Error with {image_file.name}: {e}")


# Usage:
#
# sort_photos_yolo(
#    source_folder=f'',
#    with_people_folder=f'{COMMON_SOURCE}/with_people',
#    without_people_folder=f'{COMMON_SOURCE}/without_people'
#    )