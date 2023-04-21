from main import *
import os


from werkzeug.utils import secure_filename


from flask import send_file


@app.route("/")
def index():
    return "헬로!!"




@app.route("/list")
def lists():
    board = mongo.db.board

    per_page = 10
    page = request.args.get("page", default=1, type=int)
    
    search = request.args.get("search", type=int)
    keyword = request.args.get("keyword", type=str)

    query = {}
    
    #검색 조건을 저장할 리스트
    search_list = []

    if search == 0:
        search_list.append({"title":{"$regex":keyword}})  #문자열이 제목 안에 들어있으면 검색할 수 있도록 함
    elif search == 1:
        search_list.append({"contents":{"$regex":keyword}})
    elif search == 2:
        search_list.append({"title":{"$regex":keyword}})
        search_list.append({"contents":{"$regex":keyword}})
    elif search == 2:
        search_list.append({"name":{"$regex":keyword}})

    if len(search_list) > 0: #검색 조건이 있을 경우
        query = {"$or": search_list}


    datas = board.find(query).skip((page-1)*per_page).limit(per_page).sort("pubdate", -1) #검색에서 추가로 수정됨

    total = len(list(board.find(query))) #검색에서 추가로 수정됨

    return render_template("list.html",
                            datas=datas, 
                            pagination=Pagination(
                                page = page,
                                total = total,
                                per_page = per_page,
                                alignment = "center",
                            ), 
                            total = total,
                            page=page,
                                search = search,
                                keyword = keyword,
                                title="게시판 리스트",
    )



@app.route("/file/<filename>")
def board_file(filename):
    return send_file("..\\files\\"+filename, as_attachment=True)



@app.route("/write", methods=["GET", "POST"])
@login_required
def board_write():
    if request.method == "POST":
        if len(request.form.get("contents")) > 1.8*1024*1024 :
            flash('첨부파일의 용량이 초과되었습니다.')
            return render_template("write.html", title="글쓰기")

        fname = ""
        file = request.files["attachfile"]
        if file.filename != "" :
            fname = secure_filename(file.filename)
            file.save(".\\files\\"+secure_filename(file.filename))

        name = request.form.get("name")
        title = request.form.get("title")
        contents = request.form.get("contents")
        

        current_utc_time = round(datetime.utcnow().timestamp() * 1000)

        board = mongo.db.board
        post = {
            "name" : name,
            "title" : title,
            "contents" : contents,
            "pubdate": current_utc_time,
            "writer_id": session.get("id"),
            "view": 0,
            "attachfile": fname
        }
        x = board.insert_one(post)

        #return str(x.inserted_id)
        return redirect(url_for("board_view", idx=x.inserted_id))


    else:
        return render_template("write.html", title="글쓰기")

''' 기존 방식
@app.route("/view")
def board_view():
    idx = request.args.get("idx")
'''
@app.route("/view/<idx>")
def board_view(idx):
    if idx is not None:
        board = mongo.db.board

        #data = board.find_one({"_id":ObjectId(idx)})
        data = board.find_one_and_update({"_id":ObjectId(idx)}, {"$inc": {"view": 1}}, return_document=True)

        
        page = request.args.get("page", default=1, type=int)
        search = request.args.get("search", type=int)
        keyword = request.args.get("keyword", type=str)

        if data is not None:
            '''
            result = {
                "id": data.get("_id"),
                "name": data.get("name"),
                "title": data.get("title"),
                "contents": data.get("contents"),
                "pubdate": data.get("pubdate"),
                "view": data.get("view"),
                "writer_id": data.get("writer_id", "")
            }
            '''
            '''
            comment = mongo.db.comment
            comments = comment.find({"root_idx": str(data.get("_id"))})
            '''
            return render_template("view.html", result=data,  page=page, search=search, keyword=keyword)

    return abort(404)  #not found 정해진 오류 코드들이 있음!


@app.route("/edit/<idx>", methods=["GET", "POST"])
def board_edit(idx):
    if request.method == "GET":
        board = mongo.db.board
        data = board.find_one({"_id": ObjectId(idx)})
        if data is None:
            flash("해당 게시물이 존재하지 않습니다.")
            return redirect(url_for("lists"))
        else:
            if session.get("id") == data.get("writer_id") :
                return render_template("edit.html", data=data)
            else:
                flash("글 수정 권한이 없습니다")
                return redirect(url_for("lists"))
    else:
        title = request.form.get("title")
        contents = request.form.get("contents")

        board = mongo.db.board
        data = board.find_one({"_id": ObjectId(idx)})
        if session.get("id") == data.get("writer_id"):
            board.update_one({"_id": ObjectId(idx)}, {
                "$set":{
                    "title": title,
                    "contents": contents,
                }
            })
            flash("수정되었습니다.")
            return redirect(url_for("board_view", idx=idx))
        else:
            flash("글 수정 권한이 없습니다")
            return redirect(url_for("lists"))


@app.route("/delete/<idx>")
def board_delete(idx):
    board = mongo.db.board
    data = board.find_one({"_id":ObjectId(idx)})
    if session.get("id") == data.get("writer_id"):
        board.delete_one({"_id":ObjectId(idx)})
        flash("삭제되었습니다.")
        return redirect(url_for("lists"))

    else:
        flash("글 수정 권한이 없습니다")
        return redirect(url_for("lists"))




@app.route("/comment_write", methods=["POST"])
@login_required
def comment_write():
    if request.method == "POST":
        name = session.get("name")
        writer_id = session.get("id")
        root_idx = request.form.get("root_idx")
        comment = request.form.get("comment")
        current_utc_time = round(datetime.utcnow().timestamp()*1000)

        c_comment = mongo.db.comment

        post = {
            "root_idx": str(root_idx),
            "writer_id": writer_id,
            "name": name,
            "comment": comment,
            "pubdate": current_utc_time
        }

        c_comment.insert_one(post)
        return redirect(url_for("board_view", idx=root_idx))
    

@app.route("/comment_list/<root_idx>")
def comment_list(root_idx):
    comment = mongo.db.comment
    comments = comment.find({"root_idx":str(root_idx)}).sort("pubdate", -1)  # MongoDB에서 find()의 결과물은 커서이며, 지금까지는 이 커서로 html에서 데이터를 뿌려왔으나, ajax를 통한 통신으로 전달해 줄 수는 없음

    comment_list = []
    for c in comments:
        if c.get("writer_id") == session.get("id"):
            owner = True
        else:
            owner = False

        comment_list.append({
            "id": str(c.get("_id")),
            "root_idx": c.get("root_idx"),
            "name": c.get("name"),
            "writer_id": c.get("writer_id"),
            "comment": c.get("comment"),
            "pubdate": format_datetime(c.get("pubdate")),
            "owner" : owner,
        })
    return jsonify(error="success", lists=comment_list)


@app.route('/comment_edit', methods=["POST"])
def comment_edit():
    if request.method == "POST":
        idx = request.form.get("id")
        comment = request.form.get("comment")

        c_comment = mongo.db.comment
        data = c_comment.find_one({"_id": ObjectId(idx)})
        if data.get("writer_id") == session.get("id") : # 권한 추가 확인
            c_comment.update_one(
                {"_id":ObjectId(idx)},
                {"$set": {"comment": comment}},  # DB에서 comment 속성만 수정
            )
            return jsonify(error="success")
        else:
            return jsonify(error="error")
    else:
        return abort(401)


@app.route("/comment_delete", methods=["POST"])
@login_required
def comment_delete():
    if request.method == "POST":
        idx = request.form.get("id")  # Ajax 통신을 통해 받아온 값
        comment = mongo.db.comment
        data = comment.find_one({"_id": ObjectId(idx)})    # 권한은 한번 더 확인하더라도 모자라지 않음
        if data.get("writer_id") == session.get("id"):    # 접속 유저가 작성한 댓글인지 확인
            comment.delete_one({"_id": ObjectId(idx)})
            return jsonify(error="success")     # 댓글 삭제 성공 시,
        else:
            return jsonify(error="error")     # 댓글 삭제 실패 시,
    return abort(401)    # GET 메소드 등으로 접속했을 상황에서의 처리
