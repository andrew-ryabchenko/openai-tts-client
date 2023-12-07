from io import TextIOWrapper

data = """I am a feather on the bright sky
I am the blue horse that runs in the plain
I am the fish that rolls, shining, in the water
I am the shadow that follows a child
I am the evening light, the lustre of meadows
I am an eagle playing with the wind
I am a cluster of bright beads
I am the farthest star
I am the cold of dawn
I am the roaring of the rain
I am the glitter on the crust of the snow
I am the long track of the moon in a lake
I am a flame of four colors
I am a deer standing away in the dusk
I am a field of sumac and the pomme blanche
I am an angle of geese in the winter sky
I am the hunger of a young wolf
I am the whole dream of these things

You see, I am alive, I am alive
I stand in good relation to the earth
I stand in good relation to the gods
I stand in good relation to all that is beautiful
I stand in good relation to the daughter of Tsen-tainte
You see, I am alive, I am alive"""

def check_eof(file: TextIOWrapper) -> True:

    current_file_pos = file.tell()
    c = file.read(1)

    if (not c):
        return True
    
    file.seek(current_file_pos)

    return False
