import { createWebHistory, createRouter } from 'vue-router'

import Homepage from './pages/Homepage.vue'
import Main from './pages/Main.vue'
import Login from './pages/Login.vue'

const routes = [
    { path: '/', component: Homepage },
    { path: '/main', component: Main },
    { path: '/login', component: Login },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router