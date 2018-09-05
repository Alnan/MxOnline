from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth import authenticate ,login ,logout
from django.contrib.auth.backends import ModelBackend
from MxOnline import forms
from users.models import UserProfile,EmailVerifyRecord
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from utils import email_send
from users.models import Banner
from course.models import Course,CourseOrg

# Create your views here.

def index(request):
    """首页"""
    if request.method =="GET":
        # 轮播图
        all_banners = Banner.objects.all().order_by('index')
        # 课程
        courses = Course.objects.filter(is_banner=False)[:6]
        # 轮播课程
        banner_courses = Course.objects.filter(is_banner=True)[:3]
        # 课程机构
        course_orgs = CourseOrg.objects.all()[:15]
        return render(request, 'index.html',locals())



class CustomBackend(ModelBackend):
    """
    用于mx_login下的authenticate，
    setting中需配置全局路径AUTHENTICATION_BACKENDS，当用户登录验证时，用到mx_login下的authenticate进行验证，会
    跳到此处进行验证
    """
    def authenticate(self, request, username=None, password=None, **kwargs):# 重写authenticate方法
        try:
            # 不希望用户存在两个，get的结果只能有一个，否则报错
            user = UserProfile.objects.get(Q(username=username)|Q(email=username))
            print(user)
            # django的后台中密码是加密处理的，拿到客户登录的密码需要加密后才能对比判断，所以不能直接password==password
            # UserProfile继承的AbstractUser中有check_password（）方法，会直接将传入的密码加密后于后台的作比较:
            print(user.check_password(password))
            if user.check_password(password):# 如果为False，则密码不一致，否则密码正确

                return user
        except Exception as e:
            return None

def mx_login(request):
    """登录"""
    login_form = forms.LoginForm()
    if request.method == "POST":
        login_form = forms.LoginForm(request.POST)
        if login_form.is_valid():# form验证通过
            # 获取用户提交的用户名和密码
            user_name = request.POST.get('username', None)
            pass_word = request.POST.get('password', None)
            # 成功返回user对象,失败None
            user = authenticate(username=user_name, password=pass_word)
            # 如果不是null说明验证成功
            if user:
                if user.is_active:
                    # 只有注册激活才能登录
                    login(request, user)
                # request.session["is_login"] = True
                # request.session["username"] = user_name
                # request.session.set_expiry(5)
                    return redirect("/index/")
                else:
                    return render(request, 'login.html', {'msg': '用户未激活', 'login_form': login_form})
            # 账号或密码错误
            else:
                return render(request, 'login.html', {'msg': '用户名或密码错误','login_form': login_form})
        else:
            return render(request, 'login.html', {'msg': '请正确输入用户名及密码','login_form': login_form})


    # return render(request,'login.html',{'login_form': login_form})
    return render(request,'login.html')


def mx_logout(request):
    """退出登录"""
    logout(request)
    return redirect('/index/')


def register(request):
    """用户注册"""

    if request.method == "POST":
        register_form = forms.RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get('email',None)
            if UserProfile.objects.filter(email=user_name):
                # 用户已经存在，不用再注册
                return render(request,'register.html',{'msg':'用户已经存在','register_form':register_form})
            pass_word = request.POST.get('password',None)
            pass_word = make_password(pass_word) # 密码加密后再保存
            UserProfile.objects.create(
                username=user_name,
                email=user_name,
                is_active=False,
                password=pass_word
            )
            email_send.send_register_email(user_name,'register') # 发送邮件，用户激活账号
            return redirect('/login/')
        else:
            status_form = True  #用于前端注册时判断是否填充客户输入原数据
            return render(request,'register.html',locals())
    else:
        register_form = forms.RegisterForm()
        return render(request,'register.html',{'register_form':register_form})

def user_active(request,ac_code):
    """用户账号激活"""
    if request.method == "GET":
        ac_record = EmailVerifyRecord.objects.filter(code=ac_code,)
        if ac_record:
            ac_email = ac_record[0].email
            ac_user = UserProfile.objects.get(email=ac_email)
            ac_user.is_active = True
            ac_user.save()
        else:
            return render(request,'active_fail.html')
        email_count = ac_record[0].email
        # return render(request,'login.html',{'email_count':email_count})
        return render(request,'active_success.html',{'email_count':email_count})


def forget_pwd(request):
    """忘记密码"""
    message ={}
    if request.method == "POST":
        forgetpwd_form = forms.ForgetPwdForm(request.POST)
        if forgetpwd_form.is_valid():
            email = request.POST.get('email',None)
            user_count = UserProfile.objects.filter(email=email)
            if user_count:# 判断邮箱是否存在
                send_status = email_send.send_register_email(email,'forget')
                # print("send:",send_status)
                if send_status:
                    return render(request,'send_email_success.html')
            else:
                message['msg'] = '该邮箱不存在'
                message['status'] =True
                return render(request,'forgetpwd.html',{'message':message,'forgetpwd_form':forgetpwd_form})
        else:  # form表单验证不通过
            message['msg'] = '邮箱或验证码错误'
            message['status'] = True
            return render(request,'forgetpwd.html',{'message':message,'forgetpwd_form':forgetpwd_form})

    else:
        forgetpwd_form = forms.ForgetPwdForm()
    return render(request,'forgetpwd.html',{'forgetpwd_form':forgetpwd_form})


def pwd_reset(request,ac_code):
    """用户重置密码链接"""
    if request.method =="GET":
        records = EmailVerifyRecord.objects.filter(code=ac_code)
        if records:
            email = records[0].email
            return render(request, "password_reset.html", {"email": email})
        else:# 链接不对
            return render(request, "active_fail.html")
    # return render(request, "login.html")


def modify_pwd(request):
    """重置密码"""
    if request.method == "POST":
        modify_form = forms.ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", None)
            pwd2 = request.POST.get("password2", None)
            email = request.POST.get("email", None)
            if pwd1 != pwd2:
                return render(request, "password_reset.html", {"email": email, "msg": "密码不一致！"})
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd2)
            user.save()
            return render(request, "login.html")
        else:
            email = request.POST.get("email", None)
            return render(request, "password_reset.html", {"email": email, "modify_form": modify_form})


