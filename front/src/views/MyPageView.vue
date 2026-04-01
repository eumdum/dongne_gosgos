<template>
  <div class="mypage-container">
    <h2 class="mypage-title">🥐 나의 빵 기록</h2>

    <div v-if="isOwner" class="owner-choice-box">
      <button class="choice-btn pickup" @click="$router.push('/MyOrderView')">
        🛒 픽업 현황 확인 (사장님용)
      </button>
      <button class="choice-btn history active">
        📜 나의 빵 기록 (손님용)
      </button>
    </div>

    <div v-if="orders.length === 0" class="empty-msg">
      <p>아직 주문한 내역이 없어요! 🍞❓</p>
      <button class="go-home-btn" @click="$router.push('/')">빵 보러 가기</button>
    </div>

    <div v-else class="order-grid">
      <div v-for="order in orders" :key="order.id" class="order-card">
        <div class="card-header">
          <span class="shop-name">{{ order.shop_name }}</span>
          <span class="status-tag">{{ order.status }}</span>
        </div>

        <div class="card-body">
          <p class="items-text">{{ order.items_summary }}</p>
          <p class="price-text">결제금액: <strong>{{ order.total_price.toLocaleString() }}원</strong></p>
        </div>

        <div class="card-footer">
          <span class="date-text">주문일시: {{ formatDate(order.created_at) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/api';

const orders = ref([]);
const isOwner = ref(false);

const fetchOrders = async () => {
  try {
    const myNickname = localStorage.getItem('userName');
    const res = await api.get(`/api/my-orders/?nickname=${myNickname}`);
    orders.value = res.data;

    if (res.data.length > 0 && res.data[0].is_owner !== undefined) {
      isOwner.value = res.data[0].is_owner;
    }
  } catch (err) {
  }
};

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`;
};

onMounted(() => {
  fetchOrders();
});
</script>

<style scoped>
.mypage-container {
  padding: 15px 20px;
  background: #F4E2D0;
  min-height: 100vh;
}

.mypage-title {
  font-family: 'Black Han Sans', sans-serif;
  font-size: 4rem;
  margin-bottom: 40px;
  text-align: center;
  color: #3A5635;
  -webkit-text-stroke: 0.2px #202020;
}

.owner-choice-box {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-bottom: 35px;
}

.choice-btn {
  padding: 12px 20px;
  font-family: 'Black Han Sans', sans-serif;
  font-size: 1.1rem;
  border: 3px solid #222;
  border-radius: 10px;
  cursor: pointer;
  box-shadow: 4px 4px 0px #222;
  transition: 0.2s;
}

.choice-btn.pickup {
  background: #fff;
  color: #222;
}

.choice-btn.history.active {
  background: #3A5635;
  color: white;
}

.choice-btn:hover {
  transform: translate(-2px, -2px);
  box-shadow: 6px 6px 0px #222;
}

.order-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 25px;
  max-width: 1200px;
  margin: 0 auto;
}

.order-card {
  background: white;
  border: 3px solid #222;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 6px 6px 0px #222;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.shop-name {
  font-weight: 900;
  font-size: 1.3rem;
  color: #D57B0E;
}

.status-tag {
  background: #3A5635;
  color: white;
  padding: 4px 12px;
  border-radius: 50px;
  font-size: 0.85rem;
  font-weight: 800;
}

.items-text {
  font-size: 1.1rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 10px;
}

.price-text {
  font-size: 1rem;
  color: #666;
}

.card-footer {
  margin-top: 20px;
  padding-top: 10px;
  border-top: 1px dashed #ccc;
  font-size: 0.85rem;
  color: #888;
}

.empty-msg {
  text-align: center;
  margin-top: 100px;
  font-weight: 900;
  font-size: 1.2rem;
  color: #3A5635;
}

.go-home-btn {
  margin-top: 20px;
  background: #D57B0E;
  color: white;
  border: 3px solid #222;
  padding: 10px 25px;
  border-radius: 8px;
  font-weight: 900;
  cursor: pointer;
  box-shadow: 4px 4px 0px #222;
}
</style>