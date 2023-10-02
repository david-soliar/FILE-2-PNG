from flask import Flask, render_template, request, send_file
from PIL import Image
import os
import math
import time

app = Flask(__name__)

YOUR_PATH = app.root_path

absolute_path_files = YOUR_PATH+"/files/"
absolute_path_export = YOUR_PATH+"/to_export/"

app.config['UPLOAD_FOLDER'] = absolute_path_files


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/2PNG', endpoint='index_2PNG')
def index_2PNG():
    return render_template('2PNG.html')


@app.route('/2FILE', endpoint='index_2FILE')
def index_2FILE():
    return render_template('2FILE.html')


@app.route('/2PNG', methods=['POST'])
def upload_file_2PNG():
    uploaded_file = request.files['file']

    path_to_file = os.path.join(app.config['UPLOAD_FOLDER'],
                                uploaded_file.filename)

    uploaded_file.save(path_to_file)

    pnged_file = File2PNG(path_to_file, globals()['absolute_path_export'])
    return send_file(pnged_file, as_attachment=True)


@app.route('/2FILE', methods=['POST'])
def upload_file_2FILE():
    uploaded_file = request.files['file']

    path_to_file = os.path.join(app.config['UPLOAD_FOLDER'],
                                uploaded_file.filename)

    uploaded_file.save(path_to_file)

    repnged_file = PNG2File(path_to_file, globals()['absolute_path_export'])
    return send_file(repnged_file, as_attachment=True)


def File2PNG(file_name, path2):
    with open(file_name, "rb") as f:
        x = f.read()

    original_length = len(x)
    a = math.ceil(math.sqrt(original_length/3))

    width = a
    height = a+1

    og_extension = file_name.split(".")[-1]

    og_extension = "a"*(width*3-len(og_extension)-1) + "." + og_extension
    original_extension = og_extension.encode()

    ammount_of_pixels = width*height

    last_row = original_length.to_bytes(length=width*3, byteorder='big')

    to_add_len = ammount_of_pixels*3-original_length-len(last_row)

    x = x + bytes(to_add_len) + last_row + original_extension

    data = list()
    for i in range(0, int(len(x)/3)):
        data.append((x[i*3], x[i*3+1], x[i*3+2]))

    file_name_timestamp = path2+f"{time.time()}.png"

    with Image.new(mode="RGB", size=(width, height+1)) as im:
        im.putdata(data)

        im.save(file_name_timestamp)

    return file_name_timestamp


def PNG2File(file_name, path2):
    with Image.open(file_name) as f:
        pixels = list(f.getdata())
        width, height = f.size

    original_length_pixels = pixels[len(pixels)-1-2*width:len(pixels)-width]
    original_extension_pixels = pixels[len(pixels)-width:]

    data = bytes()
    for i in original_extension_pixels:
        data += (i[0]).to_bytes(length=1, byteorder='big')
        data += (i[1]).to_bytes(length=1, byteorder='big')
        data += (i[2]).to_bytes(length=1, byteorder='big')

    original_extension = (data.decode()).split(".")[-1]

    data = bytes()
    for i in original_length_pixels:
        data += (i[0]).to_bytes(length=1, byteorder='big')
        data += (i[1]).to_bytes(length=1, byteorder='big')
        data += (i[2]).to_bytes(length=1, byteorder='big')

    original_length = int.from_bytes(data, "big")

    data_pixels = pixels[:len(pixels)-1-2*width]
    data = bytes()
    for pix in data_pixels:
        data += (pix[0]).to_bytes(length=1, byteorder='big')
        data += (pix[1]).to_bytes(length=1, byteorder='big')
        data += (pix[2]).to_bytes(length=1, byteorder='big')

    data = data[:original_length]

    file_name_timestamp = path2+f"{time.time()}.{original_extension}"

    with open(file_name_timestamp, "wb+") as f:
        f.write(data)

    return file_name_timestamp


@app.before_request
def remove_previous_files():
    path = globals()['absolute_path_files']
    for i in os.listdir(path):
        os.remove(path+i)

    current = time.time()
    path = globals()['absolute_path_export']
    for i in os.listdir(path):
        ts = i.split(".")[:2]
        ts = float(".".join(ts))
        if ts < current:
            os.remove(path+i)
