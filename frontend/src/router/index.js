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
		path: '/help',
		name: 'Help',
		component: () => import(/* webpackChunkName: "help" */ '../components/Help.vue')
	},
	{
		path: '/status',
		name: 'Status',
		component: () => import(/* webpackChunkName: "status" */ '../components/Status.vue')
	},
	{
		path: '/',
		name: 'Home',
		component: () => import(/* webpackChunkName: "home" */ '../components/Menu.vue')
	},
]

const router = new VueRouter({
  mode: process.env.NODE_ENV === "development" ? 'hash' : 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
