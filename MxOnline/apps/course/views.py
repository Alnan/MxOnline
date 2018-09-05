from django.shortcuts import render,HttpResponse
from django.views.generic import View
from course import models
from django.db.models import Q
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from operation.models import UserFavorite,UserCourse,CourseComments
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

class CourseListView(View):
    '''课程列表'''
    def get(self, request):
        # 所有公开课
        all_courses = models.Course.objects.filter(is_public=True).order_by('add_time')

        # 热门课程推荐
        hot_courses = models.Course.objects.all().order_by('-click_nums')[:3]

        # 搜索功能
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            # 在name字段进行操作,做like语句的操作。i代表不区分大小写
            # or操作使用Q
            all_courses = all_courses.filter(Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords) | Q(
                detail__icontains=search_keywords))
        # 排序
        sort = request.GET.get('sort', "")
        if sort:
            all_courses = all_courses.order_by('-' + sort)
        # 分页
        paginator = Paginator(all_courses, 6)
        page = request.GET.get('_page', 1)
        try:
            all_courses = paginator.page(page)  # 当前页显示的5个数据
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            all_courses = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            all_courses = paginator.page(paginator.num_pages)  # paginator.num_pages：总页数，即返回最后一页
        return render(request, "course/course-list.html",locals())


class CourseDetailView(View):
    '''课程详情'''
    def get(self, request, course_id):
        course = models.Course.objects.get(id=course_id)
        # 课程的点击数加1
        course.click_nums += 1
        course.save()
        # 课程标签
        # 通过当前标签，查找数据库中的课程
        has_fav_course = False
        has_fav_org = False

        # 必须是用户已登录我们才需要判断。
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course.id, fav_type=1):
                has_fav_course = True
            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_org = True
        tag = course.tag
        if tag:
            # 需要从1开始不然会推荐自己
            relate_courses = models.Course.objects.filter(tag=tag)[:2]
        else:
            relate_courses = []
        return  render(request, "course/course-detail.html", locals())


class CourseInfoView(LoginRequiredMixin,View):
    '''课程章节信息'''
    def get(self,request,course_id):
        course = models.Course.objects.get(id=course_id)
        course.students += 1
        course.save()
        # 查询用户是否已经学习了该课程
        user_courses = UserCourse.objects.filter(user=request.user,course=course)
        if not user_courses:
            # 如果没有学习该门课程就关联起来
            user_course = UserCourse.objects.create(user=request.user,course=course)

        #相关课程推荐
        # 找到学习这门课的所有用户
        user_courses = UserCourse.objects.filter(course=course)
        # 找到学习这门课的所有用户的id
        user_ids = [user_course.user_id for user_course in user_courses]
        # 通过所有用户的id,找到所有用户学习过的所有过程
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出所有课程id
        course_ids = [all_user_course.course_id for all_user_course in all_user_courses]
        # 通过所有课程的id,找到所有的课程，按点击量去五个
        relate_courses = models.Course.objects.filter(id__in=course_ids).order_by("-click_nums")[:5]

        # 资源
        all_resources = models.CourseResource.objects.filter(course=course)
        return render(request,'course/course-video.html',locals())


class CommentsView(LoginRequiredMixin,View):
    '''课程评论'''
    def get(self, request, course_id):
        course = models.Course.objects.get(id=course_id)
        all_resources = models.CourseResource.objects.filter(course=course)
        all_comments = CourseComments.objects.filter(course=course)

        # 相关课程推荐
        # 找到学习这门课的所有用户
        user_courses = UserCourse.objects.filter(course=course)
        # 找到学习这门课的所有用户的id
        user_ids = [user_course.user_id for user_course in user_courses]
        # 通过所有用户的id,找到所有用户学习过的所有过程
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出所有课程id
        course_ids = [all_user_course.course_id for all_user_course in all_user_courses]
        # 通过所有课程的id,找到所有的课程，按点击量去五个
        relate_courses = models.Course.objects.filter(id__in=course_ids).order_by("-click_nums")[:5]
        return render(request, "course/course-comment.html", locals())


#添加评论
class AddCommentsView(View):
    '''用户评论'''
    def post(self, request):
        if not request.user.is_authenticated:
            # 未登录时返回json提示未登录，跳转到登录页面是在ajax中做的
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')
        course_id = request.POST.get("course_id", 0)
        comments = request.POST.get("comments", "")
        if int(course_id) > 0 and comments:
            # 实例化一个course_comments对象
            course_comments = CourseComments()
            # 获取评论的是哪门课程
            course = models.Course.objects.get(id = course_id)
            # 分别把评论的课程、评论的内容和评论的用户保存到数据库
            course_comments.course = course
            course_comments.comments = comments
            course_comments.user = request.user
            course_comments.save()
            return HttpResponse('{"status":"success", "msg":"评论成功"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"评论失败"}', content_type='application/json')

class VideoPlayView(LoginRequiredMixin, View):
    '''课程章节视频播放页面'''
    def get(self,request,video_id):
        video = models.Video.objects.get(id=video_id)
        #通过外键找到章节再找到视频对应的课程
        course = video.lesson.course

        course.students += 1
        course.save()

        # 查询用户是否已经学习了该课程
        user_courses = UserCourse.objects.filter(user=request.user,course=course)
        if not user_courses:
            # 如果没有学习该门课程就关联起来
            user_course = UserCourse(user=request.user,course=course)
            user_course.save()

        #相关课程推荐
        # 找到学习这门课的所有用户
        user_courses = UserCourse.objects.filter(course=course)
        # 找到学习这门课的所有用户的id
        user_ids = [user_course.user_id for user_course in user_courses]
        # 通过所有用户的id,找到所有用户学习过的所有过程
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 取出所有课程id
        course_ids = [all_user_course.course_id for all_user_course in all_user_courses]
        # 通过所有课程的id,找到所有的课程，按点击量去五个
        relate_courses = models.Course.objects.filter(id__in=course_ids).order_by("-click_nums")[:5]

        # 资源
        all_resources = models.CourseResource.objects.filter(course=course)
        return render(request,'course/course-play.html',locals())