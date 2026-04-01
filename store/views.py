import os
import io
import tempfile
import requests
import base64
import environ
import random
from roboflow import Roboflow
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, viewsets, generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.exceptions import PermissionDenied
from roboflow import Roboflow  
from django.db.models import F
from .models import DiscountProduct, Product, Store, Order
from .serializers import StoreSerializer, DiscountProductSerializer, ProductSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.contrib.auth import get_user_model
from google.cloud import vision
import re
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw  
import concurrent.futures # 병렬처리!
import time

env = environ.Env()

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_key.json"

# ----------------------------------------------------------------
# 로보플로 모델
# ---------------------------------------------------------------
rf = Roboflow(api_key=env('ROBOFLOW_API_KEY'))

# 네임텍 전용 모델
rf_project_tag = rf.workspace().project("name-tag-hzadd")
rf_model_tag = rf_project_tag.version(2).model

rf_project_bread = rf.workspace().project("1_redbeen-bread")
rf_model_bread = rf_project_bread.version(5).model


def normalize_text(text):
    if not text:
        return ""
    text = str(text)
    text = text.replace(" ", "")
    text = re.sub(r'[^가-힣0-9]', '', text)
    return text.strip()

def deduplicate_items(items):
    seen = set()
    result = []

    for item in items:
        key = normalize_text(item["name"])
        if key and key not in seen:
            seen.add(key)
            result.append(item)

    return result

def match_best_product_from_candidates(db_products, raw_texts):
    """
    OCR에서 뽑힌 모든 텍스트 후보(raw_texts)를
    빵 사전(db_products)의 display_name과 전부 비교해서
    가장 잘 맞는 상품 1개를 반환
    """
    if not raw_texts:
        return None, None

    stopwords = {
        "best", "행사", "추천", "원", "판매", "가격", "할인", "정가",
        "kcal", "g"
    }

    best_product = None
    best_candidate = None
    best_score = 0

    for raw in raw_texts:
        if not raw:
            continue

        raw_clean = str(raw).strip()
        raw_norm = normalize_text(raw_clean)

        if not raw_norm:
            continue

        if len(raw_norm) < 2:
            continue

        if raw_norm.lower() in stopwords:
            continue

        for p in db_products:
            db_name = p.get("display_name", "")
            db_norm = normalize_text(db_name)

            if not db_norm:
                continue

            score = 0

            if raw_norm == db_norm:
                score = 100

            elif raw_norm in db_norm or db_norm in raw_norm:
                score = 80 + min(len(raw_norm), len(db_norm))

            else:
                common = sum(1 for ch in set(raw_norm) if ch in db_norm)
                score = common * 10

            if score > best_score:
                best_score = score
                best_product = p
                best_candidate = raw_clean

    if best_score < 20:
        return None, None

    return best_product, best_candidate

def refine_bread_name(candidates):
    if not candidates:
        return None

    garbage_patterns = [
        r'\d+g',
        r'\d+kcal',
        r'\d+%',
        r'BEST',
        r'best',
        r'행사',
        r'추천',
        r'원',
        r'파우더',
        r'밀크',
        r'초콜릿',
    ]

    clean_candidates = []

    for text in candidates:
        if not text:
            continue

        txt = str(text).strip()

        if re.fullmatch(r'[a-zA-Z]{1,5}', txt.replace(" ", "")):
            continue
        if re.fullmatch(r'[\d,]+', txt.replace(" ", "")):
            continue

        for pattern in garbage_patterns:
            txt = re.sub(pattern, '', txt, flags=re.IGNORECASE)

        txt = re.sub(r'[^가-힣0-9\s]', ' ', txt)
        txt = re.sub(r'\s+', ' ', txt).strip()

        if len(txt.replace(" ", "")) >= 2:
            clean_candidates.append(txt)

    if not clean_candidates:
        return None

    keywords = [
        '빵', '소라', '샌드위치', '크림', '바게트', '식빵',
        '도넛', '고로케', '쿠키', '피자', '브레드', '패스츄리',
        '크루아상', '치아바타', '베이글'
    ]

    keyword_hits = [c for c in clean_candidates if any(k in c for k in keywords)]
    if keyword_hits:
        return max(keyword_hits, key=lambda x: len(x.replace(" ", "")))

    return max(clean_candidates, key=lambda x: len(x.replace(" ", "")))


def match_product_by_name(db_products, detected_name):
    if not detected_name:
        return None

    detected_norm = normalize_text(detected_name)
    if not detected_norm:
        return None

    for p in db_products:
        db_norm = normalize_text(p["display_name"])
        if db_norm == detected_norm:
            return p

    for p in db_products:
        db_norm = normalize_text(p["display_name"])
        if db_norm and (db_norm in detected_norm or detected_norm in db_norm):
            return p

    best_product = None
    best_score = 0

    for p in db_products:
        db_norm = normalize_text(p["display_name"])
        if not db_norm:
            continue

        common = sum(1 for ch in set(detected_norm) if ch in db_norm)

        if common > best_score:
            best_score = common
            best_product = p

    if best_score >= 2:
        return best_product

    return None

def extract_price_candidates(candidates):
    prices = []

    if not candidates:
        return prices

    for text in candidates:
        clean_text = re.sub(r'[^\d,]', '', str(text))
        clean_text = clean_text.replace(",", "").strip()

        if re.fullmatch(r'\d{3,6}', clean_text):
            price = int(clean_text)
            if 500 <= price <= 20000:
                prices.append(price)

    return prices


def choose_best_price(raw_texts, db_price):
    """
    OCR에서 읽은 가격 후보들 중에서
    DB 가격과 가장 가까운 값을 선택.
    너무 차이가 크면 DB 가격 사용.
    """
    price_candidates = extract_price_candidates(raw_texts)

    if not price_candidates:
        return db_price

    best_price = min(price_candidates, key=lambda x: abs(x - db_price))

    if abs(best_price - db_price) > 3000:
        return db_price

    return best_price


def save_detection_debug_image(image_path, predictions, save_path):
    with Image.open(image_path) as img:
        img = img.convert("RGB")
        draw = ImageDraw.Draw(img)

        for pred in predictions:
            x = float(pred["x"])
            y = float(pred["y"])
            w = float(pred["width"])
            h = float(pred["height"])
            conf = float(pred.get("confidence", 0))
            cls = str(pred.get("class", ""))

            left = x - w / 2
            top = y - h / 2
            right = x + w / 2
            bottom = y + h / 2

            draw.rectangle([left, top, right, bottom], outline="red", width=3)
            draw.text((left, max(0, top - 15)), f"{cls} {conf:.2f}", fill="red")

        img.save(save_path)

def preprocess_for_ocr(img):
    from PIL import ImageOps, ImageEnhance, ImageFilter

    img = img.convert("L")
    img = ImageOps.autocontrast(img)
    img = ImageEnhance.Contrast(img).enhance(1.6)
    img = img.filter(ImageFilter.SHARPEN)
    img = img.point(lambda x: 255 if x > 145 else 0)

    return img.convert("RGB")


class ShelfScanningView(APIView):
    def post(self, request):
        total_start = time.perf_counter()
        resized_path = None
        original_path = None
        detect_640_path = None

        stage_times = {
            "image_prepare": 0,
            "parallel_inference": 0,
            "stage1_full_ocr": 0,
            "stage2_nametag": 0,
            "stage3_bread": 0,
            "total": 0,
        }

        try:
            image_file = request.FILES.get("image")
            if not image_file:
                return Response({"error": "사진이 없습니다."}, status=400)

            # -----------------------------------------------------------
            # 0. 원본 이미지 로드 + 축소본/640본 생성
            # -----------------------------------------------------------
            t0 = time.perf_counter()
            image_bytes = image_file.read()

            with Image.open(io.BytesIO(image_bytes)) as original_img:
                original_img = ImageOps.exif_transpose(original_img)
                original_img = original_img.convert("RGB")
                original_width, original_height = original_img.size

                resized_img = original_img.copy()
                resized_img.thumbnail((1280, 1280))
                resized_width, resized_height = resized_img.size

                detect_img_640 = original_img.resize((640, 640), Image.LANCZOS)

                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_resized:
                    resized_img.save(temp_resized, format="JPEG", quality=88)
                    resized_path = temp_resized.name

                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_640:
                    detect_img_640.save(temp_640, format="JPEG", quality=90)
                    detect_640_path = temp_640.name

                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_original:
                    original_img.save(temp_original, format="PNG")
                    original_path = temp_original.name

            stage_times["image_prepare"] = round(time.perf_counter() - t0, 4)

            # -----------------------------------------------------------
            # 1. 병렬 처리
            #  - 1단계 OCR: 1280 축소본
            #  - 2단계 네임택 detect: 640 강제 resize본
            #  - 3단계 빵 detect: 1280 축소본
            # -----------------------------------------------------------
            t1 = time.perf_counter()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future_rf_tag = executor.submit(rf_model_tag.predict, detect_640_path, confidence=40)
                future_rf_bread = executor.submit(rf_model_bread.predict, resized_path, confidence=50)
                future_fast_ocr = executor.submit(self._get_full_text_and_blocks, resized_path)

                res_tag = future_rf_tag.result().json()
                res_bread = future_rf_bread.result().json()
                fast_ocr = future_fast_ocr.result()

            stage_times["parallel_inference"] = round(time.perf_counter() - t1, 4)

            db_products = list(Product.objects.values(
                "id",
                "display_name", 
                "price", 
                "category_name"))
            detected_items = []
            used_names = set()

            # -----------------------------------------------------------
            # 2. 1단계 - 전체 OCR 다이렉트 매칭
            # -----------------------------------------------------------
            t2 = time.perf_counter()
            full_text_clean = normalize_text(fast_ocr["full_text"])

            for prod in db_products:
                db_name_norm = normalize_text(prod["display_name"])
                if db_name_norm and db_name_norm in full_text_clean:
                    if db_name_norm not in used_names:
                        detected_items.append({
                            "name": prod["display_name"],
                            "price": prod["price"],
                            "product_id": prod["id"],
                            "method": "direct_text_match"
                        })
                        used_names.add(db_name_norm)
                        print(f"✅ [1단계] 다이렉트 OCR 성공: {prod['display_name']}")

            stage_times["stage1_full_ocr"] = round(time.perf_counter() - t2, 4)

            # -----------------------------------------------------------
            # 3. 2단계 - 네임텍 detect(640) -> 원본 crop -> OCR
            # -----------------------------------------------------------
            t3 = time.perf_counter()
            stage2_logs = []

            if not detected_items:
                tag_predictions = sorted(
                    res_tag.get("predictions", []),
                    key=lambda p: float(p.get("confidence", 0)),
                    reverse=True
                )
                print("=== TAG PREDICTIONS ===", tag_predictions)

                scale_x = original_width / 640
                scale_y = original_height / 640

                with Image.open(original_path) as original_for_crop:
                    original_for_crop = original_for_crop.convert("RGB")

                    for pred in tag_predictions:
                        pred_class = str(pred.get("class", "")).strip().lower()
                        if pred_class not in ["nametag", "name_tag", "tag", "label", "price_tag"]:
                            continue

                        item_start = time.perf_counter()

                        try:
                            x = float(pred["x"])
                            y = float(pred["y"])
                            w = float(pred["width"])
                            h = float(pred["height"])
                            conf = float(pred.get("confidence", 0))

                            left_640 = int(x - w / 2)
                            top_640 = int(y - h / 2)
                            right_640 = int(x + w / 2)
                            bottom_640 = int(y + h / 2)

                            orig_left = int(left_640 * scale_x)
                            orig_top = int(top_640 * scale_y)
                            orig_right = int(right_640 * scale_x)
                            orig_bottom = int(bottom_640 * scale_y)

                            margin_x = int((orig_right - orig_left) * 0.25)
                            margin_y = int((orig_bottom - orig_top) * 0.25)

                            orig_left = max(0, orig_left - margin_x)
                            orig_top = max(0, orig_top - margin_y)
                            orig_right = min(original_width, orig_right + margin_x)
                            orig_bottom = min(original_height, orig_bottom + margin_y)

                            if orig_right <= orig_left or orig_bottom <= orig_top:
                                print("❌ [2단계] invalid crop box")
                                continue

                            raw_crop_img = original_for_crop.crop((orig_left, orig_top, orig_right, orig_bottom))
                            raw_w, raw_h = raw_crop_img.size

                            ocr_base_img = raw_crop_img.copy()
                            if raw_w < 300 or raw_h < 120:
                                ocr_base_img = ocr_base_img.resize((raw_w * 4, raw_h * 4), Image.LANCZOS)
                            elif raw_w < 500 or raw_h < 200:
                                ocr_base_img = ocr_base_img.resize((raw_w * 3, raw_h * 3), Image.LANCZOS)
                            else:
                                ocr_base_img = ocr_base_img.resize((raw_w * 2, raw_h * 2), Image.LANCZOS)

                            ocr_preprocessed_img = preprocess_for_ocr(ocr_base_img.copy())

                            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_crop_raw:
                                ocr_base_img.save(temp_crop_raw, format="PNG")
                                crop_raw_path = temp_crop_raw.name

                            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_crop_pre:
                                ocr_preprocessed_img.save(temp_crop_pre, format="PNG")
                                crop_pre_path = temp_crop_pre.name

                            try:
                                crop_ocr_raw = self._get_full_text_and_blocks(crop_raw_path)
                                crop_ocr_pre = self._get_full_text_and_blocks(crop_pre_path)

                                raw_texts = []

                                raw_texts.extend([b["text"] for b in crop_ocr_raw["blocks"] if b.get("text")])
                                if crop_ocr_raw["full_text"]:
                                    raw_texts.append(crop_ocr_raw["full_text"])

                                raw_texts.extend([b["text"] for b in crop_ocr_pre["blocks"] if b.get("text")])
                                if crop_ocr_pre["full_text"]:
                                    raw_texts.append(crop_ocr_pre["full_text"])

                                raw_texts = [t.strip() for t in raw_texts if t and t.strip()]
                                raw_texts = list(dict.fromkeys(raw_texts))

                            finally:
                                if os.path.exists(crop_raw_path):
                                    os.unlink(crop_raw_path)
                                if os.path.exists(crop_pre_path):
                                    os.unlink(crop_pre_path)

                            matching_prod, matched_text = match_best_product_from_candidates(db_products, raw_texts)

                            final_price=0
                            if matching_prod:
                                final_price = choose_best_price(raw_texts, matching_prod["price"])

                            stage2_logs.append({
                                "confidence": round(conf, 4),
                                "box_640": [left_640, top_640, right_640, bottom_640],
                                "box_original": [orig_left, orig_top, orig_right, orig_bottom],
                                "raw_texts": raw_texts,
                                "matched_text": matched_text,
                                "matched_product": matching_prod["display_name"] if matching_prod else None,
                                "price": final_price,
                                "time": round(time.perf_counter() - item_start, 4),
                            })

                            print(
                                f"[2단계] conf={conf:.3f}, matched_text={matched_text}, "
                                f"matched_product={matching_prod['display_name'] if matching_prod else None}, "
                                f"f_price={final_price}, raw_texts={raw_texts}"
                            )

                            if matching_prod:
                                normalized_name = normalize_text(matching_prod["display_name"])
                                if normalized_name not in used_names:

                                    detected_items.append({
                                        "name": matching_prod["display_name"],
                                        "price": final_price,
                                        "product_id": matching_prod["id"],
                                        "method": "nametag_inference"
                                    })
                                    used_names.add(normalized_name)

                                    print(
                                        f"✅ [2단계] 네임텍 추론 성공: {matching_prod['display_name']} / "
                                    )   
                            else:
                                print(f"❌ [2단계] DB 매칭 실패: raw_texts={raw_texts}")

                        except Exception as e:
                            print(f"❌ [2단계] 예외 발생: {e}")

            stage_times["stage2_nametag"] = round(time.perf_counter() - t3, 4)

            # -----------------------------------------------------------
            # 4. 3단계 - 비주얼 분류 fallback
            # -----------------------------------------------------------
            t4 = time.perf_counter()
            stage3_logs = []

            if not detected_items:
                for pred in res_bread.get("predictions", []):
                    pred_class = pred.get("class")
                    if pred_class == "nametag":
                        continue

                    stage3_logs.append({
                        "class": pred_class,
                        "confidence": round(float(pred.get("confidence", 0)), 4)
                    })

                    matching_prod = next(
                        (p for p in db_products if p["category_name"] == pred_class),
                        None
                    )

                    if matching_prod:
                        normalized_name = normalize_text(matching_prod["display_name"])
                        if normalized_name not in used_names:
                            detected_items.append({
                                "name": matching_prod["display_name"],
                                "price": matching_prod["price"],
                                "product_id": matching_prod["id"],
                                "method": "visual_classification"
                            })
                            used_names.add(normalized_name)
                            print(f"✅ [3단계] 비주얼 인식 성공: {matching_prod['display_name']}")

            stage_times["stage3_bread"] = round(time.perf_counter() - t4, 4)

            detected_items = deduplicate_items(detected_items)
            stage_times["total"] = round(time.perf_counter() - total_start, 4)

            print(f"🏁 최종 탐지 완료: {len(detected_items)}개")
            print("⏱ stage_times =", stage_times)

            return Response({
                "status": "success",
                "items": detected_items,
                "times": stage_times,
                "debug": {
                    "stage1_full_text": fast_ocr["full_text"],
                    "stage2": stage2_logs,
                    "stage3": stage3_logs,
                }
            })

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return Response({"error": str(e)}, status=500)

        finally:
            if resized_path and os.path.exists(resized_path):
                os.unlink(resized_path)
            if original_path and os.path.exists(original_path):
                os.unlink(original_path)
            if detect_640_path and os.path.exists(detect_640_path):
                os.unlink(detect_640_path)

    # --------------------------------------------------------
    # 내부 OCR 함수
    # --------------------------------------------------------
    def _get_full_text_and_blocks(self, image_path):
        """
        1) text_detection으로 전체 텍스트 확보
        2) document_text_detection으로 블록/문단 bbox 확보
        """
        client = vision.ImageAnnotatorClient()

        with open(image_path, "rb") as f:
            content = f.read()

        image = vision.Image(content=content)

        text_response = client.text_detection(image=image)
        full_text = ""
        if text_response.text_annotations:
            full_text = text_response.text_annotations[0].description.strip()

        doc_response = client.document_text_detection(image=image)
        blocks = []

        if doc_response.full_text_annotation:
            for page in doc_response.full_text_annotation.pages:
                for block in page.blocks:
                    for para in block.paragraphs:
                        para_words = []
                        para_vertices = []

                        for word in para.words:
                            word_text = "".join([s.text for s in word.symbols]).strip()
                            if not word_text:
                                continue

                            w_vertices = word.bounding_box.vertices
                            xs = [v.x for v in w_vertices]
                            ys = [v.y for v in w_vertices]

                            blocks.append({
                                "text": word_text,
                                "center": ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2),
                                "bbox": (min(xs), min(ys), max(xs), max(ys)),
                                "level": "word",
                            })

                            para_words.append(word_text)
                            para_vertices.extend(w_vertices)

                        if para_words and para_vertices:
                            xs = [v.x for v in para_vertices]
                            ys = [v.y for v in para_vertices]

                            blocks.append({
                                "text": " ".join(para_words).strip(),
                                "center": ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2),
                                "bbox": (min(xs), min(ys), max(xs), max(ys)),
                                "level": "paragraph",
                            })

        return {
            "full_text": full_text,
            "blocks": blocks
        }


class BulkProductSaveView(APIView):
    def post(self, request):
        user = request.user
        store = Store.objects.filter(owner=user).first()
        if not store:
            return Response({"error": "가게 정보를 찾을 수 없습니다."}, status=400)

        products_data = request.data.get('products', [])
        saved_count = 0

        for item in products_data:
            product_id = item.get('product') or item.get('product_id')
            if not product_id:
                return Response({"error": "product_id가 없습니다."}, status=400)
            
            orig_price = item.get('price', 0) 
            dis_price = item.get('discount_price', orig_price)

            DiscountProduct.objects.create(
                store=store,
                product_id=product_id,
                discount_price=dis_price,
                original_price=orig_price,
                count=item.get('count', 1),
                is_sold_out=(item.get('count', 1) <= 0),
            )
            saved_count += 1

        return Response({"status": "success", "message": f"{saved_count}개 빵 등록 완료! 🥐"})


# 재고 수량 조절
class UpdateCountView(APIView):
    def post(self, request, pk):
        try:
            product = DiscountProduct.objects.get(pk=pk)
            delta = int(request.data.get('delta', 0))
            product.count = max(0, product.count + delta)
            product.is_sold_out = (product.count == 0)
            product.save()
            return Response({
                "status": "success", 
                "count": product.count, 
                "is_sold_out": product.is_sold_out
                })
        except DiscountProduct.DoesNotExist:
            return Response({"error": "상품을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 할인목록 조회
class DiscountProductListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        store = get_my_store(request.user)
        products = DiscountProduct.objects.filter(store=store).order_by('-created_at')
        data = [{
            "id": p.id,
            "name": p.name,
            "original_price": p.original_price,
            "discount_price": p.discount_price,
            "count": p.count,
            "is_sold_out": p.is_sold_out,
            "created_at": p.created_at.strftime('%Y-%m-%d %H:%M'),
            "lat": p.store.lat if p.store else None,
            "lng": p.store.lng if p.store else None,
            "store_name": p.store.store_name if p.store else "알 수 없는 빵집"
        } for p in products]
        return Response(data)

# 상품 목록 조회 + 상품 등록
class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        store = get_my_store(self.request.user)
        return Product.objects.filter(store=store).order_by('-created_at')

    def perform_create(self, serializer):
        store = get_my_store(self.request.user)
        serializer.save(store=store)


# 상품 상세 조회 + 수정 + 삭제
class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        store = get_my_store(self.request.user)
        return Product.objects.filter(store=store)

def get_my_store(user):
    try:
        return user.store
    except Store.DoesNotExist:
        raise PermissionDenied("사장님 계정만 상품 관리가 가능합니다.")

# 가게 목록 및 등록
class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

# 할인 상품 목록 및 등록
class DiscountProductViewSet(viewsets.ModelViewSet):
    serializer_class = DiscountProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        store = get_my_store(self.request.user)
        return DiscountProduct.objects.filter(store=store).order_by('-created_at')

# 재고차감 로직
@api_view(['POST'])
def create_order(request):
    data = request.data
    
    order = Order.objects.create(
        pickup_number=data.get('pickup_number'),
        customer_name=data.get('customer_name', '손님1'),
        shop_name=data.get('shop_name'),
        items_summary=data.get('items_summary'),
        total_price=data.get('total_price'),
        status=data.get('status', '결제완료'),
        pickup_time=data.get('pickup_time')
    )
    
    # 2. 재고 차감
    cart_items = data.get('cartItems', []) 
    print(f"🛒 차감할 아이템 리스트: {cart_items}")

    for item in cart_items:
        product_id = item.get('id')
        qty = int(item.get('quantity', 0))

        if product_id and qty > 0:
            DiscountProduct.objects.filter(id=product_id).update(count=F('count') - qty)
            
            p = DiscountProduct.objects.filter(id=product_id).first()
            if p and p.count <= 0:
                p.count = 0
                p.is_sold_out = True
                p.save()
            
            print(f"✅ 상품ID {product_id} 업데이트 완료")

    return Response({"message": "주문 완료!", "order_id": order.id}, status=status.HTTP_201_CREATED)

# 알바용의 빵 등록 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_products(request):
    user = request.user
    store = Store.objects.filter(owner=user).first() 

    if not store:
        return Response({"error": "등록된 가게 정보가 없습니다."}, status=400)

    products_data = request.data.get('products', [])

    for data in products_data:
        product_id = data.get('product') or data.get('product_id')
        if not product_id:
            return Response({"error": "product_id가 없습니다."}, status=400)

        orig_p = data.get('original_price') # 원가
        disc_p = data.get('discount_price') # 할인가

        DiscountProduct.objects.create(
            store=store,
            product_id=product_id,
            discount_price=disc_p,
            original_price=orig_p,
            count=data.get('count', 1),
            is_sold_out=(int(data.get('count', 1)) <= 0)
        )
    return Response({"message": "지도 등록 완료!"})



# 해당 계정의 주문리스트
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_orders(request):
    user_nickname = request.query_params.get('nickname')
    
    if not user_nickname:
        return Response({"error": "닉네임이 필요해요!"}, status=400)

    orders = Order.objects.filter(customer_name=user_nickname).order_by('-created_at')
    
    if not orders.exists():
         print("❌ 이 사용자로 등록된 주문이 하나도 없어요!")

    order_list = []
    for order in orders:
        order_list.append({
            "id": order.id,
            "pickup_number": order.pickup_number, 
            "customer_name": order.customer_name,
            "items_summary": order.items_summary,
            "total_price": order.total_price,
            "status": order.status,
            "shop_name": order.shop_name,
            "created_at": order.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return Response(order_list)


# 알바용 전체 주문 목록 조회
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_orders(request):
    store = Store.objects.filter(owner=request.user).first()

    if not store:
        return Response({"error": "등록된 가게 정보가 없습니다."}, status=400)
    
    orders = Order.objects.filter(shop_name=store.store_name).order_by('-created_at')
    
    order_list = []
    for order in orders:
        order_list.append({
            "id": order.id,
            "pickup_number": order.pickup_number, 
            "customer_name": order.customer_name,
            "items_summary": order.items_summary,
            "total_price": order.total_price,
            "status": order.status,
            "shop_name": order.shop_name,
            "created_at": order.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return Response(order_list)

@api_view(['POST'])
def complete_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        order.status = "픽업완료" # 🌟 상태 변경!
        order.save()
        return Response({"message": "픽업이 완료되었습니다."})
    except Order.DoesNotExist:
        return Response({"error": "주문을 찾을 수 없습니다."}, status=404)

@api_view(['GET'])
def get_order_status(request, order_id):
    try:
        order = Order.objects.get(pickup_number=order_id)
        return Response({"status": order.status})
    except Order.DoesNotExist:
        return Response({"error": "주문 없음"}, status=404)

def test_upload_page(request):
    return render(request, 'test_upload.html')

User = get_user_model()
@api_view(['POST'])
def signup_view(request):
    data = request.data 
    
    try:
        u_name = data.get('username')
        u_pwd = data.get('password')
        u_role = data.get('role', 'user')
        u_nick = data.get('nickname')

        if User.objects.filter(username=u_name).exists():
            return Response({"error": "이미 사용 중인 아이디입니다."}, status=400)

        if not u_nick or u_nick.strip() == "":
            import random
            suffix = f"{random.randint(1000, 9999)}"
            u_nick = f"사장님{suffix}" if u_role == 'owner' else f"손님{suffix}"

        user = User.objects.create_user(
            username=u_name, 
            password=u_pwd, 
            first_name=u_nick
        )

        if u_role == 'owner':
            Store.objects.create(
                owner=user, 
                store_name=data.get('store_name', ''), 
                store_address=data.get('store_address', ''), 
                lat=data.get('lat'), 
                lng=data.get('lng'),
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "회원가입 및 로그인 성공!",
            "access": str(refresh.access_token),
            "nickname": u_nick,
            "username": u_name,
            "role": u_role
        }, status=201)

    except Exception as e:
        print(f"회원가입 에러 발생: {str(e)}") # 서버 터미널에서 에러 확인용
        return Response({"error": "회원가입 처리 중 오류가 발생했습니다."}, status=400)


@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user:
        refresh = RefreshToken.for_user(user)

        user_role = 'owner' if '사장님' in user.first_name else 'user'

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'nickname': user.first_name if user.first_name else user.username,
            'role': user_role,
            'username': user.username
        }, status=status.HTTP_200_OK)
    else:
        return Response({"error": "아이디 또는 비밀번호가 틀렸습니다."}, status=status.HTTP_401_UNAUTHORIZED)