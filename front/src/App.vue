<template>
  <div class="min-h-screen bg-gray-100">
    <header class="bg-[#68ac97] text-white p-4 shadow-md">
      <div class="container mx-auto flex justify-between items-center">
        <!-- <h1 class="text-xl font-bold">감정분석 음악추천 일기</h1> -->
      </div>
    </header>
    
    <main>
      <router-view />
    </main>
    
    <footer class="bg-gray-800 text-white p-4 mt-8">
      <div class="container mx-auto text-center">
        <!-- <p>© 2023 감정분석 음악추천 일기 앱</p> -->
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
/* 전역 스타일 */
body {
  /* 메인 컬러보다 아주 연한 톤으로 설정해 가독성을 높임 */
  background-color: #a8b69a; 
  font-family: 'Pretendard', 'Noto Sans KR', sans-serif;
  margin: 0;
  color: #333;
}

#app {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* 모든 페이지에서 사용할 수 있는 컬러 변수 */
:root {
  --primary-color: #869a69;
  --text-dark: #333;
  --text-light: #f5f5f5;
  --bg-light: #ffffff;
  --border-color: #e5e7eb;
}
</style>
