#引入标准库
from time import sleep
from platform import *
from sys import *
from socket import *
from shutil import *
from ctypes import *

#根据系统加载按键模块
if system().startswith("Win"):
    import msvcrt
else:
    import termios
    import tty
    import select

#Linux加载身份校验接口
if not system().startswith("Win"):
    from os import geteuid

#跨平台按键检测
class KBHit:
    def __init__(self):
        if not system().startswith("Win"):
            self.fd = stdin.fileno()
            self.old_settings = termios.tcgetattr(self.fd)

    def kb_hit(self):
        if system().startswith("Win"):
            return msvcrt.kbhit()
        try:
            tty.setraw(stdin.fileno(), termios.TCSANOW)
            readable, _, _ = select.select([stdin], [], [], 0)
            return bool(readable)
        finally:
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_settings)

    def get_char(self):
        if system().startswith("Win"):
            return msvcrt.getch()
        try:
            tty.setraw(stdin.fileno(), termios.TCSANOW)
            return stdin.read(1)
        finally:
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_settings)

    def restore_terminal(self):
        if not system().startswith("Win"):
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_settings)

kb = KBHit()

#获取局域网IP
def get_lan_ip():
    try:
        s = socket(AF_INET, SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except PermissionError:
        return "无法获取IP"
    except Exception:
        return "IP读取失败"

lan_ip = get_lan_ip()

#获取磁盘总容量
def disk_info():
    try:
        path = "C:\\" if system().startswith("Win") else "/"
        usage = disk_usage(path)
        total_gb = usage.total // (1024 ** 3)
        return total_gb
    except PermissionError:
        return "无磁盘读取权限"
    except Exception:
        return "磁盘读取失败"

#识别用户权限
def privilege():
    if system().startswith("Win"):
        try:
            return "administrator" if windll.shell32.IsUserAnAdmin() else "user"
        except:
            return "权限状态获取失败"
    else:
        try:
            return "root" if geteuid() == 0 else "普通用户(非root)"
        except:
            return "权限读取异常"

if __name__ == "__main__":
    print(f"你的系统是 {system()} {release()} {machine()}")
    print(f"你的局域网IP：{lan_ip}")

    disk_data = disk_info()
    if system().startswith("Win"):
        print(f"C盘总大小: {disk_data}GB")
    else:
        print(f"根目录总大小: {disk_data}GB")

    print(f"当前用户身份：{privilege()}")
    print("【提示】倒计时期间按下键盘任意键可立刻退出程序\n")

    timer = 10
    exit_flag = False
    remaining = timer
    #改用细粒度轮询，不用等整1秒才检测按键
    while remaining > 0 and not exit_flag:
        print(f"\r{' ' * 60}\r剩余{remaining}秒钟自动退出", end="", flush=True)
        for _ in range(10):
            if kb.kb_hit():
                kb.get_char()
                exit_flag = True
                break
            sleep(0.1)
        if not exit_flag:
            remaining -= 1

    kb.restore_terminal()
    print("\r" + " " * 60, end="")
    if exit_flag:
        print("\n已按下按键，程序手动退出")
    else:
        print("\n倒计时结束，程序正常退出")
