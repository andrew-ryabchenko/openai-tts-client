from io import TextIOWrapper
from exceptions import InputDataError

class SegmentGenerator:

    infile = None
    sentences: [dict] = []
    segments: list = []
    segment_size = 0
    num_sentences = 0
    num_segments = 0
    len_text = 0

    def __init__(self, size: int, infile: TextIOWrapper) -> None:
        self.segment_size = size
        self.infile = infile

    def __del__(self) -> None:
        del self.infile

    def generate_sentences(self) -> None:
        sentence: str = ""

        while True:
            c = self.infile.read(1)
            if c == "":
                break
            if c == ".":
                sentence += c
                if len(sentence) > self.segment_size:
                    raise InputDataError(f"Sentence size beyond {self.segment_size} characters:\n\n{sentence}")
                
                self.sentences.append({"length": len(sentence), "sentence": sentence})
                sentence = ""
            else:
                sentence += c
        
        if sentence:
            if len(sentence) > self.segment_size:
                    raise InputDataError(f"Sentence size beyond {self.segment_size} characters:\n\n{sentence}")
            self.sentences.append({"length": len(sentence), "sentence": sentence})

        self.num_sentences = len(self.sentences)

    def generate_segments(self):

        segment: str = ""

        for sentence in self.sentences:
            sentence_text = sentence["sentence"]
            sentence_len = sentence["length"]
            segment_len = len(segment)

            if segment_len + sentence_len > self.segment_size:
                
                self.segments.append(segment)
                self.num_segments += 1
                self.len_text += segment_len

                #Segment constructed. Begin new segment from the current sentence.
                segment = sentence_text

            else:
                segment += sentence_text

        if segment:
            self.segments.append(segment)
            self.num_segments += 1
            self.len_text += len(segment)

if __name__ == "__main__":
    #TODO implement unit tests
    pass
