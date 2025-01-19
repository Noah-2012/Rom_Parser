# Rom Parser

Eine kleine Bibliothek zum parsen von Roms.

- Die Batch files sind unnützlich. Sie kommen aus der alpha.

---

### Es ist wichtig diese Pakete für python vorher zu installieren: *argparse*, *rich*, *os* and *subprocess*.

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

### Das benutzen ist sehr simpel.

- Sie müssen ein terminal im jeweiligen Verzeichnis (z. B. GB, GBA, GBC) öffnen.
  - Geben sie dann ein:
    ```bash
    make read_rom <datei>
    ```
  - Nun werden ihnen viele Informationen angezeigt über das Rom.

---

### Unterfunktionen

- Sie haben jetzt ein input der so aussieht:
  ```bash
  Was möchten Sie tun?
  [1] Kompletter ROM-Inhalt anzeigen
  [2] HEX-Datei erstellen
  [3] Bestimmte Adresse anzeigen
  [4] Spiel in mGBA starten
  [5] Beenden
  Bitte Auswahl eingeben (1/2/3/4/5):
  ```
  - Die Funktion 1 printet ihnen den gesamten Inhalt des Roms in hex und ascii.
  - Die Funktion 2 macht das gleiche wie Funktion eins nur das er den gesamten Rom Inhalt in eine hex-Datei exportiert.
  - Bei Funktion 3 können sie sich den Inhalt einer bestimmten Adresse anzeigen lassen (Hex und Ascii).
  - Die Funktion 4 startet das Rom in mGBA. Bitte vorher auch installieren falls sie wollen.
  - Die Funktion 5 beendet das Script.
 
---

### mGBA Pfad

- Es ist wichtig das sie den richtigen Pfad in den python dateien angeben. Nicht meinen.
- Das sollte so aussehen:
```Python
mgba_path = 'c:\\Program Files\\mGBA\\mGBA.exe'
```
