import openai
import json

def load_api_key():
    with open("openai_api_key.txt", "r") as file:
        key = file.read().strip()
        return key
    

def extract_DSD(response_form, user_prompt, prior_dist = None):
    OPENAI_API_KEY = f"{load_api_key()}"
    client = openai.OpenAI(
        api_key = OPENAI_API_KEY
    )

    prior_context = ""
    if prior_dist:
        prior_context = f"이전 경로는 다음과 같아 : {json.dumps(prior_dist, ensure_ascii=False)}"
    # print(prior_context)

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"""너는 내비게이션 보조 프로그램이야 너는 다음 지시사항들을 무조건 따라야해 \
            1. 사용자의 답변에서 출발지와 경유지, 목적지를 확인해줘 \
            2. 무조건 JSON 형식으로 {response_form}로만 답해줘 \
            3. 사용자가 장소를 추가해달라고 하면 null인 경유지에서 하나 장소를 추가해줘 \
            4. 출발지 또는 목적지 또는 경유지가 없다면 null으로 처리해줘 \
            5. 이전 경로가 주어지면 해당 경로를 기반으로 새로운 경유지 또는 데이터를 추가해줘 \
            6. <사용자의 답변에서의 출발지>, <사용자의 답변에서의 경유지1>, <사용자의 답변에서의 경유지2>, <사용자의 답변에서의 경유지3>, <사용자의 답변에서의 도착지>는 한글로만 말해줘"""},
            {
                "role": "user",
                "content": f"{prior_context} {user_prompt}"
            }
        ]
    )

    response = completion.choices[0].message.content
    if response.strip().startswith("```json"):
        response = response.strip()[7:] # ```json 제거
        response = response.strip()[:-3] # ``` 제거
    
    response_json = json.loads(response)

    return response_json

RESPONSE_FORM = '''
{
    "Departure": "<사용자의 답변에서의 출발지>",
    "Stopover1": "<사용자의 답변에서의 경유지1>",
    "Stopover2": "<사용자의 답변에서의 경유지2>",
    "Stopover3": "<사용자의 답변에서의 경유지3>",
    "Destination": "<사용자의 답변에서의 도착지>"
}
'''