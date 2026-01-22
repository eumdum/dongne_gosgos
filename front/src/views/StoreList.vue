<template>
  <div class="min-h-screen bg-gray-50 p-6 font-sans">
    
    <!-- 헤더 영역 -->
    <header class="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center mb-8 gap-4">
      <div>
        <h1 class="text-3xl font-extrabold text-blue-600 tracking-tight">우리 동네 상품 목록</h1>
        <p class="text-gray-500 mt-1">현재 등록된 마감 할인 상품들입니다.</p>
      </div>

      <div class="flex items-center gap-4">
        <!-- 정렬 버튼 그룹 -->
        <div class="bg-white p-1.5 rounded-xl shadow-sm border border-gray-200 flex">
          <button 
            @click="setSortOrder('desc')"
            class="px-4 py-2 rounded-lg text-sm font-bold transition-all duration-200"
            :class="sortOrder === 'desc' ? 'bg-blue-50 text-blue-600 shadow-sm' : 'text-gray-400 hover:text-gray-600 hover:bg-gray-50'"
          >
            최신 등록
          </button>
          <div class="w-px bg-gray-200 my-1"></div>
          <button 
            @click="setSortOrder('asc')"
            class="px-4 py-2 rounded-lg text-sm font-bold transition-all duration-200"
            :class="sortOrder === 'asc' ? 'bg-blue-50 text-blue-600 shadow-sm' : 'text-gray-400 hover:text-gray-600 hover:bg-gray-50'"
          >
            과거 등록
          </button>
        </div>

        <!-- 상품 등록 버튼 -->
        <router-link 
          to="/" 
          class="bg-blue-600 text-white font-bold py-3 px-6 rounded-2xl shadow-lg hover:bg-blue-700 transition-all flex items-center"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
          </svg>
          상품 등록하기
        </router-link>
      </div>
    </header>

    <!-- 로딩 상태 -->
    <div v-if="isLoading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-16 w-16 border-[5px] border-blue-100 border-t-blue-600"></div>
    </div>

    <!-- 상품 목록 그리드 -->
    <div v-else class="max-w-7xl mx-auto grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
      
      <!-- 상품 카드 -->
      <div 
        v-for="store in sortedStores" 
        :key="store.id" 
        class="bg-white rounded-[2rem] shadow-xl overflow-hidden border border-gray-100 hover:shadow-2xl transition-all hover:-translate-y-1 duration-300"
      >
        <!-- 상품 이미지 -->
        <div class="h-64 overflow-hidden relative group bg-gray-100">
          <img 
            v-if="store.image"
            :src="getImageUrl(store.image)" 
            alt="상품 이미지" 
            class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
            @error="handleImageError(store, $event)"
          />
          <div v-else class="w-full h-full flex flex-col items-center justify-center text-gray-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mb-2 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span class="text-sm font-bold">이미지 없음</span>
          </div>

          <div class="absolute top-4 right-4 bg-white/90 backdrop-blur px-3 py-1 rounded-full text-xs font-bold text-blue-600 shadow-sm">
            신뢰도 {{ store.confidence ? (store.confidence * 100).toFixed(0) : 0 }}%
          </div>
        </div>

        <!-- 상품 정보 -->
        <div class="p-6">
          <div class="flex justify-between items-start mb-2">
            <h3 class="text-2xl font-bold text-gray-800 line-clamp-1">{{ store.item || '이름 없음' }}</h3>
          </div>
          <div class="flex items-baseline mb-4">
            <span class="text-3xl font-black text-blue-600">
              {{ store.price ? store.price.toLocaleString() : '0' }}
            </span>
            <span class="text-gray-400 font-bold ml-1">원</span>
          </div>
          
          <div class="flex justify-between items-center text-sm text-gray-400 pt-4 border-t border-gray-100">
            <span>{{ formatDate(store.created_at) }}</span>
            <span class="bg-gray-100 px-2 py-1 rounded text-gray-500 font-medium">판매중</span>
          </div>
        </div>
      </div>

      <!-- 데이터가 없을 때 -->
      <div v-if="stores.length === 0" class="col-span-full text-center py-20">
        <p class="text-xl text-gray-400 font-bold">아직 등록된 상품이 없습니다.</p>
        <p class="text-gray-400 mt-2">첫 번째 상품을 등록해보세요!</p>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';

const stores = ref([]);
const isLoading = ref(true);
const sortOrder = ref('desc');

const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' });
};

// [수정] 이미지 경로 안전하게 만들기
const getImageUrl = (imagePath) => {
  if (!imagePath) return '';
  
  // 1. 이미 완전한 URL인 경우 그대로 반환
  if (imagePath.startsWith('http')) return imagePath;
  
  // 2. 경로 앞에 슬래시(/)가 없으면 붙여주기 (예: 'media/...' -> '/media/...')
  // Django가 가끔 상대 경로로만 줄 때가 있어서 필요합니다.
  let path = imagePath;
  if (!path.startsWith('/')) {
    path = `/${path}`;
  }
  
  // 3. 백엔드 주소 붙여서 반환
  return `http://127.0.0.1:8000${path}`;
};

// [수정] 에러 발생 시 어떤 주소였는지 로그 출력 ($event 추가)
const handleImageError = (store, event) => {
  console.warn(`[이미지 로드 실패] ID: ${store.id}, 시도한 URL: ${event.target.src}`);
  store.image = null; // 엑박 대신 '이미지 없음' 상자로 교체
};

const setSortOrder = (order) => {
  sortOrder.value = order;
};

const sortedStores = computed(() => {
  return [...stores.value].sort((a, b) => {
    const dateA = new Date(a.created_at).getTime();
    const dateB = new Date(b.created_at).getTime();
    
    if (sortOrder.value === 'desc') {
      return dateB - dateA;
    } else {
      return dateA - dateB;
    }
  });
});

const fetchStores = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/stores/');
    stores.value = response.data;
  } catch (error) {
    console.error("데이터 로딩 실패:", error);
    alert("목록을 불러오지 못했습니다.");
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchStores();
});
</script>