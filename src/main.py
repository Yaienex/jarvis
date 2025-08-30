import sounddevice as sd
import os
import vosk
from vosk import SetLogLevel
import webrtcvad
import numpy as np
import threading
import queue
import sys
import json
import time
import notify_sys
import action
import grammar

#TRAY
import gi
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Gtk', '3.0')
from gi.repository import AppIndicator3, Gtk

def on_quit(_):
    Gtk.main_quit()
    notify_sys.notifier("","Going to sleep")
    os._exit(0)
   

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, "robot.png")
def start_tray():
    indicator = AppIndicator3.Indicator.new(
        "Jarvis",
        filename, 
        AppIndicator3.IndicatorCategory.APPLICATION_STATUS,
    )

    # Menu contextuel
    menu = Gtk.Menu()
    item_quit = Gtk.MenuItem(label="Quitter")
    item_quit.connect("activate", on_quit)
    menu.append(item_quit)
    menu.show_all()

    indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
    indicator.set_menu(menu)

    Gtk.main()  

# Constantes 
DIRNAME = os.path.dirname(__file__)
SAMPLE_RATE = 16000          # Hz
FRAME_MS = 30                # ms (10, 20, 30)
FRAME_SIZE = int(SAMPLE_RATE * FRAME_MS / 1000)  # samples par frame
SILENCE_FRAMES_TO_END = 5    # nombre de frames de silence pour finaliser

MODEL_PATH = os.path.join(DIRNAME, "models/vosk-model-small-fr-0.22")

GRAMMAR = grammar.GRAMMAR

QUEUE = queue.Queue()

# --- Configuration ---
# transforme en JSON string pour le Recognizer
grammar_str = json.dumps(GRAMMAR)
# --- Initialiser Vosk ---
SetLogLevel(-1)#disabling log 
model = vosk.Model(MODEL_PATH)
recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE,grammar_str)

# --- Initialiser VAD ---
vad = webrtcvad.Vad(1)  # 0=quality, 3=très agressif
frame_bytes = FRAME_SIZE * 2  # 16-bit samples => 2 bytes

# --- Buffers ---
speech_buffer = bytearray()
silence_counter = 0



def cmd_handler(text):
    command = text.split(" ")
    if command[0] != "jarvis":
        return #ignore if the request doesnt start with jarvis
    
    command.pop(0)
    if len(command) ==0 :
        return #the user may have said jarvis but doesn't want it
    if command[0] not in grammar.ACTIONS:
        return #we want an action first 
    else :
        print(command)
        notify_sys.notifier("","Jarvis execute votre requête " + " ".join(command))
        action.main_actions(command)


def audio_callback(indata, frames, time_info, status):
    
    """callback du micro : push dans la queue"""
    if status:
        print(status, file=sys.stderr)
    # on prend que la première channel (mono)
    QUEUE.put(indata.copy())


notify_sys.notifier("","Waking up")
#launching the tray icon
threading.Thread(target=start_tray, daemon=True).start()


# --- Lancer le stream micro ---
with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16',
                        callback=audio_callback, blocksize=FRAME_SIZE):
    try:
        while True:
            try:
                data = QUEUE.get(timeout=1)  # attendre 1 sec max
            except queue.Empty:
                continue

            # convertir en bytes
            raw_bytes = data.tobytes()

            # splitter en frames de taille FRAME_SIZE
            for i in range(0, len(raw_bytes), frame_bytes):
                frame = raw_bytes[i:i+frame_bytes]
                if len(frame) < frame_bytes:
                    continue

                # VAD
                if vad.is_speech(frame, SAMPLE_RATE):
                    silence_counter = 0
                    speech_buffer.extend(frame)
                else:
                    silence_counter += 1
                    # si on a de la parole accumulée et assez de silence => finaliser
                    if speech_buffer and silence_counter >= SILENCE_FRAMES_TO_END:
                        if recognizer.AcceptWaveform(bytes(speech_buffer)):
                            result = json.loads(recognizer.Result())
                            text = result.get("text", "")
                            if text.strip():
                                cmd_handler(text)
                        else:
                            # fallback: partial/final result
                            result = json.loads(recognizer.FinalResult())
                            text = result.get("text", "")
                            if text.strip():
                                cmd_handler(text)
                        speech_buffer = bytearray()
                        silence_counter = 0
    except KeyboardInterrupt:
        notify_sys.notifier("","Going to sleep")
        exit(0)


