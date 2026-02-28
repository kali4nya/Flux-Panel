# Flask settings
HOST = "0.0.0.0" # better dont change it
PORT = 5000 # you can change this
DEBUG = True # dont touch for now

# SocketIO / client settings
DEFAULT_INTERVAL_MS = 1000 # you can change this one
MIN_INTERVAL_MS = 100 # dont go below 100
MAX_INTERVAL_MS = 5000 # you can change this freely

# CORS
CORS_ALLOWED_ORIGINS = "*" # dont touch this one