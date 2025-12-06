# WiFi configuration - Now loaded from wifi_config_service
import wifi_config_service

# Try to load saved configuration
WIFI_SSID, WIFI_PASSWORD = wifi_config_service.get_current_config()

# If no saved configuration, use defaults (can be empty to force AP mode)
if not WIFI_SSID:
    WIFI_SSID = 'mg'
    WIFI_PASSWORD = 'zmg123456'
    print("使用默认WiFi配置（无保存的配置）")

# WiFi connection timeout in seconds
WIFI_TIMEOUT = 15

# Timezone offset (in hours) from UTC
TIMEZONE_OFFSET = 8  # e.g., UTC+8 for China

# NTP server configuration
NTP_SERVER = 'pool.ntp.org'
NTP_PORT = 123
