<template>
  <div v-if="isOwnerChecked" class="mypage-container">
    <h2 class="mypage-title">🥐 사장님 메뉴</h2>

    <div class="owner-gate-container">
      <button class="choice-card pickup" @click="goPath('/pickup')">
        <div class="icon">🛒</div>
        <div class="text">실시간 픽업 현황</div>
      </button>

      <button class="choice-card product" @click="goPath('/product-manage')">
        <div class="icon">📚</div>
        <div class="text">상품 관리</div>
      </button>

      <button class="choice-card history" @click="goPath('/mypage')">
        <div class="icon">📜</div>
        <div class="text">나의 빵 기록</div>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const isOwnerChecked = ref(false);

const goPath = (path) => {
  router.push(path);
};

onMounted(() => {
  const userRole = localStorage.getItem('userRole');

  if (userRole === 'owner') {
    isOwnerChecked.value = true;
  } else {
    alert("사장님만 접근 가능한 페이지입니다!");
    router.push('/mypage');
  }
});
</script>

<style scoped>
.mypage-container {
  padding: 15px 20px;
  background: #F4E2D0;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.mypage-title {
  font-family: 'Black Han Sans', sans-serif;
  font-size: 4rem;
  margin-top: 50px;
  margin-bottom: 60px;
  text-align: center;
  color: #3A5635;
  -webkit-text-stroke: 0.2px #202020;
}

.owner-gate-container {
  display: flex;
  flex-direction: column;
  gap: 30px;
  width: 100%;
  max-width: 400px;
}

.choice-card {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  background: white;
  border: 4px solid #222;
  border-radius: 20px;
  cursor: pointer;
  box-shadow: 8px 8px 0px #222;
}

.choice-card .icon {
  font-size: 3rem;
  margin-right: 15px;
}

.choice-card .text {
  font-family: 'Black Han Sans', sans-serif;
  font-size: 2rem;
  color: #222;
}

.choice-card.pickup {
  border-color: #D57B0E;
}

.choice-card.pickup .text {
  color: #D57B0E;
}

.choice-card.history {
  border-color: #3A5635;
}

.choice-card.history .text {
  color: #3A5635;
}
</style>