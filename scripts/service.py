# Developed by Mirko J. Rodríguez mirko.rodriguezm@gmail.com
#Reference: https://towardsdatascience.com/deploying-keras-models-using-tensorflow-serving-and-flask-508ba00f1037

#Import Flask
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS

#Import Keras
from keras.preprocessing import image

#Import python files
import numpy as np



import requests
import json
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api

from werkzeug.utils import secure_filename
from model_loader import cargarModelo

UPLOAD_FOLDER = '../images/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


cloudinary.config(
    cloud_name: "dvasik8ut",
    api_key: "319746686451239",
    api_secret: "gBCoSvDpjx4gAYvgEHnFKhhs1eA"
);




port = int(os.getenv('PORT', 5000))
print ("Port recognized: ", port)

#Initialize the application service
app = Flask(__name__)
CORS(app)
global loaded_model, graph
loaded_model, graph = cargarModelo()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Define a route
@app.route('/')
def main_page():
	return '¡Servicio REST activo!'

@app.route('/model/caries/', methods=['GET','POST'])
def default():
    data = {"success": False}
    if 'file' not in request.files:
        print('No file part')
        return jsonify(data), 400

    file = request.files['file']
    if file.filename == '':
        print('No selected file')
        return jsonify(data), 400

    if file and allowed_file(file.filename):
        # Guarda la imagen localmente (opcional, dependiendo de tus necesidades)
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Sube la imagen a Cloudinary
        cloudinary_response = upload(file)
        cloudinary_url = cloudinary_response['secure_url']
        print("URL de Cloudinary:", cloudinary_url)

        # Resto de tu código para cargar la imagen y realizar predicciones
        # ...

        # Aquí puedes usar cloudinary_url en lugar de la ruta local si es necesario

        # Success
        data["success"] = True

    return jsonify(data)







# Nuevo endpoint para obtener el listado de imágenes
# Nuevo endpoint para obtener el listado de imágenes
@app.route('/images', methods=['GET', 'POST'])
def get_image_list():
    data = {"success": False}
    try:
        image_list = os.listdir(app.config['UPLOAD_FOLDER'])
        data["image_list"] = image_list
        data["success"] = True
    except Exception as e:
        data["error"] = str(e)
    
    return jsonify(data)

    
# Run de application
app.run(host='0.0.0.0',port=port, threaded=False)
