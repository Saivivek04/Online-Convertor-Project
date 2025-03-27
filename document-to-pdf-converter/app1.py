from flask import Flask, render_template, request, send_file
import os
from werkzeug.utils import secure_filename
from docx2pdf import convert

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "converted_pdfs"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/convert", methods=["POST"])
def convert_docx():
    if "file" not in request.files:
        return "No file uploaded", 400

    file = request.files["file"]
    if file.filename == "":
        return "No file selected", 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    # Ensure it's a .docx file
    if not filename.endswith(".docx"):
        return "Only DOCX files are supported", 400

    pdf_filename = os.path.splitext(filename)[0] + ".pdf"
    pdf_path = os.path.join(app.config["OUTPUT_FOLDER"], pdf_filename)

    try:
        # Convert DOCX to PDF directly
        convert(file_path, app.config["OUTPUT_FOLDER"])
        return send_file(pdf_path, as_attachment=True)

    except Exception as e:
        return f"Error: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)