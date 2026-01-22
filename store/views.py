# # from rest_framework import viewsets, status, parsers
# # from rest_framework.response import Response
# # from rest_framework.decorators import action
# # from .models import Store
# # from .serializers import StoreSerializer
# # from .vision_analyzer import analyze_product_image
# # import traceback

# # class StoreViewSet(viewsets.ModelViewSet):
# #     queryset = Store.objects.all()
# #     serializer_class = StoreSerializer
# #     parser_classes = (parsers.MultiPartParser, parsers.FormParser)

# #     # [1] 최종 저장: '등록 확정하기' 버튼을 눌렀을 때 실행
# #     # 사장님이 모달에서 확인/수정한 최종 데이터가 들어옵니다.
# #     def perform_create(self, serializer):
# #         # 저장할 데이터 미리보기
# #         final_item = serializer.validated_data.get('item', '알 수 없음')
# #         final_price = serializer.validated_data.get('price', 0)

# #         # 실제 DB 저장
# #         serializer.save()

# #         # [요청하신 부분] 저장 버튼을 눌렀을 때 비로소 결과 로그를 띄웁니다.
# #         print("\n" + "═" * 50)
# #         print(f"🤖 [최종 데이터 확정] 상품명: {final_item} | 가격: {final_price}")
# #         print("✅ [DB 저장 성공] 매대 등록이 완료되었습니다.")
# #         print("═" * 50 + "\n")

# #     # [2] 단순 분석: 사진을 선택했을 때 실행 (저장 X)
# #     @action(detail=False, methods=['post'], url_path='analyze')
# #     def analyze(self, request):
# #         # 여기서는 로그를 최소화하여 '아직 저장 안 됨'을 암시합니다.
# #         print(f"🔍 [미리보기] 사장님이 사진({request.FILES.get('image')})을 확인하고 있습니다...")
        
# #         image = request.FILES.get('image')
# #         if not image:
# #             return Response({"error": "이미지가 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

# #         try:
# #             # AI 분석 수행
# #             result = analyze_product_image(image)
# #             # 결과는 프론트엔드(모달)로만 조용히 보냅니다.
# #             return Response(result, status=status.HTTP_200_OK)
# #         except Exception as e:
# #             print(f"❌ [분석 에러] {str(e)}")
# #             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# #     def create(self, request, *args, **kwargs):
# #         try:
# #             return super().create(request, *args, **kwargs)
# #         except Exception as e:
# #             print("\n🔥 [서버 내부 에러 발생] 🔥")
# #             print(traceback.format_exc())
# #             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
# import os
# from django.shortcuts import render
# from ultralytics import YOLO
# from django.conf import settings

# def predict_bread(request):
#     # 1. 모델 파일 경로 설정
#     model_path = os.path.join(settings.BASE_PATH, 'models', 'best.pt')
    
#     # 2. YOLO 모델 로드
#     model = YOLO(model_path)
    
#     # 3. 테스트용 이미지 추론 (나중에 사용자가 업로드한 이미지로 바꿀 거야)
#     # 지금은 일단 모델이 잘 로드되는지만 확인하는 단계!
#     print("모델 로드 성공!")
    
#     return render(request, 'predict.html') # 아직 페이지 안 만들었어도 
import requests
import base64
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ProductDetectionView(APIView):
    def post(self, request):
        file = request.FILES.get('image')
        if not file:
            return Response({"error": "사진이 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. 이미지를 Base64로 안전하게 인코딩
        image_bytes = file.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

        # 2. 로보플로우 API 호출 (주소와 키를 다시 확인하세요!)
        # ⚠️ 여기서 'redbean-bread/3' 부분을 로보플로우 웹 주소창에 있는 것과 똑같이 쓰세요!
        project_id = "redbean-bread" 
        version = "5"
        url = f"https://detect.roboflow.com/1_redbeen-bread/5"
        
        params = {
            "api_key": "GduHmcxbyeKZQjHOdTT6",
            "confidence": "0.1",  # 👈 10%만 넘어도 무조건 다 알려달라고 설정!
            "overlap": "30"
        }

        try:
            # 3. API 요청 (헤더에 Content-Type 명시)
            response = requests.post(
                url, 
                params=params, 
                data=image_base64,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            data = response.json()

            # 디버깅용: 서버 터미널에 로보플로우가 보내준 생(Raw) 데이터를 출력해봅니다.
            print("Roboflow Raw Data:", data)

            detected_items = []
            if "predictions" in data:
                for pred in data["predictions"]:
                    detected_items.append({
                        "name": pred["class"],
                        "confidence": round(pred["confidence"], 2)
                    })

            return Response({
                "status": "success",
                "count": len(detected_items),
                "items": detected_items
            })

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
def test_upload_page(request):
    return render(request, 'test_upload.html')