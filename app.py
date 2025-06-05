from flask import Flask, request, render_template, redirect, session, send_file, url_for
from datetime import datetime
import os
import json
import pandas as pd

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Directory paths
SETTINGS_FILE = 'settings.json'
LOGS_DIR = 'logs'
os.makedirs(LOGS_DIR, exist_ok=True)

# Helper: Load settings
def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {
            "enable_question_1": True,
            "form_enabled": True
        }
    with open(SETTINGS_FILE, 'r') as f:
        return json.load(f)

# Helper: Save settings
def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

# Helper: Get today's Excel file path
def get_today_excel_filename():
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"attendance_{today}.xlsx"
    return os.path.join(LOGS_DIR, filename)


@app.route('/')
def index():
    settings = load_settings()
    return render_template('form.html', settings=settings)


@app.route('/submit', methods=['POST'])
def submit():
    settings = load_settings()

    name = request.form.get('name', '').strip()
    lastname = request.form.get('lastname', '').strip()
    q1 = request.form.get('question1', '').strip() if settings['enable_question_1'] else ''
    q2 = request.form.get('question2', '').strip() if settings['enable_question_2'] else ''

    if not name or not lastname:
        return "Nombre y Apellido son obligatorios", 400

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    today_file = get_today_excel_filename()

    try:
        if os.path.exists(today_file):
            df_old = pd.read_excel(today_file)

            # Check for duplicate by name + last name
            match_found = ((df_old['Name'] == name) & (df_old['Last Name'] == lastname)).any()
            if match_found:
                session['duplicate_attempt'] = True
                session['phone_number'] = q1
                session['name'] = name
                session['lastname'] = lastname
                return redirect(url_for('already_logged_in'))

        new_data = {
            'Name': name,
            'Last Name': lastname
        }

        if settings['enable_question_1']:
            q1_label = settings.get("question_1_label", "Pregunta 1")
            new_data[q1_label] = q1

        if settings['enable_question_2']:
            q2_label = settings.get("question_2_label", "Pregunta 2")
            new_data[q2_label] = q2

        new_data['Timestamp'] = timestamp

        if os.path.exists(today_file):
            df_old = pd.read_excel(today_file)
            df_new = pd.DataFrame([new_data])
            df_combined = pd.concat([df_old, df_new], ignore_index=True)
        else:
            df_combined = pd.DataFrame([new_data])

        df_combined.to_excel(today_file, index=False)

        session.pop('duplicate_attempt', None)
        session['phone_number'] = q1
        session['name'] = name
        session['lastname'] = lastname

    except Exception as e:
        print("Error saving data:", e)
        return "Sistema error: No se pudo guardar la asistencia", 500

    return redirect(url_for('success'))


@app.route('/success')
def success():
    settings = load_settings()
    return render_template('success.html', settings=settings)


@app.route('/already_logged_in')
def already_logged_in():
    settings = load_settings()
    if not session.get('duplicate_attempt'):
        return redirect(url_for('index'))
    
    full_name = session.get('name', '') + ' ' + session.get('lastname', '')
    subtitle = 'Ya te has registrado hoy.'
    if full_name.strip():
        subtitle += f" ({full_name})"

    return render_template('already_logged_in.html', settings=settings, subtitle=subtitle)


@app.route('/admin/settings', methods=['GET', 'POST'])
def admin_settings():
    if request.method == 'POST':
        updated = {
            "page_title": request.form.get("page_title"),
            "subtitle": request.form.get("subtitle"),
            "logo_url": request.form.get("logo_url"),
            "form_name_label": request.form.get("form_name_label"),
            "enable_question_1": 'enable_question_1' in request.form,
            "question_1_label": request.form.get("question_1_label"),
            "enable_question_2": 'enable_question_2' in request.form,
            "question_2_label": request.form.get("question_2_label"),
            "submit_button_label": request.form.get("submit_button_label"),
            "form_enabled": 'form_enabled' in request.form
        }
        save_settings(updated)
        return redirect(url_for('admin_settings'))

    settings = load_settings()
    return render_template('admin_settings.html', settings=settings)


@app.route('/admin/logs')
def view_logs():
    settings = load_settings()
    today_file = get_today_excel_filename()

    if not os.path.exists(today_file):
        return render_template('admin_logs.html', headers=[], logs=[], settings=settings)

    try:
        df = pd.read_excel(today_file)
        headers = list(df.columns)
        logs = df.to_dict(orient='records')
    except Exception as e:
        print("Error loading logs:", e)
        headers = []
        logs = []

    return render_template('admin_logs.html', headers=headers, logs=logs, settings=settings)


@app.route('/admin/download')
def download_log():
    today_file = get_today_excel_filename()
    if not os.path.exists(today_file):
        return "No se encontró archivo de registros", 404
    return send_file(today_file, as_attachment=True)


@app.route('/admin/clear')
def clear_logs():
    today_file = get_today_excel_filename()
    if os.path.exists(today_file):
        os.remove(today_file)
    return redirect(url_for('view_logs'))

if __name__ == '__main__':
    app.run(debug=True)