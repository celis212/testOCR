from classes.ocr import Ocr
import os
import re
import sys

# Check if the image name was entered
if len(sys.argv) < 2:
  print("Error: You must enter the image name")
  sys.exit(1)

# Set the path of the image folder
path_image_folder = "./img"
# Get the list of the images
file_names = os.listdir(path_image_folder)
# Get the image name
image = sys.argv[1]

# Check if the image exists
if not image in file_names:
  print("Error: The image does not exist")
  sys.exit(1)

ocr = Ocr()
data = ocr.get_data(file_name = image)

# Check if the data exists
if not data:
  print("Error: The image is not allowed")
  sys.exit(1)

# Check if the client is valid
if not re.match(r"^\wix\s\w+\s\worum", data["vendor"]["name"]):
  print("Error: The image is not allowed")
  sys.exit(1)

# Get the data of the image
data_ocr_text = data.get("ocr_text")

# Check if the data exists
if not data_ocr_text:
  print("Error: The image does not exist")
  sys.exit(1)

# Get the index of the data
index_of_data = ocr.get_index(data_ocr_text)

print(index_of_data)
