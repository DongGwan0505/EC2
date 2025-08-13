# request : client -> server
# response : server -> client

#Python Server
##1) flask : 마이크로 웹 프레임워크 (12000 line)
##2) Django : 모든 기능이 포함 (flask보다 10~12배 무거움)

#가상환경 변경하는 법 : 우측 하단 3.9.13 혹은 가상환경 이름을 클릭 또는 Ctrl + Shift + P-> 인터프리터 검색 -> 인터프리터 선택
from flask import Flask             #route 경로, run 서버 실행
from flask import render_template   #html load
from flask import request           #사용자가 보낸 정보
from flask import redirect          #페이지 이동
from flask import make_response     # 페이지 이동 시 정보 유지

#aws.py 안의 detect_labels_local_file 함수만 쓰고 싶다
from aws import detect_labels_local_file
from aws import compare_faces as cf

#파일 이름 보안처리 라이브러리
from werkzeug.utils import secure_filename

import os
#static 폴더가 없으면 만들기
if not os.path.exists("static"):
    os.mkdir("static")

app = Flask(__name__)
@app.route("/")
def index():
    #return render_template("exam01.html")
    #return "DG의 웹 페이지"
    return render_template("index.html")

@app.route("/compare", methods = ["POST"])
def compare_faces():
    #/detect를 통해 한 내용과 거의 동일, file을 2개 받을 뿐이다.
    #1.compare로 오는 file1, file2를 받아 static 폴더에 저장한다. (이때, secure_filename을 사용한다)
    if request.method == "POST":
        file1 = request.files["file1"]
        file2 = request.files["file2"]

        file1_filename = secure_filename(file1.filename)
        file2_filename = secure_filename(file2.filename)

        file1.save("static/" + file1_filename)
        file2.save("static/" + file2_filename)

    #2.aws.py 얼굴 비교 aws 코드, 이 결과를 통해 웹 페이지에 "동일 인물일 확률은 00.00%입니다." 띄우기
    #3.aws.py 안의 함수를 불러와 exam01.py 사용
        r = cf("static/" + file1_filename, "static/" + file2_filename)
    return r

@app.route("/detect", methods = ["POST"])
def detect_label():
    # flask에서 보안 규칙상
    # file 이름을 secure처리 해야 한다.
    if request.method == "POST":
        file = request.files["file"]

        file_name = secure_filename(file.filename)

        #이 파일을 static 폴더에 저장하고 해당 경로를 detect_labels_local_file 함수에 전달한다
        file.save("static/" + file_name)
        r = detect_labels_local_file("static/" + file_name)

    return r

@app.route("/secret", methods = ["POST"])
def box():
    try:
        if request.method == "POST":
            #get으로 오는 데이터는 args[key]로 받고, post로 오는 데이터는 form[key]로 받는다.
            hidden = request.form["hidden"]
            return f"비밀 정보 : {hidden}"
    except:
        return "데이터 전송 실패"

@app.route("/login", methods = ["GET"])
def login():
    if request.method == "GET":
        #페이지가 이동하더라도 정보를 남겨 사용 : 세션 이용
        #페이지 이동 방식은 redirect
        login_id = request.args["login_id"]
        login_pw = request.args["login_password"]
        if login_id == "ldg1234" and login_pw == "1234ldg":
            #로그인 성공
            response = make_response(redirect("/login/success")) 
            #response에 정보를 담을 수 있는 순간
            response.set_cookie("user", login_id)
            return response
        else:
            #로그인 실패
            return redirect("/")

@app.route("/login/success", methods = ["GET"])
def login_success():
    login_id = request.cookies.get("user")
    return f"{login_id}님 환영합니다"

if __name__ == "__main__":
    app.run(host="0.0.0.0")

    #flask server run
    #1) app.run() -> localhost(127.0.0.1) : 나만 들어올 수 있다
    #2) app.run("IPv4") -> IPv4 : 내 주소를 알면 들어올 수 있다
    #3) app.run("0.0.0.0") -> local, IPv4


