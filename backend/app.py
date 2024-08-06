from flask import Flask, request, send_from_directory
from flask_restful import Resource, Api
from flask_cors import CORS
from lxml import etree
import os
import zipfile
import shutil

app = Flask(__name__)
CORS(app)
api = Api(app)

# Directory for uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def fix_xml_content(xml_content):
    try:
        parser = etree.XMLParser(recover=True)
        tree = etree.fromstring(xml_content, parser=parser)
        fixed_xml_content = etree.tostring(tree, pretty_print=True, encoding='utf-8')
        return True, fixed_xml_content
    except Exception as e:
        return False, f"An error occurred: {e}"

def process_docx(file_path):
    try:
        temp_dir = 'temp'
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        xml_file_path = os.path.join(temp_dir, 'word', 'document.xml')
        with open(xml_file_path, 'rb') as file:
            xml_content = file.read()

        success, fixed_xml_content = fix_xml_content(xml_content)
        if not success:
            return False, fixed_xml_content

        with open(xml_file_path, 'wb') as file:
            file.write(fixed_xml_content)

        fixed_file_path = file_path.replace('.docx', '_fixed.docx')
        with zipfile.ZipFile(fixed_file_path, 'w') as zip_ref:
            for folder_name, subfolders, filenames in os.walk(temp_dir):
                for filename in filenames:
                    file_path = os.path.join(folder_name, filename)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zip_ref.write(file_path, arcname)

        shutil.rmtree(temp_dir)

        return True, fixed_file_path
    except Exception as e:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return False, f"An error occurred: {e}"

class UploadFile(Resource):
    def post(self):
        if 'file' not in request.files:
            return {"success": False, "message": "No file part"}, 400
        file = request.files['file']
        if file.filename == '':
            return {"success": False, "message": "No selected file"}, 400
        if file and (file.filename.endswith('.xml') or file.filename.endswith('.docx')):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            if file.filename.endswith('.xml'):
                success, message = fix_xml_content(open(file_path, 'rb').read())
                if success:
                    with open(file_path, 'wb') as file:
                        file.write(message)
                    return {"success": True, "message": "XML file has been fixed."}
                else:
                    return {"success": False, "message": message}, 500

            elif file.filename.endswith('.docx'):
                success, message = process_docx(file_path)
                if success:
                    return {"success": True, "message": f"/uploads/{os.path.basename(message)}"}
                else:
                    return {"success": False, "message": message}, 500
        else:
            return {"success": False, "message": "Invalid file type"}, 400

@app.route('/backend/uploads/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

api.add_resource(UploadFile, '/upload')

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
