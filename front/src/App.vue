<template>
  <div id="app">
    <!-- <div v-if="isLoading && $route.path !== '/'" class="full-loading-screen"> -->
      <div v-if="isLoading" class="full-loading-screen">
      <div class="logo-wrapper">
        <div class="bouncing-bread">🥐</div>
        <h1 class="main-logo-stroke">동네곳곳</h1>
        <p class="loading-text">우리 동네의 따뜻한 빵집을 연결합니다</p>
      </div>
    </div>

    <template v-else>
      <header class="header">
        <div class="header-content">
          <router-link to="/" class="logo">🥐 동네곳곳</router-link>
          <nav class="top-nav">
            <div v-if="!isLoggedIn" class="auth-buttons">
              <button @click="$router.push('/login')" class="nav-btn login-btn">로그인</button>
              <button @click="$router.push('/signup')" class="nav-btn signup-btn">회원가입</button>
            </div>

            <div v-else-if="userRole === 'owner'" class="user-info">
              <span class="welcome-msg">👨‍🍳 <strong>{{ username }}</strong> 안녕하세요!</span>

              <button 
                v-if="userRole === 'owner'" 
                @click="$router.push(['/main', '/register', '/admin-list', '/store-pickup'].includes($route.path) ? '/' : '/main')"
                class="nav-btn pickup">
                {{ ['/main', '/register', '/admin-list', '/store-pickup'].includes($route.path) ? '빵 둘러보기' : '매장관리' }}
              </button>

              <button @click="$router.push('/mypage-owner')" class="nav-btn mypage">마이페이지</button>
              <button @click="handleLogout" class="nav-btn logout">로그아웃</button>
            </div>

            <div v-else class="user-info">
              <span class="welcome-msg">🥐 <strong>{{ username }}</strong>님 안녕하세요!</span>
              <button @click="$router.push('/pickup')" class="nav-btn pickup">픽업현황</button>
              <button @click="$router.push('/mypage')" class="nav-btn mypage">마이페이지</button>
              <button @click="handleLogout" class="nav-btn logout">로그아웃</button>
            </div>
          </nav>
        </div>
      </header>

      <router-view />
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();
const isLoading = ref(true);
const userRole = ref(localStorage.getItem('userRole') || '');
const username = ref(localStorage.getItem('userName') || '');
const userToken = ref(localStorage.getItem('userToken'));

const isLoggedIn = computed(() => !!userToken.value);

const checkLoginStatus = () => {
  userToken.value = localStorage.getItem('userToken');
  username.value = localStorage.getItem('userName') || '';
  userRole.value = localStorage.getItem('userRole') || '';
};

const handleLogout = () => {
  localStorage.clear(); 

  userToken.value = null;
  username.value = '';
  userRole.value = '';

  alert('로그아웃 되었습니다. 다음에 또 방문해주세요! 🥐');
  router.replace('/');
};

watch(() => route.path,
  (newPath) => {
    userToken.value = localStorage.getItem('userToken');
    username.value = localStorage.getItem('userName') || '';
    userRole.value = localStorage.getItem('userRole') || '';

    const ownerPaths = ['/main', '/mypage-owner'];
    if (ownerPaths.includes(newPath) && userRole.value !== 'owner') {
      alert("👨‍🍳 사장님 계정만 접근이 가능한 화면입니다!");
      router.push('/');
    }
  });

onMounted(() => {
  checkLoginStatus();
  setTimeout(() => {
    isLoading.value = false;
  }, 2000);
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&display=swap');

:global(body) {
  margin: 0;
  padding: 0;
  overflow-x: hidden;
}

.full-loading-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: linear-gradient(180deg, #3A5635 0%, #D57B0E 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.logo-wrapper {
  text-align: center;
}

.bouncing-bread {
  font-size: 100px;
  animation: bounce 0.6s ease-in-out infinite alternate;
  display: inline-block;
}

@keyframes bounce {
  from {
    transform: translateY(0px);
  }

  to {
    transform: translateY(-35px);
  }
}

.main-logo-stroke {
  font-family: 'Black Han Sans', sans-serif;
  font-size: 4.5rem;
  color: white;
  margin: 0;
  -webkit-text-stroke: 2px #222;
  text-shadow: 4px 4px 0px #222;
}

.loading-text {
  color: white;
  margin-top: 15px;
  font-weight: 600;
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.3);
}

.header {
  border-bottom: 2px solid #F4E2D0;
  padding: 1.2rem;
  background-color: #3A5635;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-family: 'Black Han Sans', sans-serif;
  font-size: 2rem;
  color: #F4E2D0;
  text-decoration: none;
  -webkit-text-stroke: 1px #222;
}

.nav-btn {
  border: 2px solid #222;
  border-radius: 4px;
  padding: 6px 14px;
  margin-left: 8px;
  font-weight: 800;
  color: white;
  cursor: pointer;
  box-shadow: 2px 2px 0px #222;
  text-decoration: none;
  transition: all 0.1s;
  display: inline-flex;
  align-items: center;
}

.nav-btn:active {
  transform: translate(2px, 2px);
  box-shadow: 0px 0px 0px #222;
}

.login-btn {
  background: #D57B0E;
}

.signup-btn {
  background: #96580c;
}

.pickup {
  background: #ffa63a;
}

.logout {
  background: #96580c;
}

.top-nav {
  display: flex;
  align-items: center;
}

.welcome-msg {
  font-weight: 800;
  color: #F4E2D0;
  margin-right: 10px;
}

.mypage {
  background: #D57B0E;
}

.nav-btn {
  margin-left: 5px;
}
</style>