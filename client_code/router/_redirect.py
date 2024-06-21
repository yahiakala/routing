class Redirect(Exception):
    def __init__(self, *, path=None, search_params=None, path_params=None, hash=""):
        self.path = path
        self.search_params = search_params
        self.path_params = path_params
        self.hash = hash
