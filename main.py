import time
import machine
from config import WIFI_SSID, WIFI_PASSWORD, WIFI_TIMEOUT, TIMEZONE_OFFSET
import wifi_service
import sync_time_service

# 初始化UART1（用户已将UART改为串口1，因为UART0被Python解释器占用）
# UART1使用TX=GPIO10, RX=GPIO9（具体引脚可能因ESP32板型而异，请根据实际调整）
# 注意：根据ESP32板型，UART1的引脚可能不同，请根据实际情况修改tx和rx参数
uart1 = machine.UART(1, baudrate=115200, tx=17, rx=16)  # 示例引脚，可能需要调整

def run_config_portal():
    """
    运行配置门户（AP模式 + Web服务器）
    允许用户通过网页配置WiFi SSID和密码
    """
    print('启动配置门户...')
    try:
        import web_config_service
        portal = web_config_service.WebConfigService()
        portal.run_config_portal(timeout=180)  # 运行3分钟
        print('配置门户已关闭，重新加载配置...')
        return True
    except Exception as e:
        print('启动配置门户失败: {}'.format(e))
        return False

def main():
    """主函数"""
    print('ESP32 MicroPython 网络时间同步程序（服务化重构 + Web配置）')
    
    # 初始化WiFi服务
    wlan = wifi_service.wifi_init()
    
    # 连接WiFi
    wifi_connected = wifi_service.wifi_connect(wlan, WIFI_SSID, WIFI_PASSWORD, WIFI_TIMEOUT)
    
    # 如果WiFi连接失败，启动配置门户
    if not wifi_connected:
        print('WiFi连接失败，启动配置门户...')
        run_config_portal()
        
        # 重新加载配置（因为用户可能通过网页保存了新配置）
        import wifi_config_service
        new_ssid, new_password = wifi_config_service.get_current_config()
        
        # 如果有新配置，重新尝试连接
        if new_ssid:
            print('使用新配置重新尝试连接WiFi...')
            wifi_connected = wifi_service.wifi_connect(wlan, new_ssid, new_password, WIFI_TIMEOUT)
        else:
            print('未保存新配置，继续使用默认配置')
    
    # 如果WiFi连接成功，初始化时间校准服务
    time_getter = None
    if wifi_connected:
        time_getter = sync_time_service.sync_time_service(wlan, TIMEZONE_OFFSET)
    
    # 主循环
    loop_count = 0
    while True:
        if time_getter is not None:
            # 如果有时间服务，则通过UART1输出时间
            time_str = time_getter()
            output_msg = '本地时间: {}'.format(time_str)
            # 调试信息通过print输出
            print(output_msg)
            # 本地时间通过UART1输出
            uart1.write(output_msg + '\r\n')
        else:
            # 如果没有时间服务（WiFi连接失败），则通过print打印失败信息
            # 每10次循环打印一次，避免刷屏
            if loop_count % 10 == 0:
                print('无法连接WiFi，请检查配置和网络。当前时间（RTC）: {}'.format(time.localtime()))
                
                # 每60次循环（约1分钟）检查一次是否应该重新尝试连接
                if loop_count % 60 == 0:
                    print('重新尝试连接WiFi...')
                    # 重新加载配置
                    import wifi_config_service
                    current_ssid, current_password = wifi_config_service.get_current_config()
                    if current_ssid:
                        wifi_connected = wifi_service.wifi_connect(wlan, current_ssid, current_password, WIFI_TIMEOUT)
                        if wifi_connected:
                            time_getter = sync_time_service.sync_time_service(wlan, TIMEZONE_OFFSET)
                            print('WiFi重新连接成功！')
        
        time.sleep(1)
        loop_count += 1

if __name__ == '__main__':
    main()
