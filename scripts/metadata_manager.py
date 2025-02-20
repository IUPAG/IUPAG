import json
import os

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
