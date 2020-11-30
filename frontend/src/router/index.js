import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

const routes = [
	{
		path: '/game',
		name: 'Game',
		component: () => import(/* webpackChunkName: "game" */ '../components/Lobby.vue')
	},
	{
		path: '/',
		name: 'Home',
		component: () => import(/* webpackChunkName: "game" */ '../components/Menu.vue')
	},
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
