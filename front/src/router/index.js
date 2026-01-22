import { createRouter, createWebHistory } from 'vue-router'
import StoreRegister from '../views/StoreRegister.vue'
import StoreList from '../views/StoreList.vue'
import Test from '../views/Test.vue' 

const routes = [
  {
    path: '/',
    name: 'StoreRegister',
    component: StoreRegister
  },
  {
    path: '/list',
    name: 'StoreList',
    component: StoreList
  },
  { 
    path: '/test',
    name: 'Test',
    component: Test
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL), //(process.env.BASE_URL)
  routes
})

export default router