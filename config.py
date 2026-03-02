# Flask settings
HOST = "0.0.0.0" # better dont change it
PORT = 5000 # you can change this
DEBUG = True # dont touch for now

# CORS
CORS_ALLOWED_ORIGINS = "*" # dont touch this one

#Real changable settings:
# SocketIO / client settings
DEFAULT_INTERVAL_MS = 500 # you can change this one
MIN_INTERVAL_MS = 250 # better dont go below 100
MAX_INTERVAL_MS = 2500 # you can change this freely
INTERVAL_STEP_MS = 250 # step for slider and clamping, trust me 250 is fine

#CUSTOMIZATION FOR MAIN PAGE
INDEX_MAX_GRAPH_POINTS = 20 # Max data points to keep for graphin 

INDEX_DYNAMIC_DRIVE_CAPACITY_COLORS = False # If true, drive boxes will change color based on capacity, (interpolates LOW->MEDIUM->HIGH) (DISABLES STORAGE_ALERT_COLOR)
INDEX_DYNAMIC_DRIVE_CAPACITY_COLOR_LOW = "#308833" # kinda green
INDEX_DYNAMIC_DRIVE_CAPACITY_COLOR_MEDIUM = "#B38118" # kinda yellow
INDEX_DYNAMIC_DRIVE_CAPACITY_COLOR_HIGH = "#6E162F" # kinda red

INDEX_STORAGE_ALERT = False # If true, storage usage will be highlighted when exceeding threshold
INDEX_STORAGE_ALERT_THRESHOLD_PERCENT = 90 # Alert on storage usage exceeding this percentage
INDEX_STORAGE_ALERT_COLOR = "#5F1228" # Alert color for storage usage exceeding threshold

#CUSTOMIZATION FOR STORAGE PAGE
STORAGE_MAX_GRAPH_POINTS = 20 # Max data points to keep for graphin 


#you can also set this to "WRITE" or "READ", this sets the bar color to the corresponding file system's read or write color
STORAGE_BAR_COLOR = "#3b82f6" # default color of the capacity bars in the storage tab

STORAGE_DYNAMIC_DRIVE_CAPACITY_COLORS = False # If true, drive boxes will change color based on capacity (interpolates LOW->MEDIUM->HIGH) (DISABLES STORAGE_ALERT and default bar color)
STORAGE_DYNAMIC_DRIVE_CAPACITY_COLOR_LOW = "#36EB3C" # kinda green
STORAGE_DYNAMIC_DRIVE_CAPACITY_COLOR_MEDIUM = "#E0D63D" # kinda yellow
STORAGE_DYNAMIC_DRIVE_CAPACITY_COLOR_HIGH = "#D61942" # kinda red

STORAGE_STORAGE_ALERT = False # If true, storage usage will be highlighted when exceeding threshold
STORAGE_STORAGE_ALERT_THRESHOLD_PERCENT = 50 # Alert on storage usage exceeding this percentage
STORAGE_STORAGE_ALERT_COLOR = "#B30B19" # Alert color for storage usage exceeding threshold

# --- FILESYSTEM THEMING ---
# Colors for Read and Write graphs based on Filesystem type
FS_THEME = {
    "NTFS":    {"read": "#3b82f6", "write": "#fbbf24"}, # Blue / Amber
    "FAT32":   {"read": "#06b6d4", "write": "#f43f5e"}, # Cyan / Rose
    "vfat":    {"read": "#2dd4bf", "write": "#ec4899"}, # Teal / Pink
    "ext4":    {"read": "#60a5fa", "write": "#22c55e"}, # Light Blue / Green
    "exFAT":   {"read": "#a78bfa", "write": "#8b5cf6"}, # Light Purple / Violet
    "APFS":    {"read": "#22d3ee", "write": "#2143da"}, # Cyan / Dark Blue
    "DEFAULT": {"read": "#94a3b8", "write": "#64748b"}  # Slate / Grey
}