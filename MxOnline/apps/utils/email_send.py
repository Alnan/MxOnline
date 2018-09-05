import random
from users.models import EmailVerifyRecord
from django.core.mail import send_mail
from MxOnline import settings

def random_str(random_length=16):
    """默认生成16位随机字符串"""
    str = ''
    # 生成字符串的可选字符串
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    ran_dom = random.Random()
    for i in range(random_length):
        str += chars[random.randint(0, length)]
    return str

# 发送邮件
def send_register_email(email, send_type="register"):
    """
    发送邮件
    发送前需要先保存到数据库，到时候查询链接是否存在
    """
    if send_type == 'update_email': # 修改密码操作
        code = random_str(4)

    else:
        code = random_str(16)

    # 保存到数据库
    EmailVerifyRecord.objects.create(
        code=code,
        email=email,
        send_type=send_type
    )

    # 定义邮箱内容：
    if send_type == "register":
        subject = "Mx在线教育注册激活链接"  # 标题
        email_body = "请复制打开下面的链接激活你的账号：http://127.0.0.1:8000/active/{0}".format(code)  # 文本邮件体
        sender = settings.DEFAULT_FROM_EMAIL  # 发件人
        receiver = [email]  # 接收人
        email_send_status = send_mail(subject, email_body, sender, receiver)
        return email_send_status
        # if email_send_status:
        #     pass
    elif send_type == 'forget':
        subject = "Mx在线教育重置密码链接"  # 标题
        email_body = "请复制打开下面的链接重置密码：http://127.0.0.1:8000/reset/{0}".format(code)  # 文本邮件体
        sender = settings.DEFAULT_FROM_EMAIL  # 发件人
        receiver = [email]  # 接收人
        email_send_status = send_mail(subject, email_body, sender, receiver)
        return email_send_status

    elif send_type == "update_email":
        subject = "Mx在线教育邮箱修改验证码"
        email_body = "你的邮箱验证码为{0}".format(code)
        sender = settings.DEFAULT_FROM_EMAIL
        receiver = [email]

        # 使用Django内置函数完成邮件发送。四个参数：主题，邮件内容，从哪里发，接受者list
        send_status = send_mail(subject, email_body, sender, receiver)
        # 如果发送成功
        if send_status:
            pass