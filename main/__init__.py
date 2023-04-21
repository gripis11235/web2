from flask import Flask
from flask import request
from flask import render_template
from flask_pymongo import PyMongo
from datetime import datetime
from datetime import timedelta
from bson.objectid import ObjectId
from flask import abort
from flask import redirect
from flask import url_for
from flask_paginate import Pagination
from flask import flash
from flask import session
from functools import wraps
from flask import jsonify
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)
csrf = CSRFProtect(app)

app.config["MONGO_URI"] = "mongodb://localhost:27017/myweb"

app.config["SECRET_KEY"] = "gripis"  # flash() 함수를 사용하기 위해서 설정해야 함. 플라스크에서 암호화 로직에 사용되므로 유출되면 안됨!
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=5)

app.config["MAX_CONTENT_LENGTH"] = 2*1024*1024

app.config["UPLOAD_FOLDER"] = "/files"

mongo = PyMongo(app)


from .common import login_required
from .filter import format_datetime
from . import board
from . import member
