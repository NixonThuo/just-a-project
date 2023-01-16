"""Module providingFunction printing python version."""
from pydub import AudioSegment
from flask import Flask, render_template, request
from deep_translator import GoogleTranslator
from gtts import gTTS
import speech_recognition as sr
import moviepy.editor as mp
import os
import random
from mutagen.wave import WAVE


app = Flask(__name__)


def something():
    """Module providingFunction printing python version."""
    return app


@app.route("/")
def hello_world():
    """home page"""
    return render_template('index.html')


def translate_text(transcribedtext, language, filenumber):
    langs_list = GoogleTranslator().get_supported_languages(as_dict=True)
    print(langs_list)
    translated = GoogleTranslator(source='auto', target=language).translate(
        transcribedtext)
    translatedtextpath = os.path.join(
        app.root_path, 'static', 'splittranslatedtext', str(filenumber)+".txt")
    with open(translatedtextpath, 'w', encoding='utf-8') as f:
        f.write(translated)
    return translated


def translate_text_from_array(textlist, language):
    translatedlist = []
    filenumber = 0
    for text in textlist:
        text = translate_text(text, language, filenumber)
        translatedlist.append(text)
        filenumber += 1
    return translatedlist


def text_to_speech(translated, language, filenumber):
    translatedaudiopath = os.path.join(
        app.root_path, 'static', 'splitranslatedaudio', str(filenumber)+".mp3")
    try:
        tts = gTTS(translated, lang=language, slow=False)
        tts.save(translatedaudiopath)
    except AssertionError:
        silencesound = AudioSegment.silent(duration=5000)
        silencesound.export(translatedaudiopath, format="mp3")
    return translatedaudiopath


def text_to_speech_from_array(translatedlist, language):
    audiopaths = []
    filenumber = 0
    for text in translatedlist:
        audiopath = text_to_speech(text, language, filenumber)
        audiopaths.append(audiopath)
        filenumber += 1
    return audiopaths


def merge_audio_files(audiopaths, filename):
    combined_sounds = AudioSegment.empty()
    combinedaudiopath = os.path.join(
        app.root_path, 'static', 'combinedsound', filename+".wav")
    for audiopath in audiopaths:
        print(audiopath)
        sound = AudioSegment.from_mp3(audiopath)
        print("sound length")
        soundduration = sound.duration_seconds
        if soundduration < 5:
            remainingseconds = 5 - soundduration
            silencesound = AudioSegment.silent(duration=remainingseconds*1000)
            sound += silencesound
        combined_sounds += sound
    combined_sounds.export(combinedaudiopath, format="wav")
    return combinedaudiopath


def transcribe_audio(AUDIO_FILE, filenumber):
    # use the audio file as the audio source
    transcribedtext = ""
    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)  # read the entire audio file

        originaltext = ""
        try:
            originaltext = r.recognize_google(audio)
            print(originaltext)
        except sr.UnknownValueError:
            print("inaudible speech or could not understand")
            originaltext = ""

        transcribepath = os.path.join(
            app.root_path, 'static', 'splittranscribe', str(filenumber)+".txt")

        with open(transcribepath, 'w') as f_f:
            f_f.write(originaltext)

        f = open(transcribepath, "r")

        for x in f:
            transcribedtext += x
    return transcribedtext


def transcribe_audio_from_array(audiopathslist):
    textlist = []
    filenumber = 0
    for AUDIO_FILE in audiopathslist:
        text = transcribe_audio(AUDIO_FILE, filenumber)
        textlist.append(text)
        filenumber += 1
    return textlist


def split_audio_two(wavpath):
    audiopaths = []

    sound = WAVE(wavpath)

    length_of_audio = sound.info.length

    AudioSegment.converter = "ffmpeg.exe"
    AudioSegment.ffmpeg = "ffmpeg.exe"
    AudioSegment.ffprobe = "ffprobe.exe"

    i = 0
    start = 0
    startsecc = 0

    endmin = 0
    endsec = 5

    breakattribute = 0

    while (True):
        startTime = start*60*1000 + startsecc*1000
        endTime = endmin*60*1000 + endsec*1000

        extract = sound[startTime:endTime]
        splitaudiopath = os.path.join(
            app.root_path, 'static', 'splitaudios', str(i)+".wav")
        extract.export(splitaudiopath, format="wav")

        i = i+1

        startsecc = startsecc+5

        endsec = 5+endsec
        if (breakattribute > length_of_audio):
            break
        breakattribute = breakattribute+5

    return audiopaths


def split_audio(wavpath):
    audiopaths = []
    audio = WAVE(wavpath)
    length_of_audio = audio.info.length
    print(length_of_audio)
    sound = AudioSegment.from_wav(wavpath)
    AudioSegment.converter = "ffmpeg.exe"
    AudioSegment.ffmpeg = "ffmpeg.exe"
    AudioSegment.ffprobe = "ffprobe.exe"
    start = 0
    end = 5000
    length_of_audio_ms = length_of_audio * 1000
    audiocount = 0

    while (end < length_of_audio_ms):
        print("end " + str(end))
        print("length of audio" + str(length_of_audio_ms))
        extract = sound[start:end]
        splitaudiopath = os.path.join(
            app.root_path, 'static', 'splitaudios', str(audiocount)+".wav")
        audiopaths.append(splitaudiopath)
        extract.export(splitaudiopath, format="wav")
        start += 5001
        end += 5000
        audiocount += 1
    else:
        print("end" + str(end))
        print("length of audio" + str(length_of_audio_ms))
        extract = sound[start:length_of_audio_ms]
        splitaudiopath = os.path.join(
            app.root_path, 'static', 'splitaudios', str(audiocount)+".wav")
        audiopaths.append(splitaudiopath)
        extract.export(splitaudiopath, format="wav")

    return audiopaths


def merge_ogvideo_to_new_sound(videopath, translatedaudiopath, filename_we):
    ogvideo = mp.VideoFileClip(r""+videopath)
    print(videopath)
    print(translatedaudiopath)
    audioclip = mp.AudioFileClip(translatedaudiopath)
    translated_audioclip = mp.CompositeAudioClip([audioclip])
    ogvideo.audio = translated_audioclip
    randomnumber = random.randint(0, 1000)
    videofilename = str(randomnumber)+"_"+filename_we+"_newlang.mp4"
    newvideo = os.path.join(
        app.root_path, 'static', 'translated', videofilename)
    ogvideo.write_videofile(newvideo)
    return videofilename


@app.route("/videoupload", methods=['POST'])
def videoupload():
    """for uploading and translating"""
    formdata = request.form
    language = str(formdata.get('languages'))
    print(language)
    if 'videoinput' in request.files:
        originalvideo = request.files['videoinput']
        filename_we = originalvideo.filename.split('.')[0]
        videopath = os.path.join(
            app.root_path, 'static', 'videos', originalvideo.filename)
        originalvideo.save(videopath)
        movieclip = mp.VideoFileClip(r""+videopath)
        audiopath = os.path.join(
            app.root_path, 'static', 'audios', filename_we+".mp3")
        movieclip.audio.write_audiofile(r""+audiopath)

        # convert mp3 file to wav
        sound = AudioSegment.from_mp3(audiopath)
        wavpath = os.path.join(
            app.root_path, 'static', 'audios', filename_we+".wav")
        sound.export(wavpath, format="wav")

        audiopathslist = split_audio(wavpath)
        print(audiopathslist)

        # transcribe audio file
        textlist = transcribe_audio_from_array(audiopathslist)

        translatedlist = translate_text_from_array(textlist, language)

        audiopaths = text_to_speech_from_array(translatedlist, language)

        translatedaudiopath = merge_audio_files(audiopaths, filename_we)

        videofilename = merge_ogvideo_to_new_sound(
            videopath, translatedaudiopath, filename_we)

        return videofilename
    return "false"


@app.route("/finalvideo",  methods=['POST'])
def final_page():
    filename = request.form.get("filename")
    print(filename)
    return render_template('final.html', filename=filename)
