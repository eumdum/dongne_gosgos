<template>
  <div class="complete-container">
    <div class="card" ref="cardRef">
      <div class="icon-group">
        <span class="pixel-icon bounce-in">🥐</span>
        <span class="stars bounce-in-delay">✨</span>
      </div>

      <h1 class="retro-title">READY TO EAT!</h1>
      <h2 class="sub-title">맛있게 드세요!</h2>

      <div class="message-card">
        <p class="status-text">SUCCESSFULLY PICKED UP! 🤝</p>
        <p class="thanks-text">
          오늘도 지구를 지켜주셔서 감사합니다!<br>
          We Save the Earth together! 🌍
        </p>
      </div>

      <div class="divider"></div>

      <button @click="goHome" class="home-btn">
        <span>⬅ GO BACK HOME</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { onMounted, ref } from 'vue';

const router = useRouter();
const isPageVisible = ref(false);
const cardRef = ref(null);

const goHome = () => router.push('/');

onMounted(() => {
  // 사용자가 이 화면을 보고 있는지 확인
  const triggerEffects = () => {
    if (document.visibilityState === 'visible' && !isPageVisible.value) {
      isPageVisible.value = true;
      
      if (cardRef.value) {
        cardRef.value.classList.add('active');
      }
      
      document.removeEventListener('visibilitychange', triggerEffects);
    }
  };

  if (document.visibilityState === 'visible') {
    triggerEffects();
  } else {
    document.addEventListener('visibilitychange', triggerEffects);
  }
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&display=swap');

.complete-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #F4E2D0;
  padding: 20px;
  box-sizing: border-box;
  font-family: 'Pretendard', sans-serif;
}

.card {
  background: #FDFFFC;
  padding: 50px 30px;
  border-radius: 12px;
  text-align: center;
  border: 4px solid #222;
  box-shadow: 10px 10px 0px #222;
  position: relative;
  max-width: 450px;
  width: 100%;
}

.icon-group {
  position: relative;
  display: inline-block;
  margin-bottom: 25px;
}

.pixel-icon {
  font-size: 100px;
  display: inline-block;
}

.stars {
  font-size: 40px;
  position: absolute;
  top: -10px;
  right: -20px;
}

.retro-title {
  font-family: 'Black Han Sans', sans-serif;
  font-size: 3.5rem;
  color: #E74C3C;
  margin: 0;
  text-shadow: 3px 3px 0px #222;
  -webkit-text-stroke: 1.5px #222;
}

.sub-title {
  font-size: 1.8rem;
  color: #222;
  font-weight: 900;
  margin-top: 5px;
  margin-bottom: 30px;
}

.message-card {
  background: #F4F4F4;
  border: 2px solid #222;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 40px;
  text-align: center;
  position: relative;
}

.status-text {
  font-weight: 900;
  color: #3A5635;
  font-size: 1.1rem;
  margin: 0 0 10px auto;
  border-bottom: 2px dashed #AAA;
  padding-bottom: 8px;
  display: inline-block;
  width: 100%;
}

.thanks-text {
  color: #555;
  font-size: 0.95rem;
  line-height: 1.7;
  margin: 0;
  font-weight: 500;
}

.divider {
  border-top: 4px solid #222;
  margin-bottom: 30px;
  position: relative;
}

.divider::after {
  content: "✂️";
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  padding: 0 10px;
}

.home-btn {
  background: #F39C12;
  color: #222;
  border: 3px solid #222;
  padding: 15px 40px;
  border-radius: 8px;
  font-weight: 900;
  font-size: 1.1rem;
  cursor: pointer;
  position: relative;
  box-shadow: 4px 4px 0px #222;
  transition: all 0.1s;
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.home-btn:hover {
  background: #E67E22;
  transform: translate(1px, 1px);
  box-shadow: 3px 3px 0px #222;
}

.home-btn:active {
  transform: translate(4px, 4px);
  box-shadow: 0px 0px 0px #222;
}

@keyframes bounceIn {
  0% {
    opacity: 0;
    transform: scale(0.3) translateY(20px);
  }

  50% {
    opacity: 1;
    transform: scale(1.05);
  }

  70% {
    transform: scale(0.9);
  }

  100% {
    opacity: 1; 
    transform: scale(1) translateY(0);
  }
}

.bounce-in { 
  opacity: 0; 
  display: inline-block;
  animation: bounceIn 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
  animation-play-state: paused; 
}

.bounce-in-delay { 
  opacity: 0;
  display: inline-block;
  animation: bounceIn 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275) 0.3s forwards;
  animation-play-state: paused;
}

.card.active .bounce-in,
.card.active .bounce-in-delay { 
  animation-play-state: running; 
}
</style>