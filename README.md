# 🥐 동네곳곳

> 버려질 수 있는 빵을 할인 판매로 연결하는 위치 기반 서비스

---

## 📌 소개

동네 베이커리의 남은 빵을 할인 판매로 연결하여

* 사장님은 재고를 줄이고
* 사용자는 저렴하게 구매할 수 있도록 만든 서비스입니다.

---

## 🖼️ 화면

### 메인 화면

<p align="center">
  <img src="./images/main_1.PNG" width="300"/>
  <img src="./images/main_2.PNG" width="300"/>
  <img src="./images/main_3.PNG" width="300"/>
</p>

### 장바구니

<p align="center">
  <img src="./images/cart_1.PNG" width="300"/>
</p>

### 결제

<p align="center">
  <img src="./images/pay_1" width="300"/>
</p>

### 주문서

<p align="center">
  <img src="./images/order_1" width="300"/>
</p>

### 빵 인식 (OCR + AI)

<p align="center">
  <img src="./images/ocr_1" width="300"/>
  <img src="./images/ocr_2" width="300"/>
</p>

---

## ⚙️ 주요 기능

* 위치 기반 매장 조회
* 할인 빵 리스트 제공
* 장바구니 및 주문 기능
* 재고 관리 및 자동 차감
* OCR + 객체 탐지 기반 빵 인식

---

## 🧠 핵심 구현

### 1. 빵 인식 파이프라인

```
OCR → 네임택 탐지 → 이미지 분류
```

### 2. Product 기반 데이터 구조

* 상품명 / OCR / AI 분류를 하나의 기준(Product)으로 통일

```python
display_name = serializers.CharField(source='product.display_name', read_only=True)
```

---

## 🧱 기술 스택

* Backend: Django, DRF
* Frontend: Vue3
* AI: Google Vision OCR, Roboflow

---

## 🚀 실행 방법

```bash
# backend
python manage.py runserver

# frontend
npm install
npm run dev
```
