import { createRouter, createWebHistory } from 'vue-router'
import StoreMain from '../views/StoreMain.vue'//알바용 메일화면
import StoreRegister from '../views/StoreRegister.vue' //알바용 등록
import StoreList from '../views/StoreList.vue' //알바용 재고관리
import Store_Pickup from '../views/Store_Pickup.vue' // 알바용 픽업
import Test from '../views/Test.vue' 
import CustomerMain from '../views/CustomerMain.vue' // 손님용 메인화면
import CartView from '../views/CartView.vue' //손님용 장바구니화면
import PickupComView from '../views/PickupComView.vue'
import PickupView from '@/views/PickupView.vue'
import LoginView from '@/views/LoginView.vue'
import SignupView from '@/views/SignupView.vue'
import MyOrderView from '@/views/MyOrderView.vue'
import MyPageView from '@/views/MyPageView.vue';
import MyPageOwner from '@/views/MyPageOwner.vue'
import ProductManageView from '@/views/ProductManageView.vue'

const routes = [
  { // 회원가입
    path: '/signup',        //브라우저에 뜨는 이름
    name: 'signup',     //코드에서 부르는 이름
    component: SignupView   //가져온 회원가입 컴포넌트 파일
  },
  { // 로그인
    path: '/login',
    name: 'Login',
    component: LoginView
  },
  { // 알바용 메인화면
    path: '/main',
    name: 'StoreMain',
    component: StoreMain
  },
  { // 알바용 등록
    path: '/register',
    name: 'StoreRegister',
    component: StoreRegister
  },
  { //알바용 재고관리
    path: '/admin-list',
    name: 'StoreList',
    component: StoreList
  },
  { // 알바용 픽업
    path: '/store-pickup',
    name: 'Store_Pickup',
    component: Store_Pickup
  },
  { // 테숫뚜 페이징
    path: '/test',
    name: 'Test',
    component: Test
  },
  { // 손님용 메인화면
    path: '/',
    name: 'CustomerMain',
    component: CustomerMain
  },
  { // 손님용 장바구니화면
    path: '/cart',
    name: 'CartView',
    component: CartView
  },
  { // 손님용 픽업화면
    path: '/pickup',
    name: 'Pickupview', 
    component: PickupView

  },
  { // 손님용 픽업완료 화면
    path: '/pickup-com',
    name: 'PickupComView',
    component: PickupComView
  },
  { // 나의 빵 기록
    path: '/mypage',          
    name: 'MyPage',
    component: MyPageView    
  },
  { // 나의 빵 기록??????????????????????????????/
    path: '/ordered-list',
    name: 'my-orders',
    component: MyOrderView
  },
  { // 마이페이지_사장님계정
    path: '/mypage-owner',
    name: 'MyPageOwner',
    component: MyPageOwner
  }, 
  { // 빵 사전_사장님용
    path: '/product-manage',
    name: 'ProductManageView',
    component: ProductManageView,
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router