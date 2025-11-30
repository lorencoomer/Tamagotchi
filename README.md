## Tamagotchi

A simple virtual pet written in Python. Includes both a terminal version  
and a Tkinter GUI version.

### Features

*   Hunger, happiness, and energy stats
*   Time-based stat decay
*   Mood system
*   ASCII face expressions
*   Feed, play, sleep, pet, insult actions
*   Automatic save/load using `save.json`

### Running

GUI version:

```plaintext
python3 tktama.py
```

Terminal version:

```plaintext
python3 tama.py
```

### Requirements

*   Python 3
*   Tkinter

### Save File

The pet's data is stored in `save.json`. Delete the file to reset  
progress.

### Project Structure

*   `tktama.py` - GUI version
*   `tama.py` - terminal version
*   `save.json` - save data (generated automatically)
