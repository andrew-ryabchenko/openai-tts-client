from io import TextIOWrapper

def check_eof(file: TextIOWrapper) -> True:

    current_file_pos = file.tell()
    c = file.read(1)

    if (not c):
        return True
    
    file.seek(current_file_pos)

    return False
