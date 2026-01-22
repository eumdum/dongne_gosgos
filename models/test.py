import os
import cv2  # 사진 편집용 (OpenCV)
from ultralytics import YOLO

# 1. 파일 경로 설정
model_path = 'ver3_best.pt'
image_path = 'test3.jpg'

# 2. 모델 로드
if not os.path.exists(model_path):
    print("❌ 모델 파일을 찾을 수 없습니다!")
else:
    model = YOLO(model_path)

    # 3. 사진 사이즈 자동 조절 (OpenCV 활용)
    # 원본 사진을 읽어옵니다.
    img = cv2.imread(image_path)
    
    if img is None:
        print("❌ 테스트할 사진을 찾을 수 없습니다!")
    else:
        # 사진을 640x640 정사각형으로 강제 변환합니다.
        img_resized = cv2.resize(img, (640, 640), interpolation=cv2.INTER_AREA)

        # 4. 예측 실행 (사이즈가 조절된 이미지를 전달)
        # conf=0.01로 설정해서 아주 작은 확신이라도 박스를 그리게 합니다.
        results = model.predict(source=img_resized, conf=0.01, save=True)

        # 5. 결과 분석
        for r in results:
            boxes = r.boxes
            print(f"🔍 검출된 빵 개수: {len(boxes)}개")
            for box in boxes:
                conf_score = box.conf.item()
                print(f" - 확신도: {conf_score:.2f}")

        print(f"📂 결과 확인 폴더: {results[0].save_dir}")