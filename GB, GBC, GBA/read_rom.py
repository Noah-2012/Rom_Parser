import argparse
from rich.console import Console
from rich.spinner import Spinner
import os
import subprocess

console = Console()

def launch_mgba(file_path):
    """Startet das Spiel in mGBA."""
    try:
        
        # Path to mGBA executable file
        mgba_path = 'c:\\Program Files\\mGBA\\mGBA.exe'  # Default name if mGBA is in PATH. Adjust if necessary.
        
        if not os.path.isfile(file_path):
            console.print("[bold red]ROM file not found![/bold red]")
            return
        
        # Check if mGBA is installed (accessible)
        result = subprocess.run([mgba_path, "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            console.print("[bold red]mGBA could not be found. Make sure it is installed and in the PATH.[/bold red]")
            return
        
        # Start game with mGBA
        subprocess.Popen([mgba_path, file_path])
        console.print(f"[bold green]Game is started in mGBA: {file_path}[/bold green]")
    except FileNotFoundError:
        console.print("[bold red]The mGBA executable was not found. Check the path to the mGBA installation.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An error has occurred: [/bold red] {e}")

def display_rom_content(file_path):
    """Displays the complete contents of the ROM with addresses."""
    try:
        with open(file_path, "rb") as rom_file:
            console.print("[bold cyan]=== Complete ROM content ===[/bold cyan]")
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
        console.print(f"[bold red]Error displaying ROM contents: [/bold red] {e}")

def export_to_hex_file(file_path):
    """Exports the entire ROM contents as a HEX file."""
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
        console.print(f"[bold green]HEX dump created successfully: {output_path}[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error exporting HEX file:[/bold red] {e}")

def view_specific_address(file_path):
    """Displays the contents of a specific address."""
    try:
        with open(file_path, "rb") as rom_file:
            rom_size = os.path.getsize(file_path)
            while True:
                user_input = console.input("[bold yellow]Enter an address (hex, e.g. 0x00001000) or 'exit' to cancel: [/bold yellow]")
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
                        console.print("[bold red]The entered address is outside the ROM size.[/bold red]")
                except ValueError:
                    console.print("[bold red]Invalid address. Please enter a valid hex address.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error displaying address:[/bold red] {e}")

def read_gba_rom(file_path):
    try:
        with open(file_path, "rb") as rom_file:
            rom_size = os.path.getsize(file_path)
            console.print(f"[bold green]ROM size:[/bold green] {rom_size} Bytes")
            
            console.print("\n[bold cyan]=== GBA ROM Header Information ===[/bold cyan] \n")
            header = rom_file.read(192)

            entry_point = header[0:4]
            console.print(f"[bold yellow]Entry Point:[/bold yellow] {entry_point.hex().upper()}")

            nintendo_logo = header[4:0xA0]
            console.print(f"[bold yellow]Nintendo-Logo (hex):[/bold yellow] {nintendo_logo.hex().upper()}")

            game_title = header[0xA0:0xAC].decode('ascii', errors='replace').strip()
            console.print(f"[bold yellow]Game title:[/bold yellow] {game_title}")

            game_code = header[0xAC:0xB0].decode('ascii', errors='replace')
            console.print(f"[bold yellow]Spielcode:[/bold yellow] {game_code}")

            maker_code = header[0xB0:0xB2].decode('ascii', errors='replace')
            console.print(f"[bold yellow]Manufacturer code:[/bold yellow] {maker_code}")

            fixed_value = header[0xB2]
            console.print(f"[bold yellow]Fixed Value:[/bold yellow] 0x{fixed_value:02X}")

            unit_code = header[0xB3]
            console.print(f"[bold yellow]Unit code:[/bold yellow] 0x{unit_code:02X}")

            device_capacity = header[0xB4]
            console.print(f"[bold yellow]Device capacity:[/bold yellow] 0x{device_capacity:02X}")

            software_version = header[0xB7]
            console.print(f"[bold yellow]Software-Version:[/bold yellow] {software_version}")

            checksum = header[0xB8]
            console.print(f"[bold yellow]Checksum (Complement Check):[/bold yellow] 0x{checksum:02X}")

            console.print("\n[bold cyan]=== ROM search ===[/bold cyan]")

            rom_file.seek(0)
            important_info = []

            with console.status("[bold cyan]Search ROM...", spinner="dots") as status:
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

            console.print(f"\n[bold green]Search completed:[/bold green] {block_count} Blöcke verarbeitet.")

            console.print("\n[bold cyan]=== Important information found ===[/bold cyan]")
            if important_info:
                for address, data in important_info:
                    console.print(f"[bold yellow]Address:[/bold yellow] 0x{address:08X} [bold yellow]Data (Hex):[/bold yellow] {data.hex().upper()}...")
            else:
                console.print("[bold red]No specific patterns found.[/bold red]")

            while True:
                console.print("\n[bold cyan]What would you like to do?[/bold cyan]")
                console.print("[1] Show complete ROM contents")
                console.print("[2] Create HEX file")
                console.print("[3] Show specific address")
                console.print("[4] Start game in mGBA")
                console.print("[5] Exit")

                choice = console.input("[bold yellow]Please enter selection (1/2/3/4/5): [/bold yellow]")

                if choice == "1":
                    display_rom_content(file_path)
                elif choice == "2":
                    export_to_hex_file(file_path)
                elif choice == "3":
                    view_specific_address(file_path)
                elif choice == "4":
                    launch_mgba(file_path)
                elif choice == "5":
                    console.print("[bold green]Program ended.[/bold green]")
                    break
                else:
                    console.print("[bold red]Invalid selection. Please try again.[/bold red]")

    except FileNotFoundError:
        console.print("[bold red]The specified file was not found.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An error has occurred:[/bold red] {e}")

def read_gb_rom(file_path):
    """Reads GB ROM specific header information and scans the ROM for patterns."""
    try:
        with open(file_path, "rb") as rom_file:
            rom_size = os.path.getsize(file_path)
            console.print(f"[bold green]ROM size:[/bold green] {rom_size} Bytes")

            console.print("\n[bold cyan]=== GB ROM Header Information ===[/bold cyan] \n")

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
            console.print(f"[bold yellow]Game title:[/bold yellow] {game_title}")

            # Hersteller-Code
            rom_file.seek(0x0143)
            maker_code = rom_file.read(1)[0]
            console.print(f"[bold yellow]Manufacturer code:[/bold yellow] 0x{maker_code:02X}")

            # Fixed Value
            rom_file.seek(0x0144)
            fixed_value = rom_file.read(1)[0]
            console.print(f"[bold yellow]Fixed Value:[/bold yellow] 0x{fixed_value:02X}")

            # Einheitencode
            rom_file.seek(0x0145)
            unit_code = rom_file.read(1)[0]
            console.print(f"[bold yellow]Unit code:[/bold yellow] 0x{unit_code:02X}")

            # Gerätekapazität
            rom_file.seek(0x0146)
            device_capacity = rom_file.read(1)[0]
            console.print(f"[bold yellow]Device capacity:[/bold yellow] 0x{device_capacity:02X}")

            # Software-Version
            rom_file.seek(0x0147)
            software_version = rom_file.read(1)[0]
            console.print(f"[bold yellow]Software-Version:[/bold yellow] {software_version}")

            # === ROM-Durchsuchung ===
            console.print("\n[bold cyan]=== ROM search ===[/bold cyan]")

            rom_file.seek(0)
            important_info = []

            with console.status("[bold cyan]Search ROM...", spinner="dots") as status:
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

            console.print(f"\n[bold green]Search completed:[/bold green] {block_count} Blöcke verarbeitet.")

            console.print("\n[bold cyan]=== Important information found ===[/bold cyan]")
            if important_info:
                for address, data in important_info:
                    console.print(f"[bold yellow]Address:[/bold yellow] 0x{address:08X} [bold yellow]Data (Hex):[/bold yellow] {data.hex().upper()}...")
            else:
                console.print("[bold red]No specific patterns found.[/bold red]")

            # Interactive menu for further options
            while True:
                console.print("\n[bold cyan]What would you like to do?[/bold cyan]")
                console.print("[1] Show complete ROM contents")
                console.print("[2] Create HEX file")
                console.print("[3] Show specific address")
                console.print("[4] Start game in mGBA")
                console.print("[5] Exit")

                choice = console.input("[bold yellow]Please enter selection (1/2/3/4/5): [/bold yellow]")

                if choice == "1":
                    display_rom_content(file_path)
                elif choice == "2":
                    export_to_hex_file(file_path)
                elif choice == "3":
                    view_specific_address(file_path)
                elif choice == "4":
                    launch_mgba(file_path)
                elif choice == "5":
                    console.print("[bold green]Program ended.[/bold green]")
                    break
                else:
                    console.print("[bold red]Invalid selection. Please try again.[/bold red]")

    except FileNotFoundError:
        console.print("[bold red]The specified file was not found.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An error has occurred:[/bold red] {e}")

def read_gbc_rom(file_path):
    """Reads header information specific to GBC ROMs and scans the ROM for patterns."""
    try:
        with open(file_path, "rb") as rom_file:
            rom_size = os.path.getsize(file_path)
            console.print(f"[bold green]ROM size:[/bold green] {rom_size} Bytes")

            console.print("\n[bold cyan]=== GB ROM Header Information ===[/bold cyan] \n")

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
            console.print(f"[bold yellow]Game title:[/bold yellow] {game_title}")

            # Hersteller-Code (ab Adresse 0x013F bis 0x0141)
            rom_file.seek(0x013F)
            maker_code = rom_file.read(2)  # 2 Bytes für den Hersteller-Code
            console.print(f"[bold yellow]Manufacturer code:[/bold yellow] 0x{maker_code.hex().upper()}")

            # Fixed Value (ab Adresse 0x014D bis 0x014E)
            rom_file.seek(0x014D)
            fixed_value = rom_file.read(2)  # 2 Bytes für den Fixed Value
            console.print(f"[bold yellow]Fixed Value[/bold yellow] 0x{fixed_value.hex().upper()}")

            # Einheitencode (ab Adresse 0x0144 bis 0x0145)
            rom_file.seek(0x0144)
            unit_code = rom_file.read(2)  # 2 Bytes für den Einheitencode
            console.print(f"[bold yellow]Unit code:[/bold yellow] 0x{unit_code.hex().upper()}")

            # Gerätekapazität (ab Adresse 0x0146)
            rom_file.seek(0x0146)
            device_capacity = rom_file.read(1)  # 1 Byte für die Gerätekapazität
            console.print(f"[bold yellow]Device capacity:[/bold yellow] 0x{device_capacity.hex().upper()}")

            # Software-Version (ab Adresse 0x014C)
            rom_file.seek(0x014C)
            software_version = rom_file.read(1)  # 1 Byte für die Software-Version
            console.print(f"[bold yellow]Software-Version:[/bold yellow] {software_version[0]}")


            # === ROM search ===
            console.print("\n[bold cyan]=== ROM search ===[/bold cyan]")

            rom_file.seek(0)
            important_info = []

            with console.status("[bold cyan]Search ROM...", spinner="dots") as status:
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

            console.print(f"\n[bold green]Search completed:[/bold green] {block_count} Blöcke verarbeitet.")

            console.print("\n[bold cyan]=== Important information found ===[/bold cyan]")
            if important_info:
                for address, data in important_info:
                    console.print(f"[bold yellow]Address:[/bold yellow] 0x{address:08X} [bold yellow]Data (Hex):[/bold yellow] {data.hex().upper()}...")
            else:
                console.print("[bold red]No specific patterns found.[/bold red]")

            # Interactive menu for further options
            while True:
                console.print("\n[bold cyan]What would you like to do?[/bold cyan]")
                console.print("[1] Show complete ROM contents")
                console.print("[2] Create HEX file")
                console.print("[3] Show specific address")
                console.print("[4] Start game in mGBA")
                console.print("[5] Exit")

                choice = console.input("[bold yellow]Please enter selection (1/2/3/4/5): [/bold yellow]")

                if choice == "1":
                    display_rom_content(file_path)
                elif choice == "2":
                    export_to_hex_file(file_path)
                elif choice == "3":
                    view_specific_address(file_path)
                elif choice == "4":
                    launch_mgba(file_path)
                elif choice == "5":
                    console.print("[bold green]Program ended.[/bold green]")
                    break
                else:
                    console.print("[bold red]Invalid selection. Please try again.[/bold red]")

    except FileNotFoundError:
        console.print("[bold red]The specified file was not found.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An error has occurred:[/bold red] {e}")

def check_file_extension(file_path_extension):
    # Extract the file name and extension
    file_name, file_extension = os.path.splitext(file_path_extension)

    # Check if the file has a .gb, .gba or .gbc extension
    if file_extension.lower() == '.gb':
        read_gb_rom(file_path_extension)
    elif file_extension.lower() == '.gba':
        read_gba_rom(file_path_extension)
    elif file_extension.lower() == '.gbc':
        read_gbc_rom(file_path_extension)
    else:
        print(f"{file_path_extension} has an unknown extension.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GBA-ROM-Inspektor")
    parser.add_argument("rom_path", type=str, help="Path to the GBA ROM file")
    args = parser.parse_args()

    check_file_extension(args.rom_path)
