# store/emotion.py 에 적용할 최종 권장 방식

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
# import logging # 필요시 로깅 추가

# --- 설정 ---
tokenizer_name = "skt/kobert-base-v1"
model_name_to_load = "jeonghyeon97/koBERT-Senti5"

# 실제 감정 레이블 매핑 (jeonghyeon97/koBERT-Senti5 모델 카드 기준)
# 순서: 분노, 슬픔, 중립, 행복, 혐오
ACTUAL_ID2LABEL = {
    0: "분노",
    1: "슬픔",
    2: "중립",
    3: "행복",
    4: "혐오"
}
# --- 전역 변수로 토크나이저 및 모델 로드 ---
try:
    # logging.info(f"토크나이저 로딩: {tokenizer_name}")
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, use_fast=False) # 중요!
    # logging.info(f"모델 로딩: {model_name_to_load}")
    model = AutoModelForSequenceClassification.from_pretrained(model_name_to_load)
    model.eval() # 추론 모드로 설정
    # logging.info("모델 및 토크나이저 로딩 완료.")
except Exception as e:
    # logging.error(f"모델 또는 토크나이저 로딩 실패: {e}")
    tokenizer = None
    model = None

def analyze_emotion(text: str) -> str:
    if not model or not tokenizer:
        # logging.error("분석기 준비 안됨. '분석 불가' 반환.")
        return "분석 불가"
    
    if not text or not text.strip():
        # logging.info("입력 텍스트 없음. '중립' 반환.")
        return "중립"

    try:
        # logging.debug(f"텍스트 토큰화: {text}")
        inputs = tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512  # KoBERT의 최대 입력 길이
        )
        
        # token_type_ids를 강제로 모두 0으로 설정 (단일 문장 입력의 경우)
        inputs['token_type_ids'] = torch.zeros_like(inputs['input_ids'])
        # logging.debug(f"모델 입력: {inputs}")

        with torch.no_grad(): # 기울기 계산 비활성화
            outputs = model(**inputs)
        
        logits = outputs.logits
        predicted_class_id = torch.argmax(logits, dim=-1).item()
        # logging.debug(f"예측된 ID: {predicted_class_id}, 로짓: {logits}")
        
        emotion = ACTUAL_ID2LABEL.get(predicted_class_id, "알 수 없음")
        # logging.info(f"분석된 감정: {emotion}")
        return emotion

    except Exception as e:
        # logging.error(f"감정 분석 중 오류: {e}")
        # logging.error(traceback.format_exc()) # 개발 중 상세 오류 확인
        return "분석 실패"

# # 간단한 테스트
# if __name__ == '__main__':
#     if model and tokenizer:
#         print(analyze_emotion("오늘 날씨 정말 좋아서 기분이 날아갈 것 같아!"))
#         print(analyze_emotion("너무 슬퍼서 눈물이 멈추지 않아."))
#         print(analyze_emotion("그 사람 때문에 화가 머리 끝까지 났어."))
#     else:
#         print("모델 또는 토크나이저가 로드되지 않았습니다.")

# -----------라이브러리 호출 테스트용-------------
# try:
#     print("테스트용 기본 모델 로딩 중...")
#     # 아주 기본적인 영어 감정 분석 모델로 테스트
#     classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
#     print("테스트용 기본 모델 로딩 완료.")
#     # 원래 모델로 다시 돌려놓으려면 아래 주석 처리된 코드를 활성화하고 위 테스트 코드는 제거/주석처리 하세요.
#     # print("감정 분석 모델 로딩 중...")
#     # classifier = pipeline("sentiment-analysis", model="jason9693/koelectra-base-v3-emotion_kor_common", return_all_scores=False)
#     # print("감정 분석 모델 로딩 완료.")
# except Exception as e:
#     print(f"모델 로딩 중 오류 발생: {e}")
#     classifier = None