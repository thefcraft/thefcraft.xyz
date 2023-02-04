from flask import Flask, send_file, request
import requests
from io import BytesIO
from PIL import Image
import PyPDF2

app = Flask(__name__)

def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=100)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

def get_random_image(width, height):
    background_image_url = f"https://source.unsplash.com/random/{width}x{height}"
    response = requests.get(background_image_url)
    background_image = Image.open(BytesIO(response.content))
    return background_image


@app.route('/api/pdf2txt', methods=['POST'])
def extract_pdf_text():
    file = request.files['file']
    pdf = PyPDF2.PdfReader(file)
    text = ''
    for page in pdf.pages:
        data = page.extract_text()
        text+=data+'\n'

    return text

@app.route('/api/random_image/')
def random_image(width=1280, height=720):
    img = get_random_image(width, height)
    return serve_pil_image(img)

@app.route('/api/random_image/<width>x<height>')
def random_image_with_dimensions(width, height): return random_image(width, height)


@app.route('/')
def home(): 
    return '/api/random_image/\n/api/random_image/<width>x<height>\n/api/pdf2txt'

if __name__ == '__main__':
    app.run(debug=False)
