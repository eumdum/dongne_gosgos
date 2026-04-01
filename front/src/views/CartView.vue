<template>
  <div class="app-container">
    <header class="app-header">
      <button class="back-btn" @click="$router.push('/')">⬅️</button>
      <h1 class="main-title">장바구니</h1>
    </header>

    <main class="cart-main">
      <div v-if="cartItems.length === 0" class="empty-cart">
        <div class="empty-icon">🍞❓</div>
        <p>장바구니가 텅 비었어요.<br>맛있는 빵을 담으러 가볼까요?</p>
        <button class="go-home-btn" @click="$router.push('/')">빵 보러 가기</button>
      </div>

      <template v-else>
        <div class="cart-list">
          <div v-for="(item, index) in cartItems" :key="index" class="cart-item-card">
            <div class="item-shop-name">{{ item.shopName }}</div>
            <div class="item-info-row">
              <div class="item-name-group">
                <span class="item-emoji">🥐</span>
                <span class="item-name">{{ item.display_name }}</span>
              </div>
              <button class="remove-btn" @click="removeItem(index)">❌</button>
            </div>

            <div class="item-control-row">
              <div class="quantity-control">
                <button class="qty-btn" @click="updateQty(index, -1)">-</button>
                <span class="qty-num">{{ item.quantity }}</span>
                <button class="qty-btn" @click="updateQty(index, 1)">+</button>
              </div>
              <div class="item-price">{{ (item.price * item.quantity).toLocaleString() }}원</div>
            </div>
          </div>
        </div>

        <div class="total-section">
          <div class="pickup-time-picker">
            <p class="picker-label">⏰ 언제 픽업하러 오실 건가요?</p>
            <div class="picker-wheel-group">
              <select v-model="selectedAmPm" class="retro-select">
                <option v-for="opt in ampmOptions" :key="opt" :value="opt">{{ opt }}</option>
              </select>
              <select v-model="selectedHour" class="retro-select">
                <option v-for="opt in hourOptions" :key="opt" :value="opt">{{ opt }}</option>
              </select>
              <span class="picker-unit">시</span>
              <select v-model="selectedMinute" class="retro-select">
                <option v-for="opt in minuteOptions" :key="opt" :value="opt">{{ opt }}</option>
              </select>
              <span class="picker-unit">분 이후</span>
            </div>
          </div>

          <div class="total-row">
            <span>주문 금액</span>
            <span>{{ totalPrice.toLocaleString() }}원</span>
          </div>
          <div class="total-row main-total">
            <span>최종 결제 금액</span>
            <span class="orange-text">{{ totalPrice.toLocaleString() }}원</span>
          </div>

          <button class="order-btn" @click="orderNow">
            총 {{ totalCount }}개 결제하기
          </button>
        </div>
      </template>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/api';

const cartItems = ref([]);
const router = useRouter();

const now = new Date();
let currentHour = now.getHours();
const currentMinute = now.getMinutes();

const selectedAmPm = ref(currentHour >= 12 ? "오후" : "오전");

if (currentHour > 12) currentHour -= 12;
if (currentHour === 0) currentHour = 12;
const selectedHour = ref(String(currentHour));

const floorMinute = Math.floor(currentMinute / 10) * 10;
const selectedMinute = ref(String(floorMinute).padStart(2, '0'));

const ampmOptions = ["오전", "오후"];
const hourOptions = Array.from({ length: 12 }, (_, i) => String(i + 1));
const minuteOptions = ["00", "10", "20", "30", "40", "50"];

onMounted(() => {
  const savedCart = localStorage.getItem('todayCart');
  if (savedCart) {
    cartItems.value = JSON.parse(savedCart);
  }
});

const totalCount = computed(() => {
  return cartItems.value.reduce((sum, item) => sum + item.quantity, 0);
});

const totalPrice = computed(() => {
  return cartItems.value.reduce((sum, item) => sum + (item.price * item.quantity), 0);
});

const updateQty = (index, delta) => {
  const item = cartItems.value[index];
  const newQty = item.quantity + delta;

  if (newQty >= 1 && newQty <= (item.maxCount || 99)) {
    item.quantity = newQty;
    saveCart();
  }
};

const removeItem = (index) => {
  if (confirm('정말 삭제할까요?')) {
    cartItems.value.splice(index, 1);
    saveCart();
  }
};

const saveCart = () => {
  localStorage.setItem('todayCart', JSON.stringify(cartItems.value));
};


// 결제하기 버튼 
const orderNow = async () => {
  if (cartItems.value.length === 0) return alert("장바구니가 비어있어요!");
  const token = localStorage.getItem('userToken');
  if (!token) {
    alert("로그인 후 이용 가능합니다!");
    return router.push({ path: '/login', query: { redirect: router.currentRoute.value.fullPath } });
  }

  // 픽업 시간 체크 
  const now = new Date();
  const currentTotalMinutes = now.getHours() * 60 + now.getMinutes();
  let selectedHourNum = parseInt(selectedHour.value);
  if (selectedAmPm.value === "오후" && selectedHourNum < 12) selectedHourNum += 12;
  if (selectedAmPm.value === "오전" && selectedHourNum === 12) selectedHourNum = 0;
  const selectedTotalMinutes = selectedHourNum * 60 + parseInt(selectedMinute.value);

  if (selectedTotalMinutes < currentTotalMinutes) {
    alert("📢 픽업 시간을 다시 확인해 주세요. 🥐");
    return;
  }

  // 포트원 결제 불러오기
  if (!window.IMP) return alert("결제 모듈을 불러오지 못했습니다. 새로고침 해주세요!");
  const { IMP } = window;
  IMP.init(import.meta.env.VITE_IMP_KEY);

  const finalPickupTime = `${selectedAmPm.value} ${selectedHour.value}시 ${selectedMinute.value}분`;

  // 결제 시작
  IMP.request_pay({
    channelKey: import.meta.env.VITE_CHANNEL_KEY,
    pay_method: "card",
    merchant_uid: `order_${new Date().getTime()}`,
    name: "🥐 동네곳곳 빵 주문",
    amount: totalPrice.value,
    buyer_name: localStorage.getItem('userName') || '손님',
  }, async (rsp) => {
    if (rsp.success) {
      try {   // 결제 성공시 서버에 보낼 데이터
        const orderData = {
          pickup_number: String(Math.floor(Math.random() * 900) + 100),
          items_summary: cartItems.value.map(i => `${i.display_name} ${i.quantity}개`).join(', '),
          total_price: totalPrice.value,
          shop_name: cartItems.value[0].store_name || 
                     cartItems.value[0].shopName ||
                     cartItems.value[0].shop_name || 
                     "알 수 없는 가게",
          customer_name: localStorage.getItem('userName'),
          status: "결제완료",
          pickup_time: finalPickupTime,
          cartItems: cartItems.value.map(item => ({
            id: item.id, 
            quantity: item.quantity
          }))
        };

        // 서버에 주문 생성 요청
        await api.post('/api/create-order/', orderData);

        // 로컬스토리지에 마지막 주문 정보 저장 (픽업 페이지용)
        localStorage.setItem('lastOrder', JSON.stringify({
          orderId: orderData.pickup_number,
          storeName: orderData.shop_name,
          totalPrice: orderData.total_price,
          itemsSummary: orderData.items_summary,
          pickupTime: finalPickupTime,
          lat: cartItems.value[0].lat,
          lng: cartItems.value[0].lng,
          storeAddress: cartItems.value[0].store_address || "주소 정보 없음"
        }));

        cartItems.value = [];
        localStorage.removeItem('todayCart');
        alert("결제가 완료되었습니다! 픽업 페이지로 이동합니다. 🥳");
        router.push('/pickup');

      } catch (error) {
        alert("결제는 성공했으나, 서버에 주문을 저장하지 못했습니다.");
      }
    } else {
      alert(`결제 실패: ${rsp.error_msg}`);
    }
  }); 
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&display=swap');

.app-container {
  background: #F4E2D0;
  min-height: 100vh;
  padding: 20px;
  box-sizing: border-box;
}

.app-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 30px;
}

.back-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}

.main-title {
  font-family: 'Black Han Sans', sans-serif;
  font-size: 2rem;
  color: #3A5635;
  -webkit-text-stroke: 1px #222;
  text-shadow: 2px 2px 0px #222;
  margin: 0;
}

.cart-list {
  margin-bottom: 30px;
}

.cart-item-card {
  background: white;
  border: 2px solid #222;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 15px;
  box-shadow: 4px 4px 0px #222;
}

.item-shop-name {
  font-size: 12px;
  font-weight: 800;
  color: #D57B0E;
  margin-bottom: 5px;
}

.item-info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.item-name {
  font-size: 1.2rem;
  font-weight: 900;
  color: #222;
}

.remove-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
}

.item-control-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.quantity-control {
  display: flex;
  align-items: center;
  border: 2px solid #222;
  border-radius: 4px;
  height: 32px;
  overflow: hidden;
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
  width: 40px;
  text-align: center;
  font-weight: 800;
  background: white;
  line-height: 32px;
  border-left: 2px solid #222;
  border-right: 2px solid #222;
}

.item-price {
  font-weight: 900;
  font-size: 1.1rem;
  color: #3A5635;
}

.total-section {
  background: white;
  border: 3px solid #222;
  border-radius: 4px;
  padding: 20px;
  box-shadow: 6px 6px 0px #222;
}

.total-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-weight: 700;
  color: #666;
}

.main-total {
  border-top: 2px dashed #eee;
  pt: 15px;
  margin-top: 15px;
  font-size: 1.3rem;
  color: #222;
}

.orange-text {
  color: #D57B0E;
  font-weight: 900;
}

.order-btn {
  width: 100%;
  background: #3A5635;
  color: white;
  border: 2px solid #222;
  padding: 15px;
  border-radius: 4px;
  font-family: 'Black Han Sans';
  font-size: 1.2rem;
  margin-top: 20px;
  cursor: pointer;
  box-shadow: 4px 4px 0px #222;
  transition: 0.1s;
}

.order-btn:active {
  transform: translate(2px, 2px);
  box-shadow: 2px 2px 0px #222;
}

.empty-cart {
  text-align: center;
  padding: 100px 20px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.empty-cart p {
  font-weight: 800;
  color: #3A5635;
  line-height: 1.6;
  margin-bottom: 30px;
}

.go-home-btn {
  background: #D57B0E;
  color: white;
  border: 2px solid #222;
  padding: 12px 25px;
  border-radius: 4px;
  font-weight: 800;
  box-shadow: 4px 4px 0px #222;
  cursor: pointer;
}

.pickup-time-picker {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 2px dashed #eee;
}

.picker-label {
  font-weight: 900;
  font-size: 0.9rem;
  color: #3A5635;
  margin-bottom: 10px;
}

.picker-wheel-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.retro-select {
  padding: 8px 5px;
  border: 2px solid #222;
  border-radius: 4px;
  font-weight: 800;
  background: white;
  cursor: pointer;
  box-shadow: 2px 2px 0px #222;
}

.retro-select:focus {
  outline: none;
  background: #F4E2D0;
}

.picker-unit {
  font-weight: 900;
  font-size: 0.9rem;
  color: #222;
}
</style>