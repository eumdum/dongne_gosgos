<template>
  <div class="store-pickup">
    <header>
      <div class="header-left">
        <router-link to="/main" class="back-btn">←</router-link>
        <h1>📦 재고 관리</h1>
      </div>
      <button @click="fetchProducts" class="refresh-btn">목록 갱신 🔄</button>
    </header>

    <div v-if="products.length === 0" class="empty-state">
      등록된 빵이 없어요. 먼저 할인 빵을 등록해주세요!
    </div>

    <div class="order-grid">
      <div v-for="product in products" :key="product.id" class="order-card"
        :class="{ 'status-complete': product.count === 0 }">
        <div class="card-header">
          <span class="pickup-num">{{ product.name }}</span>
          <span class="status" :style="{ color: product.count > 0 ? '#27ae60' : '#e74c3c' }">
            {{ product.count > 0 ? '판매중' : '품절' }}
          </span>
        </div>
        <div class="card-body">
          <p class="summary">가격: {{ product.discount_price.toLocaleString() }}원</p>

          <div class="stock-adjuster">
            <button @click="handleUpdateCount(product.id, -1)" :disabled="product.count <= 0">-</button>
            <span class="count-display">{{ product.count }}</span>
            <button @click="handleUpdateCount(product.id, 1)">+</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/api';

const products = ref([]);

const fetchProducts = async () => {
  try {
    const res = await api.get('/api/list/');
    products.value = res.data;
  } catch (err) { console.error("로드 실패", err); }
};

const handleUpdateCount = async (id, delta) => {
  try {
    const res = await api.post(`/api/update-count/${id}/`, { delta });
    if (res.data.status === 'success') {
      const target = products.value.find(p => p.id === id);
      if (target) target.count = res.data.count;
    }
  } catch (err) { alert("수량 변경 실패"); }
};

onMounted(fetchProducts);
</script>

<style scoped>
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

.back-btn {
  text-decoration: none;
  font-size: 1.5rem;
  color: #333;
}

.order-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 15px;
  margin-top: 20px;
}

.order-card {
  border: 2px solid #ddd;
  padding: 15px;
  border-radius: 12px;
  background: white;
  transition: 0.3s;
}

.status-complete {
  opacity: 0.5;
  background: #f5f5f5;
}

.pickup-num {
  font-size: 1.2rem;
  font-weight: bold;
  color: #4e342e;
}

.stock-adjuster {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  margin-top: 15px;
  background: #fdf5e6;
  padding: 10px;
  border-radius: 10px;
}

.stock-adjuster button {
  width: 30px;
  height: 30px;
  border: 1px solid #ffb84d;
  background: white;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
}

.count-display {
  font-size: 1.2rem;
  font-weight: 900;
  min-width: 30px;
  text-align: center;
}

.empty-state {
  text-align: center;
  padding: 100px 0;
  color: #999;
  font-weight: bold;
}
</style>