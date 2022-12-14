from __future__ import division, print_function
# coding=utf-8

import os
import io

import numpy as np
from PIL import Image
import tensorflow as tf
from gevent.pywsgi import WSGIServer
from flask import Flask, request, render_template, jsonify


app = Flask('crack_detection')

# Model saved with Keras model.save()
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'crack_detection.h5')

# Load trained model
model = tf.keras.models.load_model(MODEL_PATH)
model.compile(loss='categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])
# model._make_predict_function()
print('Model loaded. Start serving...')


print('Model loaded. Check http://127.0.0.1:8080/')


def predict(img, model):
    img = img.resize([128, 128])
    # img = np.reshape(img,[None,128,128,3])

    # classes = np.argmax(model.predict(img), axis = 0)

    x = tf.keras.preprocessing.image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    images = np.vstack([x])
    # print(classes)
    
    preds = model.predict(images)
    return preds


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict_image_class():
    img = request.files['file'].read()
    img = Image.open(io.BytesIO(img))
    print("IMAGES")
    prediction = predict(img, model)
    final_pred = prediction[0][0]*1000000
    class_name = "crack" if final_pred < 0.5 else "no_crack"
    print(class_name)
    response = {"prediction": class_name}
    return jsonify(response)


if __name__ == '__main__':
    http_server = WSGIServer(('', 8080), app)
    http_server.serve_forever()
