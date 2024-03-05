from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
from pdf2image import convert_from_path, pdfinfo_from_path
import shutil
import tempfile

app = Flask(__name__)

@app.route('/pdf_to_image', methods=['POST'])
def pdf_to_image():
    # Crea un directorio temporal para almacenar el archivo PDF y las imágenes
    temp_dir = tempfile.mkdtemp()
    
    if 'pdf_file' not in request.files:
        return jsonify({"error": "No se encontró el archivo PDF en la solicitud."}), 400
    
    file = request.files['pdf_file']
    if file.filename == '':
        return jsonify({"error": "No se subió ningún archivo."}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Este archivo no es un PDF. Por favor, sube un archivo PDF."}), 400
    
    pdf_path = os.path.join(temp_dir, secure_filename(file.filename))
    file.save(pdf_path)
    
    try:
        images = convert_from_path(pdf_path)
        pdf_info = pdfinfo_from_path(pdf_path)
        
        # Guarda las imágenes convertidas en el directorio temporal
        output_images = []
        for i, image in enumerate(images):
            temp_img_path = os.path.join(temp_dir, f"temp_image_{i}.png")
            image.save(temp_img_path, "PNG")
            output_images.append(temp_img_path)
        
        # En este punto, necesitas decidir cómo devolver las imágenes.
        # Por simplicidad, solo devolveremos la información del PDF y no las imágenes.
        # Para devolver imágenes, podrías comprimir las imágenes en un archivo ZIP y enviar el archivo ZIP.
        
        # Limpieza: elimina el directorio temporal y su contenido
        shutil.rmtree(temp_dir)
        
        return jsonify(pdf_info), 200
    except Exception as e:
        # Asegúrate de limpiar incluso si ocurre un error.
        shutil.rmtree(temp_dir)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
