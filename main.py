from io import TextIOWrapper
from utils import check_eof

chunk: str = ""
len_chunk = 0
last_period_position = 0

infile = open("input.txt", "r", encoding="utf-8") 
running = True

while running:

    #Read next 4096 characters
    while len_chunk < 4096:
        c = infile.read(1)
        if c == "." or c == ";":
            last_period_position = infile.tell() - 1
        chunk += c
        len_chunk += 1

    #Truncate extra chunk's content that comes after the last period
    current_file_pos = infile.tell()
    chunk = chunk[0: -(current_file_pos - last_period_position)]

    #Check for EOF
    if (check_eof(infile)):
        running = False
    #Seek file to the position immediately after the last period
    else:
        infile.seek(last_period_position + 1)

    assert len(chunk) < 4097, "Chunk length > 4096 characters"
    chunk += "."
    print(f"Length: {len(chunk)}\nContent:\n{chunk}\n\n")

    chunk = ""
    len_chunk = 0

infile.close()



    


