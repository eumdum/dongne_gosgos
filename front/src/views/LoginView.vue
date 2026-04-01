<template>
  <div class="login-container">
    <header class="login-header">
      <button @click="$router.push('/')" class="back-home">🏠</button>
      <h1 class="main-title">로그인</h1>
    </header>

    <main class="login-form-wrapper">
      <div class="login-card">
        <h2 class="card-title">Welcome! 🥐</h2>
        <form @submit.prevent="handleLogin" class="login-form">
          <div class="input-group">
            <label for="username" class="input-label">아이디</label>
            <input type="text" id="username" v-model="username" class="text-input" placeholder="아이디를 입력하세요" required>
          </div>
          <div class="input-group">
            <label for="password" class="input-label">비밀번호</label>
            <input type="password" id="password" v-model="password" class="text-input" placeholder="비밀번호를 입력하세요"
              required>
          </div>
          <button type="submit" class="submit-button login-button">로그인</button>
        </form>
        <button @click="$router.push('/signup')" class="submit-button register-button">회원가입</button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/api';

const router = useRouter();
const username = ref('');
const password = ref('');

const handleLogin = async () => {
  try {
    const response = await api.post('/api/auth/login/', {
      username: username.value,
      password: password.value,
    });

    if (response.data && response.data.access) {
      const userNick = response.data.nickname || username.value;
      const userRole = response.data.role || 'user';

      localStorage.setItem('userToken', response.data.access);
      localStorage.setItem('userName', userNick);
      localStorage.setItem('userRole', userRole);

      alert(`${userNick}님, 환영합니다! 🥳`);

      const redirectPath = router.currentRoute.value.query.redirect || '/';
      window.location.href = redirectPath;
    }
  } catch (error) {
    if (error.response && error.response.status === 401) {
      alert("아이디나 비밀번호가 틀렸어요! 🙅‍♂️");
    } else {
      alert("로그인 처리 중 에러가 발생했어요!");
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&display=swap');

.login-container {
  background: #F4E2D0;
  min-height: 100vh;
  padding: 20px;
  box-sizing: border-box;
}

.login-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 30px;
}

.back-home {
  background: white;
  border: 2px solid #222;
  border-radius: 4px;
  padding: 5px 10px;
  cursor: pointer;
  box-shadow: 2px 2px 0px #222;
}

.main-title {
  font-family: 'Black Han Sans', sans-serif;
  font-size: 1.8rem;
  color: #3A5635;
  -webkit-text-stroke: 1px #222;
  text-shadow: 2px 2px 0px #222;
  margin: 0;
}

.login-form-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-card {
  background: white;
  border: 3px solid #222;
  border-radius: 8px;
  padding: 30px;
  width: 100%;
  max-width: 400px;
  box-shadow: 8px 8px 0px #222;
  text-align: center;
}

.card-title {
  font-family: 'Black Han Sans', sans-serif;
  font-size: 2.2rem;
  color: #E74C3C;
  margin-bottom: 30px;
  -webkit-text-stroke: 1px #222;
}

.input-group {
  margin-bottom: 20px;
  text-align: left;
}

.input-label {
  display: block;
  font-weight: 800;
  color: #333;
  margin-bottom: 8px;
  font-size: 14px;
}

.text-input {
  width: 100%;
  padding: 12px;
  border: 2px solid #222;
  border-radius: 4px;
  font-size: 16px;
  box-sizing: border-box;
}

.submit-button {
  display: block;
  width: 100%;
  padding: 15px;
  border: 2px solid #222;
  border-radius: 4px;
  font-weight: 900;
  font-size: 1.1rem;
  cursor: pointer;
  box-shadow: 4px 4px 0px #222;
  transition: all 0.1s ease;
  margin-bottom: 15px;
}

.login-button {
  background: #3A5635;
  color: white;
}

.login-button:hover {
  background: #4a6d46;
  transform: translate(2px, 2px);
  box-shadow: 2px 2px 0px #222;
}

.register-button {
  background: #D57B0E;
  color: white;
}

.register-button:hover {
  background: #e09228;
  transform: translate(2px, 2px);
  box-shadow: 2px 2px 0px #222;
}
</style>