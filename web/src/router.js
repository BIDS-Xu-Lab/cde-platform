import { createWebHistory, createRouter } from 'vue-router'

import Homepage from './pages/Homepage.vue'
import Main from './pages/Main.vue'

const routes = [
    { path: '/', component: Homepage },
    { path: '/main', component: Main },
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

export default router