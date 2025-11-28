from flask import Flask,render_template,request,redirect,url_for,session
import mysql.connector
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

def db_connect(): #connect to mysql database using credentials from .env file
    return mysql.connector.connect(
        host="localhost",
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
#route for homepage that lists all quizes available
@app.route("/")
def index():
    db=db_connect()
    cursor=db.cursor(dictionary=True)
    cursor.execute("""
                   SELECT quizes.qid, quizes.title, quizes.time_created, users.username
                   FROM quizes
                   JOIN users ON quizes.user_id = users.uid
                   ORDER BY quizes.time_created DESC
    """)
    quizes=cursor.fetchall() #above query fetches all quizes along with their creators and orders them by creation time
    cursor.close()
    db.close()
    return render_template("index.html",quizes=quizes)

#this route allows user to register for the site
@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"] 
        hashed_password=generate_password_hash(password) #important that any passwords are hashed before storing in db

        db=db_connect()
        cursor=db.cursor()
        cursor.execute("INSERT INTO users (username,password_hash) VALUES (%s,%s)",(username,hashed_password)) #%s protects against sql injection via parameterized queries
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for("login"))
    return render_template("register.html")

#this route allows user to login 
@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]

        db=db_connect()
        cursor=db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s",(username,))
        user=cursor.fetchone()
        cursor.close()
        db.close()

        if user and check_password_hash(user["password_hash"],password):
            session["user_id"]=user["uid"]
            session["username"]=user["username"]
            return redirect(url_for("index"))
        else:
            return "Invalid credentials",401
    return render_template("login.html")

#simple route that allows user to logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

#this route allows user to create quiz
@app.route("/create_quiz",methods=["GET","POST"])
def create_quiz():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    if request.method=="POST":
        title=request.form.get("title")
        db=db_connect()
        cursor=db.cursor()
        cursor.execute("INSERT INTO quizes (title,user_id) VALUES (%s,%s)",(title,session["user_id"]))
        quiz_id=cursor.lastrowid
        
        for qnum in range(1,11):
            q_text=request.form.get(f"question_{qnum}")
            if not q_text or not q_text.strip():
                continue
            q_text=q_text.strip()
            cursor.execute("INSERT INTO questions (quiz_id,q_text) VALUES (%s,%s)",(quiz_id,q_text))
            question_id=cursor.lastrowid
            correct_choice = request.form.get(f"correct_choice_{qnum}")

            for cnum in range(1,5):
                c_text=request.form.get(f"question_{qnum}_choice_{cnum}")
                if not c_text or not c_text.strip():
                    continue
                c_text=c_text.strip()
                is_correct = 1 if str(cnum) == correct_choice else 0
                cursor.execute("INSERT INTO choices (question_id,c_text,correct_ans) VALUES (%s,%s,%s)",(question_id,c_text,is_correct))
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for("index"))
    return render_template("create_quiz.html")
# last app route used to take quiz
@app.route("/take_quiz/<int:quiz_id>",methods=["GET","POST"])
def take_quiz(quiz_id):
    db=db_connect()
    cursor=db.cursor(dictionary=True)
    cursor.execute("""
                   SELECT quizes.qid, quizes.title, users.username
                   FROM quizes
                   JOIN users ON quizes.user_id = users.uid
                   WHERE quizes.qid = %s
    """,(quiz_id,))
    quiz=cursor.fetchone()
    if not quiz:
        cursor.close()
        db.close()
        return "Quiz not found"
    cursor.execute("SELECT * FROM questions WHERE quiz_id=%s",(quiz_id,))
    questions=cursor.fetchall()

    # robustly find question primary key and load choices
    for q in questions:
        q_pk = q.get("lid") or q.get("question_id") or q.get("id")
        if not q_pk:
            q["choices"] = []
            q["_pk"] = None
            continue
        cursor.execute("SELECT * FROM choices WHERE question_id=%s",(q_pk,))
        q["choices"]=cursor.fetchall()
        q["_pk"] = q_pk

    score = None
    total_questions = len(questions)
    if request.method=="POST":
        amount_correct=0
        for q in questions:
            q_pk = q.get("_pk")
            if not q_pk:
                continue
            selected_choice_id=request.form.get(f"question_{q_pk}")
            if not selected_choice_id:
                continue
            for choice in q.get("choices",[]):
                choice_id = choice.get("cid") or choice.get("id")
                if str(choice_id) == selected_choice_id :
                    if choice.get("correct_ans"):
                        amount_correct+=1
                    break
        score=amount_correct
    cursor.close()
    db.close()
    return render_template(
        "take_quiz.html",
        quiz=quiz,
        questions=questions,
        score=score,
        total_questions=total_questions
    )

if __name__=="__main__":
    app.run(debug=True)
