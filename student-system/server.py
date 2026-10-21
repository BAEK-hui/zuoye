import json, sqlite3, secrets, hashlib, os
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).parent
DB = ROOT / 'students.db'
sessions = {}
def connect():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    return c
def password(value, salt):
    return hashlib.pbkdf2_hmac('sha256', value.encode(), salt.encode(), 200000).hex()
def init():
    for key in ('ADMIN_PASSWORD', 'STUDENT_PASSWORD'):
        if len(os.environ.get(key, '')) < 10:
            raise ValueError(key + ' must be set to a password of at least 10 characters')
    with connect() as c:
        c.executescript('''CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,username TEXT UNIQUE NOT NULL,password TEXT NOT NULL,salt TEXT NOT NULL,role TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS students(id INTEGER PRIMARY KEY,user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,number TEXT UNIQUE NOT NULL,name TEXT NOT NULL,major TEXT NOT NULL,class_name TEXT NOT NULL,phone TEXT DEFAULT '',email TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS courses(id INTEGER PRIMARY KEY,name TEXT UNIQUE NOT NULL,teacher TEXT NOT NULL,credits REAL NOT NULL CHECK(credits>0));
        CREATE TABLE IF NOT EXISTS grades(id INTEGER PRIMARY KEY,student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE,score REAL CHECK(score>=0 AND score<=100),UNIQUE(student_id,course_id));
        CREATE TABLE IF NOT EXISTS notices(id INTEGER PRIMARY KEY,title TEXT NOT NULL,content TEXT NOT NULL,created TEXT DEFAULT CURRENT_TIMESTAMP);''')
        if not c.execute('SELECT id FROM users').fetchone():
            for username, role in [('admin','admin'),('20260001','student')]:
                salt=secrets.token_hex(16)
                c.execute('INSERT INTO users(username,password,salt,role) VALUES(?,?,?,?)',(username,password(os.environ['ADMIN_PASSWORD'] if role=='admin' else os.environ['STUDENT_PASSWORD'],salt),salt,role))
            c.execute("INSERT INTO students(user_id,number,name,major,class_name) VALUES(2,'20260001','林同学','计算机科学与技术','计算机 2601')")
            c.execute("INSERT INTO courses(name,teacher,credits) VALUES('数据库原理','陈老师',3)")
            c.execute('INSERT INTO grades(student_id,course_id,score) VALUES(1,1,92)')
            c.execute("INSERT INTO notices(title,content) VALUES('欢迎使用学生信息管理系统','新学期已开启，请及时核对个人资料与课程成绩。')")
        # Versioned seed migration: applies once to existing and fresh databases.
        c.execute('CREATE TABLE IF NOT EXISTS migrations(version INTEGER PRIMARY KEY)')
        if not c.execute('SELECT 1 FROM migrations WHERE version=1').fetchone():
            examples = [('20260002','王晓晨','计算机科学与技术','计算机 2601',88),
                        ('20260003','李雨桐','软件工程','软件 2601',95),
                        ('20260004','张子涵','软件工程','软件 2601',81),
                        ('20260005','陈思远','信息管理与信息系统','信管 2601',90),
                        ('20260006','赵欣然','计算机科学与技术','计算机 2602',76),
                        ('20260007','刘一航','数据科学与大数据技术','数据 2601',93)]
            course = c.execute("SELECT id FROM courses WHERE name='数据库原理'").fetchone()
            for number,name,major,class_name,score in examples:
                if c.execute('SELECT 1 FROM users WHERE username=?',(number,)).fetchone():
                    continue
                salt=secrets.token_hex(16)
                uid=c.execute('INSERT INTO users(username,password,salt,role) VALUES(?,?,?,?)',(number,password(os.environ['STUDENT_PASSWORD'],salt),salt,'student')).lastrowid
                sid=c.execute('INSERT INTO students(user_id,number,name,major,class_name,email) VALUES(?,?,?,?,?,?)',(uid,number,name,major,class_name,number+'@example.com')).lastrowid
                if course:
                    c.execute('INSERT INTO grades(student_id,course_id,score) VALUES(?,?,?)',(sid,course['id'],score))
            c.execute('INSERT INTO migrations(version) VALUES(1)')

class Handler(BaseHTTPRequestHandler):
    def send(self,data,status=200):
        raw=json.dumps(data,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.end_headers();self.wfile.write(raw)
    def do_GET(self):
        if self.path=='/':
            raw=(ROOT/'index.html').read_bytes();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write(raw)
        else:self.api()
    def do_POST(self):self.api()
    def do_DELETE(self):self.api()
    def api(self):
        try:
            data=json.loads(self.rfile.read(int(self.headers.get('Content-Length',0))) or '{}')
            with connect() as c:
                if self.path=='/api/login' and self.command=='POST':
                    u=c.execute('SELECT * FROM users WHERE username=?',(data.get('username'),)).fetchone()
                    if not u or not secrets.compare_digest(u['password'],password(data.get('password',''),u['salt'])):return self.send({'error':'账号或密码错误'},401)
                    token=secrets.token_urlsafe(32);sessions[token]=dict(u);return self.send({'token':token,'role':u['role']})
                token=self.headers.get('Authorization','').removeprefix('Bearer ')
                u=sessions.get(token)
                if not u:return self.send({'error':'请先登录'},401)
                if self.path=='/api/logout':sessions.pop(token,None);return self.send({'ok':True})
                admin=u['role']=='admin'
                if self.path=='/api/data' and self.command=='GET':
                    students=[dict(r) for r in c.execute('SELECT * FROM students'+('' if admin else ' WHERE user_id=?'),() if admin else (u['id'],))]
                    grades=[dict(r) for r in c.execute('SELECT g.*,s.name student_name,s.number,c.name course_name FROM grades g JOIN students s ON s.id=g.student_id JOIN courses c ON c.id=g.course_id'+('' if admin else ' WHERE s.user_id=?'),() if admin else (u['id'],))]
                    return self.send({'role':u['role'],'students':students,'grades':grades,'courses':[dict(r) for r in c.execute('SELECT * FROM courses')],'notices':[dict(r) for r in c.execute('SELECT * FROM notices ORDER BY id DESC')]})
                if self.path=='/api/profile' and self.command=='POST':
                    c.execute('UPDATE students SET phone=?,email=? WHERE user_id=?',(data.get('phone',''),data.get('email',''),u['id']));return self.send({'ok':True})
                if not admin:return self.send({'error':'无权执行此操作'},403)
                entity=self.path.split('/')[-1]
                if entity not in ['students','courses','grades','notices']:return self.send({'error':'接口不存在'},404)
                if self.command=='DELETE':
                    if entity=='students':c.execute('DELETE FROM users WHERE id=(SELECT user_id FROM students WHERE id=?)',(data['id'],))
                    else:c.execute('DELETE FROM '+entity+' WHERE id=?',(data['id'],))
                elif self.command=='POST':
                    fields={'students':['number','name','major','class_name','phone','email'],'courses':['name','teacher','credits'],'grades':['student_id','course_id','score'],'notices':['title','content']}[entity]
                    values=[data.get(f,'') for f in fields]
                    if any(not str(data.get(f,'')).strip() for f in fields if f not in ['phone','email']):return self.send({'error':'请填写所有必填项'},400)
                    if data.get('id'):
                        c.execute('UPDATE '+entity+' SET '+','.join(f+'=?' for f in fields)+' WHERE id=?',values+[data['id']])
                    else:
                        if entity=='students':
                            salt=secrets.token_hex(16);cur=c.execute('INSERT INTO users(username,password,salt,role) VALUES(?,?,?,?)',(data['number'],password(os.environ['STUDENT_PASSWORD'],salt),salt,'student'));fields=['user_id']+fields;values=[cur.lastrowid]+values
                        c.execute('INSERT INTO '+entity+'('+','.join(fields)+') VALUES('+','.join('?' for _ in fields)+')',values)
                else:return self.send({'error':'方法不支持'},405)
            self.send({'ok':True})
        except (ValueError,KeyError,sqlite3.IntegrityError):self.send({'error':'数据不合法、编号重复或关联记录不存在'},400)
        except Exception as e:
            print(e);self.send({'error':'服务器处理失败'},500)

if __name__=='__main__':
    init();print('学生信息管理系统：http://127.0.0.1:8000');ThreadingHTTPServer(('127.0.0.1',8000),Handler).serve_forever()
