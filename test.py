import threading
import sounddevice as sd
import soundfile as sf
from pydub import AudioSegment
from whisper_STT import Speach_to_Text
from openai_DSD import extract_DSD
from wakeword_handlr import listen_for_wakeword

RESPONSE_FORM = '''
{
    "Departure": "<사용자의 답변에서의 출발지>",
    "Stopover1": "<사용자의 답변에서의 경유지1>",
    "Stopover2": "<사용자의 답변에서의 경유지2>",
    "Stopover3": "<사용자의 답변에서의 경유지3>",
    "Destination": "<사용자의 답변에서의 도착지>"
}
'''

prior_dist = None
stop_program = threading.Event() 

def record_audio(file_path: str, record_seconds: int = 5, samplerate: int = 44100):
    """마이크로부터 오디오를 녹음하여 파일로 저장합니다."""
    print("녹음을 시작합니다...")
    try:
        # 오디오 녹음
        audio_data = sd.rec(int(record_seconds * samplerate), samplerate=samplerate, channels=1, dtype='int16')
        sd.wait()  
        print("녹음이 완료되었습니다.")

        # WAV로 저장 후 MP3로 변환
        wav_path = file_path.replace(".mp3", ".wav")
        sf.write(wav_path, audio_data, samplerate) 
        print(f"WAV 파일로 저장 완료: {wav_path}")

        # MP3로 변환
        mp3_audio = AudioSegment.from_wav(wav_path)
        mp3_audio.export(file_path, format="mp3", codec="libmp3lame") 
        print(f"MP3 파일로 변환 완료: {file_path}")
    except Exception as e:
        print(f"녹음 중 오류 발생: {str(e)}")

def listen_for_exit():
    """사용자가 엔터를 입력하면 프로그램 종료."""
    input("종료하려면 엔터 키를 누르세요...\n")
    stop_program.set() 
    print("프로그램을 종료합니다.")

def process_audio(file_path: str):
    """오디오 파일을 처리하여 네비게이션 데이터를 추출."""
    global prior_dist

    try:
        # 음성 텍스트 변환
        transcription = Speach_to_Text(file_path)
        print(f"변환된 텍스트: {transcription}")

        # 종료 명령 처리
        if "종료" in transcription or "프로그램 종료" in transcription:
            print("프로그램을 종료합니다.")
            stop_program.set() 
            return

        # 이전 경로와 통합된 네비게이션 데이터 추출
        navigation_data = extract_DSD(RESPONSE_FORM, transcription, prior_dist)
        prior_dist = navigation_data  

        print("네비게이션 데이터 추출 성공:")
        print(navigation_data)
    except Exception as e:
        print(f"오디오 처리 중 오류 발생: {str(e)}")

def main():
    global prior_dist

    # 엔터 키로 종료 스레드 시작
    exit_thread = threading.Thread(target=listen_for_exit, daemon=True)
    exit_thread.start()

    try:
        while not stop_program.is_set():  
            print("Listening for '지쿠야'...")

            if listen_for_wakeword():
                print("웨이크워드가 감지되었습니다! 네비게이션 요청 처리를 시작합니다.")

                # 오디오 녹음
                audio_file_path = "test_audio.mp3" 
                record_audio(audio_file_path) 
                process_audio(audio_file_path) 

                print(f"현재 경로 정보: {prior_dist}")
    except KeyboardInterrupt:
        print("\nCtrl+C 입력 감지: 프로그램 종료 중...")
        stop_program.set() 
    finally:
        print("프로그램이 정상적으로 종료되었습니다.")

if __name__ == "__main__":
    main()