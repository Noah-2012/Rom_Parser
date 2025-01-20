# Rom Parser

A small library for parsing roms.

- The batch files are useless. They come from the alpha.

---

### It is important to install these packages for python beforehand: *argparse*, *rich*, *os* and *subprocess*.

- Argparse
```bash
pip install argparse
```

- Rich
```bash
pip install rich
```

- Os
```bash
pip install os
```

- Subprocess
```bash
pip install subprocess
```

---

### Using it is very simple.

- You need to open a terminal in the respective directory (e.g. GB, GBA, GBC).
- Then enter:
```bash
make read_rom <file>
```
- Now you will see a lot of information about the ROM.

---

### Subfunctions

- You now have an input that looks like this:
  ```bash
  What do you want to do?
  [1] Display the entire ROM content
  [2] Create a HEX file
  [3] Display a specific address
  [4] Start the game in mGBA
  [5] Exit
  Please enter your selection (1/2/3/4/5):
  ```
  - Function 1 prints the entire content of the ROM in hex and ascii.
  - Function 2 does the same as function one, except that it exports the entire ROM content to a hex file.
  - Function 3 lets you display the content of a specific address (hex and ascii).
  - Function 4 starts the ROM in mGBA. Please install it first if you want.
  - Function 5 ends the script.

---

### mGBA path

- It is important that you specify the correct path in the python files.
- It should look like this:
```Python
mgba_path = 'c:\\Program Files\\mGBA\\mGBA.exe'
```
