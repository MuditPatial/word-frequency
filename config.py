import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "wfa-dev-secret-2024")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB upload limit
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
    ALLOWED_EXTENSIONS = {"txt", "pdf", "docx", "doc"}
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
