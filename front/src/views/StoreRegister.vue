<template>
  <div class="store-pickup">
    <header class="header-container">
      <div class="header-left">
        <router-link to="/main" class="back-btn">←</router-link>
        <h1>📸 할인 빵 등록</h1>
      </div>
      <button @click="triggerFileInput" class="refresh-btn">촬영 📸</button>
    </header>

    <div v-if="!isLoading && cartItems.length === 0" class="empty-state-card" @click="triggerFileInput">
      <div class="upload-icon">🍞</div>
      <p>여기를 눌러 빵 사진을 찍어주세요!</p>
    </div>

    <div v-if="cartItems.length > 0" class="control-panel">
      <div class="bulk-actions">
        <label class="check-container">
          <input type="checkbox" :checked="isAllSelected" @change="toggleSelectAll">
          <span class="check-text">전체 선택</span>
        </label>
        <button @click="removeSelected" class="action-btn text-red">선택 삭제</button>
        <button @click="removeAll" class="action-btn text-gray">전체 비우기</button>
      </div>

      <div class="discount-input-group">
        <span class="label">선택한 빵 할인율 :</span>
        <input type="number" v-model="bulkDiscount" placeholder="20" class="discount-input" />
        <span class="unit">%</span>
        <button @click="applyBulkDiscount" class="apply-btn">적용</button>
      </div>
    </div>

    <div class="order-grid" v-if="cartItems.length > 0">
      <div 
        v-for="item in cartItems" 
        :key="item.id" 
        class="order-card" 
        :class="{ 'selected-card': item.selected }"
        @click="toggleItemSelection(item)"
      >
        <div class="card-top-row">
          <input 
            type="checkbox" 
            v-model="item.selected" 
            class="item-checkbox" 
            @click.stop
          />
          <button @click="removeItem(item.id)" class="delete-small-btn">❌</button>
        </div>

        <div class="card-header">
          <span class="pickup-num">{{ item.name }}</span>
        </div>

        <div class="card-body">
          <div class="info-row">
            <span>수량: <strong>{{ item.count }}개</strong></span>
            <span class="original-price">{{ (item.original_price * item.count).toLocaleString() }}원</span>
          </div>
          <div class="price-row">
            <span class="discount-tag">{{ item.discount }}% OFF</span>
            <span class="final-price">{{ (item.price * item.count).toLocaleString() }}원</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showModal || isLoading" class="modal-overlay">
      <div class="modal-content">

        <div v-if="isLoading" class="loading-state">
          <div class="spinner"></div>
          <h2>빵 분석 중... 🔍</h2>
          <p>잠시만 기다려주세요!<br>AI가 사진 속 빵을 열심히 세고 있어요.</p>
        </div>

        <div v-else-if="showModal">
          <h2>🔍 빵 인식 결과</h2>
          <div class="detail-box scrollable">
            <div v-for="(res, idx) in analysisResults" :key="idx" class="result-item-row">
              <input v-model="res.name" class="edit-name" />
              <div class="count-control">
                <button @click="res.count > 1 ? res.count-- : null">-</button>
                <span>{{ res.count }}</span>
                <button @click="res.count++">+</button>
              </div>
            </div>
          </div>
          <div class="modal-buttons">
            <button @click="confirmRegistration" class="btn-complete">목록에 추가</button>
            <button @click="showModal = false" class="btn-close">취소</button>
          </div>
        </div>
      </div>
    </div>

    <input type="file" ref="fileInput" class="hidden-input" accept="image/*" @change="onFileSelected" />

    <footer v-if="cartItems.length > 0" class="floating-footer">
      <button @click="registerComplete" class="btn-complete-all">
        총 {{ totalCount }}개 세일 등록 하기 🥐
      </button>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import api from '@/api';
import router from '@/router';

const fileInput = ref(null);
const cartItems = ref([]);
const analysisResults = ref([]);
const showModal = ref(false);
const isLoading = ref(false);
const bulkDiscount = ref(20); // 기본 일괄 할인율

const totalCount = computed(() => cartItems.value.reduce((acc, cur) => acc + cur.count, 0));
const isAllSelected = computed(() => cartItems.value.length > 0 && cartItems.value.every(i => i.selected));

const triggerFileInput = () => fileInput.value.click();

onMounted(() => {
  setTimeout(() => triggerFileInput(), 300);
});

const toggleSelectAll = () => {
  const target = !isAllSelected.value;
  cartItems.value.forEach(i => i.selected = target);
};

const toggleItemSelection = (item) => {
  item.selected = !item.selected;
};

const applyBulkDiscount = () => {
  cartItems.value.forEach(item => {
    if (item.selected) {
      item.discount = bulkDiscount.value;
      item.price = Math.floor(item.original_price * (1 - item.discount / 100));
    }
  });
};

const removeSelected = () => {
  cartItems.value = cartItems.value.filter(i => !i.selected);
};
const removeAll = () => {
  if (confirm("모든 목록을 비울까요?")) cartItems.value = [];
};

const onFileSelected = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  showModal.value = false; 
  isLoading.value = true;

  const formData = new FormData();
  formData.append('image', file);

  try {
    const res = await api.post('/api/detect/', formData);
    if (res.data?.items) {
      const grouped = res.data.items.reduce((acc, current) => {
        const found = acc.find(item => item.name === current.name);
        if (found) found.count += 1;
        else acc.push({
          name: current.name,
          product_id: current.product_id,
          original_price: current.price, // 원가
          price: current.price * 0.8, // 기본 20% 할인된 가격 
          count: 1,
          discount: 20, 
          selected: true 
        });
        return acc;
      }, []);
      analysisResults.value = grouped;
      isLoading.value = false;
      showModal.value = true;
    }
  } catch (err) {
    isLoading.value = false;
    alert("분석 실패!");
  }
  
  event.target.value = '';
};

const confirmRegistration = () => {
  analysisResults.value.forEach(item => {
    cartItems.value.push({ ...item, id: Date.now() + Math.random() });
  });
  showModal.value = false;
};

const removeItem = (id) => {
  cartItems.value = cartItems.value.filter(i => i.id !== id);
};

const registerComplete = async () => {
  if (cartItems.value.length === 0) {
    alert("등록할 빵이 없습니다!");
    return;
  }

  try {
    const formattedProducts = cartItems.value.map(item => ({
      name: item.name,
      product_id: item.product_id,
      count: item.count,
      // AI가 분석한 원가 (onFileSelected에서 original_price 혹은 originalPrice로 저장된 값)
      original_price: item.original_price || item.originalPrice, 
      // 사장님이 할인율 적용해서 계산된 할인가
      discount_price: item.price 
    }));

    await api.post('/api/save-products/', { 
      products: formattedProducts 
    });

    alert("✅ 세일 등록이 완료되었습니다!");
    cartItems.value = [];
    router.push('/main'); 
    
  } catch (err) {
    alert("저장에 실패했습니다. 다시 시도해주세요.");
  }
};
</script>

<style scoped>
.store-pickup {
  padding: 20px;
  max-width: 900px;
  margin: 0 auto;
  padding-bottom: 120px;
  background: #fdfdfd;
}

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-left h1 {
  font-size: 1.8rem;
  margin: 0;
  color: #3A5635;
}

.control-panel {
  background: white;
  border: 3px solid #222;
  border-radius: 12px;
  padding: 15px;
  margin-bottom: 25px;
  box-shadow: 5px 5px 0px #222;
}

.bulk-actions {
  display: flex;
  gap: 15px;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px dashed #ccc;
}

.discount-input-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.discount-input {
  width: 60px;
  padding: 8px;
  border: 2px solid #222;
  border-radius: 6px;
  text-align: center;
  font-weight: 900;
}

.apply-btn {
  background: #4c7045;
  color: white;
  border: 2px solid #222;
  padding: 8px 15px;
  border-radius: 6px;
  font-weight: 800;
  cursor: pointer;
}

.order-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.order-card {
  position: relative;
  border: 3px solid #222;
  padding: 15px;
  border-radius: 12px;
  background: white;
  box-shadow: 4px 4px 0px #222;
  transition: 0.2s;
  cursor: pointer;
  user-select: none;;
}

.order-card:active {
  transform: scale(0.98);
}

.selected-card {
  background: #fff9f0;
  border-color: #D57B0E;
}

.card-top-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.item-checkbox {
  width: 20px;
  height: 20px;
  cursor: pointer;
}

.pickup-num {
  font-size: 1.2rem;
  font-weight: 900;
  color: #4e342e;
}

.info-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.original-price {
  text-decoration: line-through;
  color: #999;
}

.price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.discount-tag {
  background: #e74c3c;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 900;
}

.final-price {
  font-size: 1.1rem;
  font-weight: 900;
  color: #4c7045;
}

.floating-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 20px;
  background: white;
  box-shadow: 0 -5px 15px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: center;
}

.btn-complete-all {
  width: 90%;
  max-width: 500px;
  background: #4c7045;
  color: white;
  border: 3px solid #222;
  padding: 15px;
  border-radius: 12px;
  font-size: 1.2rem;
  font-weight: 900;
  box-shadow: 6px 6px 0px #222;
  cursor: pointer;
}



.back-btn {
  text-decoration: none;
  font-size: 1.5rem;
  color: #333;
}

.refresh-btn {
  background: #D57B0E;
  color: white;
  border: 3px solid #222;
  padding: 7px 12px;
  border-radius: 10px;
  font-weight: 900;
  cursor: pointer;
  box-shadow: 4px 4px 0px #222;
  transition: 0.1s;
}

.refresh-btn:active {
  transform: translate(3px, 3px);
  box-shadow: 0px 0px 0px #222;
}

.empty-state-card {
  border: 4px dashed #3A5635;
  border-radius: 20px;
  padding: 80px 20px;
  text-align: center;
  margin-top: 40px;
  cursor: pointer;
  background: #fff;
  transition: 0.2s;
}

.empty-state-card:hover {
  background: #f9f9f9;
  border-color: #D57B0E;
}

.upload-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  display: block;
}

.empty-state-card p {
  font-weight: 900;
  font-size: 1.3rem;
  color: #3A5635;
}

.hidden-input {
  display: none;
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
  max-width: 500px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #ffb84d;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

.loading-state {
  text-align: center;
  padding: 20px 0;
}

.loading-state h2 {
  color: #4e342e;
  margin-bottom: 10px;
}

.loading-state p {
  color: #666;
  font-size: 0.9rem;
  line-height: 1.5;
}

.scrollable {
  max-height: 400px;
  overflow-y: auto;
}

.result-item-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.edit-name {
  border: none;
  font-weight: bold;
  font-size: 1rem;
  width: 300px;
}

.count-control {
  display: flex;
  gap: 10px;
  align-items: center;
}

.btn-complete {
  background: #27ae60;
  color: white;
  border: none;
  padding: 12px 25px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: bold;
}

.btn-close {
  background: #eee;
  border: none;
  padding: 12px 25px;
  border-radius: 10px;
  cursor: pointer;
}
.delete-small-btn {
  position: absolute; 
  top: 10px;
  right: 10px;
  
  border: none;
  background: none;
  font-size: 16px;
  cursor: pointer;
  padding: 5px;
  line-height: 1;
  transition: transform 0.2s;
}

.action-btn {
  background: none;
  border: none;
  font-weight: 800;
  cursor: pointer;
  text-decoration: underline; 
  font-size: 0.9rem;
}

.text-red { color: #e74c3c; } 
.text-gray { color: #7f8c8d; }

.check-text {
  font-weight: 900;
  color: #333;
  margin-left: 5px;
  cursor: pointer;
}

.check-container {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.card-top-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.item-checkbox {
  width: 22px;
  height: 22px;
  accent-color: #D57B0E;
  cursor: pointer;
}
</style>