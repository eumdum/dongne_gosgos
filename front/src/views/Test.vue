<template>
  <!-- 1. 전체 배경: 파란색(#DBEAFE)이 나와야 함 -->
  <div class="min-h-screen bg-blue-100 flex flex-col items-center justify-center space-y-5">
    
    <!-- 2. 글자: 빨간색, 아주 커야 함 -->
    <h1 class="text-5xl font-bold text-red-600 border-4 border-black p-4">
      테일윈드 생존 확인
    </h1>

    <p class="text-xl text-gray-700">
      아래 초록색 버튼을 눌러보세요.
    </p>

    <!-- 3. 버튼: 초록색 배경, 마우스 올리면 진한 초록색으로 변해야 함 -->
    <button 
      @click="showModal = true" 
      class="px-8 py-4 bg-green-500 hover:bg-green-700 text-white font-bold rounded-full shadow-2xl transition-all"
    >
      모달 열기 (작동 테스트)
    </button>

    <!-- 4. 모달 영역 -->
    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center">
      
      <!-- 
        [중요 체크포인트] 
        bg-black/80: 뒤쪽이 아주 어두운 검은색(80% 불투명)이어야 함.
        backdrop-blur-sm: 뒷배경이 흐릿하게 보여야 함.
      -->
      <div 
        class="absolute inset-0 bg-black/80 backdrop-blur-sm"
        @click="showModal = false"
      ></div>

      <!-- 모달 박스: 흰색 배경, 둥근 모서리 -->
      <div class="relative bg-white p-10 rounded-3xl shadow-xl text-center max-w-sm w-full">
        <h2 class="text-3xl font-black text-purple-600 mb-4">테스트 성공! 🎉</h2>
        <p class="text-gray-600 mb-6">
          1. 뒤쪽이 어둡고 흐린가요?<br>
          2. 이 박스가 흰색인가요?<br>
          3. 글씨가 보라색인가요?
        </p>
        <button 
          @click="showModal = false"
          class="w-full py-3 bg-gray-800 text-white rounded-xl hover:bg-black"
        >
          닫기
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue';

const showModal = ref(false);
</script>