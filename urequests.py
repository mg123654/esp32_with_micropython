
# urequests.py
# MicroPython HTTP请求库（简化版）
# 允许在ESP32等设备上用类似requests的方式进行HTTP通信
# 来源：https://github.com/micropython/micropython-lib/blob/master/python-ecosys/urequests/urequests.py

import usocket  # MicroPython的socket库，用于网络通信
import ujson    # MicroPython的json库，用于处理JSON数据

# HTTP响应对象，封装了底层socket和常用属性
class Response:
    def __init__(self, sock):
        self.raw = sock         # 原始socket对象
        self._cached = None    # 缓存读取的内容

    def close(self):
        # 关闭socket连接
        if self.raw:
            self.raw.close()
            self.raw = None

    @property
    def content(self):
        # 获取响应的原始字节内容
        if self._cached is None:
            self._cached = self.raw.read()
            self.close()
        return self._cached

    @property
    def text(self):
        # 获取响应的文本内容（utf-8解码）
        return str(self.content, "utf-8")

    def json(self):
        # 以JSON格式解析响应内容
        return ujson.loads(self.content)

# 发送HTTP请求的主函数
def request(method, url, data=None, json=None, headers={}, stream=None):
    # 解析URL，获取协议、主机、路径
    try:
        proto, dummy, host, path = url.split('/', 3)
    except ValueError:
        proto, dummy, host = url.split('/', 2)
        path = ''
    if proto == 'http:':
        port = 80
    else:
        raise ValueError('Unsupported protocol: ' + proto)
    # 支持主机:端口格式
    if ':' in host:
        host, port = host.split(':', 1)
        port = int(port)
    # 域名解析，获取IP和端口
    ai = usocket.getaddrinfo(host, port)
    addr = ai[0][-1]
    s = usocket.socket()
    s.connect(addr)
    # 发送HTTP请求行
    s.write(b"%s /%s HTTP/1.0\r\n" % (method, path))
    # 发送Host头
    if not 'Host' in headers:
        s.write(b"Host: %s\r\n" % host)
    # 发送自定义头部
    for k in headers:
        s.write(b"%s: %s\r\n" % (k, headers[k]))
    # 处理JSON数据
    if json is not None:
        assert data is None
        import ujson
        data = ujson.dumps(json)
        s.write(b"Content-Type: application/json\r\n")
    # 发送Content-Length头
    if data:
        s.write(b"Content-Length: %d\r\n" % len(data))
    # 结束头部
    s.write(b"\r\n")
    # 发送请求体
    if data:
        s.write(data)
    # 读取响应状态行
    l = s.readline()
    protover, status, msg = l.split(None, 2)
    # 跳过响应头
    while True:
        l = s.readline()
        if not l or l == b"\r\n":
            break
    # 返回Response对象
    resp = Response(s)
    resp.status_code = int(status)
    return resp

# 以下为常用HTTP方法的快捷函数
def get(url, **kw):
    return request("GET", url, **kw)

def post(url, **kw):
    return request("POST", url, **kw)

def put(url, **kw):
    return request("PUT", url, **kw)

def patch(url, **kw):
    return request("PATCH", url, **kw)

def delete(url, **kw):
    return request("DELETE", url, **kw)
