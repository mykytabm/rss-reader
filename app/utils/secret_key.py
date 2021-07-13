import os
def secret_key():
    if "SECRET_KEY" in os.environ:
        return os.environ["SECRET_KEY"]
    else:
        return "765e6d6a8fa43f75a5fdd20e31b136b1c6dc2641e2f6646a504353745285f905"