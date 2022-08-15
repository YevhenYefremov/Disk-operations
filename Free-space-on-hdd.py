import ctypes
import os
import platform
import string
from ctypes import windll


def get_drives():
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(letter)
        bitmask >>= 1

    return drives


def get_free_space_mb(folder):
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value/1024/1024/1024
    else:
        st = os.statvfs(folder)
        return st.f_bavail * st.f_frsize/1024/1024


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


if __name__ == '__main__':
    for drive in get_drives():
        free, total = get_hdd_spaces_mb(f'{drive}:\\')
        print(f'{drive}: {free.__round__(1)} GB / {total.__round__(1)} GB')
        # print(drive, ': ', get_free_space_mb(f'{drive}:\\').__round__(1), 'GB')
