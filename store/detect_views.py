import os
import io
import tempfile
import environ
from roboflow import Roboflow
from rest_framework.views import APIView
from rest_framework.response import Response
from google.cloud import vision
import re
import time
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw  
import concurrent.futures # 병렬처리
from .models import Product


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
            # 원본 이미지 로드 + 축소본/640본 생성
            # -----------------------------------------------------------
            t0 = time.perf_counter()
            image_bytes = image_file.read()

            with Image.open(io.BytesIO(image_bytes)) as original_img:
                original_img = ImageOps.exif_transpose(original_img)
                original_img = original_img.convert("RGB")
                original_width, original_height = original_img.size

                resized_img = original_img.copy()
                resized_img.thumbnail((1280, 1280))

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

            db_products = list(Product.objects.values(
                "id",
                "display_name",
                "price",
                "category_name"
            ))

            detected_items = []
            used_names = set()

            # -----------------------------------------------------------
            # 1차 병렬 처리
            #  - 전체 OCR
            #  - 네임텍 detect
            #  ※ 빵 detect는 여기서 돌리지 않음 (필요할 때만)
            # -----------------------------------------------------------
            t1 = time.perf_counter()
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                future_fast_ocr = executor.submit(self._get_full_text_and_blocks, resized_path)
                future_rf_tag = executor.submit(rf_model_tag.predict, detect_640_path, confidence=40)

                fast_ocr = future_fast_ocr.result()
                res_tag = future_rf_tag.result().json()

            stage_times["parallel_inference"] = round(time.perf_counter() - t1, 4)

            # -----------------------------------------------------------
            # 1단계 - 전체 OCR 다이렉트 매칭
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
            # 2단계 - 네임텍 detect(640) -> 원본 crop -> OCR
            # -----------------------------------------------------------
            t3 = time.perf_counter()
            stage2_logs = []

            tag_predictions = sorted(
                res_tag.get("predictions", []),
                key=lambda p: float(p.get("confidence", 0)),
                reverse=True
            )

            # 너무 많은 후보 다 보지 말고 상위 3개만
            tag_predictions = tag_predictions[:3]

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

                        if raw_w < 300 or raw_h < 120:
                            ocr_base_img = raw_crop_img.resize((raw_w * 4, raw_h * 4), Image.LANCZOS)
                        elif raw_w < 500 or raw_h < 200:
                            ocr_base_img = raw_crop_img.resize((raw_w * 3, raw_h * 3), Image.LANCZOS)
                        else:
                            ocr_base_img = raw_crop_img.resize((raw_w * 2, raw_h * 2), Image.LANCZOS)

                        # 1차: raw만 OCR
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_crop_raw:
                            ocr_base_img.save(temp_crop_raw, format="PNG")
                            crop_raw_path = temp_crop_raw.name

                        try:
                            crop_ocr_raw = self._get_full_text_and_blocks(crop_raw_path)
                        finally:
                            if os.path.exists(crop_raw_path):
                                os.unlink(crop_raw_path)

                        raw_texts = self._collect_texts(crop_ocr_raw)
                        matching_prod, matched_text = match_best_product_from_candidates(db_products, raw_texts)

                        # raw OCR 실패시에만 전처리 OCR 추가
                        if not matching_prod:
                            ocr_preprocessed_img = preprocess_for_ocr(ocr_base_img.copy())

                            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_crop_pre:
                                ocr_preprocessed_img.save(temp_crop_pre, format="PNG")
                                crop_pre_path = temp_crop_pre.name

                            try:
                                crop_ocr_pre = self._get_full_text_and_blocks(crop_pre_path)
                            finally:
                                if os.path.exists(crop_pre_path):
                                    os.unlink(crop_pre_path)

                            pre_texts = self._collect_texts(crop_ocr_pre)
                            raw_texts.extend(pre_texts)
                            raw_texts = list(dict.fromkeys([t for t in raw_texts if t and t.strip()]))

                            matching_prod, matched_text = match_best_product_from_candidates(db_products, raw_texts)

                        final_price = 0
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
                                print(f"✅ [2단계] 네임텍 추론 성공: {matching_prod['display_name']}")
                                

                        else:
                            print(f"❌ [2단계] DB 매칭 실패: raw_texts={raw_texts}")

                    except Exception as e:
                        print(f"❌ [2단계] 예외 발생: {e}")

            stage_times["stage2_nametag"] = round(time.perf_counter() - t3, 4)

            # -----------------------------------------------------------
            # 3단계 - 진짜 필요할 때만 빵 detect
            # -----------------------------------------------------------
            t4 = time.perf_counter()
            stage3_logs = []

            res_bread = rf_model_bread.predict(resized_path, confidence=50).json()

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

    def _collect_texts(self, ocr_result):
        texts = []

        if not ocr_result:
            return texts

        for b in ocr_result.get("blocks", []):
            txt = b.get("text")
            if txt and txt.strip():
                texts.append(txt.strip())

        full_text = ocr_result.get("full_text")
        if full_text and full_text.strip():
            texts.append(full_text.strip())

        return list(dict.fromkeys(texts))

    def _get_full_text_and_blocks(self, image_path):
        """
        Vision 호출 1번만 사용
        """
        client = vision.ImageAnnotatorClient()

        with open(image_path, "rb") as f:
            content = f.read()

        image = vision.Image(content=content)

        response = client.document_text_detection(image=image)

        full_text = ""
        blocks = []

        if response.full_text_annotation:
            full_text = response.full_text_annotation.text.strip()

            for page in response.full_text_annotation.pages:
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