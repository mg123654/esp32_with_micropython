# ESP32 MicroPython 网络时间同步项目

## 项目概述
本项目实现了ESP32 MicroPython设备通过WiFi连接互联网，从NTP服务器同步时间，并通过串口实时输出本地时间的功能。项目采用服务化架构设计，并新增了Web配置功能，允许用户通过网页界面配置WiFi连接信息。

## 文件说明

### 1. config.py
配置文件，包含以下配置项：
- `WIFI_SSID`: WiFi网络名称（从wifi_config_service加载，如果没有保存的配置则使用默认值）
- `WIFI_PASSWORD`: WiFi密码（从wifi_config_service加载，如果没有保存的配置则使用默认值）
- `WIFI_TIMEOUT`: WiFi连接超时时间（秒），默认15秒
- `TIMEZONE_OFFSET`: 时区偏移（小时），默认UTC+8（中国时区）
- `NTP_SERVER`: NTP服务器地址，默认使用pool.ntp.org

### 2. wifi_service.py
WiFi服务模块，包含以下功能：
- `wifi_init()`: 初始化WiFi接口
- `wifi_connect()`: 连接WiFi网络（支持超时设置）
- `wifi_disconnect()`: 断开WiFi连接
- `wifi_status()`: 获取WiFi状态

### 3. sync_time_service.py
时间校准服务模块，包含以下功能：
- `sync_time_service()`: 从NTP服务器同步时间，并返回一个获取本地时间的函数

### 4. wifi_config_service.py
WiFi配置服务模块，包含以下功能：
- `load_wifi_config()`: 从JSON文件加载WiFi配置
- `save_wifi_config()`: 保存WiFi配置到JSON文件
- `get_current_config()`: 获取当前WiFi配置（ssid和密码）
- `clear_wifi_config()`: 清除保存的WiFi配置

### 5. web_config_service.py
Web配置服务模块，包含以下功能：
- 启动AP模式（创建WiFi热点）
- 运行Web服务器，提供配置页面
- 通过网页界面接收用户输入的WiFi配置并保存
- 支持在WiFi连接失败时自动启动配置门户

### 6. main.py
主程序文件，包含以下功能：
- 初始化UART1串口通信（波特率115200，使用串口1避免与解释器冲突）
- 调用WiFi服务连接网络
- 如果WiFi连接失败，自动启动Web配置门户
- 调用时间校准服务同步时间
- 实时输出本地时间到串口1

## 使用步骤

### 方法一：通过配置文件设置（传统方式）

#### 1. 配置WiFi信息
编辑`config.py`文件，将`WIFI_SSID`和`WIFI_PASSWORD`修改为你的实际WiFi信息：

```python
WIFI_SSID = '你的WiFi名称'
WIFI_PASSWORD = '你的WiFi密码'
```

#### 2. 上传文件到ESP32
使用MicroPython工具（如Thonny、ampy等）将以下文件上传到ESP32：
- `config.py`
- `main.py`
- `wifi_service.py`
- `sync_time_service.py`
- `wifi_config_service.py`
- `web_config_service.py`

#### 3. 连接串口监视器
使用串口工具（如PuTTY、Thonny串口监视器等）连接ESP32，波特率设置为115200。

#### 4. 运行程序
在ESP32上运行`main.py`，你将看到以下输出：

```
ESP32 MicroPython 网络时间同步程序（服务化重构 + Web配置）
正在连接WiFi网络...
WiFi连接成功!
NTP时间同步成功!
开始输出本地时间...
本地时间: 2025-12-05 23:10:20 Fri
本地时间: 2025-12-05 23:10:21 Fri
...
```

### 方法二：通过Web界面设置（推荐方式）

#### 1. 上传所有文件
将所有Python文件上传到ESP32（同上）。

#### 2. 首次运行
如果`wifi_config.json`文件不存在或配置错误，ESP32会尝试使用默认配置连接WiFi。如果连接失败，会自动启动配置门户（AP模式）。

#### 3. 连接配置热点
用手机或电脑连接ESP32创建的WiFi热点：
- 热点名称：`ESP32-Config`
- 密码：`12345678`

#### 4. 访问配置页面
打开浏览器，访问 `http://192.168.4.1`（或其他显示的IP地址），进入WiFi配置页面。

#### 5. 输入WiFi信息
在配置页面中输入你要连接的WiFi名称（SSID）和密码，点击"保存配置"。

#### 6. 自动重连
ESP32会自动重启并尝试使用新配置连接WiFi。如果连接成功，将开始同步时间并通过串口输出。

## 硬件连接

- ESP32开发板
- USB数据线（用于供电和串口通信）
- 确保ESP32处于WiFi网络覆盖范围内

## 注意事项

1. 首次运行时，如果没有保存的WiFi配置，程序会使用`config.py`中的默认配置。
2. 如果WiFi连接失败，程序会自动启动配置门户（AP模式），允许用户通过网页配置。
3. 时区偏移可根据需要修改`TIMEZONE_OFFSET`值。
4. 使用UART1（TX=GPIO17, RX=GPIO16）进行串口通信，避免与MicroPython解释器冲突。
5. 配置门户默认运行3分钟，超时后会自动关闭并尝试重新连接WiFi。
6. 保存的WiFi配置存储在`wifi_config.json`文件中，即使重启也不会丢失。

## 故障排除

- **WiFi连接失败**：检查SSID和密码是否正确，确保ESP32在WiFi覆盖范围内。如果使用Web配置，请确认输入的WiFi信息正确。
- **NTP同步失败**：检查网络连接，尝试更换其他NTP服务器。
- **串口无输出**：检查波特率设置（115200），确认串口线连接正常。注意本程序使用UART1（TX=GPIO17, RX=GPIO16），请确认你的硬件连接。
- **无法访问配置页面**：确认已连接到ESP32的热点（ESP32-Config），并访问正确的IP地址（通常为192.168.4.1）。
- **配置门户未启动**：如果WiFi连接失败但配置门户没有启动，检查`web_config_service.py`是否正确上传，以及是否有语法错误。

## 扩展功能

如需扩展功能，可修改`main.py`：
- 添加OLED显示时间
- 添加按钮调整时区
- 添加定时任务功能
- 将时间信息通过MQTT发布
