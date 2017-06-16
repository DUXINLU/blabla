# coding=utf-8

from flask import Flask, request, url_for, g, redirect, render_template, flash, session
from modules import *
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/')
def home_page():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if not hasattr(g, 'db'):
        g.db = connect_db()
        cursor = g.db.cursor()

    if request.method == 'POST':
        id = request.form['id']
        password = request.form['password']
        type = request.form['type']

        if type == u'学生':
            sql = 'select * from student where id=? and password=? limit 1'
            cursor.execute(sql, (id, password))
            t = cursor.fetchall()
            if len(t) == 0:
                flash(u'用户名或密码错误')
                return render_template('login.html')
            else:
                flash(u'登陆成功')
                session['student'] = id
                return redirect(url_for('student'))
        if type == u'教师':
            sql = 'select * from teacher where id=? and password=? limit 1'
            cursor.execute(sql, (id, password))
            t = cursor.fetchall()
            if len(t) == 0:
                flash(u'用户名或密码错误')
                return render_template('login.html')
            else:
                flash(u'登陆成功')
                session['teacher'] = id
                return redirect(url_for('teacher'))
        if type == u'学院管理员':
            sql = 'select * from dep_manager where id=? and password=? limit 1'
            cursor.execute(sql, (id, password))
            t = cursor.fetchall()
            if len(t) == 0:
                flash(u'用户名或密码错误')
                return render_template('login.html')
            else:
                flash(u'登陆成功')
                session['dep_manager'] = id
                return redirect(url_for('dep_manager'))
        if type == u'系统管理员':
            sql = 'select * from system_manager where id =? and password=? limit 1'
            cursor.execute(sql, (id, password))
            t = cursor.fetchall()
            if len(t) == 0:
                flash(u'用户名或密码错误')
                return render_template('login.html')
            else:
                flash(u'登陆成功')
                session['system_manager'] = id
                return redirect(url_for('system_manager'))
    return render_template('login.html')


@app.route('/student')
def student():
    if not session.get('student'):
        flash(u'请先登录')
        return redirect(url_for('login'))

    # 查询已选课程
    # 选课
    # 查询个人信息
    return render_template('student.html')


@app.route('/select_course', methods=['GET', 'POST'])
def select_course():
    if not session.get('student'):
        flash(u'请先登录')
        return redirect(url_for('login'))
    if not hasattr(g, 'db'):
        g.db = connect_db()
        cursor = g.db.cursor()

    cursor.execute('select dep from student where id=?', (session['student'],))
    dep = cursor.fetchall()[0][0]
    cursor.execute('select * from course where dep=?', (dep,))
    courses = cursor.fetchall()

    if request.method == 'POST':
        try:
            course_ids = request.form.keys()
            for course_id in course_ids:
                sql = 'insert into student_course (sid,cid) values (?,?)'
                cursor.execute(sql, (session['student'], course_id))
                g.db.commit()
            flash(u'选课成功')
            return redirect(url_for('student'))
        except:
            flash(u'选课失败')
            return redirect(url_for('select_course'))

    return render_template('select_course.html', courses=courses)


@app.route('/selected_course')
def selected_course():
    if not session.get('student'):
        flash(u'请先登录')
        return redirect(url_for('login'))
    if not hasattr(g, 'db'):
        g.db = connect_db()
        cursor = g.db.cursor()

    try:
        cursor.execute(
            'select course.name from course,student_course where student_course.sid=? and student_course.cid=course.id',
            session['student'])
        course_name = cursor.fetchall()
    except:
        flash(u'查询失败')
        return redirect(url_for('student'))

    return render_template('selected_course.html', course_name=course_name)


@app.route('/student_info')
def student_info():
    if not session.get('student'):
        flash(u'请先登录')
        return redirect(url_for('login'))
    if not hasattr(g, 'db'):
        g.db = connect_db()
        cursor = g.db.cursor()

    try:
        cursor.execute('select name,dep from student where id=?', (session['student'],))
        info = cursor.fetchall()[0]
    except:
        flash(u'查询失败')
        return redirect(url_for('student'))

    return render_template('student_info.html', info=info)


@app.route('/teacher', methods=['GET', 'POST'])
def teacher():
    if not session.get('teacher'):
        flash(u'请先登录')
        return redirect(url_for('login'))
    if not hasattr(g, 'db'):
        g.db = connect_db()
        cursor = g.db.cursor()

    sql = 'select cid,name from teacher_course,course where tid=? and cid=id'
    cursor.execute(sql, (session['teacher'],))
    course_info = cursor.fetchall()

    if request.method == 'POST':
        course = request.form['course']
        return redirect(url_for('teacher_course', course_id=course))

    return render_template('teacher.html', courses=course_info)


@app.route('/teacher/<course_id>', methods=['GET', 'POST'])
def teacher_course(course_id):
    # 课程信息
    # 上课学生
    if not session.get('teacher'):
        flash(u'请先登录')
        return redirect(url_for('login'))
    if not hasattr(g, 'db'):
        g.db = connect_db()
        cursor = g.db.cursor()

    sql = 'select name,info from course where id=?'
    cursor.execute(sql, (course_id))
    course = cursor.fetchall()[0]
    course_name = course[0]
    course_info = course[1]

    if request.method == 'POST':
        course_info = request.form['course_info']
        sql = 'update course set info=? where id=?'
        try:
            cursor.execute(sql, (course_info, course_id))
            g.db.commit()
            flash(u'修改课程信息成功')
            return redirect(url_for('teacher_course', course_id=course_id))
        except:
            flash(u'修改课程信息失败')
            return redirect(url_for('teacher_course', course_id=course_id))

    return render_template('teacher_course.html', course_id=course_id, course_info=course_info, course_name=course_name)


@app.route('/teacher/<course_id>/students', methods=['GET', 'POST'])
def course_students(course_id):
    if not session.get('teacher'):
        flash(u'请先登录')
        return redirect(url_for('login'))
    if not hasattr(g, 'db'):
        g.db = connect_db()
        cursor = g.db.cursor()

    sql = 'select student.id,student.name,student_course.score from student,student_course where student_course.cid=? and student.id=student_course.sid'
    cursor.execute(sql, (course_id,))
    students = cursor.fetchall()

    if request.method == 'POST':
        student_id = request.form.keys()[0]
        print student_id
        score = request.form.values()[0]
        print course_id
        course_id = course_id

        sql = 'update student_course set score=? where sid=? and cid=?'
        try:
            cursor.execute(sql, (score, student_id, course_id))
            g.db.commit()
            flash(u'修改成功')
            return redirect(url_for('course_students', course_id=course_id))
        except:
            flash(u'修改失败')
            return redirect(url_for('course_students', course_id=course_id))

    return render_template('course_students.html', students=students, course_id=course_id)


@app.route('/teacher/<course_id>/enter_score', methods=['GET', 'POST'])
def enter_score(course_id):
    if not session.get('teacher'):
        flash(u'请先登录')
        return redirect(url_for('login'))
    if not hasattr(g, 'db'):
        g.db = connect_db()
        cursor = g.db.cursor()

    if request.method == 'POST':
        name = request.form['name']
        score = request.form['score']

        cursor.execute('select id from student where name=?', (name,))
        sid = cursor.fetchall()[0][0]
        print sid

        sql = 'insert into student_course values (?,?,?)'
        try:
            cursor.execute(sql, (sid, course_id, score))
            g.db.commit()
            flash(u'录入成绩成功')
            return redirect(url_for('teacher_course', course_id=course_id))
        except:
            flash(u'录入成绩失败')
            return render_template('enter_score.html', course_id=course_id)

    return render_template('enter_score.html', course_id=course_id)


@app.route('/system_manager', methods=['GET', 'POST'])
def system_manager():
    if not session.get('system_manager'):
        flash(u'请先登录')
        return redirect(url_for('login'))
    if not hasattr(g, 'db'):
        g.db = connect_db()
        cursor = g.db.cursor()

    if request.method == 'POST':
        sql = request.form['sql']
        try:
            cursor.execute(sql)
            g.db.commit()
            flash(u'执行成功')
        except:
            flash(u"查询失败")
            return render_template('system_manager.html')
        try:
            result = cursor.fetchall()
            return render_template('system_manager.html', result=result)
        except:
            flash(u'无可显示内容')
            return render_template('system_manager.html')
    return render_template('system_manager.html')


@app.route('/dep_manager')
def dep_manager():
    if not session.get('dep_manager'):
        flash(u'请先登录')
        return redirect(url_for('login'))
    return render_template('dep_manager.html')


@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    if not session.get('dep_manager'):
        flash(u'请先登录')
        return redirect(url_for('login'))
    if not hasattr(g, 'db'):
        g.db = connect_db()
        cursor = g.db.cursor()
    if request.method == 'POST':
        id = request.form['id']
        password = request.form['password']
        name = request.form['name']
        cursor.execute('select dep from dep_manager where id=?', (session['dep_manager']))
        dep = cursor.fetchall()[0][0]

        sql = 'insert into student values (?,?,?,?)'

        try:
            cursor.execute(sql, (id, password, name, dep))
            g.db.commit()
            flash(u'注册成功')
            return redirect(url_for('dep_manager'))
        except:
            flash(u'注册失败')
            return render_template('register_stydent.html')
    return render_template('register_student.html')


@app.route('/student_score')
def student_score():
    if not session.get('dep_manager'):
        flash(u'请先登录')
        return redirect(url_for('login'))
    if not hasattr(g, 'db'):
        g.db = connect_db()
        cursor = g.db.cursor()

    cursor.execute('select dep from dep_manager where id=?', (session['dep_manager']))
    dep = cursor.fetchall()[0][0]

    sql = 'select student.name,course.name,student_course.score from student,course,student_course where student.id=student_course.sid and course.id=student_course.cid and course.dep=?'
    cursor.execute(sql, (dep,))
    info = cursor.fetchall()

    return render_template('student_score.html', info=info)


@app.route('/logout')
def logout():
    if hasattr(session, 'student'):
        del session['student']
    if hasattr(session, 'teacher'):
        del session['teacher']
    if hasattr(session, 'system_manager'):
        del session['system_manager']
    if hasattr(session, 'dep_manager'):
        del session['dep_manager']

    return redirect(url_for('login'))
