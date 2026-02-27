import subprocess
import platform

def get_gpu_stats():
    system = platform.system()
    
    if system == "Linux":
        try:
            # Check if Raspberry Pi vcgencmd exists
            result = subprocess.run(
                ["vcgencmd", "measure_temp"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                # Returns something like: temp=45.2'C
                temp_str = result.stdout.strip()
                temp_value = float(temp_str.replace("temp=", "").replace("'C",""))
                return {
                    "vendor": "Raspberry Pi VideoCore",
                    "temperature_c": temp_value,
                    "usage_percent": None  # Not easy to get usage on Pi GPU
                }
        except FileNotFoundError:
            pass
        
        # Generic fallback
        return {
            "vendor": "Unknown/Unsupported GPU",
            "temperature_c": None,
            "usage_percent": None
        }

    else:
        # Placeholder for other OS types
        return {
            "vendor": system,
            "temperature_c": None,
            "usage_percent": None
        }