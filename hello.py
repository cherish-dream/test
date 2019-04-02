from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import SubmitField,StringField,PasswordField
from wtforms.validators import DataRequired,EqualTo



# 创建flask的app对象


app = Flask(__name__)

# 注册蓝图
from admin import admin
app.register_blueprint(admin)

from config import Config
from flask_script import Manager#当前脚本添加脚本命令

app.config.from_object(Config)
manager = Manager(app)



#自定义表单类，文本字段、密码字段、提交按钮
class RegisterForm(FlaskForm):
    username = StringField("用户名：", validators=[DataRequired()])
    password = PasswordField("密码：", validators=[DataRequired()])
    password2 = PasswordField("确认密码：", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("注册")


@app.route('/',methods=['GET'])
def index():
    my_str = 'Hello World'
    my_int = 10
    my_array = [3, 4, 2, 1, 7, 9]
    my_dict = {
        'name': 'xiaoming',
        'age': 18
    }
    return render_template('index.html',
                           my_str=my_str,
                           my_int=my_int,
                           my_array=my_array,
                           my_dict=my_dict)

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':



        register_form = RegisterForm()
        if register_form.validate_on_submit():
            username = request.form.get('username')
            password = request.form.get('password')
            password2 = request.form.get('password2')
            print(username,password,password2)

            return '200 ok'




@app.route('/user/<user_id>',methods=['GET'])
def show(user_id):
    return 'this is user of %s'%user_id

if __name__ == '__main__':
    # app.run()
    manager.run()










