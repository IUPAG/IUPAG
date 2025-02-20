class System:
    def __init__(self, system_id: str, name: str, description: str, version: str, 
                 author: str, homepage: str, url: str):
        self.system_id = system_id
        self.name = name
        self.description = description
        self.version = version
        self.author = author.split(', ')  # Store authors as list
        self.homepage = homepage
        self.url = url
        self.games = []  # List to store Game objects

    def add_game(self, game):
        self.games.append(game)

    def __str__(self):
        return f"{self.name} ({self.version})"

    def __repr__(self):
        return f"System(id={self.system_id}, name='{self.name}', version='{self.version}')"
