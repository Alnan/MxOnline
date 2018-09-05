from django.template import Library
from django.utils.safestring import mark_safe
import datetime,time

register = Library()

@register.simple_tag
def render_paginator(orgs,city_id='',category=''):
    """
    分页功能
    从views中拿到orgs
    paginator = Paginator(querysets, 2) ：一页显示2行
    orgs = paginator.page(page)：当前页码
    """
    ele = '''
        <nav aria-label="Page navigation">
            <ul class="pagination">
                <li>
                    <a href="?_page=1&city=%s&ct=%s" aria-label="shouye">
                        <span aria-hidden="true">首页</span>
                    </a>
                </li>
    '''%(city_id,category)
    if orgs.has_previous():
        p_ele = '''
        <li><a href="?_page=%s&city=%s&ct=%s" aria-label="Previous" >prev</a></li>
        ''' % (orgs.previous_page_number(),city_id,category)
        ele += p_ele
    # querysets.paginator=paginator，page_range:页数范围
    for i in orgs.paginator.page_range:
        # querysets.number:当前页码

        if abs(orgs.number - i) < 3:# 只显示相邻页码，最多2页
            active = ''
            # 当前页
            if orgs.number ==i :
                active = 'active'

            p_ele = '''
            <li class="%s"><a href="?_page=%s&city=%s&ct=%s">%s</a></li>
            '''% (active,i,city_id,category,i)
            ele += p_ele
        #是否有下一页
    if orgs.has_next():
        p_ele = '''
            <li><a href="?_page=%s&city=%s&ct=%s" aria-label="Next">next</a></li>
             ''' % (orgs.next_page_number(),city_id,category)
        ele += p_ele

        #querysets.paginator.num_pages：总页数
    p_ele = '''
        <li>
            <a href="?_page=%s&city=%s&ct=%s" aria-label="weiye">
                <span aria-hidden="true">尾页</span>
            </a>
        </li>
    '''% (orgs.paginator.num_pages,city_id,category)
    ele += p_ele

    ele += "</ul></nav>"
    return mark_safe(ele)


