from flask import Flask, render_template, request, redirect, session, flash
app = Flask(__name__)  
app.secret_key = 'ThisIsSecret'
from text_recognition import *

def TextFromImage(imageName):
    #TODO take parameters as POST for the image that we are looking into.
    #change the image location to uploaded image.
    res = LetterFinding("frozen_east_text_detection.pb",imageName, 0)
    texts = []
    for result in res:
        texts.append(result[1])
    return texts

@app.route('/upload', methods=['POST'])
def upload():
    print("we get here")
    file = request.files['uploaded_image']
    print(file)
    res = LetterFinding("frozen_east_text_detection.pb",file, 0)
    texts = []
    for result in res:
        texts.append(result[1])

    session['words'] = texts
    return redirect("/")

@app.route('/')         
def index():
    res = []
    if 'words' in session:
        res = session['words']
        session.clear()
    print(res)
    return render_template("index.html",list=res)

if __name__=="__main__":   
    app.run(debug=True)   

