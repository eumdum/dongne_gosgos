<template>
  <div class="admin-container">
    <header class="admin-header">
      <h1>관리자 모드</h1>
    </header>

    <main class="admin-grid">
      <router-link to="/register" class="admin-card wide">
        <span class="icon">📸</span>
        <span class="label">할인 빵 등록</span>
      </router-link>

      <div class="half-grid">
        <router-link to="/admin-list" class="admin-card">
          <span class="icon">📦</span>
          <span class="label">재고 관리</span>
        </router-link>

        <router-link to="/store-pickup" class="admin-card">
          <span class="icon">🛍️</span>
          <span class="label">픽업 관리</span>
        </router-link>
      </div>
    </main>
  </div>
</template>

<style scoped>
.admin-container {
  min-height: 100vh;
  background-color: #a8b69a;
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  font-family: 'Pretendard', sans-serif;
}

.admin-header {
  text-align: center;
  margin-bottom: 40px;
  margin-top: 15px;
}

.admin-header h1 {
  font-size: 28px;
  font-weight: 900;
  color: #111827;
  margin-bottom: 5px;
}

.admin-grid {
  width: 100%;
  max-width: 400px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.admin-card {
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 24px;
  text-decoration: none;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.admin-card.wide {
  height: 160px;
  border-color: #10b981;
}

.admin-card:active {
  transform: scale(0.95);
}

.half-grid {
  display: grid;
  /* grid-template-columns: 1fr 1fr; */
  gap: 16px;
}

.admin-card:not(.wide) {
  height: 160px;
}

.admin-card:nth-child(1) { border-color: #f59e0b; }
.admin-card:nth-child(2) { border-color: #f59e0b; }

.icon { font-size: 40px; margin-bottom: 12px; }
.label { font-size: 18px; font-weight: 800; color: #374151; }

.admin-footer {
  margin-top: auto;
  padding: 20px;
  color: #9ca3af;
  font-size: 12px;
}
</style>