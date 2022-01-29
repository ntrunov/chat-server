from flask import Flask, request, render_template

app = Flask(__name__)
USERS_FILE = '/var/www/b/users.txt'


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        username = request.form.get('login')
        password = request.form.get('password')
        if user_exists(username):
            return render_template('failed.html')
        add_user(username, password)
        return render_template('success.html')


def add_user(username, password):
    with open('users.txt', 'a') as file:
        file.write(f'{username} {password}\n')


def user_exists(username):
    with open('users.txt') as file:
        for line in file:
            if username == line.split()[0]:
                return True
    return False

