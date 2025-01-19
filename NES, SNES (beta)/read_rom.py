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

def read_nes_rom(file_path):
    try:
        with open(file_path, "rb") as rom_file:
            rom_size = os.path.getsize(file_path)
            console.print(f"[bold green]ROM Größe:[/bold green] {rom_size} Bytes")
            
            console.print("\n[bold cyan]=== NES ROM Header Informationen ===[/bold cyan] \n")
            header = rom_file.read(16)

            magic_number = header[0:4].decode('ascii', errors='replace')
            console.print(f"[bold yellow]Magic Number (iNES):[/bold yellow] {magic_number}")

            prg_rom_size = header[4]
            console.print(f"[bold yellow]PRG-ROM Größe (16 KB Blöcke):[/bold yellow] {prg_rom_size} Blöcke")

            chr_rom_size = header[5]
            console.print(f"[bold yellow]CHR-ROM Größe (8 KB Blöcke):[/bold yellow] {chr_rom_size} Blöcke")

            flags_6 = header[6]
            console.print(f"[bold yellow]Flags 6 (Mapper, Mirroring, Battery):[/bold yellow] 0x{flags_6:02X}")

            flags_7 = header[7]
            console.print(f"[bold yellow]Flags 7 (Mapper, NES 2.0 Identification):[/bold yellow] 0x{flags_7:02X}")

            prg_ram_size = header[8] if header[8] != 0 else 8
            console.print(f"[bold yellow]PRG-RAM Größe (8 KB Blöcke):[/bold yellow] {prg_ram_size} KB")

            flags_9 = header[9]
            console.print(f"[bold yellow]Flags 9 (TV System):[/bold yellow] 0x{flags_9:02X}")

            flags_10 = header[10]
            console.print(f"[bold yellow]Flags 10 (TV System, PRG-RAM):[/bold yellow] 0x{flags_10:02X}")

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

def read_snes_rom(file_path):
    """Liest spezifische Header-Informationen für GB-ROMs und durchsucht das ROM nach Mustern."""
    try:
        with open(file_path, "rb") as rom_file:
            rom_size = os.path.getsize(file_path)
            console.print(f"[bold green]ROM Größe:[/bold green] {rom_size} Bytes")

            console.print("\n[bold cyan]=== SNES ROM Header Informationen ===[/bold cyan] \n")
            header = rom_file.read(512)  # SNES-Header liegt oft bei 0x7FC0 (LoROM) oder 0xFFC0 (HiROM)

            game_title = header[0x10:0x20].decode('ascii', errors='replace').strip()
            console.print(f"[bold yellow]Spieltitel:[/bold yellow] {game_title}")

            rom_makeup = header[0x25]
            console.print(f"[bold yellow]ROM Makeup (Speed/Type):[/bold yellow] 0x{rom_makeup:02X}")

            rom_size = header[0x27]
            console.print(f"[bold yellow]ROM Größe (2^N KB):[/bold yellow] 0x{rom_size:02X} ({2 ** rom_size} KB)")

            sram_size = header[0x28]
            console.print(f"[bold yellow]SRAM Größe (2^N KB):[/bold yellow] 0x{sram_size:02X} ({2 ** sram_size} KB)")

            license_code = header[0x29]
            console.print(f"[bold yellow]Lizenz-Code:[/bold yellow] 0x{license_code:02X}")

            version_number = header[0x2A]
            console.print(f"[bold yellow]Version:[/bold yellow] {version_number}")

            checksum = header[0x2C:0x2E]
            console.print(f"[bold yellow]Checksum (Prüfsumme):[/bold yellow] {checksum.hex().upper()}")

            complement_checksum = header[0x2E:0x30]
            console.print(f"[bold yellow]Checksum Complement:[/bold yellow] {complement_checksum.hex().upper()}")

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
    if file_extension.lower() in ('.nes', '.unf', '.fds'):
        read_nes_rom(file_path_extension)
    elif file_extension.lower() in ('.sfc', '.smc', '.fig', '.bs', '.st'):
        read_snes_rom(file_path_extension)
    else:
        print(f"{file_path_extension} hat eine unbekannte Erweiterung.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NES-ROM/SNES-Inspektor")
    parser.add_argument("rom_path", type=str, help="Pfad zur NES/SNES-ROM-Datei")
    args = parser.parse_args()

    check_file_extension(args.rom_path)
