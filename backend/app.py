from flask import Flask, request, send_file
from flask_cors import CORS
from des import DES
from services.image import get_image_data, put_image_data
import os


app = Flask(__name__)
cors = CORS(app, resources={r"/encrypt": {"origins": "*"}})


@app.route("/encrypt", methods=["POST"])
def encrypt_image():
    image = request.files["image"]
    mode = request.form["mode"]

    if not image or not mode:
        return "Missing image or encryption mode", 400

    input_path = "assets/temp_input.png"
    output_path = "assets/temp_output.png"
    image.save(input_path)

    pixels = get_image_data(input_path)
    des = DES(pixels)

    match mode:
        case "ECB":
            des.mode.pad_text()
            encrypted_data = des.mode.ecb()
            des.mode.unpad_text()
        case "CBC":
            des.mode.pad_text()
            encrypted_data = des.mode.cbc()
            des.mode.unpad_text()
        case "CFB":
            encrypted_data = des.mode.cfb()
        case "OFB":
            encrypted_data = des.mode.ofb()
        case "CTR":
            encrypted_data = des.mode.ctr()
        case _:
            os.remove(input_path)
            return {"error": "Invalid encryption mode"}, 400

    put_image_data(input_path, output_path, encrypted_data)
    os.remove(input_path)

    return send_file(output_path, mimetype="image/png", as_attachment=False)
    

if __name__ == "__main__":
    app.run(debug=True)
