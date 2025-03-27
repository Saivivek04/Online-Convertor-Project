from flask import Flask, render_template, request, send_from_directory
import os
from pdf2docx import Converter
from werkzeug.utils import secure_filename
from PIL import Image
import traceback
from docx2pdf import convert

app = Flask(__name__)

# Directories for uploaded and converted files
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER

# Allowed file types
ALLOWED_EXTENSIONS = {"pdf", "docx", "png", "jpg", "jpeg"}

def allowed_file(filename):
    """Check if the uploaded file has a valid extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def upload_file():
    """Handles file uploads and conversions."""
    print("Received request...")  # Debug log

    if request.method == "POST":
        try:
            print("Processing POST request...")  # Debug log
            
            if "file" not in request.files:
                print("No file uploaded!")  # Debug log
                return "No file uploaded", 400

            file = request.files["file"]
            if file.filename == "":
                print("No file selected!")  # Debug log
                return "No selected file", 400

            if not allowed_file(file.filename):
                print("Invalid file type!")  # Debug log
                return "Invalid file format. Allowed formats: PDF, DOCX, PNG, JPG", 400

            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

            conversion_type = request.form["conversion_type"]
            print(f"Conversion type selected: {conversion_type}")  # Debug log

            output_filename = None
            output_path = None

            # PDF to DOCX Conversion
            if conversion_type == "pdf_to_docx":
                if not filename.endswith(".pdf"):
                    return "Invalid file type for PDF to DOCX conversion", 400

                output_filename = filename.replace(".pdf", ".docx")
                output_path = os.path.join(app.config["OUTPUT_FOLDER"], output_filename)

                print(f"Converting {file_path} to {output_path}...")  # Debug log
                cv = Converter(file_path)
                cv.convert(output_path, start=0, end=None)
                cv.close()
                print("PDF to DOCX conversion successful!")

            # DOCX to PDF Conversion
            elif conversion_type == "docx_to_pdf":
                if not filename.endswith(".docx"):
                    return "Invalid file type for DOCX to PDF conversion", 400

                output_filename = filename.replace(".docx", ".pdf")
                output_path = os.path.join(app.config["OUTPUT_FOLDER"], output_filename)

                print(f"Converting {file_path} to {output_path}...")  # Debug log
                convert(file_path, output_path)
                print("DOCX to PDF conversion successful!")

            # PNG to JPG Conversion
            elif conversion_type == "png_to_jpg":
                if not filename.endswith(".png"):
                    return "Invalid file type for PNG to JPG conversion", 400

                output_filename = filename.replace(".png", ".jpg")
                output_path = os.path.join(app.config["OUTPUT_FOLDER"], output_filename)

                print(f"Converting {file_path} to {output_path}...")  # Debug log
                img = Image.open(file_path)
                rgb_im = img.convert("RGB")
                rgb_im.save(output_path, "JPEG")
                print("PNG to JPG conversion successful!")

            # JPG to PNG Conversion
            elif conversion_type == "jpg_to_png":
                if not filename.endswith(".jpg") and not filename.endswith(".jpeg"):
                    return "Invalid file type for JPG to PNG conversion", 400

                output_filename = filename.replace(".jpg", ".png").replace(".jpeg", ".png")
                output_path = os.path.join(app.config["OUTPUT_FOLDER"], output_filename)

                print(f"Converting {file_path} to {output_path}...")  # Debug log
                img = Image.open(file_path)
                img.save(output_path, "PNG")
                print(f"JPG to PNG conversion successful! File saved at: {output_path}")

            else:
                return "Invalid conversion type selected", 400

            # Ensure the converted file exists before generating the download link
            if output_path and os.path.exists(output_path):
                print(f"File converted successfully! Download link: /download/{output_filename}")
                return render_template("index.html", download_link=f"/download/{output_filename}")
            else:
                print("Error: Converted file not found!")
                return "Conversion failed", 500

        except Exception as e:
            print("Error during conversion:", traceback.format_exc())
            return f"Conversion failed: {str(e)}", 500

    print("Rendering homepage...")  # Debug log
    return render_template("index.html")

@app.route("/download/<filename>")
def download_file(filename):
    """Serve converted files for download."""
    file_path = os.path.join(app.config["OUTPUT_FOLDER"], filename)
    
    if os.path.exists(file_path):
        print(f"Serving file: {file_path}")  # Debug log
        return send_from_directory(app.config["OUTPUT_FOLDER"], filename, as_attachment=True)
    else:
        print(f"Error: File {filename} not found in output folder.")
        return "File not found", 404

if __name__ == "__main__":
    app.run(debug=True)
    