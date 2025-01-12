import openai
import logging

logging.getLogger("openai").setLevel(logging.WARNING)

def load_api_key():
    """OpenAI API 키를 로드합니다."""
    with open("openai_api_key.txt", "r") as file:
        key = file.read().strip()
        return key

def Speach_to_Text(audio_file_path):
    """
    Whisper를 사용하여 음성을 텍스트로 변환합니다.
    :param audio_file_path: 처리할 오디오 파일 경로 (MP3, WAV 등)
    :return: 변환된 텍스트
    """
    OPENAI_API_KEY = f"{load_api_key()}"
    client = openai.OpenAI(
        api_key = OPENAI_API_KEY
    )

    try:
        # 파일 객체를 열어 API 호출
        with open(audio_file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file  # 파일 객체 전달
            )
        return transcription.text
    except Exception as e:
        print(f"Whisper 변환 중 오류 발생: {str(e)}")
        return ""
