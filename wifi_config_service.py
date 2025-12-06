import json
import os
import sys

# 兼容MicroPython和标准Python
try:
    import uos
    # MicroPython环境
    def listdir():
        return uos.listdir()
    
    def remove_file(filename):
        uos.remove(filename)
except ImportError:
    # 标准Python环境
    def listdir():
        return os.listdir()
    
    def remove_file(filename):
        os.remove(filename)

CONFIG_FILE = 'wifi_config.json'
DEFAULT_CONFIG = {
    'ssid': '',
    'password': ''
}

def load_wifi_config():
    """
    加载WiFi配置
    
    返回:
        包含ssid和password的字典，如果文件不存在或格式错误，返回默认配置
    """
    try:
        if CONFIG_FILE in listdir():
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # 验证必要的字段
                if 'ssid' in config and 'password' in config:
                    return config
                else:
                    print('WiFi配置文件格式错误，使用默认配置')
        else:
            print('WiFi配置文件不存在，使用默认配置')
    except Exception as e:
        print('加载WiFi配置时出错: {}'.format(e))
    
    return DEFAULT_CONFIG.copy()

def save_wifi_config(ssid, password):
    """
    保存WiFi配置
    
    参数:
        ssid: WiFi网络名称
        password: WiFi密码
    
    返回:
        True如果保存成功，否则False
    """
    config = {
        'ssid': ssid,
        'password': password
    }
    
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
        print('WiFi配置已保存到 {}'.format(CONFIG_FILE))
        return True
    except Exception as e:
        print('保存WiFi配置时出错: {}'.format(e))
        return False

def get_current_config():
    """
    获取当前WiFi配置（如果没有保存的配置，则返回空字符串）
    
    返回:
        (ssid, password) 元组
    """
    config = load_wifi_config()
    return config.get('ssid', ''), config.get('password', '')

def clear_wifi_config():
    """
    清除保存的WiFi配置
    """
    try:
        if CONFIG_FILE in listdir():
            remove_file(CONFIG_FILE)
            print('WiFi配置已清除')
            return True
        else:
            print('WiFi配置文件不存在，无需清除')
            return True
    except Exception as e:
        print('清除WiFi配置时出错: {}'.format(e))
        return False
