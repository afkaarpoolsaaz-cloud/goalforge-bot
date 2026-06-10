import win32serviceutil
import win32service
import win32event
import subprocess
import sys
import os


class ForgeService(win32serviceutil.ServiceFramework):
    _svc_name_ = "ForgeBotService"
    _svc_display_name_ = "Forge AI Bot Service"

    def __init__(self, args):
        super().__init__(args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.process = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

        if self.process:
            self.process.kill()

    def SvcDoRun(self):
        self.process = subprocess.Popen(
            [sys.executable, os.path.join(os.getcwd(), "bot.py")]
        )

        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)


if __name__ == "__main__":
    win32serviceutil.HandleCommandLine(ForgeService)