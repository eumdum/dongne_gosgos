import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import './index.css' // Tailwind CSS

createApp(App)
  .use(store)
  .use(router)
  .mount('#app')
// import { createApp } from 'vue'
// import App from './App.vue'
// import router from './router'
// import './assets/main.css'

// const app = createApp(App)

// app.use(router)

// app.mount('#app')
