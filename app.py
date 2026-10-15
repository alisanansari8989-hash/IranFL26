from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import json
import os
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'IranFL26_secret_key_2026'

# ===== مسیرها =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')

ADMIN_PASSWORD = '1234561391anasari@'

# ===== توابع کمکی =====
def read_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def write_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_id():
    return str(uuid.uuid4())

def save_txt(txt_file, txt_links):
    if txt_file and txt_file.filename:
        txt_name = f"{generate_id()}.txt"
        txt_file.save(os.path.join(UPLOAD_DIR, 'files', txt_name))
        return txt_name
    elif txt_links:
        txt_name = f"{generate_id()}.txt"
        with open(os.path.join(UPLOAD_DIR, 'files', txt_name), 'w', encoding='utf-8') as f:
            f.write(txt_links)
        return txt_name
    return ''

# ===== context processor =====
@app.context_processor
def inject_active():
    return dict(current_path=request.path)

# ===== روت‌ها =====
@app.route('/')
def index():
    kits = read_json('kits.json')
    return render_template('index.html', kits=kits[::-1][:6])

@app.route('/kits')
def kits():
    kits = read_json('kits.json')
    return render_template('kits.html', kits=kits[::-1])

@app.route('/downloads')
def downloads():
    kits = read_json('kits.json')
    return render_template('downloads.html', kits=kits[::-1])

@app.route('/iranian')
def iranian():
    kits = read_json('kits.json')
    iranian_kits = [k for k in kits if k.get('category') == 'iranian']
    return render_template('iranian.html', kits=iranian_kits[::-1])

@app.route('/foreign')
def foreign():
    kits = read_json('kits.json')
    foreign_kits = [k for k in kits if k.get('category') == 'foreign']
    return render_template('foreign.html', kits=foreign_kits[::-1])

@app.route('/videos')
def videos():
    videos = read_json('videos.json')
    return render_template('videos.html', videos=videos[::-1])

@app.route('/logos')
def logos():
    logos = read_json('logos.json')
    return render_template('logos.html', logos=logos[::-1])

@app.route('/faces')
def faces():
    faces = read_json('faces.json')
    return render_template('faces.html', faces=faces[::-1])

@app.route('/leagues')
def leagues():
    leagues = read_json('leagues.json')
    return render_template('leagues.html', leagues=leagues[::-1])

@app.route('/packages')
def packages():
    packages = read_json('packages.json')
    return render_template('packages.html', packages=packages[::-1])

@app.route('/kit/<kit_id>')
def kit_detail(kit_id):
    kits = read_json('kits.json')
    kit = next((k for k in kits if k['id'] == kit_id), None)
    if not kit:
        return redirect('/')
    return render_template('kit.html', kit=kit)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/guide')
def guide():
    return render_template('guide.html')

@app.route('/support', methods=['GET', 'POST'])
def support():
    success = ''
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()
        if name and email and message:
            messages = read_json('messages.json')
            messages.append({
                'id': generate_id(), 'name': name, 'email': email,
                'message': message,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            write_json('messages.json', messages)
            success = 'پیام شما ارسال شد.'
    return render_template('support.html', success=success)

@app.route('/request', methods=['GET', 'POST'])
def request_kit():
    success = ''
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        kit_name = request.form.get('kit_name', '').strip()
        team = request.form.get('team', '').strip()
        notes = request.form.get('notes', '').strip()
        if name and kit_name and team:
            requests = read_json('requests.json')
            requests.append({
                'id': generate_id(), 'name': name, 'kit_name': kit_name,
                'team': team, 'notes': notes,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            write_json('requests.json', requests)
            success = 'درخواست شما ثبت شد.'
    return render_template('request.html', success=success)

# ===== پنل مدیریت =====
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    error = ''
    success = ''
    
    if request.method == 'POST':
        if 'login' in request.form:
            if request.form.get('password') == ADMIN_PASSWORD:
                session['admin'] = True
                return redirect('/admin')
            else:
                error = 'رمز عبور اشتباه است'
        
        elif 'upload_kit' in request.form and session.get('admin'):
            name = request.form.get('name', '').strip()
            team = request.form.get('team', '').strip()
            category = request.form.get('category', 'iranian')
            txt_links = request.form.get('txt_links', '').strip()
            image = request.files.get('image')
            txt_file = request.files.get('txt_file')
            if name and team and image:
                ext = image.filename.rsplit('.', 1)[-1].lower()
                if ext in ['jpg', 'jpeg', 'png', 'webp']:
                    image_name = f"{generate_id()}.{ext}"
                    image.save(os.path.join(UPLOAD_DIR, 'images', image_name))
                    txt_name = save_txt(txt_file, txt_links)
                    kits = read_json('kits.json')
                    kits.append({
                        'id': generate_id(), 'name': name, 'team': team,
                        'category': category, 'image': image_name,
                        'txt_file': txt_name,
                        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    write_json('kits.json', kits)
                    success = 'کیت با موفقیت آپلود شد'
                else:
                    error = 'فرمت عکس مجاز نیست'
            else:
                error = 'همه فیلدها الزامی است'
        
        elif 'upload_logo' in request.form and session.get('admin'):
            name = request.form.get('name', '').strip()
            txt_links = request.form.get('txt_links', '').strip()
            image = request.files.get('image')
            txt_file = request.files.get('txt_file')
            if name and image:
                ext = image.filename.rsplit('.', 1)[-1].lower()
                if ext in ['jpg', 'jpeg', 'png', 'webp']:
                    image_name = f"{generate_id()}.{ext}"
                    image.save(os.path.join(UPLOAD_DIR, 'images', image_name))
                    txt_name = save_txt(txt_file, txt_links)
                    logos = read_json('logos.json')
                    logos.append({
                        'id': generate_id(), 'name': name,
                        'image': image_name, 'txt_file': txt_name,
                        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    write_json('logos.json', logos)
                    success = 'لوگو با موفقیت آپلود شد'
                else:
                    error = 'فرمت عکس مجاز نیست'
            else:
                error = 'همه فیلدها الزامی است'
        
        elif 'upload_face' in request.form and session.get('admin'):
            name = request.form.get('name', '').strip()
            team = request.form.get('team', '').strip()
            txt_links = request.form.get('txt_links', '').strip()
            image = request.files.get('image')
            txt_file = request.files.get('txt_file')
            if name and team and image:
                ext = image.filename.rsplit('.', 1)[-1].lower()
                if ext in ['jpg', 'jpeg', 'png', 'webp']:
                    image_name = f"{generate_id()}.{ext}"
                    image.save(os.path.join(UPLOAD_DIR, 'images', image_name))
                    txt_name = save_txt(txt_file, txt_links)
                    faces = read_json('faces.json')
                    faces.append({
                        'id': generate_id(), 'name': name, 'team': team,
                        'image': image_name, 'txt_file': txt_name,
                        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    write_json('faces.json', faces)
                    success = 'فیس با موفقیت آپلود شد'
                else:
                    error = 'فرمت عکس مجاز نیست'
            else:
                error = 'همه فیلدها الزامی است'
        
        elif 'upload_league' in request.form and session.get('admin'):
            name = request.form.get('name', '').strip()
            country = request.form.get('country', '').strip()
            txt_links = request.form.get('txt_links', '').strip()
            image = request.files.get('image')
            txt_file = request.files.get('txt_file')
            if name and image:
                ext = image.filename.rsplit('.', 1)[-1].lower()
                if ext in ['jpg', 'jpeg', 'png', 'webp']:
                    image_name = f"{generate_id()}.{ext}"
                    image.save(os.path.join(UPLOAD_DIR, 'images', image_name))
                    txt_name = save_txt(txt_file, txt_links)
                    leagues = read_json('leagues.json')
                    leagues.append({
                        'id': generate_id(), 'name': name, 'country': country,
                        'image': image_name, 'txt_file': txt_name,
                        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    write_json('leagues.json', leagues)
                    success = 'لیگ با موفقیت آپلود شد'
                else:
                    error = 'فرمت عکس مجاز نیست'
            else:
                error = 'همه فیلدها الزامی است'
        
        elif 'upload_package' in request.form and session.get('admin'):
            name = request.form.get('name', '').strip()
            desc = request.form.get('desc', '').strip()
            txt_links = request.form.get('txt_links', '').strip()
            image = request.files.get('image')
            txt_file = request.files.get('txt_file')
            if name and image:
                ext = image.filename.rsplit('.', 1)[-1].lower()
                if ext in ['jpg', 'jpeg', 'png', 'webp']:
                    image_name = f"{generate_id()}.{ext}"
                    image.save(os.path.join(UPLOAD_DIR, 'images', image_name))
                    txt_name = save_txt(txt_file, txt_links)
                    packages = read_json('packages.json')
                    packages.append({
                        'id': generate_id(), 'name': name, 'desc': desc,
                        'image': image_name, 'txt_file': txt_name,
                        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    write_json('packages.json', packages)
                    success = 'پکیج با موفقیت آپلود شد'
                else:
                    error = 'فرمت عکس مجاز نیست'
            else:
                error = 'همه فیلدها الزامی است'
        
        elif 'upload_video' in request.form and session.get('admin'):
            title = request.form.get('title', '').strip()
            category = request.form.get('video_category', 'goal')
            video = request.files.get('video')
            if title and video:
                ext = video.filename.rsplit('.', 1)[-1].lower()
                if ext == 'mp4':
                    video_name = f"{generate_id()}.mp4"
                    video.save(os.path.join(UPLOAD_DIR, 'videos', video_name))
                    videos = read_json('videos.json')
                    videos.append({
                        'id': generate_id(), 'title': title,
                        'category': category, 'file': video_name,
                        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    write_json('videos.json', videos)
                    success = 'ویدیو با موفقیت آپلود شد'
                else:
                    error = 'فرمت ویدیو باید mp4 باشد'
            else:
                error = 'عنوان و فایل ویدیو الزامی است'
    
    logged_in = session.get('admin', False)
    return render_template('admin.html', logged_in=logged_in, error=error, success=success)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/admin')

# ===== سرو فایل‌های آپلودی =====
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
