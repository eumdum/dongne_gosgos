# # konlpy와 감정사전을 이용. 가장 많이 나타나는 감정을 찾는 코드.
# # from .emotion_d import EMOTION_DICT

# def analyze_emotion(text):
#     #     # 텍스트를 형태소 단위로 나누고, 기본형으로 바꿈 (예: '슬펐어' -> '슬프다')
#     morphs = okt.pos(text, stem=True)

#     emotion_scores = {emotion: 0 for emotion in EMOTION_DICT.keys()}

#     # 문장의 모든 단어를 반복
#     for word, _ in morphs:
#         # 감정 사전을 반복
#         for emotion, emotion_words in EMOTION_DICT.items():
#             # 만약 단어가 감정 사전에 있다면, 해당 감정 점수 +1
#             if word in emotion_words:
#                 emotion_scores[emotion] += 1

#     # 가장 높은 점수를 받은 감정을 찾음
#     # 만약 모든 점수가 0이라면 '분석불가' 반환
#     if all(score == 0 for score in emotion_scores.values()):
#         return "중립" # 또는 "분석불가"

#     dominant_emotion = max(emotion_scores, key=emotion_scores.get)

#     return dominant_emotion
# ---------------------------------------------------------------------------------(아래)
# import json
# import os
# # # 1단계에서 만든 emotion_dictionary.py 파일에서 부사, 부정어 목록 가져오기
# from .emotion_d import BOOSTER_DICT, NEGATION_LIST

# # --- KNU 감성 사전 불러오기 ---
# # 현재 파일의 위치를 기준으로 사전 파일의 절대 경로를 찾음
# try:
#     BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#     knu_senti_dict_path = os.path.join(BASE_DIR, 'SentiWord_info.json')

#     knu_senti_dict = {}
#     with open(knu_senti_dict_path, 'r', encoding='utf-8') as f:
#         data = json.load(f)
#         for item in data:
#             # key: 단어의 원형, value: 감성 점수 (-2 ~ 2)
#             knu_senti_dict[item['word_root']] = int(item['polarity'])
# except FileNotFoundError:
#     # SentiWord_info.json 파일이 없을 경우를 대비한 예외 처리
#     print("Error: SentiWord_info.json 파일을 back/store/ 폴더에 넣어주세요.")
#     knu_senti_dict = {}
# # --- 사전 불러오기 끝 ---


# def analyze_emotion(text: str) -> str:
#     """
#     KNU 감성 사전을 기반으로 문장의 감성을 분석합니다.
#     부사(booster)와 부정어(negation)를 고려하여 점수를 계산합니다.
#     """
#     #     # 문장을 형태소 단위로 나누고, 단어의 원형을 찾음 (예: '슬펐어' -> '슬프다')
#     morphs = okt.pos(text, stem=True)
    
#     total_score = 0
#     negation_flag = False
    
#     # 문장을 단어별로 순회
#     for i, (word, pos) in enumerate(morphs):
        
#         # 1. 현재 단어의 기본 감성 점수 가져오기 (사전에 없으면 0)
#         score = knu_senti_dict.get(word, 0)
        
#         if score != 0:
#             # 2. 부사(booster) 처리: 바로 앞 단어가 부사이면 점수에 가중치 적용
#             if i > 0:
#                 prev_word = morphs[i-1][0]
#                 booster_weight = BOOSTER_DICT.get(prev_word, 1.0)
#                 score *= booster_weight

#             # 3. 부정어 처리: 이전에 부정어가 나왔었다면 점수의 극성을 반전 (예: 2점 -> -2점)
#             if negation_flag:
#                 score *= -1
#                 negation_flag = False # 부정어 효과는 한 번만 적용

#             total_score += score
        
#         # 4. 부정어 플래그 설정: 현재 단어가 부정어 목록에 있으면 플래그를 True로 변경
#         if word in NEGATION_LIST:
#             negation_flag = True
#         # '슬프지 않다' 처럼 단어 뒤에 붙는 부정어 처리를 위해,
#         # 동사/형용사 뒤에 부정어가 나오지 않으면 플래그를 다시 False로 초기화
#         elif pos in ['Verb', 'Adjective'] and negation_flag:
#             negation_flag = False
            
#     # 5. 최종 점수에 따라 감정 분류
#     if total_score > 3:
#         return "행복"
#     elif total_score > 0:
#         return "평온"
#     elif total_score < -3:
#         return "분노"
#     elif total_score < 0:
#         return "슬픔"
#     else:
#         return "중립"
# import json
# import os
# # from .emotion_d import BOOSTER_DICT, NEGATION_LIST, CUSTOM_DICT, REPLACE_DICT

# # --- KNU 감성 사전 불러오기 (기존과 동일) ---
# try:
#     BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#     knu_senti_dict_path = os.path.join(BASE_DIR, 'SentiWord_info.json')
#     knu_senti_dict = {}
#     with open(knu_senti_dict_path, 'r', encoding='utf-8') as f:
#         data = json.load(f)
#         for item in data:
#             knu_senti_dict[item['word_root']] = int(item['polarity'])
#     knu_senti_dict.update(CUSTOM_DICT) # 두 사전 합짐
# except FileNotFoundError:
#     print("Error: SentiWord_info.json 파일을 back/store/ 폴더에 넣어주세요.")
#     knu_senti_dict = {}



# def analyze_emotion(text: str) -> str:
#     print(f"\n===== \"{text}\" 분석 시작 =====") # --- 디버깅용 print ---
    
#     # 원본 텍스트에서 단어 바꿔치기
#     for old_word, new_word in REPLACE_DICT.items():
#         text = text.replace(old_word, new_word)

#     # 바꿔치기한 텍스트로 형태소 분석 시작
#     #     morphs = okt.pos(text, stem=True)
#     print(f"1. 형태소 분석 결과: {morphs}") # --- 디버깅용 print ---
    
#     total_score = 0
#     negation_flag = False
    
#     # detected_words = [] # --- 디버깅용 리스트 ---
#     # ignored_words = []
    
#     # for i, (word, pos) in enumerate(morphs):

#     #     # 필터링: 의미 없는 단어들은 분석에서 제외
#     #     if pos in ['Josa', 'Punctuation', 'Suffix', 'Foreign', 'Number', 'Determiner']:
#     #         ignored_words.append(f"  - '{word}' (품사: {pos})")
#     #         continue
#     #     # 한 글자나, 사전에 추가한 단어가 아니라면 무시
#     #     if len(word) < 2 and word not in knu_senti_dict:
#     #         ignored_words.append(f"  - '{word}' (한 글자 단어)")
#     #         continue

#     #     # 점수 가져옴
#     #     score = knu_senti_dict.get(word, 0)
        
#     #     # 점수 있는 단어들만 계산
#     #     if score != 0:
#     #         original_score = score
            
#     #         # 부사 처리
#     #         if i > 0:
#     #             prev_word, prev_pos = morphs[i-1]
#     #             # 바로 앞 단어가 부사(Adverb)이고, 우리 부사 사전에 있다면 가중치 적용
#     #             if prev_pos == 'Adverb' and prev_word in BOOSTER_DICT:
#     #                 score *= BOOSTER_DICT[prev_word]

#     #         # 부정어 처리
#     #         if negation_flag:
#     #             score *= -1
#     #             negation_flag = False

#     #         # 최종 점수 합산
#     #         total_score += score

#     #         # --- 디버깅용 print ---
#     #         detected_words.append(f"  - 단어: '{word}', 기본점수: {original_score}, 최종점수: {score:.2f}")

#     #     # 부정어 플래그 관리
#     #     if word in NEGATION_LIST:
#     #         negation_flag = True
#     #     # 현재 단어가 동사/형용사이고 이전에 부정어가 나왔었다면, 플래그를 다시 초기화
#     #     # (예: '못' 먹었다 -> '먹었다'에서 효과 적용 후 초기화)
#     #     elif pos in ['Verb', 'Adjective']:
#     #         negation_flag = False

#     for i, (word, pos) in enumerate(morphs):
        
#         # --- 필터링 (기존과 동일) ---
#         if len(word) < 2 or pos in ['Josa', 'Punctuation', 'Suffix', 'Foreign']:
#             continue
            
#         score = knu_senti_dict.get(word, 0)
        
#         if score != 0:
#             # ✨ 부사 처리 로직 수정!
#             # 바로 앞 단어가 우리 부사 사전에 있으면, 품사와 상관없이 가중치 적용
#             if i > 0:
#                 prev_word = morphs[i-1][0]
#                 if prev_word in BOOSTER_DICT: # Okt의 품사 태깅(pos)을 믿지 않고 우리 사전을 우선함
#                     score *= BOOSTER_DICT[prev_word]

#             # 부정어 처리 (기존과 동일)
#             if negation_flag:
#                 score *= -1
#                 negation_flag = False

#             total_score += score
        
#         # 부정어 플래그 관리 (기존과 동일)
#         if word in NEGATION_LIST:
#             negation_flag = True
#         elif pos in ['Verb', 'Adjective'] and negation_flag:
#             negation_flag = False
            
#     # print("2. 감지된 단어 및 점수 계산:") # --- 디버깅용 print ---
#     # if not detected_words:
#     #     print("  - 감지된 감정 단어 없음")
#     # else:
#     #     for line in detected_words:
#     #         print(line)

#     print(f"3. 최종 점수: {total_score}") # --- 디버깅용 print ---

#     if total_score > 3:
#         return "행복"
#     elif total_score > 0:
#         return "평온"
#     elif total_score < -3:
#         return "분노"
#     elif total_score < 0:
#         return "슬픔"
#     else:
#         return "중립"
        
#     # print(f"4. 최종 감정: {result}") # --- 디버깅용 print ---
#     # print("=" * 30)
#     # return result

# import json
# import os
# # from .emotion_d import BOOSTER_DICT, NEGATION_LIST, REPLACE_DICT, CUSTOM_SCORE_DICT

# # --- KNU 사전 불러오기 ---
# try:
#     BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#     knu_senti_dict_path = os.path.join(BASE_DIR, 'SentiWord_info.json')
#     knu_senti_dict = {}
#     with open(knu_senti_dict_path, 'r', encoding='utf-8') as f:
#         data = json.load(f)
#         for item in data:
#             knu_senti_dict[item['word_root']] = int(item['polarity'])
# except FileNotFoundError:
#     print("Error: SentiWord_info.json 파일을 back/store/ 폴더에 넣어주세요.")
#     knu_senti_dict = {}


# def analyze_emotion(text: str) -> str:
#     # ✨ 1. '암호'가 어떤 단어에서 왔는지 추적하기 위한 '역방향 지도' 생성
#     reverse_replace_map = {}
#     for original, symbol in REPLACE_DICT.items():
#         if symbol not in reverse_replace_map:
#             reverse_replace_map[symbol] = []
#         reverse_replace_map[symbol].append(original)
    
#     print(f"\n===== \"{text}\" 분석 시작 =====")
    
#     # 2. '바꿔치기' 로직
#     for old_word, new_word in REPLACE_DICT.items():
#         text = text.replace(old_word, new_word)
    
#     # 3. 형태소 분석
#     #     morphs = okt.pos(text, stem=True)
#     print(f"2. 형태소 분석 결과: {morphs}")
    
#     total_score = 0
#     negation_flag = False
#     detected_words = []
    
#     for i, (word, pos) in enumerate(morphs):
        
#         # 4. '암호' 또는 '커스텀 단어' 우선 처리
#         if word in CUSTOM_SCORE_DICT:
#             score = CUSTOM_SCORE_DICT[word]
#             total_score += score
            
#             # ✨ 5. 출력 형식 개선
#             # 만약 단어가 '암호'라면, '역방향 지도'를 참고해서 원래 단어를 함께 보여줌
#             if word in reverse_replace_map:
#                 original_candidates = '/'.join(reverse_replace_map[word])
#                 detected_words.append(f"  - [암호 변환] '{original_candidates}' -> '{word}', 점수: {score}")
#             else:
#                 # '암호'가 아닌 일반 커스텀 단어일 경우
#                 detected_words.append(f"  - [커스텀 단어] '{word}', 점수: {score}")
#             continue

#         # 6. 필터링
#         if len(word) < 2 or pos in ['Josa', 'Punctuation', 'Suffix', 'Foreign']:
#             continue
            
#         # 7. KNU 사전에서 점수 가져오기
#         score = knu_senti_dict.get(word, 0)
        
#         # 8. 점수 계산 (부사/부정어 처리)
#         if score != 0:
#             original_score = score
#             if i > 0:
#                 prev_word = morphs[i-1][0]
#                 if prev_word in BOOSTER_DICT:
#                     score *= BOOSTER_DICT[prev_word]
#             if negation_flag:
#                 score *= -1
#                 negation_flag = False
#             total_score += score
#             detected_words.append(f"  - [일반 단어] '{word}', 기본점수: {original_score}, 최종점수: {score:.2f}")
        
#         # 9. 부정어 플래그 관리
#         if word in NEGATION_LIST:
#             negation_flag = True
#         elif pos in ['Verb', 'Adjective'] and negation_flag:
#             negation_flag = False
            
#     # 최종 감정 분류
#     print("3. 감지된 단어 및 점수 계산:")
#     if not detected_words:
#         print("  - 감지된 감정 단어 없음")
#     else:
#         for line in detected_words:
#             print(line)

#     print(f"4. 최종 점수: {total_score}")

#     if total_score > 3:
#         result = "행복"
#     elif total_score > 0:
#         result = "평온"
#     elif total_score < -3:
#         result = "분노"
#     elif total_score < 0:
#         result = "슬픔"
#     else:
#         result = "중립"
        
#     print(f"5. 최종 감정: {result}")
#     print("=" * 30)
#     return result
import json
import os
from .emotion_d import BOOSTER_DICT, NEGATION_LIST, REPLACE_DICT, CUSTOM_SCORE_DICT

# --- KNU 사전 불러오기 (기존과 동일) ---
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    knu_senti_dict_path = os.path.join(BASE_DIR, 'SentiWord_info.json')
    knu_senti_dict = {}
    with open(knu_senti_dict_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for item in data:
            knu_senti_dict[item['word_root']] = int(item['polarity'])
except FileNotFoundError:
    print("Error: SentiWord_info.json 파일을 back/store/ 폴더에 넣어주세요.")
    knu_senti_dict = {}


def analyze_emotion(text: str) -> str:
    print(f"\n===== \"{text}\" 분석 시작 =====")
    
    # 1. '바꿔치기' 로직
    for old_word, new_word in REPLACE_DICT.items():
        text = text.replace(old_word, new_word)
    
    # 2. 형태소 분석
    morphs = okt.pos(text, stem=True)
    print(f"2. 형태소 분석 결과: {morphs}")
    
    total_score = 0
    negation_flag = False
    detected_words = []
    
    for i, (word, pos) in enumerate(morphs):
        
        # ✨ --- 새로운 처리 순서 ---
        # 1. 'VIP 통로': 커스텀/암호 단어인지 먼저 확인
        if word in CUSTOM_SCORE_DICT:
            score = CUSTOM_SCORE_DICT[word]
            
            # 커스텀 단어도 부사/부정어 영향을 받도록 수정
            original_score = score
            if i > 0:
                prev_word = morphs[i-1][0]
                if prev_word in BOOSTER_DICT:
                    score *= BOOSTER_DICT[prev_word]
            if negation_flag:
                score *= -1
                
            total_score += score
            detected_words.append(f"  - [커스텀/암호] '{word}', 기본점수: {original_score}, 최종점수: {score:.2f}")
            
            # 부정어 플래그는 여기서도 관리
            if word in NEGATION_LIST:
                negation_flag = True
            else:
                negation_flag = False
            
            continue # VIP 단어는 처리했으니, 아래 로직은 건너뜀

        # 2. 일반 단어 필터링
        if len(word) < 2 or pos in ['Josa', 'Punctuation', 'Suffix', 'Foreign']:
            continue
            
        # 3. KNU 사전에서 점수 가져오기
        score = knu_senti_dict.get(word, 0)
        
        # 4. 점수 계산 (부사/부정어 처리)
        if score != 0:
            original_score = score
            if i > 0:
                prev_word = morphs[i-1][0]
                if prev_word in BOOSTER_DICT:
                    score *= BOOSTER_DICT[prev_word]
            if negation_flag:
                score *= -1

            total_score += score
            detected_words.append(f"  - [일반 단어] '{word}', 기본점수: {original_score}, 최종점수: {score:.2f}")
        
        # 5. 부정어 플래그 관리
        if word in NEGATION_LIST:
            negation_flag = True
        else:
            negation_flag = False
            
    # 최종 감정 분류
    print("3. 감지된 단어 및 점수 계산:")
    if not detected_words:
        print("  - 감지된 감정 단어 없음")
    else:
        for line in detected_words:
            print(line)

    print(f"4. 최종 점수: {total_score}")

    if total_score > 3:
        result = "행복"
    elif total_score > 0:
        result = "평온"
    elif total_score < -3:
        result = "분노"
    elif total_score < 0:
        result = "슬픔"
    else:
        result = "중립"
        
    print(f"5. 최종 감정: {result}")
    print("=" * 30)
    return result
