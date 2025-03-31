import os
from flask import current_app

class FilesService:
    def upload_file(self, file):
        upload_folder = current_app.config['UPLOAD_FOLDER']
        filepath = os.path.join(upload_folder, file.filename)
        try:
            file.save(filepath)
            return {"message": "File uploaded successfully", "filepath": filepath}
        except Exception as e:
            return {"error": str(e)}