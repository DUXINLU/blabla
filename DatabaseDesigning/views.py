# -*- coding:utf-8 -*-
from flask import Flask, g, request, session, render_template, flash, url_for, redirect
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
    return render_template('home_page.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if not hasattr(g, 'db'):
        g.db = connect_db()
        cursor = g.db.cursor()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        type = request.form['type']
        if type == u'学生':
            sql = 'select * from s where id=? limit 1'
            cursor.execute(sql, (username,))
            if len(cursor.fetchall()) == 1:
                session['logged_in'] = True
                flash('登陆成功')
                return redirect(url_for('student', student_number=username))
            else:
                flash('登录失败')
                return render_template('login.html')
        if type == u'管理员':
            sql = 'select * from administrator where id=? and password=?'
            cursor.execute(sql, (username, password))
            if len(cursor.fetchall()) == 1:
                session['logged_in'] = True
                flash('登陆成功')
                return render_template('manager.html')
        if type == 'super_user':
            if username == 'duxinlu' and password == 'duxinlu':
                session['logged_in'] = True
                return render_template('super_user.html')

    return render_template('login.html')


@app.route('/super_user')
def super_user():
    if session.get('logged_in', False) != True:
        flash('请先登录')
        return render_template('home_page.html')
    if not hasattr(g, 'db'):
        g.db = connect_db()
        cursor = g.db.cursor()
    if request.method == 'POST':
        cursor.execute(request.form['sql'])

    return render_template('super_user.html')


# 管理员界面 录入学生信息  修改学生信息
@app.route('/manager')
def manager():
    if session.get('logged_in', False) == True:
        return render_template('manager.html')
    # 管理员页面 应该有  录入 及  修改学生状态
    else:
        flash('请先登录')
        return render_template('login.html')


# 录入学生信息
@app.route('/manager_entering', methods=['GET', 'POST'])
def manager_entering():
    if session.get('logged_in', False) != True:
        flash('请先登录')
        return render_template('home_page.html')
    if not hasattr(g, 'db'):
        g.db = connect_db()
        cursor = g.db.cursor()
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        note = request.form['note']
        suspend = request.form['suspend']
        register = request.form['register']

        sql = 'insert into s values (?,?,?,?,?)'
        cursor.execute(sql, (id, name, note, suspend, register))
        g.db.commit()
        flash('录入成功')
        return redirect(url_for('manager'))

    return render_template('manager_entering.html')


@app.route('/manager_modify', methods=['GET', 'POST'])
def manager_modify():
    if session.get('logged_in', False) != True:
        flash('请先登录')
        return render_template('home_page.html')
    if not hasattr(g, 'db'):
        g.db = connect_db()
        cursor = g.db.cursor()
    if request.method == 'POST':
        id = request.form['id']
        suspend = request.form['suspend']

        sql = 'update s set suspend=? where id=?;'
        try:
            cursor.execute(sql, (suspend, id))
            flash('修改成功')
            return redirect(url_for('manager'))
        except:
            flash('修改失败')
            return render_template('manager_modify.html')
    return render_template('manager_modify.html')


@app.route('/manager_query', methods=['GET', 'POST'])
def manager_query():
    if session.get('logged_in', False) != True:
        flash('请先登录')
        return render_template('home_page.html')
    if not hasattr(g, 'db'):
        g.db = connect_db()
        cursor = g.db.cursor()
    if request.method == 'POST':
        id = request.form['id']

        sql = 'select * from s where id=?'
        try:
            cursor.execute(sql, (id,))
            info = cursor.fetchall()[0]
            flash('查询成功')
            # 查询结果还木有显示
            return render_template('manager_query_result.html', info=info)
        except:
            flash('查询失败')
            return render_template('manager_query.html')
    return render_template('manager_query.html')


@app.route('/manager_entering_score', methods=['GET', 'POST'])
def manager_entering_score():
    if session.get('logged_in', False) != True:
        flash('请先登录')
        return render_template('home_page.html')
    if not hasattr(g, 'db'):
        g.db = connect_db()
        cursor = g.db.cursor()
    g.error_info = ''

    if request.method == 'POST':
        sid = request.form['sid']
        cid = request.form['cid']
        score = request.form['score']
        sql = 'select * from sc where sid=? and cid=? limit 1'
        cursor.execute(sql, (sid, cid))
        if len(cursor.fetchall()) == 0:
            g.error_info = u'学生未选择该门课程'
            return render_template('manager_entering_score.html', error=g.error_info)
        sql = 'insert into sc values (?,?,datetime("now"),?)'
        try:
            cursor.execute(sql, (sid, cid, score))
            g.db.commit()
            flash('学生成绩录入成功')
            return redirect(url_for('manager'))
        except:
            flash('学生成绩录入失败')
            return render_template('manager_entering_score.html')
    return render_template('manager_entering_score.html')


# 学生界面 选课 查询选课信息
@app.route('/student/<student_number>', methods=['GET', 'POST'])
def student(student_number):
    if session.get('logged_in', False) != True:
        flash('请先登录')
        return render_template('home_page.html')
    return render_template('student.html', student_number=student_number)


# 学生选课界面
@app.route('/student/<student_number>/select_course', methods=['GET', 'POST'])
def select_course(student_number):
    if session.get('logged_in', False) != True:
        flash('请先登录')
        return render_template('home_page.html')
    if not hasattr(g, 'db'):
        g.db = connect_db()
        cursor = g.db.cursor()

    g.error_info = ''

    cursor.execute('select * from c')
    courses = cursor.fetchall()
    if request.method == 'POST':
        judge_info = judge_select_course(student_number, request.form)
        if judge_info[0] == True:
            sql = 'insert into sc values (?,?,datetime("now"),0)'
            for i in judge_info[1]:
                cursor.execute(sql, (student_number, i))
                g.db.commit()
            return redirect(url_for('student', student_number=student_number))
        else:
            print judge_info[1]
            g.error_info = judge_info[1]
    return render_template('select_course.html', courses=courses, student_number=student_number, error=g.error_info)


# 得到选课结果
@app.route('/student/<student_number>/get_selected_course')
def get_selected_course(student_number):
    if session.get('logged_in', False) != True:
        flash('请先登录')
        return render_template('home_page.html')
    if not hasattr(g, 'db'):
        g.db = connect_db()
        cursor = g.db.cursor()

    sql = 'select c.name from s,sc,c where s.id=? and s.id=sc.sid and c.id=sc.cid'
    cursor.execute(sql, (student_number,))
    courses = cursor.fetchall()

    return render_template('get_selected_course.html', courses=courses, student_number=student_number)


# 删除选课
@app.route('/student/<student_number>/delete_course', methods=['GET', 'POST'])
def delete_course(student_number):
    if session.get('logged_in', False) != True:
        flash('请先登录')
        return render_template('home_page.html')
    if not hasattr(g, 'db'):
        g.db = connect_db()
        cursor = g.db.cursor()

    sql = 'select c.id,c.name from c,sc where sc.sid=? and sc.cid=c.id'
    cursor.execute(sql, (student_number,))
    courses = cursor.fetchall()
    if request.method == 'POST':
        key_list = request.form.keys()
        sql = 'delete from sc where sid=? and cid=?'
        for i in key_list:
            try:
                print i
                cursor.execute(sql, (student_number, i))
                g.db.commit()
                flash('注销课程成功')
                return redirect(url_for('student', student_number=student_number))
            except:
                flash('注销课程失败')
                return redirect(url_for('student', student_number=student_number))

    return render_template('delete_course.html', courses=courses, student_number=student_number)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if not hasattr(g, 'db'):
        g.db = connect_db()
        cursor = g.db.cursor()
    if request.method == 'POST':
        pass


@app.route('/logout')
def logout():
    del session['logged_in']
    flash('登出成功')
    return redirect(url_for('home_page'))


if __name__ == '__main__':
    pass
