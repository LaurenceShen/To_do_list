#######################################
# 檔名: blog.py
# 功能: 主要功能實作
# TODO: 很多
#######################################

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort

from auth import login_required
from db import get_db
from functions import *

bp = Blueprint('blog', __name__)

def take_second(elem):
    return elem[1]
def take_third(elem):
    return elem[2]
def take_sixth(elem):
    return elem[5]
# 連接到index.html 關於主畫面顯示
@bp.route('/', methods=('POST', 'GET'))
@login_required
def index():
    db = get_db()

    # 取得所有該使用者的TODO事項，posts is a list of posts
    posts = db.execute(
        'SELECT p.id, title, due, body, done, created, p.labels, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE u.id = ?',
        (g.user['id'],)
    ).fetchall()
    labels = g.user['labels'] # 取得該使用者的標籤們
    #print(posts)
    # 若收到「過濾」的指令，存下要用哪些filter
    if request.method == 'POST' and 'filter' in request.form:
        session['filter'] = request.form.getlist('filter')
        print('filter')
    
    # 若收到「排序」的指令，存下要用哪種方式排序
    if request.method == 'POST' and 'sort_key' in request.form:
        session['sort_key'] = request.form['sort_key']
        print('sorted')
    fs = session.get('filter') # fs is a list of filters to be applied
    #Finished
    # TODO: 將posts用fs中的filter過濾
    ######################################
    ##                                  ##
    ##  ######   ####   #####    ####   ##
    ##    ##    ##  ##  ##  ##  ##  ##  ##
    ##    ##    ##  ##  ##  ##  ##  ##  ##
    ##    ##     ####   #####    ####   ##
    ##                                  ##
    ######################################
    #print (fs)
    label_list = []
    for f in fs:
        if f =='Finished':
            label_list.append(1)
        if f =='Not Finished':
            label_list.append(0)
        else:
            label_list.append(f)
    print(label_list)
    #if 'All' in label_list:
    #    return render_template('blog/index.html', posts=posts, filters=filters, labels=labels, sort_keys=sort_keys)
    post = []
    if 'All' not in label_list:
        for i in range(len(posts)):
            if posts[i][4] in label_list or posts[i][6] in label_list:
                post.append(posts[i])
    else:
        post = posts
    
    k = session.get('sort_key') # k is the sort key
    # TODO: 將posts用k排序
    ######################################
    ##                                  ##
    ##  ######   ####   #####    ####   ##
    ##    ##    ##  ##  ##  ##  ##  ##  ##
    ##    ##   ##  ##  ##  ##  ##  ##  ##
    ##    ##     ####   #####    ####   ##
    ##                                  ##
    ######################################
    if k == "Created Time":
        post = sorted(posts, key=take_sixth)
        print(posts[0][5])
    elif k == "Deadline":
        post = sorted(posts, key=take_third)
        print(posts[0][2])
    else:
        post = sorted(posts, key=take_second)
        print(posts[0][1])
    return render_template('blog/index.html', posts=post, filters=filters, labels=labels, sort_keys=sort_keys)

# 實作新增TODO事項的功能，連接到create.html
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        # 接收資料
        title = request.form['title']
        due = request.form['due']
        body = request.form['body']
        labels = " ".join(request.form.getlist('labels'))
        error = None

        # 判斷資料是否符合格式
        if not title:
            error = 'Title is required.'
        elif not is_date(due):
            error = 'Required format: YYYY/MM/DD'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            # 將資料新增到db
            db.execute(
                'INSERT INTO post (title, due, body, author_id, labels)'
                ' VALUES (?, ?, ?, ?, ?)',
                (title, due, body, g.user['id'], labels)
            )
            db.commit()
            return redirect(url_for('blog.index')) # 新增完成，回到主畫面

    return render_template('blog/create.html')

# 取得某一個TODO事項
def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, due, body, done, p.labels, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

# 更新TODO事項，連接到update.html，跟create有87分像
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)
    if request.method == 'POST':
        # TODO: 接收資料、檢查資料格式、修改db中的資料
        # HINT: 跟create有87分像
        ######################################
        ##                                  ##
        ##  ######   ####   #####    ####   ##
        ##    ##    ##  ##  ##  ##  ##  ##  ##
        ##    ##    ##  ##  ##  ##  ##  ##  ##
        ##    ##     ####   #####    ####   ##
        ##                                  ##
        ######################################
        title = request.form['title']
        due = request.form['due']
        body = request.form['body']
        labels = " ".join(request.form.getlist('labels'))
        error = None

        # 判斷資料是否符合格式
        if not title:
            error = 'Title is required.'
        elif not is_date(due):
            error = 'Required format: YYYY/MM/DD'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            # 將資料新增到db
            db.execute(
                'UPDATE post SET title = ?, due = ?, body = ?, author_id = ?, labels = ?'
                'WHERE title = ?',
                (title, due, body, g.user['id'], labels, title)
            )
            db.commit()
            return redirect(url_for('blog.index')) # 新增完成，回到主畫面

    return render_template('blog/update.html', post=post)

# 更改TODO事項的完成狀態
@bp.route('/<int:id>/done', methods=('POST',))
@login_required
def done(id):
    d = get_post(id)["done"]
    db = get_db()
    # 更新db中的資料（某事項從未完成改成完成，或反之）
    db.execute(
        'UPDATE post SET done = ?'
        ' WHERE id = ?',
        (1-d, id)
    )
    db.commit()
    return redirect(url_for('blog.index'))

# 刪除某TODO事項
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    # 刪除db中的那筆資料
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

#finish
# 編輯標籤，連接到labels.html
# TODO: 讓/labels這個網址對應到edit_labels這個函數，並且讓畫面顯示出labels.html的頁面
# REMARK: labels.html中會用到labels這個參數，所以記得要傳過去
# HINT: 參考上面其他的函式，應該只要寫兩行
######################################
##                                  ##
##  ######   ####   #####    ####   ##
##    ##    ##  ##  ##  ##  ##  ##  ##
##    ##    ##  ##  ##  ##  ##  ##  ##
##    ##     ####   #####    ####   ##
##                                  ##
######################################

@bp.route('/labels', methods=('POST','GET'))
@login_required
def edit_labels():
    labels = g.user['labels']

    if request.method == 'POST':
        new_labels = request.form.get('labels')
        db = get_db()
        posts = db.execute('SELECT p.id, p.labels FROM post p WHERE author_id = ?', (g.user['id'],))

        # 檢查是否有TODO事項用到被刪掉的label，如果有的話刪掉那個label，並更新db
        for post in posts:
            tmp = post['labels'].split()
            for label in tmp:
                if label not in new_labels:
                    tmp.remove(label)
            db.execute(
                'UPDATE post SET labels = ?'
                ' WHERE id = ?',
                (" ".join(tmp), post['id'])
            )

        db.execute(
            'UPDATE user SET labels = ?'
            ' WHERE id = ?',
            (new_labels, g.user['id'])
        )
        db.commit()
        return redirect(url_for('blog.index'))

    return render_template('blog/labels.html', labels = labels)

# Task0
######################################
##                                  ##
##  ######   ####   #####    ####   ##
##    ##    ##  ##  ##  ##  ##  ##  ##
##    ##    ##  ##  ##  ##  ##  ##  ##
##    ##     ####   #####    ####   ##
##                                  ##
######################################


@bp.route('/hello', methods=('POST','GET'))
@login_required
def hello():
    posts = get_db().execute(
        'SELECT p.id'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE u.id = ?',
        (g.user['id'],)
    ).fetchall()
    return render_template('hello.html', n = len(posts))

