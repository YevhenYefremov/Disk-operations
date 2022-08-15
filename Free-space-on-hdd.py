import ctypes
import os
import sys
import platform
import string
from ctypes import windll
import json
import logging
import filecmp
from shutil import copyfile

filename = 'Server 40 HDD'
dstpath = '\\\\192.168.11.107\\test\\'

logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s',
                              '%m-%d-%Y %H:%M:%S')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler(f'{filename}.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stdout_handler)


def get_drives():
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(letter)
        bitmask >>= 1

    return drives


def get_hdd_spaces_mb(folder):
    if platform.system() == 'Windows':
        total_bytes = ctypes.c_ulonglong(0)
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, ctypes.pointer(total_bytes),
                                                   ctypes.pointer(free_bytes))
        return free_bytes.value/1024/1024/1024, total_bytes.value/1024/1024/1024
    else:
        st = os.statvfs(folder)
        return st.f_bavail * st.f_frsize/1024/1024, st.f_blocks * st.f_frsize/1024/1024 * st.f_ffree


def main():
    data = [{'Drive': ('free', 'total')}]
    for drive in get_drives():
        free, total = get_hdd_spaces_mb(f'{drive}:\\')
        data[0][drive] = (free, total)
    try:
        with open(f'{dstpath}{filename}.json', 'w') as outfile:
            json.dump(data, outfile)
            if os.path.exists(f'{filename}.log'):
                if os.path.exists(f'{dstpath}{filename}.log'):
                    if not filecmp.cmp(f'{filename}.log', f'{dstpath}{filename}.log'):
                        copyfile(rf'{filename}.log', rf'{dstpath}{filename}.log')
                else:
                    copyfile(rf'{filename}.log', rf'{dstpath}{filename}.log')

    except FileNotFoundError:
        logger.error('FileNotFoundError: No such file or directory')
        logger.info(data)
    except Exception as e:
        logger.error(e.with_traceback)
        logger.info(data)


if __name__ == '__main__':
    main()
