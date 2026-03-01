# Flask settings
HOST = "0.0.0.0" # better dont change it
PORT = 5000 # you can change this
DEBUG = True # dont touch for now

# SocketIO / client settings
DEFAULT_INTERVAL_MS = 1000 # you can change this one
MIN_INTERVAL_MS = 250 # better dont go below 100
MAX_INTERVAL_MS = 2500 # you can change this freely
INTERVAL_STEP_MS = 250 # step for slider and clamping, trust me 250 is fine

# CORS
CORS_ALLOWED_ORIGINS = "*" # dont touch this one

#Real changable settings
MAX_GRAPH_POINTS = 20 # Max data points to keep for graphin

DYNAMIC_DRIVE_CAPACITY_COLORS = False # If true, drive boxes will change color based on capacity (green->yellow->red) (DISABLES STORAGE_ALERT_COLOR)
DYNAMIC_DRIVE_CAPACITY_COLOR_LOW = "#308833" # kinda green
DYNAMIC_DRIVE_CAPACITY_COLOR_MEDIUM = "#B38118" # kinda yellow
DYNAMIC_DRIVE_CAPACITY_COLOR_HIGH = "#6E162F" # kinda red

STORAGE_ALERT = False # If true, storage usage will be highlighted when exceeding threshold
STORAGE_ALERT_THRESHOLD_PERCENT = 90 # Alert on storage usage exceeding this percentage
STORAGE_ALERT_COLOR = "#5F1228" # Alert color for storage usage exceeding threshold
