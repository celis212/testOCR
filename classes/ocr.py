from config.config import  CLIENT_ID, CLIENT_SECRET,  API_KEY 
from veryfi import Client
import hashlib
import json
import os
import re

class Ocr:
  CLIENT_ID = CLIENT_ID
  CLIENT_SECRET = CLIENT_SECRET
  USERNAME = 'celis212'
  API_KEY = API_KEY
  CATEGORIES = ['Grocery', 'Utilities', 'Travel', 'Airfare', 'Lodging', 'Job Supplies']
  LOG_PATH = "./json/processing_logs.json"
  VALID_EXTENSIONS = ["jpg", "jpeg"]####
  INVALID_LIST_TO_SHIP = ["instruc", "attach", "inventory", "balanc"]

  # Constructor
  def __init__(self):
    try:
      self.veryfi_client = Client(self.CLIENT_ID, self.CLIENT_SECRET, self.USERNAME, self.API_KEY)
    except Exception as e:
      print(f"error: {e}")
      return 
    
  # Get data from the image
  # Return the data from the image
  def get_data(self, file_name: str):
    if not file_name:
      raise ValueError("You must add the file name")
    
    file_name_path = f"./img/{file_name}"

    # Check if the file exists
    if not self.is_valid_file(file_name_path):
      return {}
    
    # Generate the id of the file
    id = f"{self.generate_id(file_name_path)}"

    # Check if the file has been processed
    processed_file = self.get_processed_file(id)

    # If the file has been processed, return the result
    if bool(processed_file):
      return processed_file[0]
    
    # If the file has not been processed, process the file
    file_name_path = f"./img/{file_name}"
    process_file = self.process_file_image(file_name_path, id)

    return process_file
  
  # Get the extension of the file
  def is_valid_file(self, path: str):
    # Check if the file exists
    if not self.is_file_exist(path):
      print(f"File {path} file is empty")
      return False
    
    # Check if the file has a valid extension
    if not self.get_file_extension(path) in self.VALID_EXTENSIONS:
      print(f"File {path} has an invalid extension")
      return False
    
    return True
  
  # Check if the file exists
  def is_file_exist(self, path: str):
    if not os.path.exists(path):
      return False
    
    return True
  
  # Get the extension of the file
  def get_file_extension(self, path: str):
    return path.split(".")[-1]

  # Private methods
  # Generate the id of the file
  def generate_id(self, file_name: str):
    # Read the file
    # Generate the hash
    # Return the hash
    # using with open() as f: is a good practice because it automatically closes the file when you are done
    with open(file_name, "rb") as f:
      file_bytes = f.read()
      return hashlib.md5(file_bytes).hexdigest()

  # Get the processed file
  # Return the result of the process
  def get_processed_file(self, id: str):
    image_json = {} 

    try:
      # Set the get_documents method because it allows us to use the variable external_id to validate the file
      image_json = self.veryfi_client.get_documents(external_id=id)
    except Exception as e:
      print(f"error: {e}")

    # Check if the file has been processed
    if not image_json:
      return {}
    
    print(f"The image has already been processed")
    self.set_log_process(image_json[0])

    return image_json
  
  # Process the file
  # Return the result of the process
  def process_file_image(self, path: str, id: str):
    image_json_process = {}

    if not path or not id:
      raise ValueError("The parameters can not be empty")

    try:
      image_json_process = self.veryfi_client.process_document(path, categories=self.CATEGORIES, external_id=id)
    except Exception as e:
      print(f"error: {e}")

    # Check if the file has been processed
    if not image_json_process:
      return {}
    
    print(f"A new image has been processed")
    self.set_log_process(image_json_process)

    return image_json_process
  
  # Set the new log
  # Return the new log
  def set_log_process(self, image_info: dict):
    log_file = {}

    # Check if the file exists
    if not image_info:
      raise ValueError("El parámetro param1 no puede estar vacío.")

    # Get the id of the file
    id = image_info.get('id')

    # Check if the file exists
    if not self.is_file_exist(self.LOG_PATH):
      print(f"The log file {self.LOG_PATH} does not exist")

      # Set the log
      log_file = {"logs" : []}

      # Create the new json file to the log
      with open(self.LOG_PATH, "w") as f:
        json.dump(log_file, f, indent=2)
        print(f"File {self.LOG_PATH} created")

    # Check if the id exists
    if id and self.is_id_exist(id):
      print(f"The id {id} already exists")
      return
    
    # Read the file
    with open(self.LOG_PATH, "r") as f:
      # Get the json file
      log_file = json.load(f)

    # Set the new log
    new_log = self.set_new_log(image_info)

    # Add the new log to the json file
    log_file["logs"].append(new_log)

    # Write the file
    with open(self.LOG_PATH, "w") as f:
      # Write the json file
      json.dump(log_file, f, indent=2)

    return
  
  # Check if the id exists
  # Return true if the id exists
  def is_id_exist(self, id: str):
    # Read the file
    with open(self.LOG_PATH, "r") as f:
      # load the json file
      logs = json.load(f)

    # Check if the id exists
    for log in logs["logs"]:
      # Check if the id exists
      if log['id'] == id:
        return True
    
    return False
  
  # Set the new log
  # Return the new log
  def set_new_log(self, image_json: dict):
    log = {}

    # Set the new log
    log["id"] = image_json.get("id")
    log["external_id"] = image_json.get("external_id")
    log["file_name"] = image_json.get("img_file_name")
    log["date"] = image_json.get("created_date")

    return log
  
  def get_index(self, ocr_text: str):
    index = {}
    
    index["vendor_name"] = self.get_index_vendor_name(ocr_text)

    ship_to_and_bill_to = self.get_index_ship_and_bill(ocr_text)

    index["bill_to_name"] = ship_to_and_bill_to["ship_to_name"]
    index["bill_to_address"] = ship_to_and_bill_to["ship_to_address"]
    index["ship_to_name"] = ship_to_and_bill_to["bill_to_name"]
    index["ship_to_address"] = ship_to_and_bill_to["bill_to_address"]

    index["line_items"] = {}
    line_items = self.get_index_line_items(ocr_text)
    index["line_items"]["description"] = line_items["description"]
    index["line_items"]["quantity"] = line_items["quantity"]
    index["line_items"]["price"] = line_items["price"]

    return index  

  # Get the index of the vendor name variable in the ocr text
  def get_index_vendor_name(self, ocr_text: str):
    regex_vendor_name = r"(?<=\s)\w{2,}\s\w{4,}\s\w{2,}(?=\s{0,})"
    vendor_name_compile = re.compile(regex_vendor_name)
    index_vendor_name = vendor_name_compile.findall(ocr_text)

    # Check if the index is empty
    if len(index_vendor_name) == 0:
      return ""
    
    return index_vendor_name[0].strip()
  
  # Get the index of the ship to and bill to variables in the ocr text
  def get_index_ship_and_bill(self, ocr_text: str):
    index = {}

    # Get the index of the ship to and bill to variables in the ocr text
    ship_bill_regex = r"((?<=(TO|to):).*?(?=\w{8}\s\w{2}\s\w{5,6}))"
    ship_bill_compile = re.compile(ship_bill_regex, re.DOTALL)
    index_ship_bill = re.findall(ship_bill_compile, ocr_text)
    
    # Check if the index is empty
    if len(index_ship_bill) == 0:
      index["bill_to_name"] = ""
      index["bill_to_address"] = ""
      index["ship_to_name"] = ""
      index["ship_to_address"] = ""
      return index
    
    ship_to_and_bill_to_data = index_ship_bill[0][0]

    # filter the extracted information
    # filter for spaces between the postal code
    ship_to_and_bill_to_data = re.sub(r'([a-zA-Z]{2})\s+(\d{5})', r'\1 \2', ship_to_and_bill_to_data)
    ship_to_and_bill_to_data = re.split("\t|\n", ship_to_and_bill_to_data)
    # remove empty strings
    ship_to_and_bill_to_data = list(filter(bool, ship_to_and_bill_to_data))


    invalidation_list_compile = re.compile('|'.join(self.INVALID_LIST_TO_SHIP), re.IGNORECASE)

    # remove the invalid strings
    ship_to_and_bill_to_data = [elem for elem in ship_to_and_bill_to_data if not invalidation_list_compile.search(elem)]
    # remove the strings with less than 2 characters
    ship_to_and_bill_to_data = [x for x in ship_to_and_bill_to_data if len(x) > 2]

    # set the regexof name for bill and ship
    regex_name = r"(\w(TT|tt)\w:)"
    regex_name_compile = re.compile(regex_name, re.IGNORECASE)

    # Validate if the data have more than 7 elements
    if len(ship_to_and_bill_to_data) < 7:
      # Validate if the data have the name of the bill to
      bill_to_name = [elem for elem in ship_to_and_bill_to_data if regex_name_compile.search(elem)]

      # Validate if the data have info
      if len(bill_to_name) == 0:
        index["bill_to_name"] = ""
      else:
        bill_to_name = bill_to_name[0]
        # remove the name from the list
        ship_to_and_bill_to_data.remove(bill_to_name)
        index["bill_to_name"] = bill_to_name.split(":")[1].strip().split("\t")[0].strip()
        
      index["bill_to_address"] = " ".join(ship_to_and_bill_to_data)
      index["ship_to_name"] = ""
      index["ship_to_address"] = ""
    else:
      suppliers = []
      to_ship = []

      # split the data in two lists
      for i, column in enumerate(ship_to_and_bill_to_data):
        if i % 2 == 0:
          suppliers.append(column)
        else:
          to_ship.append(column)

      # search the name for bill
      bill_to_name = [elem for elem in suppliers if regex_name_compile.search(elem)]
      if len(bill_to_name) == 0:
        index["bill_to_name"] = ""
      else:
        # remove the name from the list
        suppliers.remove(bill_to_name[0])
        index["bill_to_name"] = bill_to_name[0].split(":")[1].strip().split("\t")[0].strip()
      
      # search the name for ship
      ship_to_name = [elem for elem in to_ship if regex_name_compile.search(elem)]
      if len(ship_to_name) == 0:
        index["ship_to_name"] = ""
      else:
        # remove the name from the list
        to_ship.remove(ship_to_name[0])
        index["ship_to_name"] = ship_to_name[0].split(":")[1].strip().split("\t")[0].strip()

      index["bill_to_address"] = " ".join(suppliers)
      index["ship_to_address"] = " ".join(to_ship)
      
    return index
  
  # Get the price, quantity and description of the line items
  def get_index_line_items(self, ocr_text: str):
    index = {}

    regex_line_items = r"((?<=PRICE).*?(?=(?:\w{9}\s\w{2}\s\w{4}\s\w{4}|\w{10}\s\w{6}\s\w{2}\.)))"
    line_items_compile = re.compile(regex_line_items, re.DOTALL)
    line_items = re.findall(line_items_compile, ocr_text)
    
    if len(line_items) == 0:
      index["description"] = {}
      index["quantity"] = ""
      index["line_items"]["price"] = ""
      return index

    line_items = line_items[0]

    # search for quantity and price
    regex_quantity_price = r"((\d{1,3}(,\d{3})*|\d+)\s*(.*?)\s*\$(\d+(\.\d{2,})?)|(Additional Separation Charge\s*\$([\d,]+\.?\d*)))"
    quantity_price_compile = re.compile(regex_quantity_price, re.DOTALL)
    quantity_price = re.findall(quantity_price_compile, line_items)

    # validate if the quantity and price are empty
    if len(quantity_price) == 0:
      index["quantity"] = ""
      index["price"] = ""
    else:
      price = []
      index["quantity"] = quantity_price[0][1]
      price.append(quantity_price[0][-4])
      if len(quantity_price) > 1:
        price.append(quantity_price[1][-1])

      index["price"] = sum([float(val) for val in price]) 
        
    # filter the line items for description
    line_items = re.split("\t|\n", line_items)
    # remove empty strings
    line_items = list(filter(bool, line_items))
    # remove the strings with only numbers and $
    line_items = [elem for elem in line_items if not elem.isdigit() and not elem.startswith('$')]
    index["description"] = " ".join(line_items)

    return index