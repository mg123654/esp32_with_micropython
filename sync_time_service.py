import time
from ntptime import settime

def sync_time_service(wlan, timezone_offset=8):
    """
    时间校准服务：负责从NTP同步时间，并提供本地时间获取和格式化
    
    参数:
        wlan: wlan对象，用于检查网络连接
        timezone_offset: 时区偏移（小时），默认UTC+8
    
    返回:
        如果同步成功，返回一个函数get_local_time_str()，用于获取格式化后的本地时间字符串
        否则返回None
    """
    # 检查网络连接
    if wlan is None or not wlan.isconnected():
        print('时间服务：网络未连接，无法同步时间')
        return None
    
    try:
        settime()  # 设置UTC时间
        print('NTP时间同步成功!')
    except Exception as e:
        print('NTP时间同步失败: {}'.format(e))
        return None
    
    def get_local_time_str():
        """获取本地时间字符串（考虑时区偏移）"""
        # 获取UTC时间戳
        utc_timestamp = time.time()
        # 加上时区偏移（小时转换为秒）
        local_timestamp = utc_timestamp + (timezone_offset * 3600)
        # 转换为本地时间元组
        local_time = time.localtime(local_timestamp)
        # 格式化时间
        year, month, day, hour, minute, second, weekday, yearday = local_time
        weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        return '{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d} {}'.format(
            year, month, day, hour, minute, second, weekdays[weekday])
    
    return get_local_time_str
