import re
from urllib.request import pathname2url
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import datetime
import os



app = Flask(__name__)
app.secret_key = "Secret Key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:3283624@localhost/flaskapi'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
sessions = []

class teamproject(db.Model):

    id = db.Column(db.Integer, primary_key = True)
    s_name = db.Column(db.String(50))
    sess = db.Column(db.String(50))
    p_title = db.Column(db.String(50))
    p_desc = db.Column(db.String())
    p_ptnr1 = db.Column(db.String(50))
    p_ptnr2 = db.Column(db.String(50))
    p_sup = db.Column(db.String(50))
    date = db.Column(default=datetime.datetime.utcnow)
    def __init__(self, s_name,sess, p_title,p_desc,p_ptnr1,p_ptnr2,p_sup):
 
        self.s_name = s_name
        self.sess = sess
        self.p_title = p_title
        self.p_desc = p_desc
        self.p_ptnr1 = p_ptnr1
        self.p_ptnr2 = p_ptnr2
        self.p_sup = p_sup
 
    

@app.route("/", methods=['GET'])
def index():
    from urllib.request import urlopen

    # import json
    import json
    # store the URL in url as
    # parameter for urlopen
    url = "https://cms.mlcs.xyz/api/view/program_sessions/all/"

    # store the response of URL
    response = urlopen(url)

    # storing the JSON response
    # from url in data
    data_json = json.loads(response.read())

    # print the json response
    cs_session = []
    for a in data_json:
        cs_session.append(a['Session_Title'])
    return render_template("index.html", cs_session=cs_session)

@app.route("/session", methods=['GET','POST'])
def student():
        if request.method == "POST":
            sess = request.form["program"]
            sessions.append(sess)
            from urllib.request import urlopen
            # import json
            import json
            # store the URL in url as
            # parameter for urlopen
            url = "https://cms.mlcs.xyz/api/view/students_of/" + sess +"/all/"

            # store the response of URL
            response = urlopen(url)

            # storing the JSON response
            # from url in data
            data_json = json.loads(response.read())
            # print the json response
            student_name = []
            for a in data_json:
                data = teamproject.query.filter_by(s_name = a['student_name'] +" "+a['student_roll_number']).first()
                if not data:
                    p_name1 = teamproject.query.filter_by(p_ptnr1 = a['student_name'] +" "+a['student_roll_number']).first()
                    if not p_name1:
                        p_name2 = teamproject.query.filter_by(p_ptnr2=a['student_name'] + " " + a['student_roll_number']).first()
                        if not p_name2:
                            student_name.append({"s_name":a['student_name'],"s_roll":a['student_roll_number']})

            return render_template("student.html", student_name=student_name)
        else:
            if sessions:
                sessions.pop(0)
            else:
                return redirect(url_for("index"))
@app.route("/FYP", methods = ['GET','POST'])
def FYP():
    if request.method == "POST":
        name = request.form["student"]
        print(name)
        from urllib.request import urlopen
        # import json
        import json
        # store the URL in url as
        # parameter for urlopen
        urlstd = "https://cms.mlcs.xyz/api/view/students_of/"+sessions[0]+"/all/"
        urlstf = "https://cms.mlcs.xyz/api/view/teaching_staff/all/"


        # store the response of URL
        responsestd = urlopen(urlstd)
        responsestf = urlopen(urlstf)

        # storing the JSON response
        # from url in data
        data_json1 = json.loads(responsestd.read())
        data_json2 = json.loads(responsestf.read())
        # print the json response
        student_name = []
        staff_name = []
        query = teamproject.query.all()
        for i in data_json1:
            comname = i['student_name'] +" "+i['student_roll_number'] 
            if comname != name:
                student_name.append({"s_name":i['student_name'],"s_roll":i['student_roll_number']})
        for s in data_json2:
            data = teamproject.query.filter_by(p_sup = s['teacher_name']).first()
            if not data:    
                staff_name.append(s['teacher_name'])

        return render_template("FYP.html", name=name, all_name = student_name, staff_name=staff_name)
    else:
        if sessions:
            sessions.pop(0)
        else:
            return redirect(url_for("index"))

@app.route("/submit", methods= ['GET','POST'])
def submit():
    if request.method == "POST":
        s_name = request.form['s_name']
        P_title= request.form['P_title']
        P_desc = request.form['P_desc']
        Ptnr1 = request.form['Ptnr1']
        Ptnr2 = request.form['Ptnr2']
        P_sup = request.form['P_sup']
        sess = sessions[0]
        my_data = teamproject(s_name,sess,P_title,P_desc,Ptnr1,Ptnr2,P_sup)
        db.session.add(my_data)
        db.session.commit()
        flash("data is succesfully uploaded")
        sessions.pop(0)
        return redirect(url_for("index"))
    else:
        if sessions:
            sessions.pop(0)
        else:
            return redirect(url_for("index"))

    
@app.route('/dashboard', methods= ['GET','POST'])
def dashboard():
    data = teamproject.query.all()
    count = 1
    countlist = []
    for i in data:
        countlist.append(count)
        count +=1
    return render_template('dashboard.html', data = data, count = countlist)

if __name__ == "__main__":
    app.run(debug=True)
