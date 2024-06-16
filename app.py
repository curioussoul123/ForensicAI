import os
from flask import Flask, render_template, request, redirect, url_for
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
from keras.models import load_model
import base64
from io import BytesIO

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

def get_opened_image(image):
    return Image.open(image).convert('RGB')

def _loadmodel():
    return load_model('/Users/nafeessiddiqui/PycharmProjects/pythonProject8/model.keras')

def difference(org):
    resaved_name = 'temp.jpg'
    org.save(resaved_name, 'JPEG', quality=92)
    resaved = Image.open(resaved_name)
    diff = ImageChops.difference(org, resaved)
    extrema = diff.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    if max_diff == 0:
        max_diff = 1
    scale = 255.0 / max_diff
    diff = ImageEnhance.Brightness(diff).enhance(scale)
    return diff

def pred(img):
    model = _loadmodel()
    diff = np.array(difference(img).resize((128, 128))).flatten() / 255.0
    diff = diff.reshape(-1, 128, 128, 3)
    pred = model.predict(diff)[0]
    if pred[0] > pred[1]:
        return "Not Forged"
    else:
        return 'Forged'

@app.route('/', methods=['GET', 'POST'])
def index():
    prediction = None
    img_data = None
    if request.method == 'POST':
        if 'input_image' not in request.files:
            return redirect(request.url)
        file = request.files['input_image']
        if file.filename == '':
            return redirect(request.url)
        if file:
            img = get_opened_image(file)
            prediction = pred(img)
            buffered = BytesIO()
            img.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            img_data = img_str
    return render_template('base.html', output=prediction, img_data=img_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8001)





    