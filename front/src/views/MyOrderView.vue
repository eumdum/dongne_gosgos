<template>
  <div class="history-container">
    <header class="history-header">
      <button @click="$router.go(-1)" class="hip-back-btn">
        <span class="btn-icon">◀</span>
      </button>
      <div class="title-group">
        <h2 class="main-title">나의 빵 기록</h2>
        <span class="sub-deco">BAKERY LOG</span>
      </div>
    </header>

    <main class="history-list">
      <div v-if="orders.length === 0" class="empty-history">
        <div class="empty-emoji">🥨?</div>
        <p>아직 먹은 빵이 없어요!</p>
      </div>

      <div v-for="order in orders" :key="order.id" class="order-card">
        <div class="card-header-bar">
          <span class="order-no">ORDER NO.{{ order.pickup_number }}</span>
          <span class="order-date">{{ order.created_at }}</span>
        </div>
        
        <div class="card-content">
          <p class="store-name">{{ order.shop_name }}</p>
          <h3 class="bread-title">{{ order.items_summary }}</h3>
          
          <div class="card-footer-row">
            <span class="status-sticker" :class="order.status">{{ order.status }}</span>
            <span class="price-tag">{{ order.total_price.toLocaleString() }}원</span>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
  

<script setup>
  import { ref, onMounted } from 'vue';
  import { useRouter } from 'vue-router'; 
  import api from '@/api';
  
  const router = useRouter();
  const orders = ref([]);
  
  const fetchOrders = async () => {
    try {
      const token = localStorage.getItem('userToken'); 
      const res = await api.get('/api/my-orders/', {
       headers: {
         Authorization: `Token ${token}` 
        }
      });
     orders.value = res.data;
    } catch (err) {
      if (err.response && err.response.status === 401) {
        alert("로그인이 필요하거나 세션이 만료되었습니다. 다시 로그인해주세요! 🥨");
        router.push('/login'); 
     }
    }
  };

  onMounted(fetchOrders);
</script>
  
<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&display=swap');

.history-container {
  background: #F4E2D0; 
  min-height: 100vh;
  padding: 25px 20px;
}

.history-header {
  display: flex;
  align-items: center;
  margin-bottom: 35px;
  gap: 15px;
}

.hip-back-btn {
  background: #FF5C00; 
  border: 4px solid #222;
  width: 50px;
  height: 50px;
  box-shadow: 4px 4px 0px #222;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.hip-back-btn:active {
  box-shadow: 0px 0px 0px #222;
  transform: translate(4px, 4px);
}

.btn-icon {
  color: #fff;
  font-size: 1.5rem;
  font-weight: 900;
}

.main-title {
  font-family: 'Black Han Sans', sans-serif;
  font-size: 2rem;
  color: #222;
  margin: 0;
  line-height: 1;
}

.sub-deco {
  font-size: 0.7rem;
  font-weight: 900;
  background: #222;
  color: #fff;
  padding: 2px 5px;
}

.order-card {
  background: #fff;
  border: 4px solid #ffff;
  margin-bottom: 25px;
  box-shadow: 8px 8px 0px #222; 
}

.card-header-bar {
  background: #222;
  color: #fff;
  padding: 8px 15px;
  display: flex;
  justify-content: space-between;
  font-weight: 900;
  font-size: 0.75rem;
}

.card-content {
  padding: 15px;
}

.store-name {
  color: #FF5C00;
  font-weight: 900;
  font-size: 1.5rem;
  margin-bottom: 0px;
}

.bread-title {
  font-size: 1.4rem;
  font-weight: 900;
  color: #222;
  margin: 0 0 15px 0;
}

.card-footer-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-sticker {
  border: 3px solid #222;
  padding: 5px 12px;
  font-weight: 900;
  font-size: 0.9rem;
  transform: rotate(-3deg); 
}

.status-sticker.결제완료 { background: #FFD300; } 
.status-sticker.픽업완료 { background: #3A5635; color: #fff; }

.price-tag {
  font-size: 1.5rem;
  font-weight: 900;
  font-family: 'Black Han Sans', sans-serif;
}
</style>