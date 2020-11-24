import Vue from 'vue'
import App from './App.vue'

Vue.config.productionTip = false
import VueSocketIO from 'vue-socket.io'
Vue.use(new VueSocketIO({
	debug: Vue.config.devtools,
	connection: Vue.config.devtools?'http://localhost:5001':process.env.BACKEND,
}))

new Vue({
  render: h => h(App),
}).$mount('#app')
