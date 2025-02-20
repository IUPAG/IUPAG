import json
import xml.etree.ElementTree as ET
import re
import os
from models.game import Game
from models.system import System

def load_region_metadata(json_path):
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading metadata: {e}")
        return None

def find_matching_region(token, metadata):
    token = token.strip().upper()
    # Check single regions first
    for region_key, region_data in metadata['region_codes'].items():
        if token in region_data['codes']:
            return region_data['name']
    # Check multi-regions
    for region_key, region_data in metadata['multi_region_codes'].items():
        if token in region_data['codes']:
            return region_data['name']
    return None

def find_matching_language(token, metadata):
    token = token.strip().upper()
    for lang_key, lang_data in metadata['language_codes'].items():
        if token in lang_data['codes']:
            return lang_data['name']
    return None

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
            game.languages = extract_languages(game_name)
            parse_game_info(game, game_name)
            
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
    metadata_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'meta_data_to_match.json')
    metadata = load_region_metadata(metadata_path)
    return convert_region(game_name).strip('(#)')

def extract_languages(game_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, 'meta_data_to_match.json')
    metadata = load_region_metadata(json_path)
    
    if not metadata:
        return []

    # Look for language codes in parentheses
    lang_matches = re.findall(r'\(([^)]+)\)', game_name)
    matched_languages = set()

    for match in lang_matches:
        # Split by comma or space
        tokens = [token.strip() for token in re.split(r'[,\s]+', match)]
        for token in tokens:
            lang = find_matching_language(token, metadata)
            if lang:
                matched_languages.add(lang)

    return sorted(list(matched_languages))

def parse_game_info(game, name):
    # Parse revision
    rev_match = re.search(r'\(Rev (\d+)\)', name, re.IGNORECASE)
    if rev_match:
        game.revision = rev_match.group(1).zfill(2)

def convert_region(game):
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, 'meta_data_to_match.json')
    
    metadata = load_region_metadata(json_path)
    if not metadata:
        return "(#World)"

    game = game.upper()

    groups = re.findall(r'\(([^)]+)\)', game)
    matched_regions = set()
    
    for group in groups:
        tokens = [token.strip().upper() for token in group.split(',')]
        for token in tokens:
            region = find_matching_region(token, metadata)
            if region:
                # If it's a multi-region code, expand it
                if region in metadata['multi_region_codes']:
                    includes = metadata['multi_region_codes'][region].get('includes', [])
                    if includes == ["ALL"]:
                        return "(#World)"
                    # matched_regions.update(includes)
                    matched_regions.add(region)
                else:
                    matched_regions.add(region)

    if matched_regions:
        # Sort to ensure consistent output
        region_str = ", ".join(sorted(matched_regions))
        return f"(#{region_str})"
    return "(#World)"

def print_games(dat_file):
    print(f"\nProcessing {dat_file}:")
    print("-" * 50)
    
    system = parse_dat_file(dat_file)
    if not system:
        return
    
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'datFiles')
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

# List of DAT files to process
dat_files = [
    "../.downloads/Nintendo - Game Boy Advance (20250216-134516).dat"
]

# Process each DAT file
for dat_file in dat_files:
    print_games(dat_file)