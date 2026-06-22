<template>
  <div class="app-container">
    <header class="app-header">
      <h1 class="main-title">우리 동네<br><span class="orange-text">마감 세일</span> 빵집</h1>
      <div class="tab-menu">
        <button @click="viewType = 'list'" :class="{ active: viewType === 'list' }">📋 리스트</button>
        <button @click="handleMapTab" :class="{ active: viewType === 'map' }">🗺️ 지도</button>
      </div>
    </header>

    <main v-if="viewType === 'list'" class="list-view">
      <div v-if="isFetching" class="empty-state">
        <div class="empty-state">
          <p> 🥐 주변의 맛있는 빵집을 찾고 있어요<span class="dots"></span></p>
        </div>
      </div>


      <template v-else>
        <template v-if="filteredShops.length > 0">
          <div v-for="shop in filteredShops" :key="shop.id" class="shop-card-wrapper">
            <div class="shop-main-info" @click="toggleAccordion(shop.id)">
              <div class="shop-text">
                <span class="badge">
                  {{ shop.distance < 1000 ? Math.round(shop.distance) + 'm' : (shop.distance / 1000).toFixed(1) + 'km'
                  }} </span>
                    <h2 class="shop-title">{{ shop.store_name }}</h2>
                    <p class="shop-sub">{{ shop.store_address }}</p>
              </div>
              <div class="sale-status">
                <span class="sale-count">{{ getAvailableCount(shop) }}개 세일</span>
                <div class="chevron-box">
                  <div class="chevron" :class="{ open: expandedShopId === shop.id }">▼</div>
                </div>
              </div>
            </div>

            <div v-show="expandedShopId === shop.id" class="bread-list-inside">
              <div v-for="item in shop.discounts" :key="item.id" class="bread-item">
                <span class="bread-emoji">🥐</span>
                <div class="bread-info">
                  <div class="name">{{ item.display_name }}</div>
                  <div class="price-row">
                    <span class="old">{{ item.original_price?.toLocaleString() }}원</span>
                    <span class="new">{{ item.discount_price?.toLocaleString() }}원</span>
                    <span class="stock-tag">재고 {{ item.count }}개</span>
                  </div>
                </div>

                <div class="cart-action-area" v-if="item.count > 0 && !item.is_sold_out">
                  <div class="quantity-control">
                    <button class="qty-btn" @click="changeTempCount(item, -1)">-</button>
                    <span class="qty-num">{{ item.tempCount || 1 }}</span>
                    <button class="qty-btn" @click="changeTempCount(item, 1)">+</button>
                  </div>
                  <button class="add-btn" @click="addToCart(shop, item)">담기</button>
                </div>
                <button v-else class="add-btn sold-out" disabled>품절</button>
              </div>
            </div>
          </div>
        </template>
        <div v-else class="empty-state">
          <p>주변에 현재 할인 중인 빵집이 없어요. 🏜️</p>
        </div>
      </template>
    </main>

    <main v-else class="map-view-layout">
      <div class="map-wrapper">
        <div id="kakao-map" class="kakao-map-canvas"></div>
      </div>
      <div class="map-info-panel">
        <div v-if="selectedShop" class="shop-card-wrapper inner-card">
          <div class="shop-main-info" @click="isMapPanelOpen = !isMapPanelOpen">
            <div class="shop-text">
              <span class="badge">
                {{ selectedShop.distance < 1000 ? Math.round(selectedShop.distance) + 'm' : (selectedShop.distance /
                  1000).toFixed(1) + 'km' }} </span>
                  <h2 class="shop-title">{{ selectedShop.store_name }}</h2>
                  <p class="shop-sub">{{ selectedShop.store_address }}</p>
            </div>
            <div class="sale-status">
              <span class="sale-count">{{ getAvailableCount(selectedShop) }}개 세일</span>
              <div class="chevron-box">
                <div class="chevron" :class="{ open: isMapPanelOpen }">▼</div>
              </div>
            </div>
          </div>

          <div v-show="isMapPanelOpen" class="bread-list-inside">
            <div v-for="item in selectedShop.discounts" :key="item.id" class="bread-item">
              <span class="bread-emoji">🥐</span>
              <div class="bread-info">
                <div class="name">{{ item.display_name }}</div>
                <div class="price-row">
                  <span class="old">{{ item.original_price?.toLocaleString() }}원</span>
                  <span class="new">{{ item.discount_price?.toLocaleString() }}원</span>
                  <span class="stock-tag">재고 {{ item.count }}개</span>
                </div>
              </div>

              <div class="cart-action-area" v-if="item.count > 0 && !item.is_sold_out">
                <div class="quantity-control">
                  <button class="qty-btn" @click="changeTempCount(item, -1)">-</button>
                  <span class="qty-num">{{ item.tempCount || 1 }}</span>
                  <button class="qty-btn" @click="changeTempCount(item, 1)">+</button>
                </div>
                <button class="add-btn" @click="addToCart(selectedShop, item)">담기</button>
              </div>
              <button v-else class="add-btn sold-out" disabled>품절</button>
            </div>
          </div>
        </div>
        <div v-else class="no-selection">📍 지도의 마커를 눌러 상세 정보를 확인하세요</div>
      </div>
    </main>
    <div class="floating-cart" @click="goToCart">
      🛒
      <div 
        v-if="totalCartCount > 0" 
        class="cart-badge" 
        :key="totalCartCount"
      >
        {{ totalCartCount }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/api';

const router = useRouter();
const isFetching = ref(true);
const viewType = ref('list');
const shops = ref([]);
const expandedShopId = ref(null);
const userCoords = ref({ lat: 37.359, lng: 127.105 }); // ✨ GPS 실패 시 백업용 기본값 (네이버 본사)
const selectedShop = ref(null);
const isMapPanelOpen = ref(false);
const cart = ref([]);

const refreshCart = () => {
  const saved = localStorage.getItem('todayCart');
  cart.value = saved ? JSON.parse(saved) : [];
};

const filteredShops = computed(() => {
  return shops.value.filter(shop => {
    if (!shop.discounts || shop.discounts.length === 0) return false;
    return shop.discounts.some(item => item.count > 0 && !item.is_sold_out);
  });
});

const totalCartCount = computed(() => cart.value.reduce((sum, item) => sum + item.quantity, 0));

const getAvailableCount = (shop) => {
  return shop.discounts?.filter(item => item.count > 0 && !item.is_sold_out).length || 0;
};

// 카카오맵 스크립트를 안전하게 로드하는 정석 함수
const loadKakaoMapScript = () => {
  return new Promise((resolve, reject) => {
    if (window.kakao && window.kakao.maps) {
      resolve();
      return;
    }

    const existingScript = document.getElementById('kakao-map-script');
    if (existingScript) {
      existingScript.addEventListener('load', () => resolve());
      return;
    }

    const script = document.createElement('script');
    script.id = 'kakao-map-script';
    // 💡 백엔드 환경변수에 저장해둔 카카오 키를 안전하게 주입합니다!
    script.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${import.meta.env.VITE_KAKAO_MAP_KEY}&libraries=services&autoload=false`;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('카카오맵 스크립트 로드 실패'));
    document.head.appendChild(script);
  });
};

// 🗺️ 지도 탭 클릭 시 실행되는 핵심 함수 (순서 최적화!)
const handleMapTab = async () => {
  viewType.value = 'map';
  selectedShop.value = null;
  await nextTick(); // Vue가 지도 div(#kakao-map)를 화면에 그릴 때까지 대기!

  try {
    await loadKakaoMapScript();
    // kakao.maps.load를 여기서 명확히 감싸서 실행 타이밍을 확보합니다!
    window.kakao.maps.load(() => {
      initKakaoMap();
    });
  } catch (error) {
    console.error("카카오 지도 로드 중 에러 발생:", error);
  }
};

// 🎨 진짜 지도를 그리는 함수
const initKakaoMap = () => {
  const container = document.getElementById('kakao-map');
  if (!container) return;

  // GPS 잡기 실패 시 채워진 기본값(네이버 본사) 또는 내 진짜 GPS 좌표가 여기 들어갑니다!
  const centerPos = new window.kakao.maps.LatLng(userCoords.value.lat, userCoords.value.lng);
  
  const map = new window.kakao.maps.Map(container, {
    center: centerPos,
    level: 3
  });

  // 빨간색 핀으로 "내 위치" 마커 찍기
  const myPosImage = new window.kakao.maps.MarkerImage(
    'https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/marker_red.png',
    new window.kakao.maps.Size(35, 35)
  );
  
  new window.kakao.maps.Marker({
    position: centerPos,
    image: myPosImage,
    map: map
  });

  // 주변 빵집 마커들 찍기
  filteredShops.value.forEach(shop => {
    const saleCount = getAvailableCount(shop);
    const shopPos = new window.kakao.maps.LatLng(shop.lat, shop.lng);

    const content = `
      <div onclick="handleMarkerClick(${shop.id})" style="position: relative; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; cursor: pointer;">
        <div style="width: 50px; height: 50px; background: white; border: 2.5px solid #222; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 30px; box-shadow: 4px 4px 0px #222; z-index: 1;">
          🥐
        </div>
        <div style="position: absolute; top: 0px; right: 0px; background: #ef4444; color: white; font-size: 12px; font-weight: 900; min-width: 22px; height: 22px; border-radius: 11px; border: 2px solid #222; display: flex; align-items: center; justify-content: center; z-index: 2; padding: 0 4px; box-sizing: border-box;">
          ${saleCount}
        </div>
      </div>
    `;

    new window.kakao.maps.CustomOverlay({
      position: shopPos,
      content: content,
      map: map,
      xAnchor: 0.5,
      yAnchor: 0.5
    });
  });

  // 글로벌 윈도우 함수로 마커 클릭 이벤트 매칭
  window.handleMarkerClick = (id) => {
    const found = shops.value.find(s => s.id === id);
    if (found) {
      selectedShop.value = found;
      isMapPanelOpen.value = true;
    }
  };
};

const changeTempCount = (item, delta) => {
  const current = item.tempCount || 1;
  const next = current + delta;
  if (next >= 1 && next <= (item.count || 99)) {
    item.tempCount = next;
  }
};

const addToCart = (shop, item) => {
  const quantity = item.tempCount || 1;
  const existing = cart.value.find(c => c.id === item.id);
  if (existing) {
    existing.quantity += quantity;
  } else {
    cart.value.push({
      id: item.id, 
      display_name: item.display_name,
      price: item.discount_price,
      quantity: quantity, 
      store_name: shop.store_name, 
      maxCount: item.count,
      store_address: shop.store_address,
      lat: shop.lat,   
      lng: shop.lng, 
    });
  }
  item.tempCount = 1;
  localStorage.setItem('todayCart', JSON.stringify(cart.value));
};

const goToCart = () => { router.push('/cart'); };
const toggleAccordion = (id) => { expandedShopId.value = expandedShopId.value === id ? null : id; };

const getDistance = (lat1, lon1, lat2, lon2) => {
  const R = 6371e3;
  const φ1 = lat1 * Math.PI / 180; const φ2 = lat2 * Math.PI / 180;
  const Δφ = (lat2 - lat1) * Math.PI / 180; const Δλ = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(Δφ / 2) * Math.sin(Δφ / 2) + Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
  return R * (2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a)));
};

// 📍 브라우저 GPS 위치 요청 함수 (HTTPS가 아니면 무조건 실패하고 넘어감!)
const fetchLocation = () => {
  return new Promise((resolve) => {
    if (!navigator.geolocation) {
      resolve(); // 지원 안하면 쿨하게 기본값 유지하고 리졸브!
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        // HTTPS 환경이거나 개발 로컬 환경일 때 작동!
        userCoords.value = { 
          lat: pos.coords.latitude, 
          lng: pos.coords.longitude 
        };
        resolve(); 
      },
      (err) => {
        // ⚠️ HTTP 상태의 AWS 서버에서는 이쪽으로 무조건 튕겨 나옵니다! 
        // 기존에 적어둔 { lat: 37.359, lng: 127.105 } 네이버 본사 좌표가 안전하게 보존됩니다.
        console.warn("위치 잡기 실패 (기본값 분당 네이버 본사 사용):", err.message);
        resolve(); 
      },
      { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
    );
  });
};

const fetchStores = async () => {
  try {
    const response = await api.get('/api/stores/');
    
    shops.value = response.data.map(shop => {
      // 위치 잡기 실패 시 네이버 본사 기준 거리 계산, 성공 시 진짜 내 위치 기준 거리 계산!
      const dist = getDistance(userCoords.value.lat, userCoords.value.lng, shop.lat, shop.lng);
      return {
        ...shop,
        distance: dist,
        discounts: (shop.discounts || []).map(d => ({ ...d, tempCount: 1 }))
      };
    }).sort((a, b) => a.distance - b.distance);
  } catch (e) {
    console.error("가게 정보 로드 실패:", e);
  }
};

onMounted(async () => {
  isFetching.value = true;
  await fetchLocation(); // 1. 위치 요청 (안 잡히면 자동으로 네이버 본사 고정!)
  await fetchStores();   // 2. 그 고정된 좌표 기반으로 가게 가져오기

  refreshCart();
  window.addEventListener('focus', refreshCart);
  isFetching.value = false;
});

onUnmounted(() => {
  window.removeEventListener('focus', refreshCart);
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&display=swap');

.app-container {
  background: #F4E2D0;
  min-height: 100vh;
  padding-bottom: 80px;
}

.loading-full-screen {
  position: fixed;
  inset: 0;
  background: #F4E2D0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-box {
  text-align: center;
}

.bread-bounce {
  font-size: 50px;
  animation: bounce 0.6s infinite alternate;
}

@keyframes bounce {
  from {
    transform: translateY(0);
  }

  to {
    transform: translateY(-20px);
  }
}

.loading-text {
  font-family: 'Black Han Sans';
  color: #3A5635;
  margin-top: 20px;
  line-height: 1.4;
}

.app-header {
  padding: 30px 20px 10px;
}

.main-title {
  font-family: 'Black Han Sans', sans-serif;
  font-size: 2.2rem;
  color: #3A5635;
  -webkit-text-stroke: 1px #222;
  text-shadow: 2px 2px 0px #222;
}

.orange-text {
  color: #D57B0E;
}

.tab-menu {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.tab-menu button {
  flex: 1;
  border: 2px solid #222;
  padding: 10px;
  border-radius: 4px;
  font-weight: 800;
  background: white;
  box-shadow: 3px 3px 0px #222;
}

.tab-menu button.active {
  background: #3A5635;
  color: white;
  transform: translate(1px, 1px);
  box-shadow: 1px 1px 0px #222;
}

.list-view {
  padding: 20px;
}

.map-view-layout {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 160px);
}

.map-wrapper {
  flex: 1.5;
  padding: 20px;
  box-sizing: border-box;
}

.kakao-map-canvas {
  width: 100%;
  height: 100%;
  border: 2px solid #222;
  box-shadow: 5px 5px 0px #222;
  border-radius: 4px;
}

.map-info-panel {
  flex: 1;
  background: #F4E2D0;
  border-top: 3px solid #222;
  padding: 20px;
  overflow-y: auto;
}

.shop-card-wrapper {
  background: white;
  border: 2px solid #222;
  margin-bottom: 25px;
  box-shadow: 5px 5px 0px #222;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
}

.inner-card {
  margin-bottom: 0;
}

.shop-main-info {
  padding: 18px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
  cursor: pointer;
}

.shop-text {
  flex: 1;
}

.sale-status {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 85px;
  justify-content: flex-end;
}

.chevron-box {
  width: 20px;
  display: flex;
  justify-content: center;
}

.loading-card {
  background: #fffcf9;
  border: 2px dashed #3A5635;
}

.inline-loading-text {
  font-weight: 800;
  color: #3A5635;
  animation: pulse 1.5s infinite;
}

.shop-title {
  font-size: 1.4rem;
  font-weight: 900;
  color: #3A5635;
  margin: 4px 0;
}

.badge {
  background: #3A5635;
  color: white;
  padding: 3px 8px;
  font-size: 11px;
  font-weight: 800;
}

.bread-list-inside {
  background: #fffcf9;
  border-top: 1px dashed #222;
  padding: 10px 20px;
}

.bread-item {
  display: flex;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #eee;
}

.bread-item:last-child {
  border-bottom: none;
}

.bread-info {
  flex: 1;
  margin-left: 10px;
}

.b-stock {
  font-size: 11px;
  color: #3A5635;
  font-weight: 800;
  margin-top: 4px;
}

.new {
  color: #ef4444;
  font-weight: 900;
  font-size: 14px;
}

.old {
  text-decoration: line-through;
  color: #999;
  font-size: 11px;
  margin-right: 6px;
}

.cart-action-area {
  display: flex;
  align-items: center;
  gap: 10px;
}

.quantity-control {
  display: flex;
  align-items: center;
  border: 2px solid #222;
  border-radius: 4px;
  overflow: hidden;
  height: 32px;
}

.qty-btn {
  width: 30px;
  height: 100%;
  border: none;
  background: #f0f0f0;
  font-weight: bold;
  cursor: pointer;
}

.qty-num {
  width: 30px;
  text-align: center;
  font-weight: 800;
  font-size: 14px;
  background: white;
  height: 100%;
  line-height: 32px;
  border-left: 2px solid #222;
  border-right: 2px solid #222;
}

.add-btn {
  background: #D57B0E;
  color: white;
  border: 2px solid #222;
  padding: 0 12px;
  height: 32px;
  font-weight: 800;
  font-size: 13px;
  box-shadow: 2px 2px 0px #222;
  cursor: pointer;
}

.add-btn.sold-out {
  background: #ccc;
  cursor: not-allowed;
  box-shadow: none;
}

.floating-cart { 
  position: fixed;
  right: 25px;
  bottom: 30px;
  width: 100px;
  height: 100px;
  background: #3A5635;
  border: 3px solid #222;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 4px 4px 0px #222;
  cursor: pointer;
  z-index: 999;
  font-size: 50px;
}

.cart-badge {
  position: absolute;
  top: -8px; 
  right: -8px;
  background: #D57B0E; 
  color: white;
  font-size: 20px;
  font-weight: 800;
  
  width: 32px;     
  height: 32px;       
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;   
  
  border: 3px solid #222;
  box-shadow: 2px 2px 0px #222;
  z-index: 10;

  animation: badge-pop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}

@keyframes badge-pop {
  0% { transform: scale(0.5); opacity: 0; }
  70% { transform: scale(1.4); } /* 살짝 과하게 커졌다가 */
  100% { transform: scale(1); opacity: 1; } /* 딱 정사이즈 */
}

.empty-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 0 20px;
  text-align: center;
  color: #3A5635;
  font-weight: 800;
  height: 300px;
  box-sizing: border-box;
}

.dots::after {
  content: '';
  animation: dot-play 1s infinite;
}

@keyframes dot-play {
  0% {
    content: '';
  }

  33% {
    content: '.';
  }

  66% {
    content: '..';
  }

  100% {
    content: '...';
  }
}

.chevron {
  transition: 0.3s;
  color: #3A5635;
  font-weight: bold;
}

.chevron.open {
  transform: rotate(180deg);
}

.stock-tag {
  font-size: 11px;
  background: #eee;
  color: #666;
  padding: 2px 6px;
  border-radius: 4px;
  margin-left: 8px;
  font-weight: bold;
}

.map-info-panel .shop-text {
  text-align: left;
}

.bread-marker-wrapper {
  position: relative;
  width: 60px;   
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}
</style>