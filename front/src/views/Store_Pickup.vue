<template>
  <div class="store-pickup">
    <header>
      <div class="header-left">
        <router-link to="/main" class="back-btn">←</router-link>
        <h1>👨‍🍳 사장님 전용 대시보드</h1>
      </div>
      <div class="header-right">
        <button @click="toggleAlarm" class="alarm-btn" :class="{ 'alarm-on': isAlarmEnabled }">
          {{ isAlarmEnabled ? '🔔 알림 켜짐' : '🔕 알림 꺼짐' }}
        </button>
        <button @click="fetchOrders" class="refresh-btn">새로고침 🔄</button>
      </div>
    </header>

    <div class="order-grid">
      <div v-for="order in orders" :key="order.id" class="order-card"
        :class="{ 'status-complete': order.status === '픽업완료' }" @click="selectedOrder = order">
        <div class="card-header">
          <span class="pickup-num">#{{ order.pickup_number }}</span>
          <span class="status">{{ order.status }}</span>
        </div>
        <div class="card-body">
          <p class="summary">{{ order.items_summary }}</p>
          <span class="time">{{ order.created_at }}</span>
        </div>
      </div>
    </div>

    <div v-if="selectedOrder" class="modal-overlay" @click="selectedOrder = null">
      <div class="modal-content" @click.stop>
        <h2>주문 상세 확인</h2>
        <div class="detail-box">
          <p><strong>주문 번호:</strong> <span class="highlight">{{ selectedOrder.pickup_number }}</span></p>
          <p><strong>주문자:</strong> {{ selectedOrder.customer_name }}</p>
          <hr>
          <p><strong>상세 품목:</strong></p>
          <div class="items">{{ selectedOrder.items_summary }}</div>
          <p class="price"><strong>결제 금액:</strong> {{ selectedOrder.total_price.toLocaleString() }}원</p>
        </div>

        <div class="modal-buttons">
          <button v-if="selectedOrder.status !== '픽업완료'" @click="completeOrder(selectedOrder.id)"
            class="btn-complete">픽업 완료 처리</button>
          <button @click="selectedOrder = null" class="btn-close">닫기</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import api from '@/api';

const orders = ref([]);
const selectedOrder = ref(null);
const isAlarmEnabled = ref(false);
const lastOrderId = ref(null);
let timer = null;

// 알림음 재생 함수
const playNotification = () => {
  if (!isAlarmEnabled.value) return;
  const audio = new Audio('/notification.mp3'); // public 폴더서 알림음 수정 가능
  audio.play().catch(e => console.log("소리 재생 실패:", e));
};

const toggleAlarm = () => {
  isAlarmEnabled.value = !isAlarmEnabled.value;
  if (isAlarmEnabled.value) {
    alert("새 주문이 들어오면 띵동! 소리가 납니다. 🥐");
  }
};

// 주문 목록 가져오기
const fetchOrders = async () => {
  try {
    const response = await api.get('/api/get-orders/');
    const newOrders = response.data;

    if (newOrders.length > 0) {
      const latestId = newOrders[0].id;

      if (lastOrderId.value && latestId !== lastOrderId.value) {
        playNotification();
      }
      lastOrderId.value = latestId;
    }

    orders.value = newOrders;
  } catch (error) {
  }
};

// 픽업 완료 처리
const completeOrder = async (orderId) => {
  if (confirm("손님이 빵을 가져가셨나요? 픽업 완료 처리합니다!")) {
    try {
      await api.post(`/api/complete-order/${orderId}/`);
      alert("✅ 처리가 완료되었습니다. 🥐");
      selectedOrder.value = null;
      fetchOrders();
    } catch (error) {
      alert("상태 업데이트 중 오류가 발생했습니다.");
    }
  }
};

onMounted(() => {
  fetchOrders();
  timer = setInterval(fetchOrders, 30000);
});

onUnmounted(() => {
  if (timer) {
    clearInterval(timer);
    timer = null;
  }
});
</script>

<style scoped>
.back-btn {
  text-decoration: none;
  font-size: 1.5rem;
  color: #333;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.store-pickup {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.order-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  margin-top: 20px;
}

.order-card {
  border: 2px solid #ddd;
  padding: 15px;
  border-radius: 12px;
  cursor: pointer;
  transition: 0.3s;
}

.order-card:hover {
  border-color: #ffb84d;
  transform: translateY(-5px);
}

.status-complete {
  opacity: 0.5;
  background-color: #f9f9f9;
}

.pickup-num {
  font-size: 1.5rem;
  font-weight: bold;
  color: #d35400;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 20px;
  width: 90%;
  max-width: 400px;
}

.highlight {
  color: #e67e22;
  font-size: 1.2rem;
  font-weight: bold;
}

.btn-complete {
  background: #27ae60;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  margin-right: 10px;
  cursor: pointer;
}

.btn-close {
  background: #eee;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
}

.header-right {
  display: flex;
  gap: 10px;
}

.alarm-btn {
  background: #666;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
}

.alarm-btn.alarm-on {
  background: #D57B0E;
}
</style>