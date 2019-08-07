"""
This program uses RS232 serial communications to control the light.
It sends 8-bit signal to the receiver.

光源控制器通信协议：

波特率 9600 bps; 数据长度 8 bits; 停止位 1 bit; 奇偶校验 无。
数据格式：特征字（1 bit），命令字（1 bit），通道字（1 bit），数据（3 bits），异或和校验字（2 bits）

注: 所有通讯字节都采用ASCII码。
    特征字 = '￥'。
    命令字 ＝ 1，2，3，4，分别定义为：
        1：打开对应通道亮度
        2：关闭对应通道亮度
        3：设置对应通道亮度参数
        4：读出对应通道亮度参数
    通道字 ＝ 1，2。分别代表2个输出通道。
    数据 ＝ 0XX（XX=00～FF内的任一数值），对应通道电源的设置参数，高位在前，低位在后。
    异或和校验字 ＝ 除校验字外的字节（包括：特征字，命令字，通道字和数据）的异或校验和，校验和的高半字节ASCII码在前，低半字节ASCII码在后。

Author: Siqi Dai
ABB
"""


import serial
import serial.tools.list_ports
from PathsAndParameters import light_port1, light_port2


def light_on(brightness):
    """
    Turns on both lights
    :param brightness: decimal value of light brightness
    :return: return True if the operation was successful, otherwise return False
    """
    brightness = str(hex(brightness))  # convert decimal to hex; format of hex is '0x_ _'
    brightness = brightness[2:]  # remove '0x' at the beginning of the hex value
    brightness = '0' + brightness if len(brightness) == 2 else '00' + brightness  # use 3 bits to represent brightness
    signal = "$11" + brightness + "6D"  # turned on channel 1 and set user-defined brightness

    try:
        ser = serial.Serial(port=light_port1, baudrate=9600, bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=None)  # open serial port
    except:
        print('RS232 connection failed.')
        return False
    ser.write(signal.encode())  # send signal, turn on the light
    ser.close()

    try:
        ser = serial.Serial(port=light_port2, baudrate=9600, bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=None)  # open serial port
    except:
        print('RS232 connection failed.')
        return False
    ser.write(signal.encode())  # send signal, turn on the light
    ser.close()
    return True


def light_off():
    """
    Turns off both lights
    :return: return True if the operation was successful, otherwise return False
    """
    try:
        ser = serial.Serial(port=light_port1, baudrate=9600, bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=None)  # open serial port
    except:
        print('RS232 connection failed.')
        return False
    ser.write(b'$210006D')  # send signal, turn off the light
    ser.close()

    try:
        ser = serial.Serial(port=light_port2, baudrate=9600, bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=None)  # open serial port
    except:
        print('RS232 connection failed.')
        return False
    ser.write(b'$210006D')  # send signal, turn off the light
    ser.close()
    return True


# plist = list(serial.tools.list_ports.comports())
# if len(plist) <= 0:
#     print("没有发现端口!")
# else:
#     plist_0 = list(plist[0])
#     serialName = plist_0[0]
#     serialFd = serial.Serial(serialName, 9600, timeout=60)
#     print("可用端口名>>>", serialFd.name)
