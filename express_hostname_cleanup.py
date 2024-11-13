import os
import datetime

TEMP_FILE = 'express_temp.txt'
MAIN_FILE = 'express.txt'

def read_txt(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return (f.read().splitlines())
    return []

def write_txt(file_path, data):
    with open(file_path, 'w') as f:
        for item in data:
            f.write(f"{item}\n")
    return True

def main():

    temp_data = read_txt(TEMP_FILE)
    if not temp_data:
        print(f"The file '{TEMP_FILE}' does not exist.")
        return
    main_data = read_txt(MAIN_FILE)

    if not main_data:
        write_txt(MAIN_FILE, temp_data)
        
    else:
        main_data.extend(temp_data)
        main_data = list(set(main_data))
        write_txt(MAIN_FILE, main_data)
    
    
    
if __name__ == "__main__":
    main()

