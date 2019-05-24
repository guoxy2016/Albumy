# Albumy
图片分享网站
可以创建.env文件用于保存一些配置变量,可配置的变量有:
```.env
ALBUMY_ADMIN=
MAIL_SERVER=
MAIL_USERNAME=
MAIL_PASSWORD=
SECRET_KEY=
DATABASE_URI=
```

使用方法:
```
pip3 install pipenv
pipenv install --dev
pipenv shell
flask init
flask run
#或者运行
flask forge
flask run
```

