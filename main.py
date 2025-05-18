from flask import Flask, render_template, request, url_for
import sqlite3
import os
import json

app = Flask(__name__)

name123 = ''
surname123 = ''


class Olymp:
    def __init__(self, olymp, page):
        self.page = page
        self.olymp = olymp
        self.tasks = []
        self.last_ans = []


class User:
    def __init__(self, name, surname):
        self.name = name
        self.surname = surname
        self.login = ''


ol = Olymp('0', 0)
u = User('', '')


@app.route('/')
def index():
    tmp = os.listdir('static/olymps')
    return render_template('main_page.html', name=":без входа", olymps=tmp, flag=True)


@app.route('/unlogined', methods=['POST'])
def unlogined():
    tmp = os.listdir('static/olymps')
    return render_template('main_page.html', name=":без входа", olymps=tmp, flag=True)


@app.route('/logined', methods=['POST'])
def logined():
    login = request.form.get('login')
    print(login)
    if login:
        u.login = login
    password = request.form.get('password')
    con = sqlite3.connect("databases/users.sqlite")
    cur = con.cursor()
    password2 = cur.execute(f"""SELECT password FROM users 
            WHERE login = '{u.login}'""").fetchall()
    name = cur.execute(f"""SELECT name FROM users 
                WHERE login = '{u.login}'""").fetchall()
    surname = cur.execute(f"""SELECT surname FROM users 
                WHERE login = '{u.login}'""").fetchall()
    grade = cur.execute(f"""SELECT grade FROM users 
                WHERE login = '{u.login}'""").fetchall()
    con.close()

    cor = sqlite3.connect("databases/olymps.sqlite")
    cut = cor.cursor()
    tmp = cut.execute(f"""SELECT olymps FROM olymps 
                WHERE min_grade <= {grade[0][0]} AND {grade[0][0]} <= max_grade""").fetchall()
    tmp = [i[0] for i in tmp]
    if password2[0][0] == password:
        # вход
        u.name = name[0][0]
        u.surname = surname[0][0]
        return render_template('main_page.html', name=f'{name[0][0]} {surname[0][0]}', olymps=tmp, flag=False)
    elif u.name and u.surname:
        # вход повторный
        return render_template('main_page.html', name=f'{u.name} {u.surname}', olymps=tmp, flag=False)
    else:
        # войти не получилось
        return render_template('failed_login_page.html')


@app.route('/login', methods=['POST'])
def login():
    u.name = ''
    u.surname = ''
    u.login = ''
    return render_template('login_page.html')


@app.route('/register')
def register():
    return render_template('register_page.html')


@app.route('/registered', methods=['POST'])
def registered():
    data = [request.form.get('name'), request.form.get('surname'), request.form.get('login'), request.form.get('grade'),
            request.form.get('password'), request.form.get('password2')]

    con = sqlite3.connect("databases/users.sqlite")
    cur = con.cursor()
    is_there_user = cur.execute(f"""SELECT * from users where login = '{data[2]}'""").fetchall()
    if is_there_user:
        # такой пользователь уже есть при регистрации
        return render_template('failed_register_page.html', alert="Пользователь с таким логином уже есть")
    if data[4] != data[5]:
        # пароли не совпадают при регистрации
        return render_template('failed_register_page.html', alert="Пароли не совпадают")
    cur.execute(f"""INSERT INTO users
                    VALUES ('{data[0]}', '{data[1]}', '{data[2]}', {data[3]}, '{data[4]}')""")
    con.commit()
    # регистрация прошла успешно
    return render_template('login_page.html')


@app.route('/olymp1', methods=['POST'])
def olymp_first_page():
    req = request.form.get("olymps")
    with open(f'static/olymps/{req}/tasks.json', 'r') as file:
        tasks = json.load(file)
    ol.olymp = req
    ol.page = 1
    ol.tasks = [0] * len(tasks)
    ol.last_ans = [0] * len(tasks)
    type1 = tasks[f"task{str(ol.page)}"]["type"]
    print(type1)
    print(len(tasks))

    if type1 == "test":
        # тип задания тест
        anses = tasks[f"task{str(ol.page)}"]["anses"]
        return render_template('test_task_page.html',
                               src=f'static/olymps/{ol.olymp}/{tasks[f"task{str(ol.page)}"]["image"]}', page=ol.page,
                               ans=anses, last_ans=ol.last_ans[ol.page - 1])
    elif type1 == "digit":
        # тип задания ввод числа
        return render_template('digit_task_page.html',
                               src=f'static/olymps/{ol.olymp}/{tasks[f"task{str(ol.page)}"]["image"]}', page=ol.page,
                               inp=ol.last_ans[ol.page - 1])
    elif type1 == "hand":
        # тип задания c ручной проверкой
        return render_template('input_task_page.html',
                               src=f'static/olymps/{ol.olymp}/{tasks[f"task{str(ol.page)}"]["image"]}', page=ol.page,
                               inp=ol.last_ans[ol.page - 1])
    else:
        # резервный вариант
        return render_template('task_page.html',
                               src=f'static/olymps/{ol.olymp}/{tasks[f"task{str(ol.page)}"]["image"]}', page=ol.page)


@app.route('/olymp', methods=['POST'])
def olymp_page():
    ol.page += 1
    with open(f'static/olymps/{ol.olymp}/tasks.json', 'r') as file:
        tasks = json.load(file)
    print(tasks, ol.olymp)
    if ol.page == len(tasks) + 1:
        # сохранение результата
        res = dict()
        res['user'] = u.login
        res['result'] = ol.tasks
        print(res)
        with open(f'results/result{u.login}.json', 'w') as jso:
            json.dump(res, jso)
        return render_template('last_olymp_page.html')
    type1 = tasks[f"task{str(ol.page)}"]["type"]
    print(type1)
    print(request.form)
    if type1 == "test":
        # тип задания тест
        anses = tasks[f"task{str(ol.page)}"]["anses"]
        return render_template('test_task_page.html',
                               src=f'static/olymps/{ol.olymp}/{tasks[f"task{str(ol.page)}"]["image"]}', page=ol.page,
                               ans=anses, last_ans=ol.last_ans[ol.page - 1])
    elif type1 == "digit":
        # тип задания ввод числа
        return render_template('digit_task_page.html',
                               src=f'static/olymps/{ol.olymp}/{tasks[f"task{str(ol.page)}"]["image"]}', page=ol.page,
                               inp=ol.last_ans[ol.page - 1])
    elif type1 == "hand":
        # тип задания c ручной проверкой
        return render_template('input_task_page.html',
                               src=f'static/olymps/{ol.olymp}/{tasks[f"task{str(ol.page)}"]["image"]}', page=ol.page,
                               inp=ol.last_ans[ol.page - 1])
    else:
        # резервный вариант
        return render_template('task_page.html',
                               src=f'static/olymps/{ol.olymp}/{tasks[f"task{str(ol.page)}"]["image"]}', page=ol.page)


@app.route('/olymbet', methods=['POST'])
def olymp_page_bet():
    ol.page -= 1
    with open(f'static/olymps/{ol.olymp}/tasks.json', 'r') as file:
        tasks = json.load(file)
    print(tasks, ol.olymp)
    if ol.page == len(tasks) + 1:
        return render_template('last_olymp_page.html')
    type1 = tasks[f"task{str(ol.page)}"]["type"]
    print(type1)
    print(request.form)
    if type1 == "test":
        # тип задания тест
        anses = tasks[f"task{str(ol.page)}"]["anses"]
        return render_template('test_task_page.html',
                               src=f'static/olymps/{ol.olymp}/{tasks[f"task{str(ol.page)}"]["image"]}', page=ol.page,
                               ans=anses, last_ans=ol.last_ans[ol.page - 1])
    elif type1 == "digit":
        # тип задания ввод числа
        return render_template('digit_task_page.html',
                               src=f'static/olymps/{ol.olymp}/{tasks[f"task{str(ol.page)}"]["image"]}', page=ol.page,
                               inp=ol.last_ans[ol.page - 1])
    elif type1 == "hand":
        # тип задания c ручной проверкой
        return render_template('input_task_page.html',
                               src=f'static/olymps/{ol.olymp}/{tasks[f"task{str(ol.page)}"]["image"]}', page=ol.page,
                               inp=ol.last_ans[ol.page - 1])
    else:
        # резервный вариант
        return render_template('task_page.html',
                               src=f'static/olymps/{ol.olymp}/{tasks[f"task{str(ol.page)}"]["image"]}', page=ol.page)


@app.route('/olbet', methods=['POST'])
def save_page():
    with open(f'static/olymps/{ol.olymp}/tasks.json', 'r') as file:
        tasks = json.load(file)
    q = request.form['options']
    if ol.page == len(tasks) + 1:
        return render_template('last_olymp_page.html')
    type1 = tasks[f"task{str(ol.page)}"]["type"]
    print(type1)
    print(request.form)
    if type1 in ('test', 'digit'):
        ol.tasks[ol.page - 1] = q == tasks[f"task{str(ol.page)}"]['right_ans']
    elif type1 == "hand":
        ol.tasks[ol.page - 1] = q
    if type1 == "test":
        # тип задания тест
        anses = tasks[f"task{str(ol.page)}"]["anses"]
        ol.last_ans[ol.page - 1] = tasks[f"task{str(ol.page)}"]["anses"].index(q)
        return render_template('test_task_page.html',
                               src=f'static/olymps/{ol.olymp}/{tasks[f"task{str(ol.page)}"]["image"]}', page=ol.page,
                               ans=anses, last_ans=ol.last_ans[ol.page - 1])
    elif type1 == "digit":
        # тип задания ввод числа
        ol.last_ans[ol.page - 1] = q
        return render_template('digit_task_page.html',
                               src=f'static/olymps/{ol.olymp}/{tasks[f"task{str(ol.page)}"]["image"]}', page=ol.page,
                               inp=ol.last_ans[ol.page - 1])
    elif type1 == "hand":
        # тип задания c ручной проверкой
        ol.last_ans[ol.page - 1] = q
        return render_template('input_task_page.html',
                               src=f'static/olymps/{ol.olymp}/{tasks[f"task{str(ol.page)}"]["image"]}', page=ol.page,
                               inp=ol.last_ans[ol.page - 1])
    else:
        # резервный вариант
        return render_template('task_page.html',
                               src=f'static/olymps/{ol.olymp}/{tasks[f"task{str(ol.page)}"]["image"]}', page=ol.page)


if __name__ == '__main__':
    app.run()
