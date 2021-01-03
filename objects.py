class SpotifyMusic(object):

    def __init__(self, webEl):
        # Save important properties
        self.values = webEl.text
        super().__init__()
    
    def __str__(self):
        return self.values
    
    __repr__ = __str__
