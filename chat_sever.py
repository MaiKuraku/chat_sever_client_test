"""
chat room
env: python3.6
socket udp  and process
"""

from socket import *
from multiprocessing import Process

# 服务器地址
HOST = "0.0.0.0"
PORT = 8888
ADDR = (HOST, PORT)

# 用户信息存储  {name : address}
user = {}
# 违规用户名单
warn_user = {}
# 敏感词汇列表
list_words = ["蔡徐坤", "鸡你太美", "傻逼", "傻吊"]


# 处理进入聊天室
def do_login(s, name, address):
    if name in user:
        s.sendto("该用名已经存在".encode(), address)
        return
    else:
        s.sendto(b'OK', address)
        # 告知其他人
        msg = "欢迎 %s 进入聊天室" % name
        for i in user:
            s.sendto(msg.encode(), user[i])
        user[name] = address  # 字典中增加一项
        warn_user[name] = 0  # 警告名单中的警告次数初始为0


def do_judge(name, text):  # 判断语句中的敏感词,记录用户违规次数
    for item in list_words:
        if item in text:
            warn_user[name] += 1
            if warn_user[name] > 3:
                return 0  # 违规满了三次
            else:
                return 1  # 违规未满三次
    else:
        return 2  # 没有违规记录


# 违规三次以内的
def del_warning(s, name):
    msg1 = "%s : %s" % (name, '发送违规内容被警告一次')
    msg2 = "警告：您发送的消息有违规内容！！(被警告三次以上将被禁言)"
    s.sendto(msg2.encode(), user[name])
    for i in user:
        if i != name:
            s.sendto(msg1.encode(), user[i])


# 违规三次以上
def del_serious(s, name):
    msg = "您已被禁言！不能发送任何消息！"
    s.sendto(msg.encode(), user[name])


# 文明交流者
def del_civilized(s, name, text):
    msg = "%s : %s" % (name, text)
    for i in user:
        # 除去本人
        if i != name:
            s.sendto(msg.encode(), user[i])


# 处理聊天
def do_chat(s, name, text):
    judge = do_judge(name, text)
    if judge == 0:
        del_serious(s, name)
    elif judge == 1:
        del_warning(s, name)
    elif judge == 2:
        del_civilized(s, name, text)


# 处理退出
def do_quit(s, name):
    if name in warn_user:
        del warn_user[name]
    del user[name]  # 删除用户
    msg = "%s 退出聊天室" % name
    for i in user:
        s.sendto(msg.encode(), user[i])


# 接收各个客户端请求
def request(s):
    while True:
        data, addr = s.recvfrom(1024)  # 接收请求
        tmp = data.decode().split(' ', 2)  # 对请求解析
        if tmp[0] == 'L':
            # 处理进入聊天室 tmp --> ['L', 'name']
            do_login(s, tmp[1], addr)
        elif tmp[0] == 'C':
            # 处理聊天  tmp --> [C , name,xxxx]
            do_chat(s, tmp[1], tmp[2])
        elif tmp[0] == 'Q':
            # 处理退出 tmp --> [Q,  name]
            do_quit(s, tmp[1])


# 搭建基本结构
def main():
    # 创建一个udp套接字
    s = socket(AF_INET, SOCK_DGRAM)
    s.bind(ADDR)
    request(s)  # 处理发来的请求


if __name__ == '__main__':
    main()
