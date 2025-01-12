from fastapi import FastAPI, UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
import threading
from whisper_STT import Speach_to_Text
from openai_DSD import extract_DSD
from typing import Optional
from wakeword_handlr import listen_for_wakeword
from fastapi.middleware.cors import CORSMiddleware

# FastAPI 인스턴스 생성
app = FastAPI()

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용 (개발용)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)

prior_dist = None

# Threading event for wakeword detection
wake_word_event = threading.Event()

# Response form for navigation data
RESPONSE_FORM = '''
{
    "Departure": "<사용자의 답변에서의 출발지>",
    "Stopover1": "<사용자의 답변에서의 경유지1>",
    "Stopover2": "<사용자의 답변에서의 경유지2>",
    "Stopover3": "<사용자의 답변에서의 경유지3>",
    "Destination": "<사용자의 답변에서의 도착지>"
}
'''

def handle_wakeword():
    """Handle wakeword detection in a separate thread."""
    if listen_for_wakeword():
        print("Wake word detected! Start processing navigation request.")
        wake_word_event.set()

@app.post("/wakeword")
async def detect_wakeword(background_tasks: BackgroundTasks):
    """Endpoint to start wakeword detection."""
    if wake_word_event.is_set():
        return JSONResponse(content={"message": "Wake word already detected."}, status_code=400)
    
    # Run wakeword detection in background
    background_tasks.add_task(handle_wakeword)
    return {"message": "Listening for wakeword..."}

@app.post("/process_audio")
async def process_audio(file: UploadFile):
    """Endpoint to process audio file for navigation."""
    if not wake_word_event.is_set():
        raise HTTPException(status_code=400, detail="Wakeword not detected. Please start the process first.")

    try:
        # Read the uploaded audio file
        audio_data = await file.read()
        transcription = Speach_to_Text(audio_data)
        print(f"Transcription: {transcription}")

        # Extract navigation data
        global prior_dist
        navigation_data = extract_DSD(RESPONSE_FORM, transcription, prior_dist)
        prior_dist = navigation_data

        return {"status": "success", "route": navigation_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")