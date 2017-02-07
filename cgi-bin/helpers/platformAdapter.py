class OSHelper:
    def detect_environment():
        import os
        if os.name == 'nt':
            import winreg
            import glob
            import platform
            print("Windows Environment")
            try:
                ARCH_ARR = ["arm64", "arm", "x64", "x86"]
                ARCH_INDEX0 = 0 if ("arm" in platform.machine().lower()) else 2
                ARCH_INDEX1 = 0 if ("64" in platform.architecture()[0]) else 1
                ARCH_NAME = ARCH_ARR[ARCH_INDEX0 + ARCH_INDEX1]
                _ = r'SOFTWARE\WOW6432Node\Microsoft\Microsoft SDKs\Windows\v10.0'
                WK_WINREG_KEY = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE, _, 0, winreg.KEY_READ)
                WK_PATH, _ = winreg.QueryValueEx(WK_WINREG_KEY, 'InstallationFolder')
                winreg.CloseKey(WK_WINREG_KEY)

                WK_LIB_ROOT = max(glob.glob(WK_PATH + '\\Lib\\*'))
                WK_INCLUDE_ROOT = max(glob.glob(WK_PATH + '\\Include\\*'))
                WK_INCLUDE = WK_INCLUDE_ROOT + r'\ucrt'
                WK_LIB_UM = WK_INCLUDE_ROOT + r'\um'
                WK_LIB_UCRT64 = WK_LIB_ROOT + "\\ucrt\\" + ARCH_NAME

                if os.path.isdir(WK_INCLUDE):
                    os.environ['INCLUDE'] = WK_INCLUDE
                else:
                    print('Include Path for Windows Kit not exists: ' + WK_INCLUDE)

                if os.path.isdir(WK_LIB_UM) and os.path.isdir(WK_LIB_UCRT64):
                    os.environ['LIB'] = WK_LIB_UM + ';' + WK_LIB_UCRT64
                    print("Path Found.")
                else:
                    if os.path.isdir(WK_LIB_UM):
                        print('Lib Path(Windows Kit UCRT64) not exists: ' + WK_LIB_UCRT64)
                    else:
                        print('Lib Path(Windows Kit UM) not exists: ' + WK_LIB_UM)
            except WindowsError:
                print('Cannot get Windows Kit Library path from WINREG')