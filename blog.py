from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.handlers.sha2_crypt import sha256_crypt
from functools import wraps



# Kullanıcı Kayıt Formu
class RegisterForm(Form):
    name =StringField("İsim Soyisim",validators=[validators.Length(min =4,max=25)])
    username =StringField("Kullanıcı Adı",validators=[validators.Length(min =5,max=35)])
    email =StringField("E-Mail Adresi",validators=[validators.Email(message="Lütfen Geçerlşi Bir E-Mail Alanı Giriniz !")])
    password=PasswordField("Parola",validators=[validators.equal_to(fieldname ="confirm",message="Parolalar Uyuşmuyor."),validators.DataRequired(message="Lütfen Alanı Boş Bırakmayınız.")])
    confirm =PasswordField("Parola Doğrula")


class LoginForm(Form):
    username =StringField("Kullanıcı Adı")
    password =PasswordField("Parola")


class ArticleForm(Form):
    baslik =StringField("Makale Başlığı",validators=[validators.Length(min =5)])
    icerik =TextAreaField("Makale İçeriği")



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        
        else :
            flash("Bu Sayfayı Görüntülemek İçin Giriş Yapın",category="danger")
            return redirect(url_for("login"))
    return decorated_function


app =Flask(__name__)
app.secret_key = "cangerek"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "ybblog"
app.config["MYSQL_CURSORCLASS"] ="DictCursor"


mysql =MySQL(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/articles")
def articles():

    cursor = mysql.connection.cursor()
    sorgu =cursor.execute("SELECT * FROM makaleler")
    if sorgu >0:
        makaleler =cursor.fetchall()
        return render_template("articles.html",makaleler =makaleler)

    else:
        return render_template("articles.html")

@app.route("/register",methods=["GET","POST"])
def register():
    form =RegisterForm(request.form)

    if request.method=="POST" and form.validate():
        name =form.name.data
        username =form.username.data
        email = form.email.data
        password =(form.password.data)

        cursor =mysql.connection.cursor()
        
        cursor.execute("SELECT username FROM users")
        UsernamesInDb =cursor.fetchall()
        print(UsernamesInDb)
        liste =[]
        for usernames in UsernamesInDb:
            eklenecek =usernames["username"]
            print(usernames["username"])
            liste.append(eklenecek)

        print(liste)
        if username in liste:
            flash(message="Kullanıcı Adı Kullanılmaktadır...",category="danger")
            return redirect(url_for("register"))
        
        else:
           sorgu ="INSERT INTO users(name,email,username,password)VALUES(%s,%s,%s,%s)"
        
           cursor.execute(sorgu,(name,email,username,password))
           mysql.connection.commit()

           cursor.close()

           flash(message="Başarıyla Kayıt Oldunuz..",category="success")
           return redirect(url_for("login"))




    else:
        return render_template("register.html",form=form)


@app.route("/articles/<string:id>")
def articlePage(id):
    cursor =mysql.connection.cursor()
    cursor.execute("SELECT * FROM makaleler WHERE id='"+id+"'")
    makale = cursor.fetchone()
    
    return render_template("articlePage.html",makale = makale)


@app.route("/controlPanel",methods=["POST","GET"])
def controlPanel():

    if request.method =="POST":
        return redirect(url_for("addarticle"))

    else:
        return render_template("controlPanel.html")    





@app.route("/logout")
def logout():
    session.clear()
    flash(message="Oturum Başarıyla Kapatıldı",category="success")
    return redirect(url_for("index"))


@app.route("/addarticle",methods =["GET","POST"])
@login_required
def addarticle():
    form =ArticleForm(request.form)
    
    if request.method =="POST" and form.validate():
        baslik =form.baslik.data
        icerik = form.icerik.data
        
        cursor =mysql.connection.cursor()
        cursor.execute("INSERT INTO makaleler(baslik,icerik,yazar)VALUES('"+baslik+"','"+icerik+"','"+session["username"]+"')")
        mysql.connection.commit()
        cursor.close()

        flash(message="Makale Başarıyla Kaydedildi.",category="success")
        return redirect(url_for("index"))


    else:
        return render_template("addarticle.html",form =form)


@app.route("/myArticles")
@login_required
def myArticles():
    cursor =mysql.connection.cursor()
    sorgu =cursor.execute("SELECT * FROM makaleler WHERE yazar ='"+session["username"]+"'")
    if sorgu >0 :
        makalelerim =cursor.fetchall()
        return render_template("myArticles.html",makalelerim =makalelerim)
    else:
        return render_template("myArticles.html")


@app.route("/login",methods =["GET","POST"])
def login():
    form =LoginForm(request.form)
    
    if request.method == "POST":
        username =form.username.data
        password_entered =form.password.data

        cursor =mysql.connection.cursor()

        sorgu ="SELECT * FROM users WHERE username = %s"

        result = cursor.execute(sorgu,(username,))
        
        if result > 0:

            data =dict(cursor.fetchone())
            isim =data["name"]
            if password_entered == data["password"]:
                flash(message="Hoş Geldin "+isim,category="success")

                session["logged_in"] = True
                session["username"] =username

                return redirect(url_for("index"))
            


        else:
            flash(message="Kullanıcı Adı Veya Parola Hatalı...",category="danger")
            return redirect(url_for("login"))

    else:
        return render_template("login.html",form =form)
        print("can")
    

if __name__ =="__main__":
    app.run(debug=True)

