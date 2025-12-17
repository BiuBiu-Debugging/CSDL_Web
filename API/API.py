from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os
import boto3
import bcrypt
import secrets
import string
import re
load_dotenv()
import mysql.connector as msc
app = Flask(__name__) 

app.secret_key = b'_5#y2L"F4Q8z\NT\xec]/HN'

app.config['MYSQL_HOST'] = os.getenv('DB_HOST')
app.config['MYSQL_USER'] = os.getenv('DB_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('DB_NAME')
app.config['MYSQL_PORT'] = int(os.getenv('DB_PORT', 3306))

mysql = MySQL(app)


def tach_chuoi_db_table(input_string):
    if not input_string or "-" not in input_string:
        return None, None
        
    parts = input_string.split('--.--', 1)
    
    db_name = parts[0]
    table_name = parts[1]
    return db_name, table_name

def user_connect( us_n, us_password, us_db):

    us_connection = msc.connect(
        host=os.getenv('DB_HOST'),
        user=us_n,
        passwd=us_password,
        database=us_db
    )
    return us_connection

def Create_code():
    alphabet = string.ascii_letters + string.digits  
    ma = ''.join(secrets.choice(alphabet) for i in range(20))
    return ma

def is_valid_db_name(name):
    return bool(re.match(r'^[a-zA-Z0-9_]{1,64}$', name)) and not name.startswith('mysql')

def is_valid_username(name):
    return bool(re.match(r'^[a-zA-Z0-9_]{1,32}$', name))

@app.route('/api/create-user', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')
        database_name = data.get('database_name') 
        db_user_password=Create_code()

        if not all([username, email, phone, password, database_name]):
            return jsonify({"success": False, "message": "Thiếu thông tin bắt buộc"}), 400

        if not is_valid_username(username):
            return jsonify({"success": False, "message": "Username chỉ chứa chữ, số, gạch dưới"}), 400
        if not is_valid_db_name(database_name):
            return jsonify({"success": False, "message": "Tên database không hợp lệ"}), 400

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cur = mysql.connection.cursor()
        cur.execute(f"USE users")
        cur.execute("SELECT user_id FROM user_database WHERE database_name = %s ", (database_name,))
        if cur.fetchone():
            cur.close()
            return jsonify({"success": False, "message": "database đã tồn tạn"}), 409
        
        cur.execute("SELECT user_id FROM users WHERE username = %s OR email = %s", (username, email))
        if cur.fetchone():
            cur.close()
            return jsonify({"success": False, "message": "Username hoặc email đã tồn tại"}), 409
        try:
            # cre_user="CREATE USER IF NOT EXISTS %s IDENTIFIED BY %s"
            # cur.execute(cre_user, (username,db_user_password))
            # cur.execute(f"CREATE DATABASE IF NOT EXISTS `{database_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            # cur.execute(f"GRANT ALL PRIVILEGES ON `{database_name}`.* TO `{username}`@'%'")
            # cur.execute("FLUSH PRIVILEGES")
            # cur.execute(f"use `{database_name}`")
            # cur.execute(f"CREATE TABLE employee ( employee_id INT AUTO_INCREMENT PRIMARY KEY, fname VARCHAR(50) NOT NULL, lname VARCHAR(50) NOT NULL, pri_skill VARCHAR(255) NOT NULL, location VARCHAR(100) NOT NULL, email VARCHAR(100) NOT NULL, phone_number VARCHAR(100) NOT NULL);")
            # cur.execute(f"REVOKE ALTER ON employee.* FROM `{username}`@'%'")
            # cur.execute(f"GRANT ALTER ON `{database_name}`.* TO `{username}`@'%'")
            # cur.execute(f"use users")
            # mysql.connection.commit()


            cur.execute("CREATE USER IF NOT EXISTS %s IDENTIFIED BY %s", (username, db_user_password))
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{database_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cur.execute(f"GRANT ALL PRIVILEGES ON `{database_name}`.* TO `{username}`@'%'")
            cur.execute("FLUSH PRIVILEGES")
            cur.execute(f"GRANT SELECT, INSERT, DELETE ON `employee`.* TO `{username}`@'%'")
            cur.execute("FLUSH PRIVILEGES")
            mysql.connection.commit()
        except Exception as db_error:
            cur.execute(f"DROP USER {username}@'%';")
            mysql.connection.rollback()
            return jsonify({"success": False, "message": f"Lỗi tạo DB/user MySQL: {str(db_error)}"}), 500
        try:
            cur.execute(f"USE users")
            cur.execute("""
            INSERT INTO users (username, email, phone, password, database_name, role,db_pass) 
            VALUES (%s, %s, %s, %s, %s, 'user',%s)
        """, (username, email, phone, hashed_password, database_name,db_user_password))
            mysql.connection.commit()
        except Exception as db_error:
            cur.execute(f"DROP USER {username}@'%';")
            return jsonify({"success": False, "message": f"Lỗi tạo DB/user MySQL: {str(db_error)}"}), 500


        cur.close()

        return jsonify({
            "success": True,
            "message": "Tạo user và database thành công!",
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Lỗi server",
            "error": str(e)
        }), 500
    



@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        sql="select password,user_id from users where email =%s;"
        cur = mysql.connection.cursor()
        print("sau")
        cur.execute(f"USE users")
        cur.execute(sql,(email,))
        result = cur.fetchone()
        if result is None:
            return jsonify({"success": False, "message": "Email không tồn tại"}), 404

        password_hash = result[0]
        user_id = result[1]
        stored_hash_bytes = password_hash.encode('utf-8')
        input_password_bytes = password.encode('utf-8') 
        if bcrypt.checkpw(input_password_bytes, stored_hash_bytes):
            code = Create_code()
            sql2="insert into token(user_id,token_code) values (%s,%s)"
            cur.execute(sql2,(user_id,code,))
            mysql.connection.commit()
            cur.close()
            return jsonify({
                "success": True,
                "token": code
            }), 200
        else:
            return jsonify({"success": False, "message": "Sai mật khẩu"}), 401
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "Lỗi server",
            "error": str(e)
        }), 500
 




@app.route('/api/executequery', methods=['POST'])
def executequery():
    try:
        data = request.get_json()
        sql = data.get('sql', '').strip()
        token=data.get('token')
        if not sql:
            return jsonify({"success": False, "error": "Truy vấn SQL không được để trống."}), 400
        
        try:
            sys_cursor = mysql.connection.cursor() 
            sys_cursor.execute(
                "SELECT u.username, u.database_name, u.db_pass FROM users u INNER JOIN token t on u.user_id=t.user_id WHERE token_code=%s",
                (token,) 
            )
            result = sys_cursor.fetchone()
            sys_cursor.close()

            if result is None:
                return jsonify({"success": False, "error": "Không tìm thấy thông tin người dùng trong hệ thống."}), 404

            user_db_username = result[0]
            user_db_name = result[1]
            user_db_password=result[2]
            us_connection=user_connect(user_db_username,user_db_password,user_db_name)      
            curr = us_connection.cursor()
            curr.execute(sql)
            sql_lower = sql.lower().strip()
            if sql_lower.startswith('select'):
                dt = curr.fetchall()
                message = f"Truy vấn SELECT thành công. Tìm thấy {len(dt)} hàng."
                curr.close()   
                return jsonify({
                    "success": True, 
                    "message": f"{message} \n\n {dt}", 
                    "data": data
                }), 200
            else: 
                us_connection.commit()
                rows_affected = curr.rowcount 
                message = f"Thực thi thành công. {rows_affected} hàng bị ảnh hưởng."
                curr.close()
                return jsonify({
                    "success": True, 
                    "message": message
                }), 200
        except Exception as e:
            return jsonify({"success": False, "error": f"Lỗi truy vấn hệ thống: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": f"Lỗi truy vấn hệ thống: {str(e)}"}), 501




def iscorect(TOKEN):
    sys_cursor = mysql.connection.cursor() 
    sys_cursor.execute(f"USE users")
    sys_cursor.execute("SELECT u.username, u.database_name, u.db_pass FROM users u INNER JOIN token t on u.user_id=t.user_id WHERE token_code=%s",(TOKEN,))
    result = sys_cursor.fetchone()
    sys_cursor.close()
    if result is None:
        return None
    user_db_username = result[0]
    user_db_name = result[1]
    user_db_password=result[2]
    us_connection=user_connect(user_db_username,user_db_password,user_db_name)      
    return us_connection

def Get_user_id(TOKEN):
    sys_cursor = mysql.connection.cursor() 
    sys_cursor.execute(f"USE users")
    sys_cursor.execute("SELECT user_id from token WHERE token_code=%s",(TOKEN,))
    result = sys_cursor.fetchone()
    sys_cursor.close()
    if result is None:
        return None
    return result[0]


def Get_user_name(token):
    sys_cursor = mysql.connection.cursor() 
    sys_cursor.execute(f"USE users")
    sys_cursor.execute("SELECT u.username FROM users u INNER JOIN token t on u.user_id=t.user_id WHERE token_code=%s",(token,))
    result = sys_cursor.fetchone()
    sys_cursor.close()
    if result is None:
        return None
    return result[0]



def get_database_name(Token):
    sys_cursor = mysql.connection.cursor() 
    sys_cursor.execute(f"USE users")
    sys_cursor.execute("SELECT u.database_name FROM users u INNER JOIN token t on u.user_id=t.user_id WHERE token_code=%s",(Token,))
    result = sys_cursor.fetchone()
    sys_cursor.close()
    if result is None:
        return None
    return result[0]

def get_database_name_by_name(name):
    sys_cursor = mysql.connection.cursor() 
    sys_cursor.execute(f"USE users")
    sys_cursor.execute("SELECT database_name FROM user_database WHERE database_name=%s",(name,))
    result = sys_cursor.fetchone()
    sys_cursor.close()
    if result is None:
        return None
    return result[0]





@app.route('/api/createtablequery', methods=['POST'])
def createtablequery():
    data = request.get_json()
    tablename=data.get('tablename')
    columnumber=int(data.get('countcolum'))
    token=data.get('token')
    colum=data.get('col_name_1')
    datatype=data.get('col_datatype_1')
    nn=data.get('NotNull_1')
    pk=data.get('PrimaryKey_1')
    ai=data.get('AutoIncrement_')
    user_database=data.get('db_name')

    us_connect=iscorect(token)
    if us_connect==None:
        return jsonify({"success": False, "error": "Người dùng không hợp lệ"}), 404
    db_list=Get_list_database(token)
    
    if not tablename or not colum:
        return jsonify({"success": False, "error": "Thiếu dữ liệu","db_list":db_list}), 400
    curr = us_connect.cursor()
    curr.execute(f"USE `{user_database}`")
    curr.execute(f"SHOW TABLES LIKE %s", (tablename,))
    rel = curr.fetchone()

    if rel: 
        return jsonify({
        "success": False,
        "error": "Bảng đã tồn tại rồi!"
        ,"db_list":db_list
    }), 400
    try:
        sql_alter = f"CREATE TABLE IF NOT EXISTS `{tablename}` ( `{colum}` {datatype}"
        if nn == 'on':
           sql_alter += " NOT NULL"
        if pk == 'on':
           sql_alter += " PRIMARY KEY"
        if ai == 'on':
            sql_alter += " AUTO_INCREMENT"
        sql_alter+=f');'
        curr.execute(f"USE `{user_database}`")
        curr.execute(sql_alter)
        us_connect.commit()
    except Exception as e:
        return jsonify({"success": False, "error": f"Lỗi truy vấn hệ thống: {str(e)}","db_list":db_list}), 500
    for i in range(2,columnumber+1,1):
        colum="col_name_"+str(i)
        datatype="col_datatype_"+str(i)
        nn="NotNull_"+str(i)
        pk="PrimaryKey_"+str(i)
        ai="AutoIncrement_"+str(i)
        colum=data.get(colum)
        datatype=data.get(datatype)
        nn=data.get(nn)
        pk=data.get(pk)
        ai=data.get(ai)
        if not colum or not datatype:
            continue
        sql_alter = f"ALTER TABLE `{tablename}` ADD COLUMN `{colum}` {datatype}"
        if nn == 'on':
           sql_alter += " NOT NULL"
        if pk == 'on':
           sql_alter += " PRIMARY KEY"
        if ai == 'on':
            sql_alter += " AUTO_INCREMENT"
    
        try:
            curr.execute(sql_alter)
        except Exception as e:
            curr.execute(f"DROP TABLE IF EXISTS `{tablename}`")
            us_connect.commit()
            return jsonify({
            "success": False, 
        "error": f"Lỗi truy vấn hệ thống: {str(e)}","db_list":db_list
    }), 500
    us_connect.commit()
    curr.close()
    db_list=Get_list_database(token)
    return jsonify({
                    "success": True, 
                    "error":f"tạo bảng thành công" ,"db_list":db_list
                }), 200




@app.route('/api/yourtablequery', methods=['POST'])
def yourtablequery():
    try:
        data = request.get_json()
        token = data.get('token')

        if not token:
            return jsonify({"success": False, "error": "Token là bắt buộc"}), 400

        us_connect = iscorect(token)
        if us_connect is None:
            return jsonify({"success": False, "error": "Token không hợp lệ hoặc đã hết hạn"}), 401

        db_name = get_database_name(token)
        if not db_name:
            us_connect.close()
            return jsonify({"success": False, "error": "Không tìm thấy database của người dùng"}), 404

        curr = us_connect.cursor()

        query = """
    SELECT TABLE_NAME 
    FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_SCHEMA = %s 
      AND TABLE_TYPE = 'BASE TABLE'
    ORDER BY TABLE_NAME
"""

        db_list = Get_list_database(token) or [] 

        tables = []

        for item in db_list:
            db_name = item[0] if isinstance(item, (tuple, list)) else item
            curr.execute(query, (db_name,))
            tem = curr.fetchall()
            formatted_list = [f"{db_name}--.--{row[0]}" for row in tem]
    
            tables.extend(formatted_list)

        curr.close()
        us_connect.close()

        table_list = tables

        return jsonify({
            "success": True,
            "error": "Lấy danh sách bảng thành công",
            "tables": table_list,
            "count": len(table_list)
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Lỗi hệ thống khi lấy danh sách bảng",
            "detail": str(e)
        }), 500
    





def Get_list_database(token):
    sql = """ 
    SELECT ub.database_name 
    FROM user_database AS ub 
    INNER JOIN token AS t ON ub.user_id = t.user_id 
    WHERE t.token_code = %s
    """
    
    cur = mysql.connection.cursor()
    try:
        cur.execute("USE users") 
        cur.execute(sql, (token,))
        result = cur.fetchall() 
        default_db = get_database_name(token)
        db_list = [default_db] if default_db else [] 
        if result:
            for item in result:
                db_name_fetched = item[0]
                if db_name_fetched not in db_list:
                    db_list.append(db_name_fetched)
        return db_list 
    except Exception as e:
        print(f"Error in Get_list_database: {e}")
        return None
    finally:
        cur.close()

@app.route('/api/yourdbquery', methods=['POST'])
def yourdbquery():
    try:
        data = request.get_json()
        token = data.get('token')

        if not token:
            return jsonify({"success": False, "error": "Token là bắt buộc"}), 400

        us_connect = iscorect(token)
        if us_connect is None:
            return jsonify({"success": False, "error": "Token không hợp lệ hoặc đã hết hạn"}), 401
        
        db_list = Get_list_database(token)
        return jsonify({
            "success": True,
            "message": "Lấy danh sách database thành công", 
            "databases": db_list, 
            "count": len(db_list)
        }), 200

    except Exception as e:
        print(f"[ERROR] yourdbquery: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Lỗi hệ thống",
            "detail": str(e)
        }), 500
    



@app.route('/api/createdbquery', methods=['POST'])
def createdbquery():
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({"success": False, "error": "Token là bắt buộc"}), 404

        us_connect = iscorect(token)
        if us_connect is None:
            return jsonify({"success": False, "error": "Token không hợp lệ hoặc đã hết hạn"}), 404
        db_name = data.get('db_name')
        if not re.match(r'^[a-zA-Z0-9_]+$', db_name):
            db_list = Get_list_database(token)
            return jsonify({"success": False, "error": "Tên database không hợp lệ","db_list":db_list}), 201
        
        if get_database_name_by_name(db_name):
            db_list = Get_list_database(token)
            return jsonify({"success": False, "error": f"{db_name} đã tồn tại","db_list":db_list}), 201
        sys_cursor = mysql.connection.cursor()
        user_id=Get_user_id(token)
        user_name=Get_user_name(token)
        try:
            sys_cursor.execute(f"CREATE DATABASE `{db_name}`")
        except Exception as e:
            db_list = Get_list_database(token)
            return jsonify({"success": False, "error": str(e),"db_list":db_list}), 201
        try:
            sys_cursor.execute(f"GRANT ALL PRIVILEGES ON `{db_name}`.* TO `{user_name}`@'%'")
            sys_cursor.execute("FLUSH PRIVILEGES")
        except Exception as e:
            sys_cursor.execute(f"drop database if exists {db_name}")
            db_list = Get_list_database(token)
            return jsonify({"success": False, "error": str(e),"db_list":db_list}), 201
        try:
            insert_sql="""INSERT INTO user_database (user_id, database_name)
    VALUES (%s, %s);"""
            sys_cursor.execute("use users")
            sys_cursor.execute(insert_sql,(user_id,db_name,))
            mysql.connection.commit()
            sys_cursor.close()
        except Exception as e:
            sys_cursor.execute(f"drop database if exists {db_name}")
            db_list = Get_list_database(token)
            return jsonify({"success": False, "error": str(e),"db_list":db_list}), 201
        
        db_list = Get_list_database(token)
        return jsonify({"success": True, "error": "Tạo Database thành công","db_list":db_list}), 200
    except Exception as e:
        print(f"[ERROR] yourdbquery: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500




@app.route('/api/deletedbquery', methods=['POST'])
def deletedbquery():
    try:
        data = request.get_json()
        token = data.get('token')
        database_name = data.get('database_name')
        if not token:
            return jsonify({"success": False, "error": "Thiếu token"}), 400
        if not database_name or not re.match(r'^[a-zA-Z0-9_]+$', database_name): 
            return jsonify({"success": False, "error": "Tên Database không hợp lệ"}), 400

        us_connect = iscorect(token)
        if us_connect is None:
            return jsonify({"success": False, "error": "Token không hợp lệ"}), 401
        
        user_id = Get_user_id(token) 
        
        sys_cursor = mysql.connection.cursor()
        
        try:
            sys_cursor.execute("USE users")
            check_sql = "SELECT 1 FROM user_database WHERE user_id = %s AND database_name = %s"
            sys_cursor.execute(check_sql, (user_id, database_name))
            if not sys_cursor.fetchone():
                sys_cursor.close()
                db_list= Get_list_database(token)
                return jsonify({"success": False, "error": "Bạn không có quyền xóa Database này hoặc DB không tồn tại"}), 200
            drop_sql = f"DROP DATABASE IF EXISTS `{database_name}`"
            sys_cursor.execute(drop_sql)
            
            delete_record_sql = "DELETE FROM user_database WHERE database_name = %s AND user_id = %s"
            sys_cursor.execute(delete_record_sql, (database_name, user_id))
            mysql.connection.commit() 
            sys_cursor.close()

        except Exception as e:
            mysql.connection.rollback()
            sys_cursor.close() 
            return jsonify({
                "success": False,
                "error": f"Lỗi SQL: {str(e)}",
                "db_list": [] 
            }), 200 
        db_list= Get_list_database(token)


        return jsonify({
            "success": True,
            "error": f"Đã xóa Database `{database_name}` thành công!",
            "db_list": db_list
        }), 200

    except Exception as e:
        print(f"[ERROR] deletedbquery: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500








@app.route('/api/deletetablequery', methods=['POST'])
def deletetablequery():
    try:
        data = request.get_json()
        token = data.get('token')
        table_name = data.get('choice')
        db_name,table_name=tach_chuoi_db_table(table_name)

        if not token or not table_name:
            return jsonify({"success": False, "error": "Thiếu token hoặc tên bảng"}), 400

        if not re.match(r'^[a-zA-Z0-9_]+$', table_name):  # chặn tên bảng nguy hiểm
            return jsonify({"success": False, "error": "Tên bảng không hợp lệ"}), 400

        us_connect = iscorect(token)
        if us_connect is None:
            return jsonify({"success": False, "error": "Token không hợp lệ"}), 401

        curr = us_connect.cursor()
        user_database=get_database_name(token)
        try:
            curr.execute(f"USE `{db_name}`")
            sql = f"DROP TABLE IF EXISTS `{table_name}`;"
            curr.execute(sql)
            us_connect.commit()
        except Exception as e:
            print(e)
        curr.close()
        us_connect.close()
        return jsonify({
            "success": True,
            "message": f"Đã xóa bảng `{table_name}` thành công!"
        }), 200

    except Exception as e:
        print(f"[ERROR] deletetablequery: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Lỗi khi xóa bảng",
            "detail": str(e)
        }), 500
    

@app.route('/')
def home():
    return "API đang chạy."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)