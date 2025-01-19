import argparse
from rich.console import Console
from rich.spinner import Spinner
import os
import subprocess

console = Console()

def launch_mgba(file_path):
    """Startet das Spiel in mGBA."""
    try:
        # Pfad zur ausführbaren Datei von mGBA
        mgba_path = 'c:\\Program Files\\mGBA\\mGBA.exe'  # Standardname, falls mGBA in PATH liegt. Anpassen, falls nötig.
        
        if not os.path.isfile(file_path):
            console.print("[bold red]ROM-Datei nicht gefunden![/bold red]")
            return
        
        # Überprüfen, ob mGBA installiert ist (aufrufbar)
        result = subprocess.run([mgba_path, "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            console.print("[bold red]mGBA konnte nicht gefunden werden. Stellen Sie sicher, dass es installiert ist und im PATH liegt.[/bold red]")
            return
        
        # Spiel mit mGBA starten
        subprocess.Popen([mgba_path, file_path])
        console.print(f"[bold green]Spiel wird in mGBA gestartet: {file_path}[/bold green]")
    except FileNotFoundError:
        console.print("[bold red]Die mGBA-Executable wurde nicht gefunden. Prüfen Sie den Pfad zur mGBA-Installation.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Ein Fehler ist aufgetreten:[/bold red] {e}")

def display_rom_content(file_path):
    """Zeigt den kompletten Inhalt des ROMs mit Adressen an."""
    try:
        with open(file_path, "rb") as rom_file:
            console.print("[bold cyan]=== Kompletter ROM-Inhalt ===[/bold cyan]")
            address = 0
            while True:
                block = rom_file.read(16)  # 16 Bytes pro Zeile anzeigen
                if not block:
                    break
                hex_data = " ".join(f"{byte:02X}" for byte in block)
                ascii_data = "".join(chr(byte) if 32 <= byte <= 126 else '.' for byte in block)
                console.print(f"[bold yellow]0x{address:08X}[/bold yellow]: {hex_data:<47} | {ascii_data}")
                address += 16
    except Exception as e:
        console.print(f"[bold red]Fehler beim Anzeigen des ROM-Inhalts:[/bold red] {e}")

def export_to_hex_file(file_path):
    """Exportiert den gesamten ROM-Inhalt als HEX-Datei."""
    try:
        output_path = file_path + "_dump.hex"
        with open(file_path, "rb") as rom_file, open(output_path, "w") as hex_file:
            address = 0
            while True:
                block = rom_file.read(16)
                if not block:
                    break
                hex_data = " ".join(f"{byte:02X}" for byte in block)
                ascii_data = "".join(chr(byte) if 32 <= byte <= 126 else '.' for byte in block)
                hex_file.write(f"0x{address:08X}: {hex_data:<47} | {ascii_data}\n")
                address += 16
        console.print(f"[bold green]HEX-Dump erfolgreich erstellt: {output_path}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Fehler beim Exportieren der HEX-Datei:[/bold red] {e}")

def view_specific_address(file_path):
    """Zeigt den Inhalt einer bestimmten Adresse an."""
    try:
        with open(file_path, "rb") as rom_file:
            rom_size = os.path.getsize(file_path)
            while True:
                user_input = console.input("[bold yellow]Geben Sie eine Adresse ein (Hex, z.B. 0x00001000) oder 'exit' zum Abbrechen: [/bold yellow]")
                if user_input.lower() == "exit":
                    break
                try:
                    address = int(user_input, 16)
                    if 0 <= address < rom_size:
                        rom_file.seek(address)
                        block = rom_file.read(16)
                        hex_data = " ".join(f"{byte:02X}" for byte in block)
                        ascii_data = "".join(chr(byte) if 32 <= byte <= 126 else '.' for byte in block)
                        console.print(f"[bold yellow]0x{address:08X}[/bold yellow]: {hex_data:<47} | {ascii_data}")
                    else:
                        console.print("[bold red]Die eingegebene Adresse liegt außerhalb der ROM-Größe.[/bold red]")
                except ValueError:
                    console.print("[bold red]Ungültige Adresse. Bitte geben Sie eine gültige Hex-Adresse ein.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Fehler beim Anzeigen der Adresse:[/bold red] {e}")

def read_gba_rom(file_path):
    try:
        with open(file_path, "rb") as rom_file:
            rom_size = os.path.getsize(file_path)
            console.print(f"[bold green]ROM Größe:[/bold green] {rom_size} Bytes")
            
            console.print("\n[bold cyan]=== GBA ROM Header Informationen ===[/bold cyan] \n")
            header = rom_file.read(192)

            entry_point = header[0:4]
            console.print(f"[bold yellow]Entry Point:[/bold yellow] {entry_point.hex().upper()}")

            nintendo_logo = header[4:0xA0]
            console.print(f"[bold yellow]Nintendo-Logo (hex):[/bold yellow] {nintendo_logo.hex().upper()}")

            game_title = header[0xA0:0xAC].decode('ascii', errors='replace').strip()
            console.print(f"[bold yellow]Spieltitel:[/bold yellow] {game_title}")

            game_code = header[0xAC:0xB0].decode('ascii', errors='replace')
            console.print(f"[bold yellow]Spielcode:[/bold yellow] {game_code}")

            maker_code = header[0xB0:0xB2].decode('ascii', errors='replace')
            console.print(f"[bold yellow]Hersteller-Code:[/bold yellow] {maker_code}")

            fixed_value = header[0xB2]
            console.print(f"[bold yellow]Fixed Value:[/bold yellow] 0x{fixed_value:02X}")

            unit_code = header[0xB3]
            console.print(f"[bold yellow]Einheitencode:[/bold yellow] 0x{unit_code:02X}")

            device_capacity = header[0xB4]
            console.print(f"[bold yellow]Gerätekapazität:[/bold yellow] 0x{device_capacity:02X}")

            software_version = header[0xB7]
            console.print(f"[bold yellow]Software-Version:[/bold yellow] {software_version}")

            checksum = header[0xB8]
            console.print(f"[bold yellow]Checksum (Complement Check):[/bold yellow] 0x{checksum:02X}")

            console.print("\n[bold cyan]=== ROM-Durchsuchung ===[/bold cyan]")

            rom_file.seek(0)
            important_info = []

            with console.status("[bold cyan]Durchsuche ROM...", spinner="dots") as status:
                block_size = 4096
                block_count = 0
                total_blocks = rom_size // block_size + (1 if rom_size % block_size != 0 else 0)

                while True:
                    block = rom_file.read(block_size)
                    if not block:
                        break
                    if b"SAVE" in block or b"GAME" in block:
                        important_info.append((rom_file.tell() - block_size, block[:16]))
                    block_count += 1

            console.print(f"\n[bold green]Durchsuchung abgeschlossen:[/bold green] {block_count} Blöcke verarbeitet.")

            console.print("\n[bold cyan]=== Gefundene wichtige Informationen ===[/bold cyan]")
            if important_info:
                for address, data in important_info:
                    console.print(f"[bold yellow]Adresse:[/bold yellow] 0x{address:08X} [bold yellow]Daten (Hex):[/bold yellow] {data.hex().upper()}...")
            else:
                console.print("[bold red]Keine spezifischen Muster gefunden.[/bold red]")

            while True:
                console.print("\n[bold cyan]Was möchten Sie tun?[/bold cyan]")
                console.print("[1] Kompletter ROM-Inhalt anzeigen")
                console.print("[2] HEX-Datei erstellen")
                console.print("[3] Bestimmte Adresse anzeigen")
                console.print("[4] Spiel in mGBA starten")
                console.print("[5] Beenden")

                choice = console.input("[bold yellow]Bitte Auswahl eingeben (1/2/3/4/5): [/bold yellow]")

                if choice == "1":
                    display_rom_content(file_path)
                elif choice == "2":
                    export_to_hex_file(file_path)
                elif choice == "3":
                    view_specific_address(file_path)
                elif choice == "4":
                    launch_mgba(file_path)
                elif choice == "5":
                    console.print("[bold green]Programm beendet.[/bold green]")
                    break
                else:
                    console.print("[bold red]Ungültige Auswahl. Bitte versuchen Sie es erneut.[/bold red]")

    except FileNotFoundError:
        console.print("[bold red]Die angegebene Datei wurde nicht gefunden.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Ein Fehler ist aufgetreten:[/bold red] {e}")

def read_gb_rom(file_path):
    """Liest spezifische Header-Informationen für GB-ROMs und durchsucht das ROM nach Mustern."""
    try:
        with open(file_path, "rb") as rom_file:
            rom_size = os.path.getsize(file_path)
            console.print(f"[bold green]ROM Größe:[/bold green] {rom_size} Bytes")

            console.print("\n[bold cyan]=== GB ROM Header Informationen ===[/bold cyan] \n")

            # Entry Point
            rom_file.seek(0x0100)
            entry_point = rom_file.read(4)
            console.print(f"[bold yellow]Entry Point:[/bold yellow] {entry_point.hex().upper()}")

            # Nintendo-Logo (hex)
            rom_file.seek(0x0104)
            nintendo_logo = rom_file.read(48)  # 48 Bytes für das Nintendo-Logo
            console.print(f"[bold yellow]Nintendo-Logo (hex):[/bold yellow] {nintendo_logo.hex().upper()}")

            # Spieltitel
            rom_file.seek(0x0134)
            game_title = rom_file.read(16).decode('ascii', errors='replace').strip()
            console.print(f"[bold yellow]Spieltitel:[/bold yellow] {game_title}")

            # Hersteller-Code
            rom_file.seek(0x0143)
            maker_code = rom_file.read(1)[0]
            console.print(f"[bold yellow]Hersteller-Code:[/bold yellow] 0x{maker_code:02X}")

            # Fixed Value
            rom_file.seek(0x0144)
            fixed_value = rom_file.read(1)[0]
            console.print(f"[bold yellow]Fixed Value:[/bold yellow] 0x{fixed_value:02X}")

            # Einheitencode
            rom_file.seek(0x0145)
            unit_code = rom_file.read(1)[0]
            console.print(f"[bold yellow]Einheitencode:[/bold yellow] 0x{unit_code:02X}")

            # Gerätekapazität
            rom_file.seek(0x0146)
            device_capacity = rom_file.read(1)[0]
            console.print(f"[bold yellow]Gerätekapazität:[/bold yellow] 0x{device_capacity:02X}")

            # Software-Version
            rom_file.seek(0x0147)
            software_version = rom_file.read(1)[0]
            console.print(f"[bold yellow]Software-Version:[/bold yellow] {software_version}")

            # === ROM-Durchsuchung ===
            console.print("\n[bold cyan]=== ROM-Durchsuchung ===[/bold cyan]")

            rom_file.seek(0)
            important_info = []

            with console.status("[bold cyan]Durchsuche ROM...", spinner="dots") as status:
                block_size = 4096
                block_count = 0
                total_blocks = rom_size // block_size + (1 if rom_size % block_size != 0 else 0)

                while True:
                    block = rom_file.read(block_size)
                    if not block:
                        break
                    if b"SAVE" in block or b"GAME" in block:
                        important_info.append((rom_file.tell() - block_size, block[:16]))
                    block_count += 1

            console.print(f"\n[bold green]Durchsuchung abgeschlossen:[/bold green] {block_count} Blöcke verarbeitet.")

            console.print("\n[bold cyan]=== Gefundene wichtige Informationen ===[/bold cyan]")
            if important_info:
                for address, data in important_info:
                    console.print(f"[bold yellow]Adresse:[/bold yellow] 0x{address:08X} [bold yellow]Daten (Hex):[/bold yellow] {data.hex().upper()}...")
            else:
                console.print("[bold red]Keine spezifischen Muster gefunden.[/bold red]")

            # Interaktives Menü für weitere Optionen
            while True:
                console.print("\n[bold cyan]Was möchten Sie tun?[/bold cyan]")
                console.print("[1] Kompletter ROM-Inhalt anzeigen")
                console.print("[2] HEX-Datei erstellen")
                console.print("[3] Bestimmte Adresse anzeigen")
                console.print("[4] Spiel in mGBA starten")
                console.print("[5] Beenden")

                choice = console.input("[bold yellow]Bitte Auswahl eingeben (1/2/3/4/5): [/bold yellow]")

                if choice == "1":
                    display_rom_content(file_path)
                elif choice == "2":
                    export_to_hex_file(file_path)
                elif choice == "3":
                    view_specific_address(file_path)
                elif choice == "4":
                    launch_mgba(file_path)
                elif choice == "5":
                    console.print("[bold green]Programm beendet.[/bold green]")
                    break
                else:
                    console.print("[bold red]Ungültige Auswahl. Bitte versuchen Sie es erneut.[/bold red]")

    except FileNotFoundError:
        console.print("[bold red]Die angegebene Datei wurde nicht gefunden.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Ein Fehler ist aufgetreten:[/bold red] {e}")

def read_gbc_rom(file_path):
    """Liest spezifische Header-Informationen für GBC-ROMs und durchsucht das ROM nach Mustern."""
    try:
        with open(file_path, "rb") as rom_file:
            rom_size = os.path.getsize(file_path)
            console.print(f"[bold green]ROM Größe:[/bold green] {rom_size} Bytes")

            console.print("\n[bold cyan]=== GB ROM Header Informationen ===[/bold cyan] \n")

                        # Entry Point (Standard ist oft 0x0100)
            rom_file.seek(0x0100)
            entry_point = rom_file.read(4)
            console.print(f"[bold yellow]Entry Point:[/bold yellow] {entry_point.hex().upper()}")

            # Nintendo-Logo (hex) (bleibt unverändert)
            rom_file.seek(0x0104)
            nintendo_logo = rom_file.read(48)  # 48 Bytes für das Nintendo-Logo
            console.print(f"[bold yellow]Nintendo-Logo (hex):[/bold yellow] {nintendo_logo.hex().upper()}")

            # Spieltitel (bis 16 Zeichen, ab Adresse 0x0134)
            rom_file.seek(0x0134)
            game_title = rom_file.read(16).decode('ascii', errors='replace').strip()
            console.print(f"[bold yellow]Spieltitel:[/bold yellow] {game_title}")

            # Hersteller-Code (ab Adresse 0x013F bis 0x0141)
            rom_file.seek(0x013F)
            maker_code = rom_file.read(2)  # 2 Bytes für den Hersteller-Code
            console.print(f"[bold yellow]Hersteller-Code:[/bold yellow] 0x{maker_code.hex().upper()}")

            # Fixed Value (ab Adresse 0x014D bis 0x014E)
            rom_file.seek(0x014D)
            fixed_value = rom_file.read(2)  # 2 Bytes für den Fixed Value
            console.print(f"[bold yellow]Fixed Value:[/bold yellow] 0x{fixed_value.hex().upper()}")

            # Einheitencode (ab Adresse 0x0144 bis 0x0145)
            rom_file.seek(0x0144)
            unit_code = rom_file.read(2)  # 2 Bytes für den Einheitencode
            console.print(f"[bold yellow]Einheitencode:[/bold yellow] 0x{unit_code.hex().upper()}")

            # Gerätekapazität (ab Adresse 0x0146)
            rom_file.seek(0x0146)
            device_capacity = rom_file.read(1)  # 1 Byte für die Gerätekapazität
            console.print(f"[bold yellow]Gerätekapazität:[/bold yellow] 0x{device_capacity.hex().upper()}")

            # Software-Version (ab Adresse 0x014C)
            rom_file.seek(0x014C)
            software_version = rom_file.read(1)  # 1 Byte für die Software-Version
            console.print(f"[bold yellow]Software-Version:[/bold yellow] {software_version[0]}")


            # === ROM-Durchsuchung ===
            console.print("\n[bold cyan]=== ROM-Durchsuchung ===[/bold cyan]")

            rom_file.seek(0)
            important_info = []

            with console.status("[bold cyan]Durchsuche ROM...", spinner="dots") as status:
                block_size = 4096
                block_count = 0
                total_blocks = rom_size // block_size + (1 if rom_size % block_size != 0 else 0)

                while True:
                    block = rom_file.read(block_size)
                    if not block:
                        break
                    if b"SAVE" in block or b"GAME" in block:
                        important_info.append((rom_file.tell() - block_size, block[:16]))
                    block_count += 1

            console.print(f"\n[bold green]Durchsuchung abgeschlossen:[/bold green] {block_count} Blöcke verarbeitet.")

            console.print("\n[bold cyan]=== Gefundene wichtige Informationen ===[/bold cyan]")
            if important_info:
                for address, data in important_info:
                    console.print(f"[bold yellow]Adresse:[/bold yellow] 0x{address:08X} [bold yellow]Daten (Hex):[/bold yellow] {data.hex().upper()}...")
            else:
                console.print("[bold red]Keine spezifischen Muster gefunden.[/bold red]")

            # Interaktives Menü für weitere Optionen
            while True:
                console.print("\n[bold cyan]Was möchten Sie tun?[/bold cyan]")
                console.print("[1] Kompletter ROM-Inhalt anzeigen")
                console.print("[2] HEX-Datei erstellen")
                console.print("[3] Bestimmte Adresse anzeigen")
                console.print("[4] Spiel in mGBA starten")
                console.print("[5] Beenden")

                choice = console.input("[bold yellow]Bitte Auswahl eingeben (1/2/3/4/5): [/bold yellow]")

                if choice == "1":
                    display_rom_content(file_path)
                elif choice == "2":
                    export_to_hex_file(file_path)
                elif choice == "3":
                    view_specific_address(file_path)
                elif choice == "4":
                    launch_mgba(file_path)
                elif choice == "5":
                    console.print("[bold green]Programm beendet.[/bold green]")
                    break
                else:
                    console.print("[bold red]Ungültige Auswahl. Bitte versuchen Sie es erneut.[/bold red]")

    except FileNotFoundError:
        console.print("[bold red]Die angegebene Datei wurde nicht gefunden.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Ein Fehler ist aufgetreten:[/bold red] {e}")

def check_file_extension(file_path_extension):
    # Extrahiere den Dateinamen und die Erweiterung
    file_name, file_extension = os.path.splitext(file_path_extension)

    # Überprüfe, ob die Datei eine .gb oder .gba Erweiterung hat
    if file_extension.lower() == '.gb':
        read_gb_rom(file_path_extension)
    elif file_extension.lower() == '.gba':
        read_gba_rom(file_path_extension)
    elif file_extension.lower() == '.gbc':
        read_gbc_rom(file_path_extension)
    else:
        print(f"{file_path_extension} hat eine unbekannte Erweiterung.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GBA-ROM-Inspektor")
    parser.add_argument("rom_path", type=str, help="Pfad zur GBA-ROM-Datei")
    args = parser.parse_args()

    check_file_extension(args.rom_path)
