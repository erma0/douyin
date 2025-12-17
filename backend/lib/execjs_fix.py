import subprocess
import sys
from functools import partial

# Windows下隐藏控制台窗口
if sys.platform == 'win32':
    # 创建STARTUPINFO对象，隐藏窗口
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    
    # 修改默认参数：设置编码和隐藏窗口
    subprocess.Popen = partial(
        subprocess.Popen, 
        encoding="utf-8",
        startupinfo=startupinfo,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
else:
    # 非Windows系统只设置编码
    subprocess.Popen = partial(subprocess.Popen, encoding="utf-8")

import execjs

if __name__ == "__main__":

    js_code = """
    function hello() {
        return "hello world";
    }
    """
    result = execjs.compile(js_code).call("hello")
    print(result)
