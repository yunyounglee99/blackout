import pvporcupine
import pyaudio
import struct

def load_api_key():
    with open("picovoice_api_key.txt", "r") as file:
        key = file.read().strip()
        return key

def listen_for_wakeword():
    """Listen for wakeword and return True when detected."""
    ACCESS_KEY = f"{load_api_key()}"

    porcupine = pvporcupine.create(
        access_key=ACCESS_KEY,
        model_path="porcupine_params_ko.pv",
        keyword_paths=["wakeword_gcooya.ppn"]
    )

    # PyAudio 설정
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=porcupine.sample_rate,
        input=True,
        frames_per_buffer=porcupine.frame_length,
    )

    # print("Listening for '지쿠야'...")

    try:
        while True:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                # print("Wake word detected: '지쿠야'")
                return True
    finally:
        stream.close()
        audio.terminate()
        porcupine.delete()
