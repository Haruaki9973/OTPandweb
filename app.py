from flask import Flask, render_template, request, redirect, url_for, session
import secrets
import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # セッションに必要な秘密鍵

otp_code = None
otp_expire = None

@app.route("/")
def home():
    return "<a href='/generate'>ワンタイムパスワードを発行</a>"

@app.route("/generate")
def generate():
    global otp_code, otp_expire
    otp_code = str(secrets.randbelow(1000000)).zfill(6)
    otp_expire = datetime.datetime.now() + datetime.timedelta(minutes=5)
    session.clear()
    session["otp"] = otp_code  # 一応セッションにも保持

    return render_template("otp_display.html", otp=otp_code)

@app.route("/otp")
def otp_input():
    return render_template("otp_input.html")

@app.route("/verify", methods=["POST"])
def verify():
    global otp_code, otp_expire
    user_code = request.form["otp"]
    now = datetime.datetime.now()

    if otp_code is None or now > otp_expire:
        result = "期限切れ、またはコードが存在しません。"
    elif user_code == otp_code:
        session["authenticated"] = True  # 認証フラグを保存
        return redirect(url_for("otp_result"))
    else:
        result = "認証失敗。コードが違います。"
        return render_template("otp_result.html", result=result)

@app.route("/otp_result")
def otp_result():
    if not session.get("authenticated"):
        return "このページにアクセスするには認証が必要です。", 403
    return render_template("otp_result.html", result="認証成功！")

if __name__ == "__main__":
    app.run(debug=True)
