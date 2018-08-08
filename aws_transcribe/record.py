import pyaudio
import wave
import boto3
import json
import sys
import time
import datetime
import urllib

#North Virgina S3
REGION ='us-east-1'

s3=boto3.resource('s3')
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 10
WAVE_OUTPUT_FILENAME = "recordoutput.wav"



#job_result = job['TranscriptionJob']['Transcript']['TranscriptFileUri']
# Function for detecting named entities
def detect_entities(text, language_code):
    comprehend = boto3.client('comprehend', region_name=REGION)
    response = comprehend.detect_entities(Text=text, LanguageCode=language_code)
    return response


def main():
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

    print("* recording")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

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
        time.sleep(5)

    #print(status["TranscriptionJob"]["Transcript"]["TranscriptFileUri"])
    job_result = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
    with urllib.request.urlopen(job_result) as url:
        text=json.loads(url.read().decode())['results']['transcripts'][0]['transcript']
    print(text)

if __name__ == '__main__':
    main()
    print("v1")
