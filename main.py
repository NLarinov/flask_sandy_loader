import flask
from selen import TestClass
from data import db_session
from data.users import User
from forms.user import RegisterForm
from flask_login import LoginManager
from flask_login import login_user
from forms.user import LoginForm


app = flask.Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'llkjbdsfghjgsadfgbuij8734q5843269'
LINK = None
FLAG = True


@app.route('/', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
def reqister():
    global LINK
    if flask.request.args.get('link'):
        LINK = flask.request.args.get('link')
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return flask.render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return flask.render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return flask.redirect('/login')
    return flask.render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    print(LINK)
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return flask.redirect('/main')
        return flask.render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return flask.render_template('login.html', title='Авторизация', form=form)


@app.route('/main', methods=['GET', 'POST'])
def index():
    global FLAG
    if LINK and FLAG:
        print('URA')
        SELEN.easy_download(LINK)
        FLAG = False

    with open('result.txt') as line:
        context = {'list': [(i[:i.find('link: ')] + i[i.find(' status:'):],
                             i[i.find('link: ') + 6:i.find(', status:')]) for i in line.readlines()]}

    return flask.render_template('index.html', **context)


if __name__ == '__main__':
    SELEN = TestClass()
    db_session.global_init("db/blogs.db")
    login_manager = LoginManager()
    login_manager.init_app(app)


    @login_manager.user_loader
    def load_user(user_id):
        db_sess = db_session.create_session()
        return db_sess.query(User).get(user_id)


    app.run(port=8080, host='127.0.0.1')
