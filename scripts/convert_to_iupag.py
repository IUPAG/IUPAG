import json
import xml.etree.ElementTree as ET
import re
import os
from models.game import Game
from models.system import System
from metadata_manager import MetadataManager
import glob

# Create metadata manager instance
metadata_manager = MetadataManager()

def parse_dat_file(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Create System object from header
        header = root.find('header')
        system = System(
            system_id=header.find('name').text,
            name=header.find('description').text,
            description=header.find('comment').text if header.find('comment') is not None else "",
            version=header.find('version').text,
            author=header.find('author').text,
            homepage=header.find('homepage').text if header.find('homepage') is not None else "",
            url=header.find('url').text if header.find('url') is not None else ""
        )
        
        # Parse each game
        for game_elem in root.findall('.//game'):
            game_name = game_elem.get('name', '')
            game_desc = game_elem.find('description').text if game_elem.find('description') is not None else ''
            
            game = Game(
                game_id=game_elem.get('id', ''),
                name=game_name,
                description=game_desc
            )
            
            # Parse ROM information
            rom_elem = game_elem.find('rom')
            if rom_elem is not None:
                rom_name = rom_elem.get('name', '')
                # Extract file extension
                file_ext = os.path.splitext(rom_name)[1].lstrip('.')
                game.file_extension = file_ext.lower() if file_ext else ''
                
                game.add_rom(
                    name=rom_name,
                    size=int(rom_elem.get('size', 0)),
                    crc=rom_elem.get('crc', ''),
                    md5=rom_elem.get('md5', ''),
                    sha1=rom_elem.get('sha1', ''),
                    sha256=rom_elem.get('sha256', ''),
                    status=rom_elem.get('status', '')
                )
            
            # Extract region from name and set game properties
            game.region = extract_region(game_name)
            game.title = extract_title(game_name)
            game.languages = metadata_manager.extract_languages(game_name)
            game.revision = metadata_manager.get_revision_name(game_name)
            game.release_date = extract_date(game_name)
            game.meta_info = metadata_manager.extract_metainfo(game_name)
            
            system.add_game(game)
                
        return system
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def extract_title(game_name):
    # Remove everything in parentheses and brackets
    title = re.sub(r'\([^)]*\)|\[[^\]]*\]', '', game_name)
    return title.strip()

def extract_region(game_name):
    return convert_region(game_name).strip('(#)')

def convert_region(game):
    game = game.upper()
    groups = re.findall(r'\(([^)]+)\)', game)
    matched_regions = set()
    
    for group in groups:
        tokens = [token.strip().upper() for token in group.split(',')]
        for token in tokens:
            region = metadata_manager.find_matching_region(token)
            if region:
                if metadata_manager.is_world_region(region):
                    return "(#World)"
                matched_regions.add(region)

    if matched_regions:
        region_str = ", ".join(sorted(matched_regions))
        return f"(#{region_str})"
    return "(#World)"

def extract_date(game_name):
    # Example game name SomeGame (USA) (Proto) (1995-05-24)
    date_match = re.search(r'\((\d{4}-\d{2}-\d{2})\)', game_name)
    if date_match:
        return date_match.group(1)
    
    return "1970-01-01"

def print_games(dat_file):
    print(f"\nProcessing {dat_file}:")
    print("-" * 50)
    
    system = parse_dat_file(dat_file)
    if not system:
        return
    
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.exports')
    os.makedirs(output_dir, exist_ok=True)
    
    base_name = os.path.splitext(os.path.basename(dat_file))[0]
    output_file = os.path.join(output_dir, f"{base_name}.txt")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, game in enumerate(system.games, 1):
            iupag_name = game.format_iupag_name()
            print(f"{i}. no-intro: {game.name} -> IUPAG: {iupag_name}")
            f.write(f"{iupag_name}\n")
    
    print(f"\nTotal games: {len(system.games)}")
    print(f"Output saved to: {output_file}")

# Get all .dat files in the .downloads/nointro directory
dat_files = glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.imports/nointro/*.dat"))

# Process each DAT file
for dat_file in dat_files:
    print_games(dat_file)