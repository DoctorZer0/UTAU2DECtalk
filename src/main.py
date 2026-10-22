import subprocess
import os
from phoneme_map import PHONEME_MAP


# This function pareses the ust file
def parse_ust(ust_filepath):
    # Defines the dictionary holding the information of the ust file
    ust_data = {
        'settings': {},
        'notes': []
    }

    # Sets a variable for the current block being read to None initially
    current_block = None
    
    # Opens the file and reads from it
    file = open(ust_filepath, 'r', encoding='shift_jis') 
    for line in file:
        # Strips the current line
        line = line.strip()
        
        # If the line is empty after stripping, move on
        if not line:
             continue

        # Checks if it is the start of a new block
        if line.startswith('[#'):
            # If the line is the start of a new block, the type of block is checked
            if line[2:-1] == 'SETTING':
                print("Reading settings")
                # Set the current block to be the settings
                current_block = ust_data['settings']
            elif line[2:-1] == 'TRACKEND':
                # If a TRACKEND header is encountered, stop reading the file
                print("Reached track end")
                break
            elif line[2:-1].isdigit():
                # print("Reading note " + line[2:-1])
                # Set the current block to be a new note
                new_note = {}
                ust_data['notes'].append(new_note)
                current_block = new_note
            else:
                # If a header which is not recognised is encountered, warn the user and make sure no block is written to
                print("Encountered unknown header:")
                print(line)
                current_block = None
        elif '=' in line and current_block is not None:
            # If the line seems to contain a key value pair ("=") and a block is currently being written to, parse it
            # Splits the line at the equals
            key, value = line.split('=', 1)
            # Adds data to the current block
            current_block[key.strip()] = value.strip()
        else:
            # Warn the user if a line is encountered that the script doesnt know what to do with
            print("Encountered unknown line:")
            print(line)
    
    # Close file and return
    file.close()
    return ust_data

# This function creates the string for dectalk from the parsed data
def convert_to_dectalk(ust_data, default_preutterance=40):
    # Get the tempo from the ust data
    tempo = float(ust_data['settings']['Tempo'])
    
    # Begin the string for dectalk
    dectalk_string = "["

    # Iterate through the notes
    for note in ust_data["notes"]:
        # print("Converting note")

        # Get the lyric from the ust data
        ust_lyric = note["Lyric"]

        # Get the note length
        ust_length = int(note["Length"])
        # Convert the length
        length = int(round((ust_length/480) * (60000/tempo)))

        # Get pre-utterance
        try:
            pre_utterance = int(round(float(note.get('PreUtterance', ''))))
        except ValueError:
            pre_utterance = 0

        # Restrict pre_utterance to be between 0 and the length og the note
        
        pre_utterance = max(default_preutterance, pre_utterance) # floor 
        pre_utterance = min(pre_utterance, length // 2) # cap
        pre_utterance = max(1, pre_utterance) # Prevent zero (zero would result in dectalk using its default)
        
        # Get the note number
        note_number = int(note['NoteNum']) - 42

        # If the ust's lyric is mapped, convert it, if not, warn the user and replace it with a rest
        # Get just the last part of the lyric (needed for VCV)
        ust_lyric = ust_lyric.split()[-1]

        if ust_lyric not in PHONEME_MAP:
            print('Lyric "' + ust_lyric + '" not mapped, substitution rest')
            lyric = ["", "", ""]
        else:
            lyric = PHONEME_MAP[ust_lyric]
            # print(lyric)

        # Decide how to handle the lyric based on which strings are empty
        # If all strings are empty, it is a rest
        if not lyric[0] and not lyric[1] and not lyric [2]:
            dectalk_string += "_"
            dectalk_string += "<"
            dectalk_string += str(length)
            dectalk_string += ">"
        # If only the last string is used, it is a vowel
        elif not lyric[0] and not lyric[1] and lyric[2]:
            dectalk_string += lyric[2]
            dectalk_string += "<"
            dectalk_string += str(length)
            dectalk_string += ","
            dectalk_string += str(note_number)
            dectalk_string += ">"
        # If only the zeroeth string is used, it is a consonant only
        elif lyric[0] and not lyric[1] and not lyric[2]:
            dectalk_string += lyric[0]
            dectalk_string += "<"
            dectalk_string += str(length)
            dectalk_string += ","
            dectalk_string += str(note_number)
            dectalk_string += ">"
        # If both the zeroeth and last strings are used, it is a consonant and vowel pair
        elif lyric[0] and not lyric[1] and lyric[2]:
            dectalk_string += lyric[0]
            dectalk_string += "<"
            dectalk_string += str(pre_utterance)
            dectalk_string += ","
            dectalk_string += str(note_number)
            dectalk_string += ">"

            dectalk_string += lyric[2]
            dectalk_string += "<"
            dectalk_string += str(length - pre_utterance)
            dectalk_string += ","
            dectalk_string += str(note_number)
            dectalk_string += ">"
        # If all strings are used, it is a consonant, glide, and vowel
        elif lyric[0] and lyric[1] and lyric[2]:
            dectalk_string += lyric[0]
            dectalk_string += "<"
            dectalk_string += str(round(pre_utterance / 2))
            dectalk_string += ","
            dectalk_string += str(note_number)
            dectalk_string += ">"

            dectalk_string += lyric[1]
            dectalk_string += "<"
            dectalk_string += str(pre_utterance - round(pre_utterance / 2))
            dectalk_string += ","
            dectalk_string += str(note_number)
            dectalk_string += ">"

            dectalk_string += lyric[2]
            dectalk_string += "<"
            dectalk_string += str(length - pre_utterance)
            dectalk_string += ","
            dectalk_string += str(note_number)
            dectalk_string += ">"
        else:
            # If a entry in the map is not correct, warn the user and replace it with a rest
            print('Dont know what to do with map value "' + str(lyric) + '", substituting rest')
            dectalk_string += "_"
            dectalk_string += "<"
            dectalk_string += str(length)
            dectalk_string += ">"
        
    # Finish off the string and return it
    dectalk_string += "]"
    return dectalk_string


# This function runs dectalk for a string
def run_dectalk(binary_path = "dectalk/say", wav_path = "project/result.wav", text_path = "project/temp.txt"):
    print("Running dectalk")

    # Compose command
    command = [
        binary_path,
        "-pre", "[:phoneme on]",
        "-fi", text_path,
        "-fo", wav_path
    ]
   
    # print(command)
    # Run dectalk
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running DECtalk: {e}")


if __name__ == "__main__":
    print("Started")
    # Define name for file holfing the dectalk string
    dectalk_string_path = "project/temp.txt"
    # Define the path of the source ust
    ust_filepath = "project/Love Is War (Crusher Remix).ust"
    
    # Parse the ust file
    ust_data = parse_ust(ust_filepath)

    # Convert the ust file to a dectalk string
    dectalk_string = convert_to_dectalk(ust_data)
    
    # Write the dectalk string to a file
    dectalk_string_file = open(dectalk_string_path, 'w')
    dectalk_string_file.write(dectalk_string)
    dectalk_string_file.close()

    # Run dectalk
    run_dectalk(text_path=dectalk_string_path)

    print("Finished")
