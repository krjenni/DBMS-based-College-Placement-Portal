#import urllib.request as request
from flask import Flask,render_template,request,session,redirect,url_for
from flask_mysqldb import MySQL
import yaml

app = Flask(__name__)
app.secret_key = "super secret key"
db = yaml.safe_load(open('db.yaml'))

app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)

@app.route('/')
def hello_world():
    return render_template('index.html')
@app.route("/home")
def home():
    return render_template('lecturer_post.html',username = session['username'])

@app.route('/st')
def student():
    return render_template('student.html')

@app.route('/sr')
def student_reg():
    return render_template('student_reg.html')



@app.route('/pj')
def post_job():
    return render_template('post_job.html')

@app.route('/l')
def lecturerin():
    return render_template('lecturer.html')

@app.route('/s_jap')
def s_jap():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM job")
    details1 = cur.fetchall()
    #cur.execute("SELECT * FROM eligibility")
    #details2 = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    
    return render_template('apply.html',details1 = details1,username = session['username'])

@app.route('/st_dash')
def st_dash():
    return render_template('student_dash.html',username = session['username'])

@app.route('/delajob')
def delajob():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM job JOIN eligibility WHERE job.jid = eligibility.jid")
    details1 = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return render_template('delete_job.html',username = session['username'],details1 = details1)

@app.route('/del',methods = ['POST'])
def dela():
    details = request.form
    jid = details['jid']
    cur = mysql.connection.cursor()
    cur.execute("SELECT delete_jobs(%s)",[jid])
    msg  = 'Job deleted!'
    mysql.connection.commit()
    cur.close()
    return render_template('delete_job.html',username = session['username'],msg = msg)



@app.route('/vaj')
def vaj():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM applied_jobs")
    details1 = cur.fetchall()
    
    return render_template('view_applied.html',username = session['username'],details1=details1)

@app.route('/j_ap',methods = ['POST'])
def j_ap():
    msg = ''
    details = request.form
    SRN = details['SRN']
    jid = details['jid']
    cur = mysql.connection.cursor()
    cur2 = mysql.connection.cursor()
    cur.execute("SELECT * FROM applied_jobs WHERE SRN = %s AND jid = %s",(SRN,jid))
    record = cur.fetchone()
    if record:
        msg = 'Already Applied!'
        
    else:
        cur2.execute("INSERT INTO applied_jobs(SRN,jid) VALUES(%s,%s)",(SRN,jid))
        mysql.connection.commit()
        msg = 'Applied Successfully'
    return render_template('apply.html',msg = msg)


@app.route('/s_p_u',methods = ['POST'])
def s_p_u():
    msg = ''
    details = request.form
    SRN = details['SRN']
    dno = details['dno']
    fname = details['fname']
    lname = details['lname']
    email = details['email']
    phone= details['phone']
    cgpa = details['cgpa']
    marks_10 = details['marks_10']
    marks_12 = details['marks_12']
    backlog = details['backlog']
    work_exp = details['work_exp']
    project= details['project']  
    cur = mysql.connection.cursor()
    cur2 = mysql.connection.cursor()
    cur3 = mysql.connection.cursor()
    cur.execute("SELECT * FROM student_resume WHERE SRN = %s",[SRN])
    record = cur.fetchone()
    if record:
        msg = 'Profile updated successfully' 
        cur2.execute("UPDATE student_resume SET email = %s,fname = %s,lname=%s,cgpa=%s,work_exp=%s,projects=%s,phone=%s,backlog=%s,marks_10=%s,marks_12=%s WHERE SRN = %s",(email,fname,lname,cgpa,work_exp,project,phone,backlog,marks_10,marks_12,SRN))
        cur3.execute("UPDATE student SET fname = %s,lname=%s,email=%s,phone=%s,did=%s WHERE SRN = %s",(fname,lname,email,phone,dno,SRN))

    else:
        msg = 'Profile created successfully'
        cur2.execute("INSERT INTO student_resume(email,fname,lname,cgpa,work_exp,projects,phone,backlog,SRN,marks_10,marks_12) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(email,fname,lname,cgpa,work_exp,project,phone,backlog,SRN,marks_10,marks_12))
        cur3.execute("UPDATE student SET fname = %s,lname=%s,email=%s,phone=%s,did=%s WHERE SRN = %s",(fname,lname,email,phone,dno,SRN))
    mysql.connection.commit()
    return render_template('student_dash.html',msg = msg)
        
         


@app.route('/sr_s',methods = ['POST'])
def student_reg_s():
    msg = "Registration Successfull"
    details = request.form
    SRN = details['SRN']
    dno = details['dno']
    fname = details['fname']
    lname = details['lname']
    email = details['email']
    phone= details['phone']
    password1 = details['password1']
    
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO student(did,email,fname,lname,password1,phone,SRN) VALUES(%s,%s,%s,%s,%s,%s,%s)",(dno,email,fname,lname,password1,phone,SRN))
    mysql.connection.commit()
    cur.close()
    return render_template('student.html',msg = msg)

@app.route('/st_suc',methods = ['POST'])
def student_reg_suc():
    details = request.form
       # details = request.wrapper.form-container.form-inner.form
    SRN = details['SRN']
    password1 = details['password']
    msg = ''
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM student WHERE SRN = %s AND password1 = %s",(SRN,password1))
    record = cur.fetchone()
    if record:
        session['loggedin'] = True
        session['username'] = record[0]
        cur.close()
        return redirect(url_for('st_dash'))
    else:
        msg = 'Incorrect username/password.Try again!'
        
    return render_template('student.html',msg = msg)
    
@app.route('/lsignf',methods = ['POST'])
def lecturersignf():
        details = request.form
       # details = request.wrapper.form-container.form-inner.form
        fid = details['id']
        password1 = details['password']
        msg = ''
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM faculty WHERE fid = %s AND password = %s",(fid,password1))
        record = cur.fetchone()
        if record:
            session['loggedin'] = True
            session['username'] = record[1]
            cur.close()
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password.Try again!'
            
        return render_template('lecturer.html',msg = msg)
       
        
@app.route('/logout')
def logout():
    session.pop('loggedin',None)
    session.pop('username',None)
    return render_template('lecturer.html')      

@app.route('/lr1')
def lecturerreg1():
    return render_template('lecturer_reg.html')

@app.route('/j')
def viewjobs():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM job JOIN eligibility WHERE job.jid = eligibility.jid")
    details1 = cur.fetchall()
    details2 = cur.execute("SELECT COUNT(SRN) FROM applied_jobs GROUP BY jid")
    details2 = cur.fetchall()

    cur.execute("CALL count_jobs(@M)")
    cur.execute("SELECT @M")
    details3 = cur.fetchall()
    cur.execute("SELECT MAX(ctc) FROM job")
    details4 = cur.fetchall()
    cur.execute("SELECT MIN(cgpa) FROM eligibility")
    details5 = cur.fetchall()
    cur.execute("SELECT AVG(cgpa) FROM eligibility")
    details6 = cur.fetchall()

    mysql.connection.commit()
    cur.close()
    
    return render_template('jobs.html',details1 = details1,details2 = details2,details3 = details3,details4 = details4,details5 = details5,details6 = details6)

@app.route('/c_p')
def chage_profile():
    return render_template("student_profile.html")

@app.route('/lr',methods = ['POST'])
def lecturer(): 
    
        details = request.form
        fid = details['id']
        did = details['dno']
        fname = details['fname']
        lname = details['lname']
        password1 = details['password1']
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO faculty(did,fid,fname,lname,password) VALUES(%s,%s,%s,%s,%s)",(did,fid,fname,lname,password1))
        mysql.connection.commit()
        cur.close()
    
        
        return render_template('lecturer.html')
    
@app.route('/jobposted',methods = ['POST'])
def lecturer_job(): 
        details = request.form
        cname = details['cname']
        add = details['add']
        cid = details['cid']
        jname = details['jname']
        jid = details['jid']
        jdes = details['jdes']
        vacancy = details['vacancy']
        ctc = details['ctc']
        cgpa = details['cgpa']
        grade_10 = details['10thgrade']
        grade_12 = details['12thgrade']
        backlogs = details['backlogs']
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO job(cid,ctc,description,jid,title,vacancy) VALUES(%s,%s,%s,%s,%s,%s)",(cid,ctc,jdes,jid,jname,vacancy))
        cur.execute("INSERT INTO eligibility(backlogs,cgpa,jid,marks_10,marks_12) VALUES(%s,%s,%s,%s,%s)",(backlogs,cgpa,jid,grade_10,grade_12))

        mysql.connection.commit()
        cur.close()
    
        
        return render_template('job_post_succ.html')

@app.route('/j')
def jobs():
    return render_template('jobs.html')
if __name__ == "__main__":
    app.run(debug=True)
