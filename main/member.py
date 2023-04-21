from main import *


from werkzeug.security import generate_password_hash, check_password_hash


@app.route("/join", methods=["GET", "POST"])
def member_join():
    if request.method == "POST":
        name = request.form.get("name", type=str)   # 타입을 꼭 명시할 필요는 없음
        email = request.form.get("email", type=str)
        pass1 = request.form.get("pass", type=str)  # pass는 예약어
        pass2 = request.form.get("pass2", type=str)

        if name == "" or email == "" or pass1 == "" or pass2 == "" :
            flash("입력되지 않은 값이 있습니다") #html에 메세지를 알려주고 싶음
            return render_template("join.html")
        if pass1 != pass2:
            flash("비밀번호가 일치하지 않습니다")
            return render_template("join.html")
        
        members = mongo.db.members
        mem = members.find_one({"email":email})
        if mem is not None :
            flash("중복된 이메일 주소입니다")
            return render_template("join.html")
        
        current_utc_time = round(datetime.utcnow().timestamp() * 1000)
        post = {
            "name":name,
            "email":email,
            "pass":generate_password_hash(pass1),
            "joindate":current_utc_time,
        }
        members.insert_one(post)

        return ""
    else:
        return render_template("join.html")


@app.route("/login", methods=["GET", "POST"])
def member_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("pass")

        members = mongo.db.members
        data = members.find_one({"email":email})

        next_url = request.form.get("next_url")


        if data is None:
            flash("회원 정보가 없습니다")
            return render_template("login.html")
        else:
            if check_password_hash(data.get("pass"), password):
            
                #data.get("pass") == password:
                session["email"] = email
                session["name"] = data.get("name")
                session["id"] = str(data.get("_id"))
                session.permanent = True 

                if next_url :
                    return redirect(next_url)
                else:
                    return redirect(url_for("lists"))
            else:
                flash("비밀번호가 일치하지 않습니다")
                return render_template("login.html")

        return ""
    else:
        next_url = request.args.get("next_url", type=str)
        if next_url != "":
            return render_template("login.html", next_url=next_url)
        else:
            return render_template("login.html")


@app.route("/logout")
def member_logout():
    try : 
        del session["name"]
        del session["id"]
        del session["email"]
    except :
        None
    return redirect(url_for('lists'))