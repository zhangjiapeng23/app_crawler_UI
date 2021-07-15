import re
import subprocess

from log import log

timeout = 8


def execute_cmd(cmd):
    out = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
    for line in out.stdout.readlines():
        yield line
    out.communicate(timeout=timeout)
    out.stdout.close()

def kill_adb_server():
    cmd = 'adb kill-server'
    res = ''
    for i in execute_cmd(cmd):
        res += i
    return res


def get_serial_numbers_ios():
    """
    Get current connected iOS devices' udid.
    :return: list type, a list of devices udid.
    """
    serials = []
    cmd = 'idevice_id -l'
    for i in execute_cmd(cmd):
        udid = re.findall('(.*)\n', i)
        serials.append(udid[0])
    return serials


def get_serial_numbers_android():
    """
    Get current connected Android devices's udid.
    :return: list type, a list of devices uidi
    """
    serials = []
    cmd = 'adb devices'
    for i in execute_cmd(cmd):
        log.info(i)
        if any(('List of devices' in i,'daemon' in i, 'offline' in i,
               'unauthorized' in i, len(i) < 5, 'killing' in i)):
            pass
        else:
            udid = re.findall('(.*)\tdevice', i)
            serials.append(udid[0])
    return serials


def get_device_name_ios(serial_number):
    """
    Get iOS device name by corresponding device udid.
    :param serial_number: string type, device udid.
    :return: string type, device name.
    """
    device_full_name = None
    cmd = 'ideviceinfo -u {} -k ProductType'.format(serial_number)
    for i in execute_cmd(cmd):
        device_name = re.findall('(.*)\n', i)
        device_full_name = ios_devices_name_map(device_name[0])
    return device_full_name.replace(' ', '')


def get_device_name_android(serial_number):
    """
    Get Android device name by corresponding device udid.
    :param serial_number: String type, device udid.
    :return: string type, device name.
    """
    device_full_name = None
    cmd = 'adb -s {} shell getprop ro.product.model'.format(serial_number)
    for i in execute_cmd(cmd):
        device_name = re.findall('(.*)\n', i)
        device_full_name = android_devices_name_map(device_name[0])
    return device_full_name.replace(' ', '')


def get_device_system_version_ios(serial_number):
    """
    Get iOS device system version by corresponding device udid.
    :param serial_number: String type, device udid.
    :return: String type, device system version
    """
    system_version = None
    cmd = 'ideviceinfo -u {} -k ProductVersion'.format(serial_number)
    for i in execute_cmd(cmd):
        system_version = re.findall('(.*)\n', i)
    return system_version[0]


def get_device_system_version_android(serial_number):
    """
    Get Android device system version by corresponding device udid.
    :param serial_number: String type, device udid.
    :return: String type, device system version.
    """
    system_version = None
    cmd = 'adb -s {} shell getprop ro.build.version.release'.format(serial_number)
    for i in execute_cmd(cmd):
        system_version = re.findall('(.*)\n', i)
    if not system_version:
        # when error return default value.
        return 9.0
    return system_version[0]


def get_appium_port(serial_number):
    """
    According to device udid generate a appium server port.
    Rule: 4 is port first number, after three numbers take from udid's first three numbers
    :param serial_number: String type, device udid
    :return: String type, Appium port
    """
    random_number = re.findall(r'\d', serial_number)
    appium_port = '4' + random_number[0] + random_number[1] + random_number[2]
    return appium_port


def get_web_driver_agent_port(serial_number):
    """
    According to device udid generate a web driver agent server port.
    Rule: 8 is port first number, after three numbers take from udid's first three numbers
    :param serial_number: String type, device udid.
    :return: web driver agent port
    """
    random_number = re.findall(r'\d', serial_number)
    web_driver_agent_port = '8' + random_number[0] + random_number[1] + random_number[2]
    return web_driver_agent_port


def ios_devices_name_map(device_name):
    """
    Get iOS device full name
    :param device_name: String type, iOS device mode name
    :return: String type, iOS device full name.
    """
    if device_name == 'iPhone12,1':
        device_full_name = 'iPhone 11'
    elif device_name == 'iPhone12,3':
        device_full_name = 'iPhone 11 Pro'
    elif device_name == 'iPhone12,5':
        device_full_name = 'iPhone 11 Pro Max'
    elif device_name == 'iPhone11,8':
        device_full_name = 'iPhone XR'
    elif device_name == 'iPhone11,6':
        device_full_name = 'iPhone XS Max'
    elif device_name == 'iPhone11,4':
        device_full_name = 'iPhone XS Max'
    elif device_name == 'iPhone11,2':
        device_full_name = 'iPhone XS'
    elif device_name == 'iPhone10,6':
        device_full_name = 'iPhone X'
    elif device_name == 'iPhone10,5':
        device_full_name = 'iPhone 8 Plus'
    elif device_name == 'iPhone10,4':
        device_full_name = 'iPhone 8'
    elif device_name == 'iPhone10,3':
        device_full_name = 'iPhone X'
    elif device_name == 'iPhone10,2':
        device_full_name = 'iPhone 8 Plus'
    elif device_name == 'iPhone10,1':
        device_full_name = 'iPhone 8'
    elif device_name == 'iPhone9,4':
        device_full_name = 'iPhone 7 Plus'
    elif device_name == 'iPhone9,3':
        device_full_name = 'iPhone 7'
    elif device_name == 'iPhone9,2':
        device_full_name = 'iPhone 7 Plus'
    elif device_name == 'iPhone9,1':
        device_full_name = 'iPhone 7'
    elif device_name == 'iPhone8,4':
        device_full_name = 'iPhone SE'
    elif device_name == 'iPhone8,2':
        device_full_name = 'iPhone 6s Plus'
    elif device_name == 'iPhone8,1':
        device_full_name = 'iPhone 6s'
    elif device_name == 'iPhone7,2':
        device_full_name = 'iPhone 6'
    elif device_name == 'iPhone7,1':
        device_full_name = 'iPhone 6 Plus'
    elif device_name == 'iPhone6,2':
        device_full_name = 'iPhone 5s'
    elif device_name == 'iPhone6,1':
        device_full_name = 'iPhone 5s'
    elif device_name == 'iPhone5,4':
        device_full_name = 'iPhone 5c'
    elif device_name == 'iPhone5,3':
        device_full_name = 'iPhone 5c'
    elif device_name == 'iPod7,1':
        device_full_name = 'iPod touch 6G'
    elif device_name == 'iPod5,1':
        device_full_name = 'iPod touch 5G'
    elif device_name == 'iPod4,1':
        device_full_name = 'iPod touch 4G'
    elif device_name == 'iPad7,6':
        device_full_name = 'iPad 6 (Cellular)'
    elif device_name == 'iPad7,5':
        device_full_name = 'iPad 6 (WiFi)'
    elif device_name == 'iPad7,4':
        device_full_name = 'iPad Pro 10.5-inch (Cellular)'
    elif device_name == 'iPad7,3':
        device_full_name = 'iPad Pro 10.5-inch (WiFi)'
    elif device_name == 'iPad7,2':
        device_full_name = 'iPad Pro 12.9-inch 2nd-gen (Cellular)'
    elif device_name == 'iPad7,1':
        device_full_name = 'iPad Pro 12.9-inch 2nd-gen (WiFi)'
    elif device_name == 'iPad6,12':
        device_full_name = 'iPad 5 (Cellular)'
    elif device_name == 'iPad6,11':
        device_full_name = 'iPad 5 (WiFi)'
    elif device_name == 'iPad6,8':
        device_full_name = 'iPad Pro 12.9-inch (Cellular)'
    elif device_name == 'iPad6,7':
        device_full_name = 'iPad Pro 12.9-inch (WiFi)'
    elif device_name == 'iPad6,4':
        device_full_name = 'iPad Pro 9.7-inch (Cellular)'
    elif device_name == 'iPad6,3':
        device_full_name = 'iPad Pro 9.7-inch (WiFi)'
    elif device_name == 'iPad5,4':
        device_full_name = 'iPad Air 2 (Cellular)'
    elif device_name == 'iPad5,3':
        device_full_name = 'iPad Air 2 (WiFi)'
    elif device_name == 'iPad5,2':
        device_full_name = 'iPad Mini 4 (Cellular)'
    elif device_name == 'iPad5,1':
        device_full_name = 'iPad Mini 4 (WiFi)'
    elif device_name == 'iPad4,9':
        device_full_name = 'iPad Mini 3 (Cellular)'
    elif device_name == 'iPad4,8':
        device_full_name = 'iPad Mini 3 (Cellular)'
    else:
        device_full_name = device_name.replace(',', '-')
        # log.warning(device_name + " is not match up!")
    return device_full_name


def android_devices_name_map(device_name):
    """
    Get Android device full name.
    :param device_name:  String type, Android device mode name.
    :return: Sring type, Android device full name.
    """
    if device_name == 'SM-G955U':
        device_full_name = 'Samsung S8 plus'
    elif device_name == 'SM-G935U':
        device_full_name = 'Samsung S7 edge'
    else:
        device_full_name = device_name
    return device_full_name

