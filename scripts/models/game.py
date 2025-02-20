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
        self.developer = ""  # Game developer
        self.publisher = ""  # Game publisher
        self.region = "World"  # Default region if unknown
        self.release_date = "1970-01-01"  # Default Unix epoch if unknown
        self.revision = "00"  # Version string or revision number
        self.languages = []  # List of supported languages
        self.dump_flags = []  # List of dump info flags
        self.attributes = {
            "players": "1P",  # Number of players
            "genres": [],     # List of genres in L33TC0D3
            "controllers": [] # Supported controllers
        }
        self.meta_info = []  # List of additional metadata
        self.universe_prefix = ""  # Game universe prefix (Mario, Pokemon, etc)
        self.sport_prefix = ""  # Sport game prefix if applicable
        self.clone_of_id = None  # Add this new property

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
        return self.name

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
        
        Example output:
        Title <sep> Subtitle (@Dev, Pub)-(#Region)-(vDate)-(revX.Y.Z)-(T-Lang) [flag]-{Attributes}-(MetaInfo).ext
        """

        parts = []
        
        # Add universe/sport prefix if present
        if self.universe_prefix:
            parts.append(f"{self.universe_prefix} ")
        elif self.sport_prefix:
            parts.append(f"{self.sport_prefix} ")
            
        # Add main title components
        parts.append(self.title)
        if self.subtitle:
            parts.append(f"{self.separator}{self.subtitle} - ")
            
        # Add optional tags
        if self.developer or self.publisher:
            dev_pub = f"(@{self.developer}, {self.publisher})" if self.developer else f"(@{self.publisher})"
            parts.append(dev_pub)
        else:
            parts.append("-")
        parts.append(f"(#{self.region})")
        parts.append(f"(v{self.release_date})")
        
        if self.revision != "00":
            parts.append(f"(rev{self.revision})")
            
        if self.languages:
            parts.append(f"(T-{','.join(self.languages)})")
            
        if self.dump_flags:
            parts.append(f"[{''.join(self.dump_flags)}]")
            
        if any(self.attributes.values()):
            attr_parts = []
            if self.attributes["players"] != "1P":
                attr_parts.append(self.attributes["players"])
            if self.attributes["genres"]:
                attr_parts.append(",".join(self.attributes["genres"]))
            if self.attributes["controllers"]:
                attr_parts.append(",".join(self.attributes["controllers"]))
            if attr_parts:
                parts.append(f"{{{';'.join(attr_parts)}}}")
                
        if self.meta_info:
            parts.append(f"({';'.join(self.meta_info)})")
            
        return " ".join(parts)

