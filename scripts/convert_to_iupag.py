import json
import xml.etree.ElementTree as ET
import re
import os

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
            return region_key
    # Check multi-regions
    for region_key, region_data in metadata['multi_region_codes'].items():
        if token in region_data['codes']:
            return region_key
    return None

def parse_dat_file(file_path):
    try:
        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # List to store game names
        games = []
        
        # Find all game elements and extract names
        for game in root.findall('.//game'):
            name = game.get('name')
            if name:
                games.append(name)
                
        return games
    except ET.ParseError as e:
        print(f"Error parsing {file_path}: {e}")
        return []
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return []

def convert_region(game):
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, 'meta_data_to_match.json')
    
    metadata = load_region_metadata(json_path)
    if not metadata:
        return "(#WORLD)"

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
                        return "(#WORLD)"
                    # matched_regions.update(includes)
                    matched_regions.add(region)
                else:
                    matched_regions.add(region)

    if matched_regions:
        # Sort to ensure consistent output
        region_str = "-".join(sorted(matched_regions))
        return f"(#{region_str})"
    return "(#WORLD)"

def format_iupag_name(index, game):
    # Convert game to uppercase, replace spaces with underscores, remove non-alphanumerics
    game_title = re.sub(r'\([^)]*\)', '', game).strip()
    normalized = game_title.upper().replace(" ", "_")
    normalized = re.sub(r'[^A-Z0-9_]', '', normalized)
    region_tag = convert_region(game)

    # combine all parts
    return f"{game_title} {region_tag}"

def print_games(dat_file):
    print(f"\nGames in {dat_file}:")
    print("-" * 50)
    
    games = parse_dat_file(dat_file)
    
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'datFiles')
    os.makedirs(output_dir, exist_ok=True)
    
    # Create output file name based on input DAT file
    base_name = os.path.splitext(os.path.basename(dat_file))[0]
    output_file = os.path.join(output_dir, f"{base_name}_IUPAG.txt")
    
    # Write to file and print to console
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, game in enumerate(games, 1):
            iupag_name = format_iupag_name(i, game)
            line = f"{i}. no-intro {game} | IUPAG {iupag_name}"
            print(line)
            f.write(f"{iupag_name}\n")
    
    print(f"\nTotal games: {len(games)}")
    print(f"Output saved to: {output_file}")

# List of DAT files to process
dat_files = [
    "../.downloads/Nintendo - Game Boy Advance (20250216-134516).dat"
]

# Process each DAT file
for dat_file in dat_files:
    print_games(dat_file)