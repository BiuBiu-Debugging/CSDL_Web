from flask import Flask, render_template, request, flash, redirect, url_for, session
import requests
from flask import session 
app = Flask(__name__)
app.secret_key = "abc123dd"  
api_host="http://192.168.1.86:8000"

@app.route("/")
def home():
    return render_template('SIGN_IN.html')



@app.route("/addemploy")
def addemploy():
    return render_template('addemploy.html')


@app.route("/SIGN_UP", methods=['GET', 'POST'])
def SIGN_UP():
    API_URL = API_URL = f"{api_host}/api/create-user"  
    if request.method == 'POST':
        print("Lấy Dữ Liệu")
        data = {
            "username": request.form['txt'],
            "email": request.form['email'],
            "phone": request.form['number_phone'],
            "password": request.form['pswd'],
            "database_name":request.form['db_name'],
        }

        response = requests.post(API_URL, json=data)

        if response.status_code == 201:
            flash("Đăng ký thành công từ API!", "success")
        else:
            flash("API báo lỗi khi đăng ký!", "danger")
    return render_template('SIGN_IN.html')





@app.route("/login", methods=['POST'])
def login():
    API_URL = f"{api_host}/api/login"
    if request.method == 'POST':
        data ={
            "email": request.form['email'],
            "password": request.form['pswd'],
        }
        
        try:
            response = requests.post(API_URL, json=data)
            if response.status_code == 200:
                try:   
                    result=response.json()
                    session['Token']=result.get('token')            
                    flash("Đăng nhập thành công!", "success")
                    return redirect(url_for('hom')) 
                except Exception as e:
                    flash("Lỗi xử lý JSON từ API.", "danger")
            
            else:
                flash(f"Đăng nhập thất bại. Mã lỗi API: {response.status_code}", "danger")
                
        except requests.exceptions.ConnectionError as e:
            print(f"Lỗi Kết nối: {e}")

    return render_template('SIGN_IN.html')       





@app.route('/hom') 
def hom():
    return render_template('home.html')


@app.route('/createtable') 
def createtable():
    return render_template('create_table.html')



@app.route('/query')
def query():
    return render_template('query.html')



@app.route('/getemploy')
def getemploy():
    return render_template('getemploy.html')



@app.route("/execute", methods=['POST'])
def execute():
    API_URL=f"{api_host}/api/executequery"
    if not session['Token']:
        return render_template('SIGN_IN.html')
    if request.method == 'POST':
        data = {
             "sql": request.form['wquery'],
             "token": session['Token'],
        }
        sqll=request.form['wquery']
        try:
            response = requests.post(API_URL, json=data) 
            if response.status_code == 404:
                return render_template('SIGN_IN.html')
            elif  response.status_code == 200:
                dtta = response.json()
                message = dtta.get('message')
            else:
                dtta = response.json()
                message = dtta.get('error')
        except requests.exceptions.ConnectionError as e:
            return render_template('query.html',result_output=message,wquery_content=(f"Lỗi hệ thông: {e}"))
    return render_template('query.html',result_output=message,wquery_content=sqll)





@app.route("/createdb", methods=['POST'])
def createdb():
    API_URL=f"{api_host}/api/createdbquery"
    if not session['Token']:
        return render_template('SIGN_IN.html')
    if request.method =='POST':
        data = {
             "db_name": request.form['db_name'],
             "token": session['Token'],
        }
        try:
            response = requests.post(API_URL, json=data) 
            if response.status_code == 200 or response.status_code == 201:
                dtta = response.json()
                message = dtta.get('error')
                tabledata = dtta.get('db_list')
                return render_template('Database.html',tables=tabledata, result_output=message)
            elif response.status_code == 500:
                dtta = response.json()
                message = dtta.get('error')
                return render_template('Database.html',result_output=message)
            else:
                return render_template('SIGN_IN.html')
        except requests.exceptions.ConnectionError as e:
            return render_template('SIGN_IN.html')
    return render_template('Database.html',result_output="Lỗi Đường dẫn truyền, hãy thử lại sau")
    



@app.route("/deletedb", methods=['POST'])
def deletedb():
    API_URL=f"{api_host}/api/deletedbquery"
    if not session['Token']:
        return render_template('SIGN_IN.html')
    if request.method =='POST':
        data = {
             "database_name": request.form['database_name'],
             "token": session['Token'],
        }
        try:
            response = requests.post(API_URL, json=data) 
            if response.status_code == 200 :
                dtta = response.json()
                message = dtta.get('error')
                tabledata = dtta.get('db_list') if dtta.get('db_list') else []
                return render_template('Database.html',tables=tabledata, result_output=message)
            else:
                return render_template('SIGN_IN.html')
        except requests.exceptions.ConnectionError as e:
            return render_template('SIGN_IN.html')
    return render_template('Database.html',result_output="Lỗi Đường dẫn truyền, hãy thử lại sau")




@app.route('/yourtable') 
def yourtable():
    API_URL=f"{api_host}/api/yourtablequery"
    if not session['Token']:
        return render_template('SIGN_IN.html')
    data = {
         "token": session['Token'],
    }
    try:
        response = requests.post(API_URL, json=data) 
        if response.status_code == 200:
            dtta = response.json()
            message = dtta.get('error')
            tabledata=dtta.get('tables')  
        else:
            return render_template('SIGN_IN.html')
    except requests.exceptions.ConnectionError as e:
        return render_template('SIGN_IN.html')
    return render_template('delete_table.html',tables=tabledata, result_output=message)



@app.route('/yourdb') 
def yourdb():
    API_URL=f"{api_host}/api/yourdbquery"
    if not session['Token']:
        return render_template('SIGN_IN.html')
    data = {
         "token": session['Token'],
    }
    try:
        response = requests.post(API_URL, json=data) 
        if response.status_code == 200:
            dtta = response.json()
            tabledata=dtta.get('databases') 
        else:
            return render_template('SIGN_IN.html')
    except requests.exceptions.ConnectionError as e:
        return render_template('SIGN_IN.html')
    return render_template('create_table.html',tables=tabledata)





@app.route('/yourdatabase') 
def yourdatabase(crea=0,message=" "):
    API_URL=f"{api_host}/api/yourdbquery"
    if not session['Token']:
        return render_template('SIGN_IN.html')
    data = {
         "token": session['Token'],
    }
    try:
        response = requests.post(API_URL, json=data) 
        if response.status_code == 200:
            dtta = response.json()
            tabledata=dtta.get('databases')  
        else:
            return render_template('SIGN_IN.html')
    except requests.exceptions.ConnectionError as e:
        return render_template('SIGN_IN.html')
    if crea==1:
        return render_template('Database.html',tables=tabledata, result_output=message)
    return render_template('Database.html',tables=tabledata)





@app.route('/update_employ_data', methods=['POST'])
def update_employ_data():
    API_URL = f"{api_host}/api/update_employ_dataquery"

    if not session['Token']:
        return render_template('SIGN_IN.html')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    pri_skill = request.form.get('pri_skill')
    location = request.form.get('location')
    email = request.form.get('email')
    phone_number = request.form.get('phone_number')
    emp_image_file = request.files.get('emp_image_file')
    if not all([first_name, last_name, pri_skill, location, email, phone_number, emp_image_file]):
        return "Vui lòng nhập đủ thông tin"
    files = {
        "emp_image_file": (emp_image_file.filename, emp_image_file.stream, emp_image_file.mimetype)
    }

    data = {
        "token": session['Token'],
        "first_name": first_name,
        "last_name": last_name,
        "pri_skill": pri_skill,
        "location": location,
        "email": email,
        "phone_number": phone_number
    }

    try:
        response = requests.post(API_URL, data=data, files=files)

        if response.status_code == 200 or  response.status_code==401:
            dtta = response.json()
            message = dtta.get('error')
        else:
            return render_template('SIGN_IN.html')

    except requests.exceptions.ConnectionError:
        return render_template('SIGN_IN.html')

    return render_template('addemploy.html', addlabel=message)




@app.route('/deletetable', methods=['POST'])
def deletetable():
    if not session['Token']:  
        return render_template('SIGN_IN.html')

    API_URL = f"{api_host}/api/deletetablequery"
    table_name = request.form['table_name']

    try:
        response = requests.post(API_URL, json={
            "token": session['Token'],
            "choice": table_name
        })
        result = response.json()
    except:
        result = {"success": False, "error": "Lỗi kết nối"}
    return yourtable()  


@app.route('/getinfbyPhone', methods=['POST'])
def getinfbyPhone():
    if not session['Token']:  
        return render_template('SIGN_IN.html')
    API_URL = f"{api_host}/api/getinfbyPhonequery"
    number_phone = request.form['phone_number']
    try:
        response = requests.post(API_URL, json={
            "token": session['Token'],
            "number_phone": number_phone
        })
        data = response.json()
        if response.status_code == 200:
            return render_template('getemployoutput.html',id=data.get('id'), fname=data.get('fname'), lname=data.get('lname'),
                                   interest=data.get('interest'), location=data.get('location'),
                                   email=data.get('email'), phone_number=data.get('phone_number'),
                                   image_url=data.get('image_url'))
        elif response.status_code == 300:
            return render_template('getemploy.html', lbelresult=data.get('error'))
    except:
        result = {"success": False, "error": "Lỗi kết nối"}

    return render_template('SIGN_IN.html')



@app.route('/create_table',methods=['POST']) 
def create_table():
    API_URL=f"{api_host}/api/createtablequery"
    if not session['Token']:
        return render_template('SIGN_IN.html')
    if request.method == 'POST':
        data={
            "db_name":request.form['db_name'],
            "token": session['Token'],
            "countcolum":request.form['countcolum'],
            "tablename": request.form['table_name'],
            "col_name_1": request.form['col_name_1'],
            "col_datatype_1": request.form['col_datatype_1'],
            "NotNull_1": request.form.get('NotNull_1'),
            "PrimaryKey_1":request.form.get('PrimaryKey_1'),
            "AutoIncrement_1":request.form.get('AutoIncrement_1'),
        }
        numb=int(request.form['countcolum'])
        for i in range (2,numb+1,1):
            colum="col_name_"+str(i)
            datatype="col_datatype_"+str(i)
            nn="NotNull_"+str(i)
            pk="PrimaryKey_"+str(i)
            ai="AutoIncrement_"+str(i)
            temp={
            colum: request.form[colum],
            datatype: request.form[datatype],
            nn: request.form.get(nn),
            pk:request.form.get(pk),
            ai:request.form.get(ai),
            }
            data.update(temp)
        try:
            response = requests.post(API_URL, json=data)
            if response.status_code == 404:
                return render_template('SIGN_IN.html') 
            else:
                dtta = response.json()
                message = dtta.get('error')
                tabledata=dtta.get('db_list')
                return render_template('create_table.html',result_output=message,tables=tabledata)  
        except requests.exceptions.ConnectionError as e:
            print(f"Lỗi Kết nối: {e}")
    return render_template('create_table.html',result_output="phương thức truyền đi bị lỗi, hãy thử lại sau")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)