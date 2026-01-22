<template>
  <div class="min-h-screen bg-gray-50 p-4 flex flex-col items-center font-sans">
    
    <!-- 메인 컨텐츠 레이어 -->
    <!-- max-w-md: PC에서도 너무 퍼지지 않게 잡아줌 -->
    <!-- w-full: 모바일에서는 가로 꽉 차게 -->
    <div 
      class="w-full max-w-md flex flex-col items-center transition-opacity duration-300"
      :class="{ 'opacity-0 pointer-events-none': showModal }"
    >
      <!-- 헤더 -->
      <header class="w-full my-8 text-center">
        <!-- text-2xl md:text-3xl: 모바일에선 작게, PC에선 크게 -->
        <h1 class="text-2xl md:text-3xl font-extrabold text-[#82be8c] tracking-tight mb-2">
          동네곳곳 AI 등록
        </h1>
        <p class="text-sm md:text-base text-gray-500 font-medium">
          사진을 찍으면 정보가 자동 입력됩니다.
        </p>
      </header>

      <!-- 업로드 카드 -->
      <!-- w-full: 모바일에서 화면 너비에 맞춤 -->
      <!-- aspect-square: 정사각형 비율 유지 -->
      <!-- min-h-[...]: 최소 높이 지정 -->
      <div 
        class="w-full bg-white rounded-[2rem] shadow-xl p-6 border border-gray-100 
               transition-all active:scale-95 cursor-pointer flex flex-col items-center 
               justify-center min-h-[300px] md:min-h-[400px] relative overflow-hidden group"
        @click="triggerFileInput"
      >
        <div v-if="!isLoading" class="flex flex-col items-center relative z-10">
          <div class="w-16 h-16 md:w-20 md:h-20 bg-green-600 text-white rounded-full flex items-center justify-center mb-4 md:mb-6 shadow-lg shadow-red-200">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-8 h-8 md:w-10 md:h-10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/>
              <circle cx="12" cy="13" r="3"/>
            </svg>
          </div>
          <p class="text-xl md:text-2xl font-black text-gray-800 mb-2">사진 찍기</p>
        </div>

        <div v-else class="flex flex-col items-center relative z-10">
          <div class="animate-spin rounded-full h-12 w-12 md:h-16 md:w-16 border-[5px] border-black-100 border-t-purple-600 mb-4 md:mb-6"></div>
          <p class="text-pink-600 font-black text-lg md:text-xl">AI 분석 중...</p>
        </div>

        <input type="file" ref="fileInput" class="hidden" accept="image/*" @change="onFileSelected" />
      </div>
    </div>

    <!-- AI 분석 결과 모달 (반응형 적용 완료) -->
    <div v-if="showModal" class="fixed inset-0 z-[9999] flex items-center justify-center p-4">
      
      <!-- 1. 배경 오버레이 -->
      <div 
        class="absolute inset-0"
        style="background-color: #2D3748; opacity: 1;"
        @click="showModal = false"
      ></div>

      <!-- 2. 모달 컨텐츠 박스 -->
      <!-- w-[90%]: 모바일에서는 화면의 90%만 차지 -->
      <!-- md:w-auto: PC에서는 내용물 크기에 맞춤 -->
      <!-- md:min-w-[600px]: PC 최소 너비 보장 -->
      <!-- max-h-[90vh]: 세로가 너무 길면 스크롤 생기게 -->
      <div class="relative bg-white rounded-[2rem] w-[90%] md:w-auto md:min-w-[600px] max-w-3xl 
                  p-6 md:p-12 shadow-2xl transform transition-all animate-modal-pop border border-gray-100 
                  flex flex-col justify-center overflow-y-auto max-h-[90vh]">
        
        <!-- 모달 헤더 -->
        <div class="flex items-center justify-between mb-8 md:mb-16 border-b-4 border-gray-100 pb-6 md:pb-10">
          <!-- text-3xl (폰) -> text-6xl (PC) -->
          <h3 class="text-3xl md:text-6xl font-black text-gray-900 tracking-tight">✨ 분석 완료</h3>
          <button @click="showModal = false" class="p-2 md:p-6 hover:bg-gray-100 rounded-full text-gray-400 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 md:w-12 md:h-12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
          </button>
        </div>
        
        <div class="space-y-8 md:space-y-12">
          <!-- 상품명 입력 -->
          <div class="space-y-2 md:space-y-5">
            <label class="text-lg md:text-2xl font-black text-[#8d2e2e] uppercase tracking-tight ml-2 md:ml-4">상품명</label>
            <div class="bg-gray-50 rounded-2xl md:rounded-[2.5rem] p-4 md:p-10 border-4 border-transparent focus-within:border-blue-500 transition-all shadow-inner">
              <!-- text-2xl (폰) -> text-5xl (PC) -->
              <input 
                v-model="analysisResult.item" 
                class="w-full bg-transparent font-black text-2xl md:text-5xl text-gray-900 outline-none placeholder-gray-300" 
                placeholder="상품명 입력" 
              />
            </div>
          </div>
          
          <!-- 가격 입력 -->
          <div class="space-y-2 md:space-y-5">
            <label class="text-lg md:text-2xl font-black text-blue-600 uppercase tracking-widest ml-2 md:ml-4">추천 가격</label>
            <div class="bg-gray-50 rounded-2xl md:rounded-[2.5rem] p-4 md:p-10 border-4 border-transparent focus-within:border-blue-500 transition-all flex items-baseline shadow-inner">
              <!-- text-3xl (폰) -> text-6xl (PC) -->
              <input 
                v-model="analysisResult.price" 
                type="number" 
                class="w-full bg-transparent font-black text-3xl md:text-6xl text-gray-900 outline-none placeholder-gray-300" 
              />
              <span class="text-2xl md:text-5xl font-black text-gray-400 ml-2 md:ml-4">원</span>
            </div>
          </div>
        </div>

        <!-- 버튼 -->
        <button 
          @click="confirmRegistration" 
          class="w-full mt-10 md:mt-20 bg-[#3f2323] text-white font-black py-5 md:py-10 
                 rounded-2xl md:rounded-[3rem] text-2xl md:text-4xl shadow-xl shadow-blue-200 
                 hover:bg-blue-700 active:scale-[0.98] transition-all"
        >
          매대에 등록하기
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';

const fileInput = ref(null);
const isLoading = ref(false);
const showModal = ref(false);
const analysisResult = ref({ item: '', price: 0, confidence: 0 });
const selectedFile = ref(null);

const triggerFileInput = () => {
  fileInput.value.click();
};

const onFileSelected = async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  
  selectedFile.value = file;
  isLoading.value = true;
  const formData = new FormData();
  formData.append('image', file);
  
  try {
    // 1. 분석 요청 (저장 X)
    const res = await axios.post('http://127.0.0.1:8000/api/stores/analyze/', formData);
    analysisResult.value = { 
      item: res.data.item || '분석 실패', 
      price: res.data.price || 0, 
      confidence: res.data.confidence || 0.95 
    };
    showModal.value = true;
  } catch (err) {
    console.error("통신 에러:", err);
    alert("서버 연결 실패 (장고가 켜져 있는지 확인하세요)");
  } finally {
    isLoading.value = false;
    event.target.value = '';
  }
};

const confirmRegistration = async () => {
  if (!selectedFile.value) return;

  const formData = new FormData();
  formData.append('image', selectedFile.value);
  formData.append('item', analysisResult.value.item);
  formData.append('price', analysisResult.value.price);
  formData.append('confidence', analysisResult.value.confidence);
  formData.append('title', 'AI 등록 상품'); 

  try {
    // 2. 최종 저장 요청
    await axios.post('http://127.0.0.1:8000/api/stores/', formData);
    alert(`${analysisResult.value.item} 등록이 완료되었습니다!`);
    showModal.value = false;
  } catch (err) {
    console.error("저장 실패:", err);
    alert("저장에 실패했습니다.");
  }
};
</script>

<style scoped>
@keyframes modalPop {
  0% { opacity: 0; transform: scale(0.9) translateY(30px); }
  100% { opacity: 1; transform: scale(1) translateY(0); }
}
.animate-modal-pop { animation: modalPop 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
</style>