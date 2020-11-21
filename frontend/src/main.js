import Vue from 'vue'
import App from './App.vue'

Vue.config.productionTip = false
import VueSocketIO from 'vue-socket.io'
Vue.use(new VueSocketIO({
	debug: true,
	connection: Vue.config.devtools?'http://localhost:5001':'http://51.15.199.193:5001',
}))

new Vue({
  render: h => h(App),
}).$mount('#app')
