from flask import Flask, render_template, request, redirect, send_from_directory
import os
import cv2

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'exp/static/uploads/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# Encryption function
def encrypt_message(image_path, output_path, message, password):
    img = cv2.imread(image_path)
    if img is None:
        return "Error: Could not open image."

    d = {chr(i): i for i in range(255)}
    if len(message) > img.shape[0] * img.shape[1]:
        return "Error: Message too long for the image size."

    n, m, z = 0, 0, 0
    msg_length = len(message)
    img[0, 0] = [msg_length, 0, 0]

    for i, char in enumerate(message):
        n, m = divmod(i + 1, img.shape[1])
        img[n, m, z] = d.get(char, 0)
        z = (z + 1) % 3

    success = cv2.imwrite(output_path, img)
    if not success:
        return "Error: Failed to save encrypted image."

    with open("password.txt", "w") as f:
        f.write(password)

    return None


# Decryption function
def decrypt_message(image_path, entered_password):
    if not os.path.exists(image_path):
        return "Error: Encrypted image file not found."

    img = cv2.imread(image_path)
    if img is None:
        return "Error: Could not open or find the image."

    c = {i: chr(i) for i in range(255)}

    try:
        with open("password.txt", "r") as f:
            stored_password = f.read().strip()
    except FileNotFoundError:
        return "Error: Password file not found."

    if entered_password != stored_password:
        return "YOU ARE NOT AUTHORIZED!"

    msg_length = img[0, 0, 0]
    n, m, z = 0, 0, 0
    message = ""

    for i in range(msg_length):
        n, m = divmod(i + 1, img.shape[1])
        message += c[img[n, m, z]]
        z = (z + 1) % 3

    return message


# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/encrypt', methods=['GET', 'POST'])
def encrypt():
    if request.method == 'POST':
        image = request.files['image']
        message = request.form['message']
        password = request.form['password']

        input_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'encrypted_' + image.filename)
        image.save(input_path)

        error = encrypt_message(input_path, output_path, message, password)
        if error:
            return render_template('encrypt.html', error=error)
        return render_template('encrypt.html', success=True, output_image='encrypted_' + image.filename)

    return render_template('encrypt.html')


@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt():
    if request.method == 'POST':
        image = request.files['image']
        password = request.form['password']

        input_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        image.save(input_path)

        result = decrypt_message(input_path, password)
        return render_template('decrypt.html', result=result)

    return render_template('decrypt.html')


if __name__ == '__main__':
    app.run(debug=True)
