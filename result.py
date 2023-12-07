from collections import defaultdict

class EnumeratedByteSegments(defaultdict):
    def __missing__(self, __key):
        return None