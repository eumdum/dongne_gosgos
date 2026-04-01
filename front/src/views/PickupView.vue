<template>
  <div class="pickup-container">
    <header class="pickup-header">
      <button @click="$router.push('/')" class="back-home">🏠</button>
      <h2 class="main-title">예약 현황</h2>
    </header>

    <main v-if="orderInfo && orderInfo.storeName" class="pickup-content">
      <div class="order-number-card">
        <p class="guide-text">🥐 이 번호를 매장직원에게 보여주세요🥐</p>
        <p class="card-label">PICKUP NUMBER</p>
        <h1 class="p-number">{{ orderInfo.orderId }}</h1>
        <p>⏰ <strong>오늘 {{ orderInfo.pickupTime }}</strong>까지 방문해주세요! ⏰</p>
      </div>

      <div class="map-section">
        <h3 class="section-title">📍 매장 위치</h3>
        <div v-if="isMapLoading" class="map-loading-box">
          <div class="spinner">🥨</div>
          <p>지도를 굽는 중입니다...</p>
        </div>
        <div :class="{ 'map-hidden': isMapLoading }">
          <div id="pickup-map" class="small-map"></div>
          <p class="shop-addr">{{ orderInfo.storeAddress }}</p>
          <a :href="getKakaoNaviUrl()" target="_blank" class="nav-button">
            🚀 지금 내 위치에서 바로 길찾기 🚀
          </a>
        </div>
      </div>

      <div class="order-detail-card">
        <h3 class="section-title">🥐 주문 내역</h3>
        <div class="p-item">
          <span class="p-item-name">{{ orderInfo.itemsSummary || '상세 내역 없음' }}</span>
        </div>
        <div class="total-price-row">
          <span>총 결제금액</span>
          <strong>{{ (orderInfo.totalPrice || 0).toLocaleString() }}원</strong>
        </div>
      </div>
    </main>

    <main v-else class="empty-pickup">
      <div class="empty-icon">🍞❓</div>
      <p class="empty-msg">
        현재 예약된 내역이 없어요!<br>
        맛있는 빵을 담으러 가볼까요?
      </p>
      <button class="go-home-btn" @click="$router.push('/')">빵 보러 가기</button>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/api';

const router = useRouter();
const checkTimer = ref(null);
const myLat = ref(37.5668);
const myLng = ref(126.9786);
const isMapLoading = ref(true);

const orderInfo = ref({
  orderId: '',
  storeName: '',
  storeAddress: '',
  itemsSummary: '',
  totalPrice: 0,
  pickupTime: '',
  lat: 37.5668,
  lng: 126.9786
});

const getKakaoNaviUrl = () => {
  const sLat = myLat.value;
  const sLng = myLng.value;
  const eLat = orderInfo.value.lat;
  const eLng = orderInfo.value.lng;
  const eName = encodeURIComponent(orderInfo.value.storeName || '빵집');

  return `https://map.kakao.com/link/from/내위치,${sLat},${sLng}/to/${eName},${eLat},${eLng}`;
};

const renderFinalMap = (container, centerCoords, userLat, userLng) => {
  if (!window.kakao || !window.kakao.maps) return;

  const map = new window.kakao.maps.Map(container, {
    center: centerCoords,
    level: 3
  });

  const myPosImage = new window.kakao.maps.MarkerImage(
    'https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/marker_red.png',
    new window.kakao.maps.Size(35, 35)
  );
  new window.kakao.maps.Marker({
    position: new window.kakao.maps.LatLng(userLat, userLng),
    image: myPosImage,
    map: map
  });

  new window.kakao.maps.CustomOverlay({
    position: centerCoords,
    content: `
      <div style="position: relative; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center;">
        <div style="width: 50px; height: 50px; background: white; border: 2.5px solid #222; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 30px; box-shadow: 4px 4px 0px #222;">
          🥐
        </div>
      </div>
    `,
    map: map,
    yAnchor: 1
  });

  setTimeout(() => {
    isMapLoading.value = false;
  }, 500);
};

const loadMapWithFreshGPS = () => {
  navigator.geolocation.getCurrentPosition((position) => {
    const userLat = position.coords.latitude;
    const userLng = position.coords.longitude;

    myLat.value = userLat;
    myLng.value = userLng;

    window.kakao.maps.load(() => {
      const container = document.getElementById('pickup-map');
      if (!container) return;

      const targetLat = orderInfo.value.lat;
      const targetLng = orderInfo.value.lng;

      renderFinalMap(
        container,
        new window.kakao.maps.LatLng(targetLat, targetLng),
        userLat,
        userLng
      );
    });
  }, (err) => {
    isMapLoading.value = false;
    // 실패해도 빵집 지도는 띄워주기
    window.kakao.maps.load(() => {
      const container = document.getElementById('pickup-map');
      if (container) renderFinalMap(container, new window.kakao.maps.LatLng(orderInfo.value.lat, orderInfo.value.lng), myLat.value, myLng.value);
    });
  }, { enableHighAccuracy: true });
};

const checkStatus = async () => {
  if (!orderInfo.value.orderId) return;
  try {
    const res = await api.get(`/api/order-status/${orderInfo.value.orderId}/`);
    if (res.data && res.data.status === '픽업완료') {
      clearInterval(checkTimer.value);
      alert("🎉 빵 포장이 완료되었습니다!");
      localStorage.removeItem('lastOrder');
      router.push('/pickup-com');
    }
  } catch (err) { /* 무시 */ }
};

onMounted(() => {
  const saved = localStorage.getItem('lastOrder');
  if (saved) {
    const data = JSON.parse(saved);
    orderInfo.value = {
      ...data,
      lat: Number(data.lat || data.latitude) || 37.5668,
      lng: Number(data.lng || data.longitude) || 126.9786,
      storeName: data.storeName || data.shop_name,
      storeAddress: data.storeAddress || data.shop_address
    };

    nextTick(() => {
      const checkInterval = setInterval(() => {
        const mapContainer = document.getElementById('pickup-map');
        if (window.kakao && window.kakao.maps && mapContainer) {
          clearInterval(checkInterval);
          loadMapWithFreshGPS();
        } else if (!document.getElementById('kakao-map-script')) {
          const script = document.createElement('script');
          script.id = 'kakao-map-script';
          script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${import.meta.env.VITE_KAKAO_MAP_KEY}&autoload=false&libraries=services`;          document.head.appendChild(script);
        }
      }, 500);
    });
  }
  checkTimer.value = setInterval(checkStatus, 3000);
});

onUnmounted(() => { if (checkTimer.value) clearInterval(checkTimer.value); });
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&display=swap');

.pickup-container {
  background: #F4E2D0;
  min-height: 100vh;
  padding: 20px;
  box-sizing: border-box;
}

.pickup-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 25px;
}

.back-home {
  background: white;
  border: 2px solid #222;
  border-radius: 4px;
  padding: 5px 10px;
  cursor: pointer;
  box-shadow: 2px 2px 0px #222;
}

.main-title {
  font-family: 'Black Han Sans', sans-serif;
  font-size: 1.8rem;
  color: #3A5635;
  margin: 0;
}

.order-number-card {
  background: white;
  border: 3px solid #222;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  margin-bottom: 20px;
  box-shadow: 5px 5px 0px #222;
}

.card-label {
  font-size: 1.3rem;
  font-weight: 1000;
}

.p-number {
  font-family: 'Black Han Sans', sans-serif;
  font-size: 6rem;
  color: #3A5635;
  margin: 10px 0;
}

.map-section {
  background: white;
  border: 2px solid #222;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  box-shadow: 5px 5px 0px #222;
}

.small-map {
  width: 100%;
  height: 200px;
  border: 2px solid #222;
  border-radius: 4px;
  margin-bottom: 10px;
}

.nav-button {
  display: block;
  text-align: center;
  background: #D57B0E;
  color: white;
  text-decoration: none;
  padding: 12px;
  border: 2px solid #222;
  border-radius: 4px;
  font-weight: 900;
  box-shadow: 3px 3px 0px #222;
}

.order-detail-card {
  background: white;
  border: 2px solid #222;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  box-shadow: 5px 5px 0px #222;
}

.total-price-row {
  border-top: 2px dashed #ddd;
  padding-top: 10px;
  margin-top: 10px;
  display: flex;
  justify-content: space-between;
  font-weight: 900;
  color: #3A5635;
}

.time-card {
  background: #3A5635;
  color: white;
  border: 2px solid #222;
  border-radius: 8px;
  padding: 15px;
  text-align: center;
  box-shadow: 4px 4px 0px #222;
  font-weight: 700;
}

.empty-pickup {
  text-align: center;
  padding-top: 50px;
}

.empty-card {
  background: white;
  border: 3px solid #222;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 6px 6px 0px #222;
}

.go-shopping-btn {
  background: #3A5635;
  color: white;
  padding: 10px 20px;
  border: 2px solid #222;
  border-radius: 4px;
  cursor: pointer;
}

.map-loading-box {
  width: 100%;
  height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #fff;
  border: 2px dashed #222;
  border-radius: 4px;
}

.spinner {
  font-size: 2.5rem;
  margin-bottom: 10px;
  animation: rotate_pretzel 2s linear infinite;
}

@keyframes rotate_pretzel {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

.map-loading-box p {
  font-family: 'Black Han Sans', sans-serif;
  font-size: 0.9rem;
  color: #3A5635;
}

.map-hidden {
  visibility: hidden;
  height: 0;
  overflow: hidden;
}

.pickup-container {
  background: #F4E2D0;
  min-height: 100vh;
  padding: 20px;
}

.empty-pickup {
  text-align: center;
  padding: 100px 20px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  display: block;
}

.empty-msg {
  font-weight: 800;
  color: #3A5635;
  line-height: 1.6;
  margin-bottom: 30px;
  font-size: 1.1rem;
}

.go-home-btn {
  background: #D57B0E;
  color: white;
  border: 3px solid #222;
  padding: 12px 30px;
  border-radius: 4px;
  font-weight: 900;
  box-shadow: 6px 6px 0px #222;
  cursor: pointer;
  transition: 0.1s;
}

.go-home-btn:active {
  transform: translate(4px, 4px);
  box-shadow: 0px 0px 0px #222;
}
</style>