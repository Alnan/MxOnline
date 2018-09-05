from django.shortcuts import render,redirect,HttpResponse
from organization import models
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from organization import forms
from course.models import Course
from operation.models import UserFavorite
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

# Create your views here.
def org_list(request):
    """课程机构列表"""
    # 所有课程机构
    all_orgs = models.CourseOrg.objects.all()
    # 所有城市
    all_citys = models.CityDict.objects.all()

    # 热门课程机构排名
    hot_orgs = all_orgs.order_by('-click_nums')[:4]

    # 机构搜索功能
    search_keywords = request.GET.get('keywords', '')
    if search_keywords:
        # 在name字段进行操作,做like语句的操作。i代表不区分大小写
        # or操作使用Q
        all_orgs = all_orgs.filter(Q(name__icontains=search_keywords) | Q(desc__icontains=search_keywords))

    # 城市筛选
    city_id = request.GET.get('city','')
    if city_id:
        all_orgs = all_orgs.filter(city_id = int(city_id))
    # 类别筛选
    category =request.GET.get('ct','')
    if category:
        all_orgs = all_orgs.filter(category=category)

    orgs_count = all_orgs.count() # 课程机构总数

    # 学习人数和课程数筛选
    sort = request.GET.get('sort', "")
    if sort:
        all_orgs = all_orgs.order_by('-' + sort)

    # 开始分页功能
    paginator = Paginator(all_orgs, 5)
    page = request.GET.get('_page',1)
    try:
        orgs = paginator.page(page) # 当前页显示的5个数据
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        orgs = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        orgs = paginator.page(paginator.num_pages)  # paginator.num_pages：总页数，即返回最后一页

    return render(request,'organization/org-list.html',locals())


def add_user_ask(request):
    """用户咨询"""
    if request.method == 'POST':
        userask_form = forms.UserAskForm(request.POST)
        if userask_form.is_valid():
            user_ask = userask_form.save()
            # 如果保存成功,返回json字符串,后面content type是告诉浏览器返回的数据类型
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            # 如果保存失败，返回json字符串,并将form的报错信息通过msg传递到前端
            return HttpResponse('{"status":"fail", "msg":"添加出错"}', content_type='application/json')


def org_detail_home(request,org_id):
    """课程机构详情页"""

    current_page = 'home'
    # 根据id找到课程机构
    course_org = models.CourseOrg.objects.get(id=org_id)
    course_org.click_nums += 1
    course_org.save()
    # 判断收藏状态
    has_fav = False
    if request.user.is_authenticated:
        if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
            has_fav = True
    # 反向查询到课程机构的所有课程和老师

    courses = course_org.course_set.all()[:4]
    teachers = course_org.teacher_set.all()[:2]
    return render(request,'organization/org_detail_base.html',locals())

def org_course_home(request,course_org_id):
    """机构课程页"""
    current_page = 'course'

    course_org = models.CourseOrg.objects.get(id = course_org_id)
    # 通过课程机构的id找到对应课程
    all_courses = Course.objects.filter(course_org_id=course_org_id)
    # 判断收藏状态
    has_fav = False
    if request.user.is_authenticated:
        if UserFavorite.objects.filter(user=request.user, fav_id=course_org_id, fav_type=2):
            has_fav = True

    return render(request,'organization/org-detail-course.html',locals())


def org_detail_desc(request,course_org_id):
    """机构课程页"""
    current_page = 'desc'
    # 课程机构
    course_org = models.CourseOrg.objects.get(id = course_org_id)

    # 判断收藏状态
    has_fav = False
    if request.user.is_authenticated:
        if UserFavorite.objects.filter(user=request.user, fav_id=course_org_id, fav_type=2):
            has_fav = True

    return render(request,'organization/org-detail-desc.html',locals())


def org_detail_teacher(request,course_org_id):
    """机构课程页"""
    current_page = 'teacher'
    # 课程机构
    course_org = models.CourseOrg.objects.get(id = course_org_id)
    # 所有讲师
    teachers = course_org.teacher_set.all()

    # 判断收藏状态
    has_fav = False
    if request.user.is_authenticated:
        if UserFavorite.objects.filter(user=request.user, fav_id=course_org_id, fav_type=2):
            has_fav = True

    return render(request,'organization/org-detail-teachers.html',locals())


def user_fav(request):
    if request.method == 'POST':
        id = request.POST.get('fav_id', 0)  # 防止后边int(fav_id)时出错
        type = request.POST.get('fav_type', 0)  # 防止int(fav_type)出错

        if not request.user.is_authenticated:
            # 未登录时返回json提示未登录，跳转到登录页面是在ajax中做的
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')

        exist_record = UserFavorite.objects.filter(user=request.user, fav_id=int(id), fav_type=int(type))
        if exist_record:
            # 如果记录已经存在，表示用户取消收藏
            exist_record.delete()
            if int(type) == 1:
                course = Course.objects.get(id=int(id))
                course.fav_nums -= 1
                if course.fav_nums < 0:
                    course.fav_nums = 0
                course.save()
            elif int(type) == 2:
                org = models.CourseOrg.objects.get(id=int(id))
                org.fav_nums -= 1
                if org.fav_nums < 0:
                    org.fav_nums = 0
                org.save()
            elif int(type) == 3:
                teacher = models.Teacher.objects.get(id=int(id))
                teacher.fav_nums -= 1
                if teacher.fav_nums < 0:
                    teacher.fav_nums = 0
                teacher.save()
            return HttpResponse('{"status":"success", "msg":"点击收藏"}', content_type='application/json')
        else:
            user_fav = UserFavorite()
            if int(type) > 0 and int(id) > 0:
                user_fav.fav_id = int(id)
                user_fav.fav_type = int(type)
                user_fav.user = request.user
                user_fav.save()

                if int(type) == 1:
                    course = Course.objects.get(id=int(id))
                    course.fav_nums += 1
                    course.save()
                elif int(type) == 2:
                    org = models.CourseOrg.objects.get(id=int(id))
                    org.fav_nums += 1
                    org.save()
                elif int(type) == 3:
                    teacher = models.Teacher.objects.get(id=int(id))
                    teacher.fav_nums += 1
                    teacher.save()
                return HttpResponse('{"status":"success", "msg":"已收藏"}', content_type='application/json')
            else:
                return HttpResponse('{"status":"fail", "msg":"收藏出错"}', content_type='application/json')


# 讲师列表
class TeacherListView(View):
    def get(self, request):
        all_teachers = models.Teacher.objects.all().order_by('add_time')
        print(all_teachers)
        # 总共有多少老师使用count进行统计
        teacher_nums = all_teachers.count()

        # 搜索功能
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            # 在name字段进行操作,做like语句的操作。i代表不区分大小写
            # or操作使用Q
            all_teachers = all_teachers.filter(name__icontains=search_keywords)
        # 人气排序
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'hot':
                all_teachers = all_teachers.order_by('-click_nums')

        # 讲师排行榜
        sorted_teacher = models.Teacher.objects.all().order_by('-click_nums')[:3]
        # 进行分页
        paginator = Paginator(all_teachers, 3)
        page = request.GET.get('_page', 1)
        try:
            teachers = paginator.page(page)  # 当前页显示的3个数据
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            teachers = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            teachers = paginator.page(paginator.num_pages)  # paginator.num_pages：总页数，即返回最后一页
        return render(request, "teachers/teachers-list.html",locals())


#讲师详情
class TeacherDetailView(LoginRequiredMixin,View):
    def get(self,request,teacher_id):
        teacher = models.Teacher.objects.get(id=teacher_id)
        teacher.click_nums += 1
        teacher.save()
        all_course = Course.objects.filter(teacher=teacher)
        # 教师收藏和机构收藏
        has_teacher_faved = False
        if UserFavorite.objects.filter(user=request.user, fav_type=3, fav_id=teacher.id):
            has_teacher_faved = True

        has_org_faved = False
        if UserFavorite.objects.filter(user=request.user, fav_type=2, fav_id=teacher.org.id):
            has_org_faved = True
        # 讲师排行榜
        sorted_teacher = models.Teacher.objects.all().order_by('-click_nums')[:3]
        return render(request,'teachers/teacher-detail.html',locals())