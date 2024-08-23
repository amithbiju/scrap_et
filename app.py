from flask import Flask, request, jsonify,send_file
from bs4 import BeautifulSoup
import requests
from flask_cors import CORS
import imgkit
import os
import uuid
#from PIL import Image


app = Flask(__name__)

CORS(app)

config = imgkit.config(wkhtmltoimage='C:/Program Files/wkhtmltopdf/bin/bin/wkhtmltoimage.exe')

class UserData:
    def __init__(self, username, name, gender, department_id):
        self.username = username
        self.name = name
        self.gender = gender
        self.department_id = department_id
    
    def to_dict(self):
        return {
            'username': self.username,
            'name': self.name,
            'gender': self.gender,
            'department_id': self.department_id
        }

class SubjectData:
    def __init__(self, subject, attendance):
        self.subject = subject
        self.attendance = attendance

    def to_dict(self):
        return {
            'subject': self.subject,
            'attendance': self.attendance
        }

class ResponseData:
    def __init__(self, user_data, subject_data):
        self.user_data = user_data
        self.subject_data = subject_data

@app.route('/', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    payload = {
        'LoginForm[username]': username,
        'LoginForm[password]': password
    }
    userSession = requests.session()
    login_response = userSession.post(url='https://sctce.etlab.in/user/login', data=payload)
    if login_response.status_code == 200:
        profile_response = userSession.get('https://sctce.etlab.in/student/profile')
        subject_response = userSession.get('https://sctce.etlab.in/ktuacademics/student/viewattendancesubject/88')
        if profile_response.status_code == 200 and subject_response.status_code == 200:
            html_profile = BeautifulSoup(profile_response.content, 'html.parser')
            html_subject = BeautifulSoup(subject_response.content, 'html.parser')
            html_attendance = BeautifulSoup(subject_response.content, 'html.parser')
            try:
                name_tag = html_profile.find('th', string='Name')
                gender_tag = html_profile.find('th', string='Gender')
                university_id = html_profile.find('th', string='University Reg No')
                subject_by_subs = html_subject.find_all('th', class_='span2')
                attendance_by_subs = html_attendance.find_all('td', class_='span2')
                user_data = UserData(
                    username,
                    name_tag.find_next('td').text.strip(),
                    gender_tag.find_next('td').text.strip(),
                    university_id.find_next('td').text.strip()
                )
                subject_data = [SubjectData(subject.text.strip(), attendance.text.strip()) for subject, attendance in zip(subject_by_subs, attendance_by_subs)]
                user_data_dict = user_data.to_dict()
                subject_data_dicts = [subject.to_dict() for subject in subject_data]
                
                response_data = ResponseData(user_data_dict, subject_data_dicts)
                return jsonify(response_data.__dict__)
            except AttributeError:
                return jsonify({'error': 'Login failed!! Sorry plz check your credentials!'}), 400
        else:
            return jsonify({'error': 'ETLAB not responding !! Error fetching subject attendance!'}), 400
    else:
        return jsonify({'error': 'Login failed!! Sorry plz check your credentials!'}), 400
    
#only attendance get
@app.route('/att', methods=['POST'])
def api_att():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    payload = {
        'LoginForm[username]': username,
        'LoginForm[password]': password
    }
    userSession = requests.session()
    login_response = userSession.post(url='https://sctce.etlab.in/user/login', data=payload)
    if login_response.status_code == 200:
        subject_response = userSession.get('https://sctce.etlab.in/ktuacademics/student/viewattendancesubject/88')
        if subject_response.status_code == 200:
            html_subject = BeautifulSoup(subject_response.content, 'html.parser')
            html_attendance = BeautifulSoup(subject_response.content, 'html.parser')
            try:
                subject_by_subs = html_subject.find_all('th', class_='span2')
                attendance_by_subs = html_attendance.find_all('td', class_='span2')
                subject_data = [SubjectData(subject.text.strip(), attendance.text.strip()) for subject, attendance in zip(subject_by_subs, attendance_by_subs)]
                subject_data_dicts = [subject.to_dict() for subject in subject_data]
                
                return jsonify({'subject_data': subject_data_dicts})
            except AttributeError:
                return jsonify({'error': 'Error parsing profile information.'}), 400
        else:
            return jsonify({'error': 'ETLAB not responding !! Error fetching subject attendance!'}), 400
    else:
        return jsonify({'error': 'Login failed!! Sorry plz check your credentials!'}), 400

#time table
@app.route('/timetable', methods=['POST'])
def api_timetable():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    payload = {
        'LoginForm[username]': username,
        'LoginForm[password]': password
    }
    userSession = requests.session()
    login_response = userSession.post(url='https://sctce.etlab.in/user/login', data=payload)
    if login_response.status_code == 200:
        timetable_response = userSession.get('https://sctce.etlab.in/student/timetable')
        if timetable_response.status_code == 200:
            html_timetable = BeautifulSoup(timetable_response.content, 'html.parser')
            timetable_table = html_timetable.find('table', class_='items table table-striped table-bordered')
            timetable_data = []

            for row in timetable_table.find('tbody').find_all('tr'):
                day = row.find('td', class_='span2').text.strip()
                periods = [td.get_text(separator=' ').strip() for td in row.find_all('td')[1:]]
                timetable_data.append({'day': day, 'periods': periods})

            return jsonify({'timetable': timetable_data})
        else:
            return jsonify({'error': 'ETLAB not responding !! Error fetching timetable!'}), 400
    else:
        return jsonify({'error': 'Login failed!! Please check your credentials!'}), 400
    
#test annne
@app.route('/monthatt', methods=['POST'])
def api_monthatt():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    #month = data.get('month')
    payload = {
        'LoginForm[username]': username,
        'LoginForm[password]': password
    }
    userSession = requests.session()
    login_response = userSession.post(url='https://sctce.etlab.in/user/login', data=payload)
    the_data = {}#"semester": 6, "month": 8, "year": 2024
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    if login_response.status_code == 200:
        subject_response = userSession.post('https://sctce.etlab.in/ktuacademics/student/attendance', data=the_data, headers=headers)
        
        if subject_response.status_code == 200:
            html_content = subject_response.content
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Save HTML content as an image using imgkit
            options = {
                'format': 'png',
                'encoding': "UTF-8",
                "enable-local-file-access": ""
            }
            # Ensure the directory exists
            save_dir = f"saved_images/{username}"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            #geting server time
        
            save_path = os.path.join(save_dir, f"att_{uuid.uuid4()}.png")
            
            # Remove problematic tags
            for  tag in soup(['script', 'iframe']):
                tag.decompose()
            
            cleaned_html = str(soup).replace("about:blank", "")

            table = str(soup.find('style'))
            table += str(soup.find('table'))
            # Save HTML as an image
            #imgkit.from_string(cleaned_html, save_path, options=options, config=config)
            
            #return jsonify({'image_path': save_path}), 200
            #return send_file(save_path, as_attachment=True),200
            #return send_file(open(save_path, 'rb'), content_type='application/png')
            #return send_file(save_path, mimetype='image/png')
            try:
                #config = imgkit.config(wkhtmltoimage='/path/to/wkhtmltoimage')  # Adjust path as needed
                imgkit.from_string(str(table), save_path, options=options, config=config)
                 # Open the saved image and crop it
                

                return send_file(save_path, mimetype='image/png')
            except Exception as e:
                print(f"Error occurred: {e}")  # Print the error
                return jsonify({'image_path': save_path, 'error': str(e)}), 400
        else:
            return jsonify({'error': 'ETLAB not responding !! Error fetching subject attendance!'}), 400
    else:
        return jsonify({'error': 'Login failed!! Sorry plz check your credentials!'}), 400

if __name__ == '__main__':
    app.run()
