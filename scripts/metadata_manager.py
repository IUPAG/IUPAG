import json
import os
import re

class MetadataManager:
    def __init__(self):
        self.metadata = None
        self.initialize()
    
    def initialize(self):
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'game_metadata_mappings.json')
        try:
            with open(json_path, 'r') as f:
                self.metadata = json.load(f)
        except Exception as e:
            print(f"Error loading metadata: {e}")
            self.metadata = None

    def find_matching_language(self, token):
        if not self.metadata:
            return None
            
        token = token.strip().upper()
        for lang_key, lang_data in self.metadata['language_codes'].items():
            if token in lang_data['codes']:
                return lang_data['name']
        return None

    def get_revision_name(self, code):
        if not self.metadata:
            return "rev10"
            
        code = code.upper()
        for rev_type, rev_data in self.metadata['revision'].items():
            for rev_code in rev_data['codes']:
                if rev_code.upper() in code:
                    return rev_data['name']
        return "rev10"

    def is_world_region(self, region):
        if not self.metadata or region not in self.metadata['multi_region_codes']:
            return False
        return self.metadata['multi_region_codes'][region].get('includes', []) == ["ALL"]

    def extract_metainfo(self, game_name):
        # Example of a game with metainfo: Super Noah's Ark 3D (World) (Steam) (Unl)
        
        game_name = game_name.upper()
        meta_info = []
        # Find all text within parentheses
        parts = [part.strip('()') for part in game_name.split('(')[1:]]
        
        for part in parts:
            for meta_key, meta_data in self.metadata['metainfo_tags'].items():
                for meta_code in meta_data['codes']:
                    if meta_code.upper() == part:
                        meta_info.append(meta_data['name'])
        return meta_info

    def find_matching_region(self, token):
        if not self.metadata:
            return None
            
        token = token.strip().upper()
        # Check single regions first
        for region_key, region_data in self.metadata['region_codes'].items():
            if token in region_data['codes']:
                return region_data['name']
        # Check multi-regions
        for region_key, region_data in self.metadata['multi_region_codes'].items():
            if token in region_data['codes']:
                return region_data['name']
        return None

    def extract_languages(self, game_name):        
        # Look for language codes in parentheses
        lang_matches = re.findall(r'\(([^)]+)\)', game_name)
        matched_languages = set()

        for match in lang_matches:
            # Split by comma or space
            tokens = [token.strip() for token in re.split(r'[,\s]+', match)]
            for token in tokens:
                # Try direct language matching first
                lang = self.find_matching_language(token)
                if lang:
                    matched_languages.add(lang)
                else:
                    # Try region-based language detection
                    region = self.find_matching_region(token)
                    if region:
                        # Check single regions
                        if region in self.metadata['region_codes']:
                            primary_lang = self.metadata['region_codes'][region]['primary_language']
                            # Find the language code for the primary language
                            for lang_key, lang_data in self.metadata['language_codes'].items():
                                if lang_key == primary_lang:
                                    matched_languages.add(lang_data['name'])
                        # Check multi-regions
                        elif region in self.metadata['multi_region_codes']:
                            primary_lang = self.metadata['multi_region_codes'][region]['primary_language']
                            # Find the language code for the primary language
                            for lang_key, lang_data in self.metadata['language_codes'].items():
                                if lang_key == primary_lang:
                                    matched_languages.add(lang_data['name'])

        return sorted(list(matched_languages))