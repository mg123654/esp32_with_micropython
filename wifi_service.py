import network
import time

def wifi_init():
    """
    WiFi服务初始化
    
    返回:
        wlan对象
    """
    wlan = network.WLAN(network.STA_IF)
    if not wlan.active():
        wlan.active(True)
    return wlan

def wifi_connect(wlan, ssid, password, timeout_seconds=15):
    """
    连接WiFi网络
    
    参数:
        wlan: wlan对象
        ssid: WiFi网络名称
        password: WiFi密码
        timeout_seconds: 连接超时时间（秒）
    
    返回:
        True如果连接成功，否则False
    """
    # 如果已经连接，则断开以重新连接
    if wlan.isconnected():
        wifi_disconnect(wlan)
        time.sleep(0.5)
    
    print('正在连接WiFi网络: {}...'.format(ssid))
    
    wlan.connect(ssid, password)
    
    # 等待连接
    timeout = timeout_seconds
    while not wlan.isconnected() and timeout > 0:
        time.sleep(1)
        timeout -= 1
        # 每隔5秒打印一次等待信息
        if timeout % 5 == 0 and timeout != timeout_seconds:
            print('等待连接...剩余{}秒'.format(timeout))
    
    if wlan.isconnected():
        print('WiFi连接成功! 网络配置: {}'.format(wlan.ifconfig()))
        return True
    else:
        print('WiFi连接失败! 请检查SSID和密码，或网络状况。')
        return False

def wifi_disconnect(wlan):
    """
    断开WiFi连接
    
    参数:
        wlan: wlan对象
    """
    if wlan.isconnected():
        wlan.disconnect()
        print('WiFi已断开连接')

def wifi_status(wlan):
    """
    获取WiFi状态
    
    参数:
        wlan: wlan对象
    
    返回:
        状态字符串
    """
    if wlan.isconnected():
        return '已连接，IP: {}'.format(wlan.ifconfig()[0])
    else:
        return '未连接'
