from io import TextIOWrapper

infile = open("input.txt", "r", encoding="utf-8") 
sentences: [dict] = []
sentence: str = ""
chunk: str = ""

while True:
    c = infile.read(1)
    if c == "":
        break
    if c == ".":
        sentence += c
        sentences.append({"length": len(sentence), "sentence": sentence})
        sentence = ""
    else:
        sentence += c

infile.close()

for i in range(len(sentences)):
    sentence_text = sentences[i]["sentence"]
    sentence_len = sentences[i]["length"]
    chunk_len = len(chunk)

    if chunk_len + sentence_len > 4096:
        #TODO Process chunk
        assert len(chunk) < 4097, f"Chunk too long: {len(chunk)}\n\n{chunk}"
        print(f"Length: {len(chunk)}\nContent:\n{chunk}\n\n")
        #Chunk processed. Begin new chunk from the current sentence.
        chunk = sentence_text

    else:
        chunk += sentence_text

print(f"Length: {len(chunk)}\nContent:\n{chunk}\n\n")
