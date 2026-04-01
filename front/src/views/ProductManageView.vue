<template>
    <div v-if="isOwnerChecked" class="product-page">
      <h2 class="page-title">📚 빵 사전 / 상품 관리</h2>
  
      <div class="top-actions">
        <button class="back-btn" @click="goOwnerPage">← 사장님 메뉴로</button>
      </div>
  
      <!-- 등록 / 수정 폼 -->
      <div class="form-card">
        <h3 class="section-title">{{ isEditMode ? '상품 수정' : '새 상품 등록' }}</h3>
  
        <form class="product-form" @submit.prevent="submitProduct">
          <div class="form-group">
            <label>상품명</label>
            <input v-model="form.display_name" type="text" placeholder="예: 소금빵" required />
          </div>
  
          <div class="form-group">
            <label>AI 카테고리명</label>
            <input v-model="form.category_name" type="text" placeholder="예: saltbread, soboro, redbean" />
          </div>
  
          <div class="form-group">
            <label>정가</label>
            <input v-model="form.price" type="number" min="0" placeholder="예: 3000" required />
          </div>
  
          <div class="form-group">
            <label>사용 여부</label>
            <select v-model="form.is_active">
              <option :value="true">사용</option>
              <option :value="false">미사용</option>
            </select>
          </div>
  
          <div class="form-group">
            <label>대표 사진</label>
            <input type="file" accept="image/*" @change="handleImageChange" />
          </div>
  
          <div class="form-group">
            <label>빵 + 네임택 사진</label>
            <input type="file" accept="image/*" @change="handleLabelImageChange" />
          </div>
  
          <div class="preview-row" v-if="imagePreview || labelImagePreview">
            <div v-if="imagePreview" class="preview-box">
              <p>대표 사진 미리보기</p>
              <img :src="imagePreview" alt="대표 사진 미리보기" />
            </div>
  
            <div v-if="labelImagePreview" class="preview-box">
              <p>네임택 포함 사진 미리보기</p>
              <img :src="labelImagePreview" alt="네임택 포함 사진 미리보기" />
            </div>
          </div>
  
          <div class="form-buttons">
            <button type="submit" class="submit-btn">
              {{ isEditMode ? '수정 완료' : '상품 등록' }}
            </button>
  
            <button
              v-if="isEditMode"
              type="button"
              class="cancel-btn"
              @click="resetForm"
            >
              수정 취소
            </button>
          </div>
        </form>
      </div>
  
      <!-- 목록 -->
      <div class="list-card">
        <div class="list-header">
          <h3 class="section-title">등록된 상품 목록</h3>
          <button class="refresh-btn" @click="fetchProducts">새로고침</button>
        </div>
  
        <div v-if="loading" class="empty-text">불러오는 중...</div>
        <div v-else-if="products.length === 0" class="empty-text">
          아직 등록된 상품이 없습니다.
        </div>
  
        <div v-else class="product-grid">
          <div v-for="product in products" :key="product.id" class="product-card">
            <div class="card-top">
              <div>
                <h4 class="product-name">{{ product.display_name }}</h4>
                <p class="product-meta">AI 카테고리: {{ product.category_name || '-' }}</p>
                <p class="product-meta">정가: {{ Number(product.price).toLocaleString() }}원</p>
                <p class="product-meta">
                  상태:
                  <span :class="product.is_active ? 'active-text' : 'inactive-text'">
                    {{ product.is_active ? '사용' : '미사용' }}
                  </span>
                </p>
              </div>
            </div>
  
            <div class="image-row">
              <div class="image-box">
                <p>대표 사진</p>
                <img
                  v-if="product.image"
                  :src="getImageUrl(product.image)"
                  alt="대표 사진"
                />
                <div v-else class="no-image">사진 없음</div>
              </div>
  
              <div class="image-box">
                <p>네임택 포함 사진</p>
                <img
                  v-if="product.label_image"
                  :src="getImageUrl(product.label_image)"
                  alt="네임택 포함 사진"
                />
                <div v-else class="no-image">사진 없음</div>
              </div>
            </div>
  
            <div class="card-buttons">
              <button class="edit-btn" @click="startEdit(product)">수정</button>
              <button class="delete-btn" @click="deleteProduct(product.id)">삭제</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import api from '@/api'
  
  const router = useRouter()
  
  const isOwnerChecked = ref(false)
  const loading = ref(false)
  const products = ref([])
  const isEditMode = ref(false)
  const editingProductId = ref(null)
  
  const form = ref({
    display_name: '',
    category_name: '',
    price: '',
    is_active: true,
  })
  
  const imageFile = ref(null)
  const labelImageFile = ref(null)
  
  const imagePreview = ref('')
  const labelImagePreview = ref('')
  
  const goOwnerPage = () => {
    router.push('/mypage-owner')
  }
  
  const checkOwner = () => {
    const userRole = localStorage.getItem('userRole')
  
    if (userRole === 'owner') {
      isOwnerChecked.value = true
    } else {
      alert('사장님만 접근 가능한 페이지입니다!')
      router.push('/mypage')
    }
  }
  
  const getImageUrl = (path) => {
    if (!path) return ''
    if (path.startsWith('http')) return path
  
    return `http://127.0.0.1:8000${path}`
  }
  
  const handleImageChange = (event) => {
    const file = event.target.files[0]
    imageFile.value = file || null
  
    if (file) {
      imagePreview.value = URL.createObjectURL(file)
    } else {
      imagePreview.value = ''
    }
  }
  
  const handleLabelImageChange = (event) => {
    const file = event.target.files[0]
    labelImageFile.value = file || null
  
    if (file) {
      labelImagePreview.value = URL.createObjectURL(file)
    } else {
      labelImagePreview.value = ''
    }
  }
  
  const fetchProducts = async () => {
    loading.value = true
    try {
      const res = await api.get('/api/products/')
      products.value = res.data
    } catch (err) {
      alert('상품 목록을 불러오지 못했습니다.')
    } finally {
      loading.value = false
    }
  }
  
  const resetForm = () => {
    form.value = {
      display_name: '',
      category_name: '',
      price: '',
      is_active: true,
    }
  
    imageFile.value = null
    labelImageFile.value = null
    imagePreview.value = ''
    labelImagePreview.value = ''
  
    isEditMode.value = false
    editingProductId.value = null
  }
  
  const submitProduct = async () => {
    try {
      const formData = new FormData()
      formData.append('display_name', form.value.display_name)
      formData.append('category_name', form.value.category_name)
      formData.append('price', form.value.price)
      formData.append('is_active', form.value.is_active)
  
      if (imageFile.value) {
        formData.append('image', imageFile.value)
      }
  
      if (labelImageFile.value) {
        formData.append('label_image', labelImageFile.value)
      }
  
      if (isEditMode.value && editingProductId.value) {
        await api.patch(`/api/products/${editingProductId.value}/`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })
        alert('상품이 수정되었습니다.')
      } else {
        await api.post('/api/products/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })
        alert('상품이 등록되었습니다.')
      }
  
      resetForm()
      fetchProducts()
    } catch (err) {
      alert(JSON.stringify(err.response?.data || '상품 저장 실패'))
    }
  }
  
  const startEdit = (product) => {
    isEditMode.value = true
    editingProductId.value = product.id
  
    form.value = {
      display_name: product.display_name || '',
      category_name: product.category_name || '',
      price: product.price || '',
      is_active: product.is_active,
    }
  
    imagePreview.value = product.image ? getImageUrl(product.image) : ''
    labelImagePreview.value = product.label_image ? getImageUrl(product.label_image) : ''
  
    imageFile.value = null
    labelImageFile.value = null
  
    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    })
  }
  
  const deleteProduct = async (productId) => {
    const ok = confirm('정말 이 상품을 삭제하시겠습니까?')
    if (!ok) return
  
    try {
      await api.delete(`/api/products/${productId}/`)
      alert('상품이 삭제되었습니다.')
  
      // 수정 중이던 상품을 삭제한 경우 폼 초기화
      if (editingProductId.value === productId) {
        resetForm()
      }
  
      fetchProducts()
    } catch (err) {
      alert('상품 삭제에 실패했습니다.')
    }
  }
  
  onMounted(() => {
    checkOwner()
    fetchProducts()
  })
  </script>
  
  <style scoped>
  .product-page {
    min-height: 100vh;
    background: #F4E2D0;
    padding: 20px;
  }
  
  .page-title {
    font-family: 'Black Han Sans', sans-serif;
    font-size: 3rem;
    text-align: center;
    color: #3A5635;
    margin-bottom: 30px;
    -webkit-text-stroke: 0.2px #202020;
  }
  
  .top-actions {
    max-width: 1200px;
    margin: 0 auto 20px;
    display: flex;
    justify-content: flex-start;
  }
  
  .back-btn {
    background: white;
    border: 3px solid #222;
    border-radius: 10px;
    padding: 10px 16px;
    font-weight: 900;
    cursor: pointer;
    box-shadow: 4px 4px 0 #222;
  }
  
  .form-card,
  .list-card {
    max-width: 1200px;
    margin: 0 auto 25px;
    background: white;
    border: 3px solid #222;
    border-radius: 20px;
    box-shadow: 8px 8px 0 #222;
    padding: 25px;
  }
  
  .section-title {
    font-family: 'Black Han Sans', sans-serif;
    font-size: 1.8rem;
    margin-bottom: 20px;
    color: #222;
  }
  
  .product-form {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
  }
  
  .form-group {
    display: flex;
    flex-direction: column;
  }
  
  .form-group label {
    font-weight: 900;
    margin-bottom: 8px;
    color: #333;
  }
  
  .form-group input,
  .form-group select {
    border: 2px solid #222;
    border-radius: 10px;
    padding: 12px;
    font-size: 1rem;
  }
  
  .preview-row {
    grid-column: 1 / -1;
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
  }
  
  .preview-box {
    width: 220px;
  }
  
  .preview-box p {
    font-weight: 800;
    margin-bottom: 8px;
  }
  
  .preview-box img {
    width: 100%;
    height: 180px;
    object-fit: cover;
    border: 2px solid #222;
    border-radius: 12px;
    background: #fafafa;
  }
  
  .form-buttons {
    grid-column: 1 / -1;
    display: flex;
    gap: 12px;
    margin-top: 10px;
  }
  
  .submit-btn,
  .cancel-btn,
  .refresh-btn,
  .edit-btn,
  .delete-btn {
    border: 3px solid #222;
    border-radius: 10px;
    padding: 10px 16px;
    font-weight: 900;
    cursor: pointer;
    box-shadow: 4px 4px 0 #222;
  }
  
  .submit-btn {
    background: #3A5635;
    color: white;
  }
  
  .cancel-btn {
    background: #ddd;
    color: #222;
  }
  
  .refresh-btn {
    background: #fff;
  }
  
  .edit-btn {
    background: #5B7CFA;
    color: white;
  }
  
  .delete-btn {
    background: #D9534F;
    color: white;
  }
  
  .list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 18px;
  }
  
  .empty-text {
    text-align: center;
    font-weight: 800;
    color: #666;
    padding: 30px 0;
  }
  
  .product-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 20px;
  }
  
  .product-card {
    border: 3px solid #222;
    border-radius: 16px;
    padding: 18px;
    background: #fffaf5;
    box-shadow: 5px 5px 0 #222;
  }
  
  .product-name {
    font-size: 1.5rem;
    font-weight: 900;
    color: #D57B0E;
    margin-bottom: 10px;
  }
  
  .product-meta {
    margin: 6px 0;
    font-weight: 700;
    color: #333;
  }
  
  .active-text {
    color: #2E8B57;
    font-weight: 900;
  }
  
  .inactive-text {
    color: #D9534F;
    font-weight: 900;
  }
  
  .image-row {
    display: flex;
    gap: 12px;
    margin-top: 15px;
    flex-wrap: wrap;
  }
  
  .image-box {
    flex: 1;
    min-width: 140px;
  }
  
  .image-box p {
    font-weight: 800;
    margin-bottom: 8px;
  }
  
  .image-box img {
    width: 100%;
    height: 140px;
    object-fit: cover;
    border: 2px solid #222;
    border-radius: 12px;
    background: #fafafa;
  }
  
  .no-image {
    height: 140px;
    border: 2px dashed #999;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #888;
    background: #f8f8f8;
  }
  
  .card-buttons {
    display: flex;
    gap: 10px;
    margin-top: 18px;
  }
  
  @media (max-width: 768px) {
    .page-title {
      font-size: 2.2rem;
    }
  
    .product-form {
      grid-template-columns: 1fr;
    }
  
    .list-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 10px;
    }
  }
  </style>