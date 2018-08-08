# -*- coding: utf-8 -*-
# Form implementation generated from reading ui file 'Transcribe.ui'
# Created by: PyQt5 UI code generator 5.11.2
# Author : Wen Rei

#Library
import pyaudio
import wave
import boto3
import json
import sys
import time
import datetime
import urllib
from PyQt5 import QtCore, QtGui, QtWidgets

#North Virgina S3
REGION ='us-east-1'

s3=boto3.resource('s3')
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 10
WAVE_OUTPUT_FILENAME = "output.wav"
count=0


p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK)

frames = []

class Ui_Dialog(object):


    def __init__(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(822, 483)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(10, 250, 93, 28))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setGeometry(QtCore.QRect(120, 250, 93, 28))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(Dialog)
        self.pushButton_3.setGeometry(QtCore.QRect(280, 250, 93, 28))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setObjectName("pushButton_3")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(30, 20, 321, 211))
        self.label.setAutoFillBackground(False)
        self.label.setFrameShape(QtWidgets.QFrame.Box)
        self.label.setObjectName("label")
        self.retranslateUi(Dialog)
        self.pushButton.pressed.connect(self.start)
        self.pushButton_2.pressed.connect(self.stop)

 
    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.pushButton.setText(_translate("Dialog", "Start"))
        self.pushButton_2.setText(_translate("Dialog", "Stop"))
        self.pushButton_3.setText(_translate("Dialog", "Transcribing"))
        self.label.setText(_translate("Dialog", "TextLabel"))

    def transcribe(self):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText("hi")      

    def start(self):
        global count
        print("start")
        count=1
        print(count)
        while count==1:
            data = stream.read(CHUNK)
            frames.append(data)
            QtWidgets.QApplication.processEvents()
            if count==0:
                break

    def stop(self):
        global count
        count=0
        print("stop")
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
    

#job_result = job['TranscriptionJob']['Transcript']['TranscriptFileUri']
# Function for detecting named entities
def detect_entities(text, language_code):
    comprehend = boto3.client('comprehend', region_name=REGION)
    response = comprehend.detect_entities(Text=text, LanguageCode=language_code)
    return response

'''
def main():

    s3.meta.client.upload_file('./output.wav','silencedanger','output.wav')

    transcribe = boto3.client('transcribe')
    currentDT = datetime.datetime.now()
    date=currentDT.day+currentDT.hour+currentDT.minute+currentDT.second
    job_name =str(date)
    job_uri = "https://s3.amazonaws.com/silencedanger/"+"output.wav"


    transcribe.start_transcription_job(
    TranscriptionJobName=job_name,
    Media={'MediaFileUri': job_uri},
    MediaFormat='wav',
    LanguageCode='en-US'
)

    while True:
        status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
            print("Not ready yet...")
        time.sleep(5)

    #print(status["TranscriptionJob"]["Transcript"]["TranscriptFileUri"])
    job_result = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
    with urllib.request.urlopen(job_result) as url:
        text=json.loads(url.read().decode())['results']['transcripts'][0]['transcript']
    print(text)
'''

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog(Dialog)
    Dialog.show()



    
    
    ui.pushButton_3.pressed.connect(ui.transcribe)




    sys.exit(app.exec_())
