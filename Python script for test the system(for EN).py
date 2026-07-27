#Import standard libraries
from time import sleep
from platform import *
from sys import *
from socket import *
from shutil import *
from ctypes import *

#Load keyboard library for corresponding OS
if system().startswith("Win"):
    import msvcrt
else:
    import termios
    import tty
    import select

#Load UID judge module for Linux
if not system().startswith("Win"):
    from os import geteuid

#Cross-platform keyboard capture class
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

#Fetch LAN IP address
def get_lan_ip():
    try:
        s = socket(AF_INET, SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except PermissionError:
        return "IP unavailable"
    except Exception:
        return "Failed to fetch IP address"

lan_ip = get_lan_ip()

#Calculate total disk space
def disk_info():
    try:
        path = "C:\\" if system().startswith("Win") else "/"
        usage = disk_usage(path)
        total_gb = usage.total // (1024 ** 3)
        return total_gb
    except PermissionError:
        return "No permission to read disk info"
    except Exception:
        return "Disk info read failed"

#Check current user permission
def privilege():
    if system().startswith("Win"):
        try:
            return "administrator" if windll.shell32.IsUserAnAdmin() else "user"
        except:
            return "Cannot fetch privilege info"
    else:
        try:
            return "root" if geteuid() == 0 else "regular user(non-root)"
        except:
            return "Privilege detection error"

if __name__ == "__main__":
    print(f"System info: {system()} {release()} {machine()}")
    print(f"LAN IP Address: {lan_ip}")

    disk_data = disk_info()
    if system().startswith("Win"):
        print(f"C Drive Total Size: {disk_data}GB")
    else:
        print(f"Root Directory Total Size: {disk_data}GB")

    print(f"Current User Role: {privilege()}")
    print("[Notice] Press any key during countdown to exit immediately\n")

    timer = 10
    exit_flag = False
    remaining = timer
    #High frequency key polling to catch single key press
    while remaining > 0 and not exit_flag:
        print(f"\r{' ' * 60}\r{remaining} seconds remaining for auto exit", end="", flush=True)
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
        print("\nManual exit triggered by keyboard input")
    else:
        print("\nProgram exited automatically after countdown")
