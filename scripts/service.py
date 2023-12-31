#Reference: https://towardsdatascience.com/deploying-keras-models-using-tensorflow-serving-and-flask-508ba00f1037

#Import Flask
from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import cloudinary
#Import Keras
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url

from keras.preprocessing import image

#Import python files
import numpy as np

import requests
import json
import os
from werkzeug.utils import secure_filename
from model_loader import cargarModelo

UPLOAD_FOLDER = '../images/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

port = int(os.getenv('PORT', 5000))
print ("Port recognized: ", port)


cloudinary.config(
    cloud_name="dvasik8ut",
    api_key="319746686451239",
    api_secret="gBCoSvDpjx4gAYvgEHnFKhhs1eA"
)


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

@app.route('/model/caries/', methods=['POST'])
def default():
    data = {"success": False, "predictions": []}

    if request.method == "POST":
        files = request.files.getlist('file')  # Get list of files

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                # upload(file)

                # cloudinary_url = cloudinary_response['url']

                # loading image
                filename2 = filename
                filename = UPLOAD_FOLDER + '/' + filename
                print("\nfilename:", filename)

                image_to_predict = image.load_img(filename, target_size=(224, 224))
                test_image = image.img_to_array(image_to_predict)
                test_image = np.expand_dims(test_image, axis=0)
                test_image = test_image.astype('float32')
                test_image /= 255

                with graph.as_default():
                    result = loaded_model.predict(test_image)[0][0]

                # Results
                prediction = 1 if (result >= 0.5) else 0
                CLASSES = ['Normal', 'Caries']

                ClassPred = CLASSES[prediction]
                ClassProb = result

                print("Prediction:", ClassPred)
                print("Prob: {:.2%}".format(ClassProb))

                # Results as Json
                r = {"label": ClassPred, "score": float(ClassProb), "imagen": filename2}
                data["predictions"].append(r)

        # Success
        data["success"] = True

    return jsonify(data)

# Run de application
app.run(host='0.0.0.0',port=port, threaded=False)
