import argparse
from rich.console import Console
from rich.spinner import Spinner
import os
import subprocess

console = Console()

def launch_mgba(file_path):
    """Starts the game in mGBA."""

    try:

        # Path to the mGBA executable

        mgba_path = 'c:\\Program Files\\mGBA\\mGBA.exe' # Default name if mGBA is in PATH. Adjust if necessary.

        if not os.path.isfile(file_path):
            console.print("[bold red]ROM file not found![/bold red]")
            return

        # Check if mGBA is installed (callable)
        result = subprocess.run([mgba_path, "--version"], capture_output=True, text=True)
        if result.returncode != 0:
            console.print("[bold red]mGBA could not be found. Make sure it is installed and in the PATH.[/bold red]")
            return

        # Start game with mGBA
        subprocess.Popen([mgba_path, file_path])
        console.print(f"[bold green]Game is starting in mGBA: {file_path}[/bold green]")
    except FileNotFoundError:
        console.print("[bold red]The mGBA executable was not found. Check the path to the mGBA installation.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An error occurred:[/bold red] {e}")
def display_rom_content(file_path):
    """Displays the complete contents of the ROM with addresses."""
    try:
        with open(file_path, "rb") as rom_file:
            console.print("[bold cyan]=== Complete ROM content ===[/bold cyan]")
            address = 0
            whileTrue:
                block = rom_file.read(16) # Display 16 bytes per line
                if not block:
                    break
                hex_data = " ".join(f"{byte:02X}" for byte in block)
                ascii_data = "".join(chr(byte) if 32 <= byte <= 126 else '.' for byte in block)
                console.print(f"[bold yellow]0x{address:08X}[/bold yellow]: {hex_data:<47} | {ascii_data}")
                address += 16
    except Exception as e:
        console.print(f"[bold red]Error displaying ROM contents:[/bold red] {e}")
    
def export_to_hex_file(file_path):
    """Exports the entire ROM content as a HEX file."""
    try:
        output_path = file_path + "_dump.hex"
        with open(file_path, "rb") as rom_file, open(output_path, "w") as hex_file:
            address = 0
            whileTrue:
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

def read_nes_rom(file_path):
    try:
        with open(file_path, "rb") as rom_file:
            rom_size = os.path.getsize(file_path)
            console.print(f"[bold green]ROM size:[/bold green] {rom_size} Bytes")
            
            console.print("\n[bold cyan]=== NES ROM Header Information ===[/bold cyan] \n")
            header = rom_file.read(16)

            magic_number = header[0:4].decode('ascii', errors='replace')
            console.print(f"[bold yellow]Magic Number (iNES):[/bold yellow] {magic_number}")

            prg_rom_size = header[4]
            console.print(f"[bold yellow]PRG-ROM size (16 KB blocks):[/bold yellow] {prg_rom_size} Blöcke")

            chr_rom_size = header[5]
            console.print(f"[bold yellow]CHR-ROM size (8 KB blocks):[/bold yellow] {chr_rom_size} Blöcke")

            flags_6 = header[6]
            console.print(f"[bold yellow]Flags 6 (Mapper, Mirroring, Battery):[/bold yellow] 0x{flags_6:02X}")

            flags_7 = header[7]
            console.print(f"[bold yellow]Flags 7 (Mapper, NES 2.0 Identification):[/bold yellow] 0x{flags_7:02X}")

            prg_ram_size = header[8] if header[8] != 0 else 8
            console.print(f"[bold yellow]PRG-RAM size (8 KB blocks):[/bold yellow] {prg_ram_size} KB")

            flags_9 = header[9]
            console.print(f"[bold yellow]Flags 9 (TV System):[/bold yellow] 0x{flags_9:02X}")

            flags_10 = header[10]
            console.print(f"[bold yellow]Flags 10 (TV System, PRG-RAM):[/bold yellow] 0x{flags_10:02X}")

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

def read_snes_rom(file_path):
    """Reads header information specific to SNES ROMs and scans the ROM for patterns."""
    try:
        with open(file_path, "rb") as rom_file:
            rom_size = os.path.getsize(file_path)
            console.print(f"[bold green]ROM size:[/bold green] {rom_size} Bytes")

            console.print("\n[bold cyan]=== SNES ROM Header Information ===[/bold cyan] \n")
            header = rom_file.read(512)  # SNES header is often at 0x7FC0 (LoROM) or 0xFFC0 (HiROM)

            game_title = header[0x10:0x20].decode('ascii', errors='replace').strip()
            console.print(f"[bold yellow]Game title:[/bold yellow] {game_title}")

            rom_makeup = header[0x25]
            console.print(f"[bold yellow]ROM Makeup (Speed/Type):[/bold yellow] 0x{rom_makeup:02X}")

            rom_size = header[0x27]
            console.print(f"[bold yellow]ROM size (2^N KB):[/bold yellow] 0x{rom_size:02X} ({2 ** rom_size} KB)")

            sram_size = header[0x28]
            console.print(f"[bold yellow]SRAM size (2^N KB):[/bold yellow] 0x{sram_size:02X} ({2 ** sram_size} KB)")

            license_code = header[0x29]
            console.print(f"[bold yellow]License code:[/bold yellow] 0x{license_code:02X}")

            version_number = header[0x2A]
            console.print(f"[bold yellow]Version:[/bold yellow] {version_number}")

            checksum = header[0x2C:0x2E]
            console.print(f"[bold yellow]Checksum:[/bold yellow] {checksum.hex().upper()}")

            complement_checksum = header[0x2E:0x30]
            console.print(f"[bold yellow]Checksum Complement:[/bold yellow] {complement_checksum.hex().upper()}")

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

    # Check if the file has one of the file extensions
    if file_extension.lower() in ('.nes', '.unf', '.fds'):
        read_nes_rom(file_path_extension)
    elif file_extension.lower() in ('.sfc', '.smc', '.fig', '.bs', '.st'):
        read_snes_rom(file_path_extension)
    else:
        print(f"{file_path_extension} has an unknown extension.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NES-ROM/SNES-Inspektor")
    parser.add_argument("rom_path", type=str, help="Path to the NES/SNES ROM file")
    args = parser.parse_args()

    check_file_extension(args.rom_path)
