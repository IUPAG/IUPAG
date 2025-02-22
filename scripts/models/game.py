class Game:
    def __init__(self, game_id: str, name: str, description: str):
        # Basic identifiers
        self.game_id = game_id
        self.name = name
        self.description = description

        # ROM properties
        self.rom_name = ""
        self.rom_size = 0
        self.rom_crc = ""
        self.rom_md5 = ""
        self.rom_sha1 = ""
        self.rom_sha256 = ""
        self.rom_status = ""

        # IUPAG properties
        self.title = ""  # Main title
        self.subtitle = ""  # Subtitle or hack name
        self.separator = "-"  # -, -;, ;=, or ~ depending on type
        self.developer = "Dev"  # Game developer
        self.publisher = "Pub"  # Game publisher
        self.region = "World"  # Default region if unknown
        self.release_date = "1970-01-01"  # Default Unix epoch if unknown
        self.revision = "rev10"  # Default to retail release
        self.languages = []  # List of supported languages
        self.dump_flags = ["[!]"]  # List of dump info flags
        self.attributes = {
            "players": "1P",  # Number of players
            "genres": ["G3NR3"],     # List of genres in L33TC0D3
            "controllers": [] # Supported controllers
        }
        self.meta_info = []  # List of additional metadata
        self.universe_prefix = ""  # Game universe prefix (Mario, Pokemon, etc)
        self.sport_prefix = ""  # Sport game prefix if applicable
        self.clone_of_id = None  # Add this new property
        self.file_extension = ""  # Add this line with the other properties

    def add_rom(self, name: str, size: int, crc: str, md5: str, 
                sha1: str, sha256: str, status: str):
        self.rom_name = name
        self.rom_size = size
        self.rom_crc = crc
        self.rom_md5 = md5
        self.rom_sha1 = sha1
        self.rom_sha256 = sha256
        self.rom_status = status

    def __str__(self):
        return f"{self.name} ({self.region}) {self.revision}"

    def __repr__(self):
        return f"Game(id='{self.game_id}', name='{self.name}')"

    def format_iupag_dat_file(self) -> str:
        """Generate XML formatted DAT file entry for this game."""
        indent = "    "  # 4 spaces indentation
        
        # Build game opening tag with attributes
        game_attrs = [f'name="{self.name}"', f'id="{self.game_id}"']
        if self.clone_of_id:
            game_attrs.append(f'cloneofid="{self.clone_of_id}"')
        
        xml = [f'  <game {" ".join(game_attrs)}>']
        
        # Add description
        xml.append(f'{indent}<description>{self.description}</description>')
        
        # Add ROM info
        xml.append(f'{indent}<rom name="{self.rom_name}" size="{self.rom_size}" '
                  f'crc="{self.rom_crc}" md5="{self.rom_md5}" '
                  f'sha1="{self.rom_sha1}" sha256="{self.rom_sha256}"/>')
        
        xml.append('  </game>')
        return '\n'.join(xml) + '\n'

    def format_iupag_name(self) -> str:
        """Generate filename according to IUPAG naming convention.
        
        Format:
        Title <sep> Subtitle (@Developer, Publisher)-(#Region)-(vDate)-(revX.Y.Z)-(T-Lang) [flag]-{Attributes}-(MetaInfo).ext
        """
        parts = []
        
        # Title and Subtitle
        if self.subtitle:
            parts.append(f"{self.title} {self.separator} {self.subtitle}")
        else:
            parts.append(self.title)
            
        # Developer/Publisher
        if self.developer or self.publisher:
            dev_pub = f"(@{self.developer}, {self.publisher})" if self.developer else f"(@{self.publisher})"
            parts.append(dev_pub)
            
        # Region
        parts.append(f"(#{self.region})")
        
        # Release Date
        parts.append(f"(v{self.release_date})")
        
        parts.append(f"({self.revision})")
            
        # Languages
        if self.languages:
            sorted_langs = sorted(self.languages)
            # If English is present, move it to the front
            if 'En' in sorted_langs:
                sorted_langs.remove('En')
                sorted_langs.insert(0, 'En')
            parts.append(f"(T-{','.join(sorted_langs)})")
            
        # Dump flags
        if self.dump_flags:
            parts.append(''.join(self.dump_flags))
            
        # Attributes
        if any(v for k, v in self.attributes.items() if v):
            attr_parts = []
            if self.attributes["players"] != "1P":
                attr_parts.append(self.attributes["players"])
            if self.attributes["genres"]:
                attr_parts.append(",".join(self.attributes["genres"]))
            if self.attributes["controllers"]:
                attr_parts.append(",".join(self.attributes["controllers"]))
            if attr_parts:
                parts.append(f"{{{';'.join(attr_parts)}}}")
        
        # Meta info
        if self.meta_info:
            parts.append(f"({';'.join(self.meta_info)})")
        
        # Join with hyphens
        if len(parts) > 1:
            result = " ".join(parts[0:1] + ["-".join(parts[1:])]).rstrip()
        # Add extension
        if self.file_extension:
            result += f".{self.file_extension}"
            
        return result

