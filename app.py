
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session

from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from database.db import db, get_all_collection, storage
from firebase_admin import firestore
from functools import wraps

# ===============================================

# Starter Template Flask
# By Makassar Coding

# ================================================
# Menentukan Nama Folder Penyimpanan Asset
app = Flask(__name__, static_folder='static', static_url_path='')
# Untuk Menggunakan flash pada flask
app.secret_key = 'iNiAdalahsecrEtKey'
# Untuk Mentukan Batas Waktu Session
app.permanent_session_lifetime = datetime.timedelta(days=7)
# Menentukan Jumlah Maksimal Upload File
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' in session:
            return f(*args, **kwargs)
        else:
            flash('Anda harus login', 'danger')
            return redirect(url_for('halaman_login'))
    return wrapper


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/mahasiswa')
@login_required
def mahasiswa():
    
    daftar_mahasiswa = get_all_collection('mahasiswa')

    
    return render_template('mahasiswa/mahasiswa.html', daftar_mahasiswa=daftar_mahasiswa)


@app.route('/mahasiswa/tambah', methods=['GET', 'POST'])
@login_required
def tambah_mahasiswa():
    if request.method == 'POST':
        # tampung di dictionary
        data = {
            'created_at': firestore.SERVER_TIMESTAMP,
            'nama_lengkap': request.form['nama_lengkap'],
            'nim': request.form['nim'],
            'jurusan': request.form['jurusan'],
            'status': request.form['status'],
            'tanggal_lahir': request.form['tanggal_lahir'],
            'jenis_kelamin': request.form['jenis_kelamin'],
        }
        if 'image' in request.files and request.files['image']:
            image = request.files['image']
            ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
            filename = image.filename
            lokasi = f"mahasiswa/{filename}"
            ext = filename.rsplit('.', 1)[1].lower()
            if ext in ALLOWED_EXTENSIONS:
                storage.child(lokasi).put(image)
                data['photoURL'] = storage.child(lokasi).get_url(None)
            else:
                flash("Foto tidak diperbolehkan", "danger")
                return redirect(url_for('mahasiswa'))

        # masukkan data ke database
        db.collection('mahasiswa').document().set(data)
        # kembali ke halaman mahasiswa
        flash('Berhasil menambahkan data', 'success')
        return redirect(url_for('mahasiswa'))

        # return jsonify()
    jurusan = get_all_collection('jurusan')
    return render_template('mahasiswa/tambah_mahasiswa.html', data=jurusan)

    



@app.route('/mahasiswa/<uid>')
@login_required
def lihat_mahasiswa(uid):
    mahasiswa = db.collection('mahasiswa').document(uid).get().to_dict()
    return render_template('mahasiswa/lihat_mahasiswa.html', data=mahasiswa)

# update
@app.route('/mahasiswa/edit/<uid>', methods=['GET', 'POST'])
def edit_mahasiswa(uid):
    if request.method == 'POST':
        # tampung di dictionary
        data = {

            'nama_lengkap': request.form['nama_lengkap'],
            'nim': request.form['nim'],
            'jurusan': request.form['jurusan'],
            'status': request.form['status'],
            'tanggal_lahir': request.form['tanggal_lahir'],
            'jenis_kelamin': request.form['jenis_kelamin'],
        }
        # masukkan data ke database
        db.collection('mahasiswa').document(uid).update(data)
        # kembali ke halaman mahasiswa
        flash('Berhasil mengedit data', 'success')
        return redirect(url_for('mahasiswa'))

    mahasiswa = db.collection('mahasiswa').document(uid).get().to_dict()
    return render_template('mahasiswa/edit_mahasiswa.html', data=mahasiswa)

# hapus
@app.route('/mahasiswa/hapus/<uid>')
@login_required
def hapus_mahasiswa(uid):
    db.collection('mahasiswa').document(uid).delete()
    flash('Berhasil menghapus data', 'danger')
    return redirect(url_for('mahasiswa'))


@app.route('/login', methods=['POST', 'GET'])
def halaman_login():
    if request.method == 'POST':
        data = {
            'username':  request.form['username'],
            'password': request.form['password']
        }
# tangkap data

        users_ref = db.collection('users').where('username', '==', data['username']).stream()
        user = {}
        for use in users_ref:
            user = use.to_dict()
        if user:
            if check_password_hash(user['password'], data['password']):
                session['user'] = user
                flash('berhasil login', 'success')
                return redirect(url_for('mahasiswa'))
            else:
                flash('username / password anda salah', 'danger')
                return redirect(url_for('halaman_login'))
        else:
            flash('username tidak di temukan', 'danger')
            return redirect(url_for('halaman_login'))

        
    if 'user' in session:
        return redirect(url_for('mahasiswa'))
    return render_template('login.html')
    

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('halaman_login'))










@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        data = {
            'created_at': firestore.SERVER_TIMESTAMP,
            'username' : request.form['username'].lower()
        }
        password = request.form ['password']
        confirm_password = request.form['confirm_password']

        if confirm_password != password:
            flash('Password tidak sama','danger')
            return redirect(url_for(register))

        users_ref = db.collection('users').where('username', '==', data['username']).stream()
        user = {}
        for use in users_ref:
            user = use.to_dict()
        
        if user:
            flash('username sudah terdaftart', 'danger')
            return redirect(url_for('register'))

        data['password'] = generate_password_hash(password, 'sha256')

        db.collection('users').document().set(data)
        flash('pendaftaran berhasil','success')

        return redirect(url_for('halaman_login'))
    return render_template('register.html')

@app.route('/jurusan',methods=['POST','GET'])
def jurusan():
    if request.method == 'POST':
        data = {
            'created_at': firestore.SERVER_TIMESTAMP,
            'jurusan': request.form['jurusan']
        }
        db.collection('jurusan').document().set(data)
        flash('Berhasil menambahkan jurusan', 'success')
        return redirect(url_for('jurusan'))


    daftar_jurusan = get_all_collection('jurusan')
    return render_template('jurusan/jurusan.html', data=daftar_jurusan)

@app.route('/jurusan/hapus/<uid>')
@login_required
def hapus_jurusan(uid):
    db.collection('jurusan').document(uid).delete()
    flash('Berhasil menghapus jurusan', 'danger')
    return redirect(url_for('jurusan'))



@app.route('/jurusan/edit', methods=['POST'])
def edit_jurusan():
    if request.method == 'POST':
        uid = request.form['id_jurusan']
        data = {
            'jurusan' : request.form ['nama_jurusan']
        }

        db.collection('jurusan').document(uid).update(data)
        flash('Berhasil edit jurusan','success')
        return redirect(url_for('jurusan'))




# Untuk Menjalankan Program Flask
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
