import subprocess
from functools import partial  # 锁定参数

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
