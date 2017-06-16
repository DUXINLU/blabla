# -*- coding:utf-8 -*-
import sqlite3

db_path = '/Users/duxinlu/Desktop/DatabaseDesigning/XKXT.db'


def connect_db():
    db = sqlite3.connect(db_path)
    return db


# 判断选课是否成功
# 所选课程的先修课还没有记录，系统提示“缺先修课，选课失败”；
# 本学期所选课程的上课时间有冲突，系统提示“上课时间有冲突，选课失败”；
# 学生一学期所选课程的学分最多不能超18学分
def judge_select_course(student_number, form):
    db = connect_db()
    cursor = db.cursor()

    credit = 0
    course_time_list = []
    cursor.execute('SELECT c.time FROM sc,c WHERE sc.sid=? AND c.id=sc.cid;', (student_number,))
    t = cursor.fetchall()

    for i in t:
        course_time_list.append(i[0])

    cursor.execute('SELECT register FROM s WHERE id=?', (student_number,))
    try:
        t = cursor.fetchall()[0][0]
        if int(t) != 1:
            return (False, u'学生未注册，选课失败')
    except:
        return (False, u'学生未注册，选课失败')
    for k, v in form.items():
        course_id = k
        course_time = v.split('+')[0]
        course_credit = v.split('+')[1]
        # 判断先修课
        cursor.execute('SELECT precourse FROM c WHERE id=?', (k,))
        precourse = cursor.fetchall()[0][0]
        if precourse:
            cursor.execute('SELECT * FROM sc,c WHERE c.precourse=sc.cid AND sc.sid=?', (student_number,))
            t = cursor.fetchall()
            if len(t) == 0:
                return (False, u'缺先修课，选课失败')
                # 判断时间是否冲突
        if course_time in course_time_list:
            return (False, u'上课时间有冲突，选课失败')
        credit += int(course_credit)

    if credit > 18:
        return (False, u'选课学分超过18，选课失败')

    return (True, form.keys())
