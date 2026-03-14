from flask import Flask, render_template, request, send_file
from PIL import Image
import numpy as np
from gtts import gTTS
import os, time
import base64
from io import BytesIO

app = Flask(__name__)
STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
if not os.path.exists(STATIC_DIR): os.makedirs(STATIC_DIR)

@app.route('/', methods=['GET', 'POST'])
def index():
    full_message = ""
    msg = ""
    ts = str(int(time.time()))
    img_data = None
    voice_data = None

    if request.method == 'POST':
        
        # --- 1. HIDE MESSAGE ---
        if 'hide' in request.form:
            f = request.files['img']
            text = request.form['text_input']
            
            if f and text:
                # Convert to Grayscale (L) and resize to 300x300 for consistency
                img = Image.open(f).convert('L').resize((300, 300))
                pixels = np.array(img).flatten()
                
                # Store length of text in the first pixel
                pixels[0] = len(text) 
                
                # Hide characters
                for i in range(len(text)):
                    pixels[i + 1] = ord(text[i])
                
                encoded_img = Image.fromarray(pixels.reshape((300, 300)))
                img_io = BytesIO()
                encoded_img.save(img_io, 'PNG')
                img_io.seek(0)
                img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
                msg = "Full message hidden successfully!"
                img_data = img_base64

        # --- 2. RETRIEVE FROM UPLOADED IMAGE ---
        elif 'show' in request.form:
            # Check if user uploaded a file for decoding
            f = request.files.get('img') 
            
            if f and f.filename != '':
                # Open the image from the uploaded file
                img = Image.open(f)
                pixels = np.array(img).flatten()
                
                try:
                    # 1. Read length
                    length = pixels[0] 
                    
                    # 2. Reconstruct string
                    chars = []
                    for i in range(1, length + 1):
                        chars.append(chr(pixels[i]))
                    full_message = "".join(chars)
                    
                    # 3. Speak
                    tts = gTTS(text=f"The hidden message is: {full_message}", lang='en')
                    voice_io = BytesIO()
                    tts.write_to_fp(voice_io)
                    voice_io.seek(0)
                    voice_base64 = base64.b64encode(voice_io.getvalue()).decode('utf-8')
                    msg = "Message retrieved from uploaded image!"
                    voice_data = voice_base64
                    
                except Exception as e:
                    msg = "Error: Could not decode message. Ensure this is a valid secret image."
            else:
                msg = "Please upload the Grayscale Image to retrieve the message."

    return render_template('index.html', msg=msg, secret=full_message, ts=ts, img_data=img_data, voice_data=voice_data)

if __name__ == '__main__':
    app.run(debug=True)