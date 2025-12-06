import socket
import network
import time

class WebConfigService:
    def __init__(self, ap_ssid='ESP32-Config', ap_password='12345678'):
        """
        Web配置服务初始化
        
        参数:
            ap_ssid: AP模式下的热点名称
            ap_password: AP模式下的密码（至少8个字符）
        """
        self.ap_ssid = ap_ssid
        self.ap_password = ap_password
        self.ap = None
        self.server_socket = None
        
    def start_ap(self):
        """
        启动AP模式（创建WiFi热点）
        
        返回:
            True如果成功启动，否则False
        """
        try:
            self.ap = network.WLAN(network.AP_IF)
            self.ap.active(True)
            self.ap.config(essid=self.ap_ssid, password=self.ap_password)
            
            # 等待AP启动
            time.sleep(2)
            
            if self.ap.active():
                print('AP模式已启动')
                print('热点名称: {}, 密码: {}'.format(self.ap_ssid, self.ap_password))
                print('AP IP地址: {}'.format(self.ap.ifconfig()[0]))
                return True
            else:
                print('AP模式启动失败')
                return False
        except Exception as e:
            print('启动AP模式时出错: {}'.format(e))
            return False
    
    def stop_ap(self):
        """
        停止AP模式
        """
        if self.ap and self.ap.active():
            self.ap.active(False)
            print('AP模式已停止')
    
    def handle_client(self, client_socket):
        """
        处理客户端HTTP请求
        
        参数:
            client_socket: 客户端socket对象
        """
        try:
            request = client_socket.recv(1024).decode('utf-8')
            
            # 解析请求
            if 'GET / ' in request or 'GET /index.html' in request:
                # 返回配置页面
                response = self.get_config_page()
                client_socket.send(response)
            elif 'POST /configure' in request:
                # 处理配置提交
                content_length = 0
                lines = request.split('\r\n')
                for line in lines:
                    if 'Content-Length:' in line:
                        content_length = int(line.split(':')[1].strip())
                        break
                
                # 读取POST数据
                body = request.split('\r\n\r\n')[1] if '\r\n\r\n' in request else ''
                if len(body) < content_length:
                    # 可能需要更多数据，但简单起见我们假设一次性收到
                    pass
                
                # 解析表单数据
                config_data = {}
                for pair in body.split('&'):
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        config_data[key] = value
                
                # 保存配置
                ssid = config_data.get('ssid', '')
                password = config_data.get('password', '')
                
                # 导入wifi_config_service并保存
                import wifi_config_service
                saved = wifi_config_service.save_wifi_config(ssid, password)
                
                if saved:
                    response = self.get_success_page(ssid)
                else:
                    response = self.get_error_page('保存配置失败')
                
                client_socket.send(response)
            else:
                # 404 Not Found
                response = 'HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n<h1>404 Not Found</h1>'
                client_socket.send(response)
        
        except Exception as e:
            print('处理客户端请求时出错: {}'.format(e))
            response = 'HTTP/1.1 500 Internal Server Error\r\nContent-Type: text/html\r\n\r\n<h1>500 Internal Server Error</h1>'
            client_socket.send(response)
        
        finally:
            client_socket.close()
    
    def get_config_page(self):
        """
        获取配置页面HTML
        
        返回:
            HTTP响应字符串
        """
        html = """HTTP/1.1 200 OK
Content-Type: text/html
Connection: close

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESP32 WiFi配置</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 400px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"], input[type="password"] { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background-color: #45a049; }
        .message { margin-top: 20px; padding: 10px; border-radius: 5px; }
        .success { background-color: #dff0d8; color: #3c763d; }
        .error { background-color: #f2dede; color: #a94442; }
        .info { background-color: #d9edf7; color: #31708f; }
    </style>
</head>
<body>
    <div class="container">
        <h1>ESP32 WiFi配置</h1>
        <div class="info message">
            请配置ESP32要连接的WiFi网络
        </div>
        <form method="POST" action="/configure">
            <div class="form-group">
                <label for="ssid">WiFi名称 (SSID):</label>
                <input type="text" id="ssid" name="ssid" required placeholder="输入WiFi名称">
            </div>
            <div class="form-group">
                <label for="password">WiFi密码:</label>
                <input type="password" id="password" name="password" required placeholder="输入WiFi密码">
            </div>
            <button type="submit">保存配置</button>
        </form>
        <div class="info message">
            配置保存后，ESP32将尝试连接指定的WiFi网络
        </div>
    </div>
</body>
</html>"""
        return html.replace('\n', '\r\n')
    
    def get_success_page(self, ssid):
        """
        获取成功页面HTML
        
        参数:
            ssid: 已配置的WiFi名称
        
        返回:
            HTTP响应字符串
        """
        html = """HTTP/1.1 200 OK
Content-Type: text/html
Connection: close

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>配置成功</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 400px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .success { background-color: #dff0d8; color: #3c763d; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .info { background-color: #d9edf7; color: #31708f; padding: 15px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>配置成功</h1>
        <div class="success">
            <strong>WiFi配置已保存！</strong><br>
            SSID: {ssid}<br>
            ESP32将尝试连接到此网络。
        </div>
        <div class="info">
            您可以关闭此页面并等待ESP32重启或手动重启设备。
        </div>
        <div class="info">
            <a href="/">返回配置页面</a>
        </div>
    </div>
</body>
</html>""".format(ssid=ssid)
        return html.replace('\n', '\r\n')
    
    def get_error_page(self, error_message):
        """
        获取错误页面HTML
        
        参数:
            error_message: 错误信息
        
        返回:
            HTTP响应字符串
        """
        html = """HTTP/1.1 200 OK
Content-Type: text/html
Connection: close

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>配置错误</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 400px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .error { background-color: #f2dede; color: #a94442; padding: 15px; border-radius: 5px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>配置错误</h1>
        <div class="error">
            <strong>错误:</strong> {error_message}
        </div>
        <div class="info">
            <a href="/">返回配置页面</a>
        </div>
    </div>
</body>
</html>""".format(error_message=error_message)
        return html.replace('\n', '\r\n')
    
    def run_server(self, port=80, timeout=300):
        """
        运行Web服务器
        
        参数:
            port: 服务器端口（默认80）
            timeout: 服务器运行超时时间（秒，默认300秒/5分钟）
        
        返回:
            无
        """
        try:
            # 创建socket服务器
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', port))
            self.server_socket.listen(5)
            
            print('Web服务器已启动，端口: {}'.format(port))
            print('请在浏览器中访问: http://{}'.format(self.ap.ifconfig()[0]))
            
            # 设置超时
            self.server_socket.settimeout(1)
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    client_socket, addr = self.server_socket.accept()
                    print('客户端连接: {}'.format(addr))
                    self.handle_client(client_socket)
                except OSError as e:
                    # MicroPython中，超时错误号可能是110或116，具体取决于平台
                    # 110: ETIMEDOUT (某些平台)
                    # 116: ETIMEDOUT (其他平台)
                    if hasattr(e, 'errno') and e.errno in (110, 116):
                        # 超时，继续循环
                        pass
                    elif hasattr(e, 'args') and e.args and e.args[0] in (110, 116):
                        # 另一种错误号表示方式
                        pass
                    else:
                        # 其他错误，重新抛出
                        raise
            
            print('Web服务器已停止（超时）')
            
        except Exception as e:
            print('运行Web服务器时出错: {}'.format(e))
        finally:
            if self.server_socket:
                self.server_socket.close()
    
    def run_config_portal(self, timeout=300):
        """
        运行配置门户（启动AP + Web服务器）
        
        参数:
            timeout: 配置门户运行时间（秒）
        
        返回:
            无
        """
        print('启动配置门户...')
        
        # 启动AP
        if not self.start_ap():
            print('无法启动AP模式，配置门户失败')
            return
        
        # 运行Web服务器
        self.run_server(port=80, timeout=timeout)
        
        # 停止AP
        self.stop_ap()
        print('配置门户已关闭')

def main():
    """
    独立运行配置门户
    """
    config_portal = WebConfigService()
    config_portal.run_config_portal(timeout=300)  # 运行5分钟

if __name__ == '__main__':
    main()
