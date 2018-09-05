from django.urls import path,include,re_path
from .views import CourseListView,CourseDetailView,CourseInfoView,CommentsView,AddCommentsView,VideoPlayView


urlpatterns = [
    # 课程列表
    path('list/', CourseListView.as_view(), name='course_list'),
    #课程详情
    re_path('detail/(\w+)/', CourseDetailView.as_view(), name="course_detail"),
    # 课程章节信息页
    re_path('info/(\w+)/', CourseInfoView.as_view(), name="course_info"),
    # 课程评论
    re_path('comment/(\w+)/', CommentsView.as_view(), name="course_comments"),
    # 添加评论
    path('add_comment/', AddCommentsView.as_view(), name="add_comment"),
    # 课程视频播放页,未完成，不开放api接口
    # re_path('video/(\w+)/', VideoPlayView.as_view(), name="video_play"),

]