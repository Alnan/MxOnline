"""MxOnline URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path,include,re_path
from django.views.static import serve
# from django.conf.urls.static import static
from MxOnline.settings import MEDIA_ROOT,STATICFILES_DIRS

import xadmin
from MxOnline import views

urlpatterns = [
    path('xadmin/', xadmin.site.urls),
    path('index/', views.index, name = 'index'),
    path('login/', views.mx_login, name = 'login'),
    path('logout/', views.mx_logout, name = 'logout'),
    path('register/', views.register, name = 'register'),
    # re_path('active/(?P<active_code>.*)/',ActiveUserView.as_view(),name='user_active'),
    re_path(r'^active/(\w+)/',views.user_active,name='user_active'),# 邮箱激活账号
    path('forgetpwd/',views.forget_pwd,name='forgetpwd'), # 忘记密码
    re_path(r'^reset/(\w+)/',views.pwd_reset,name='reset'), # 邮箱重置密码链接
    path('modify_pwd/',views.modify_pwd,name='modify_pwd'), # 重置密码

    # 验证码
    re_path(r'^captcha', include('captcha.urls')),

    # 所有organization相关的url链接，都转到organization包中的urls.py处理
    path('org/',include("organization.urls")),
    #course下的url跳转
    path("course/", include('course.urls')),
    #个人信息
    path("users/", include('users.urls')),

    # 处理静态文件,使用Django自带serve,传入setting中路径配置MEDIAROOT，让它根据路径找media下的文件
    re_path(r'^media/(?P<path>.*)', serve, {"document_root": MEDIA_ROOT }),

    #当setting中DEBUG设置为False时，django不会再自动帮你处理setting中设置好的static_dirs路径，
    #需要手动static_dirs路径，然后使用serve根据路径帮忙找到static下的文件
    # re_path(r'^static/(?P<path>.*)', serve, {"document_root": STATICFILES_DIRS[0] }),

    # 富文本相关url
    path('ueditor/',include('DjangoUeditor.urls' )),

]
# urlpatterns += static('/media/', document_root=MEDIA_ROOT)

# 全局404页面配置
# handler404 = 'users.views.pag_not_found'
# 全局500页面配置
# handler500 = 'MxOnline.views.page_error'