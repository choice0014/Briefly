import google.genai as genai
import os
from dotenv import load_dotenv

load_dotenv()

def list_available_models():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("API 키가 없습니다.")
        return

    client = genai.Client(api_key=api_key)
    print(f"--- 사용 가능한 모델 목록 (Key: {api_key[:10]}...) ---")
    try:
        for model in client.models.list():
            # 모델 객체의 모든 속성 대신 이름만 출력
            print(f"Model Name: {model.name}")
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    list_available_models()
