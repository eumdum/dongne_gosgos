<template>
  <div class="signup-page-wrapper">
    <div class="signup-form-container">
      <div class="form-header">
        <span class="retro-icon">🥐</span>
        <h2 class="retro-title">{{ isOwner ? 'OWNER SIGNUP' : 'USER SIGNUP' }}</h2>
        <p class="sub-title">{{ isOwner ? '사장님 회원가입' : '일반 회원가입' }}</p>
      </div>

      <form @submit.prevent="handleSignup" class="retro-form">
        <div class="input-group">
          <label>ID / 아이디</label>
          <input v-model="formData.username" type="text" placeholder="아이디를 입력해주세요" required>
        </div>

        <div class="input-group">
          <label>PW / 비밀번호</label>
          <input v-model="formData.password" type="password" placeholder="비밀번호를 입력해주세요" required>
        </div>

        <div v-if="isOwner" class="owner-fields fade-in">
          <div class="input-group">
            <label class="biz-label">BIZ NO / 사업자 번호</label>
    
            <p class="biz-notice">
              <span class="highlight">⚠️ 사업자 번호를 등록해야 빵 등록 및 판매가 가능합니다! ⚠️</span>
            </p>

            <input 
              v-model="formData.business_number" 
              type="text" 
              placeholder="'-' 없이 숫자만 입력"
              class="biz-input"
            >
          </div>

          <div class="input-group">
            <label>SHOP NAME / 가게 이름</label>
            <input v-model="formData.store_name" type="text" placeholder="가게 이름을 입력하세요">
          </div>

          <div class="input-group">
            <label>매장 주소</label>
            <div class="address-box">
              <input v-model="formData.store_address" readonly placeholder="주소를 검색해주세요" class="retro-input">
              <button type="button" @click="openAddressPopup" class="search-btn">주소 찾기</button>
            </div>
          </div>
        </div>

        <div v-else class="user-fields fade-in">
          <div class="input-group">
            <label>NICKNAME / 닉네임 <span class="optional-tag">(선택)</span></label>
            <input v-model="formData.nickname" type="text" placeholder="미입력 시 '손님'으로 표시됩니다">
          </div>
        </div>

        <button type="submit" class="submit-btn">가입하기 / JOIN NOW!</button>
      </form>

      <div class="switch-role">
        <p v-if="!isOwner">
          <button @click="switchRole('owner')" class="switch-link">사장님으로 회원가입 ➡ </button>
        </p>
        <p v-else>
          일반 사용자이신가요?
          <button @click="switchRole('user')" class="switch-link">일반 회원가입 ➡ </button>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '@/api';

const route = useRoute();
const router = useRouter();

const isOwner = computed(() => route.query.role === 'owner');

const address = ref('');
const lat = ref(null);
const lng = ref(null);

const formData = ref({
  username: '',
  password: '',
  role: route.query.role || 'user',
  business_number: '',
  store_name: '',
  store_address: '',
  store_name:'',
  nickname: '',
  lat: null,
  lng: null,
});

const switchRole = (newRole) => {
  router.push({ query: { role: newRole } });
  formData.value.role = newRole;
};

watch(() => route.query.role, (newRole) => {
  formData.value.role = newRole;
});

const handleSignup = async () => {
  try {
    const response = await api.post('/api/auth/signup/', formData.value);

    if (response.status === 201) {
      localStorage.setItem('userToken', response.data.access);
      localStorage.setItem('userName', response.data.nickname);
      localStorage.setItem('userRole', response.data.role);

      let welcomeMsg = `${response.data.nickname}님, 환영합니다! 가입과 동시에 로그인되었어요! 🥐`;

      if (response.data.role === 'owner' && (!formData.value.business_number || formData.value.business_number.trim() === '')) {
        welcomeMsg += "\n\n⚠️ 사장님! 사업자등록번호를 입력해야 빵 등록이 가능하니, 마이페이지에서 꼭 등록해 주세요!⚠️";
      }

      alert(welcomeMsg);
      window.location.href = '/'; 
    }
  } catch (error) {
    const errorMsg = error.response?.data?.error || "가입 중 오류가 발생했습니다.";
    alert(errorMsg);
  }
};

const openAddressPopup = () => {
  new window.daum.Postcode({
    oncomplete: (data) => {
      // 사용자가 선택한 주소 타입(도로명/지번)에 따라 변수 할당
      let selectedAddr = '';
      
      if (data.userSelectedType === 'R') {
        selectedAddr = data.roadAddress;
      } else {
        selectedAddr = data.jibunAddress;
      }

      let extraAddr = '';
      if (data.userSelectedType === 'R') {
        if (data.bname !== '' && /[동|로|가]$/g.test(data.bname)) {
          extraAddr += data.bname;
        }
        if (data.buildingName !== '') {
          extraAddr += (extraAddr !== '' ? ', ' + data.buildingName : data.buildingName);
        }
        selectedAddr += (extraAddr !== '' ? ` (${extraAddr})` : '');
      }

      formData.value.store_address = selectedAddr;

      if (data.buildingName) {
        formData.value.store_name = data.buildingName;
      }

      const geocoder = new window.kakao.maps.services.Geocoder();
      geocoder.addressSearch(data.address, (result, status) => {
        if (status === window.kakao.maps.services.Status.OK) {
          formData.value.lat = result[0].y;
          formData.value.lng = result[0].x;
        }
      });
    }
  }).open();
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&display=swap');

.signup-page-wrapper {
  min-height: 100vh;
  background-color: #F4E2D0;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 20px;
}

.signup-form-container {
  max-width: 420px;
  width: 100%;
  background: white;
  padding: 40px 30px;
  border: 3px solid #222;
  border-radius: 12px;
  box-shadow: 10px 10px 0px #222;}

.form-header {
  text-align: center;
  margin-bottom: 30px;
}

.retro-icon {
  font-size: 50px;
  display: block;
  margin-bottom: 10px;
}

.retro-title {
  font-family: 'Black Han Sans', sans-serif;
  font-size: 2.2rem;
  color: #E74C3C;
  margin: 0;
  -webkit-text-stroke: 1px #222;
  text-shadow: 2px 2px 0px #222;
}

.sub-title {
  font-weight: 800;
  color: #222;
  margin-top: 5px;
}

.input-group {
  margin-bottom: 20px;
  text-align: left;
}

.input-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 900;
  font-size: 13px;
  color: #3A5635;
}

.input-group input {
  width: 100%;
  padding: 12px;
  border: 2px solid #222;
  border-radius: 6px;
  box-sizing: border-box;
  font-weight: 600;
  background: #f9f9f9;
}

.input-group input:focus {
  outline: none;
  background: white;
  border-color: #D57B0E;
}

.submit-btn {
  width: 100%;
  padding: 15px;
  background: #D57B0E;
  color: white;
  border: 3px solid #222;
  border-radius: 8px;
  font-weight: 900;
  font-size: 1.1rem;
  cursor: pointer;
  margin-top: 20px;
  box-shadow: 4px 4px 0px #222;
  transition: all 0.1s;
}

.submit-btn:hover {
  background: #ee8e32;
  transform: translate(2px, 2px);
  box-shadow: 2px 2px 0px #222;
}

.submit-btn:active {
  transform: translate(4px, 4px);
  box-shadow: 0px 0px 0px #222;
}

.switch-role {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 2px dashed #ccc;
  text-align: center;
}

.switch-role p {
  font-size: 0.9rem;
  font-weight: 600;
  color: #666;
}

.switch-link {
  background: none;
  border: none;
  color: #E74C3C;
  font-weight: 900;
  text-decoration: underline;
  cursor: pointer;
  font-size: 0.95rem;
  margin-left: 5px;
}

.switch-link:hover {
  color: #c0392b;
}

.fade-in {
  animation: fadeIn 0.4s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.biz-label {
  display: block;
  font-weight: 900;
  margin-bottom: 5px;
}

.biz-notice {
  background: none !important; 
  border: none !important;
  margin: 10px 0;
  padding: 0;
  text-align: left; 
}

.highlight {
  display: inline; 
  background-color: #fff3e0; 
  color: #D57B0E;
  padding: 3px 8px; 
  border-radius: 4px;
  font-weight: 700;
  font-size: 0.85rem;
}

.biz-label {
  display: block;
  font-weight: 900;
  font-size: 0.9rem;
  margin-bottom: 8px;
}
</style>