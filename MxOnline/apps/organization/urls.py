from django.urls import path,include,re_path
from organization import views
from organization.views import TeacherListView,TeacherDetailView

urlpatterns = [
    # 列表页
    path('list/', views.org_list, name = 'org_list'),
    path('user_ask/', views.add_user_ask, name = 'user_ask'),
    re_path(r'^org_detail_home/(\w+)/$', views.org_detail_home, name='org_detail_home'), # 机构首页
    re_path(r'^org_course_home/(\w+)/$', views.org_course_home, name='org_course_home'), # 该机构所有课程
    re_path(r'^org_detail_desc/(\w+)/$', views.org_detail_desc, name='org_detail_desc'), # 该机构详细介绍
    re_path(r'^org_detail_teacher/(\w+)/$', views.org_detail_teacher, name='org_detail_teacher'),  # 该机构所有讲师

    path('user_fav/', views.user_fav, name='user_fav'),  # 用户收藏

    # 讲师列表
    path('teacher/list/', TeacherListView.as_view(), name="teacher_list"),
    # 讲师详情
    re_path('teacher/detail/(\w+)/', TeacherDetailView.as_view(), name="teacher_detail"),


]