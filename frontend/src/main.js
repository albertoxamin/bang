import Vue from 'vue'
import App from './App.vue'

Vue.config.productionTip = false
import VueSocketIO from 'vue-socket.io'
Vue.use(new VueSocketIO({
	debug: Vue.config.devtools,
	connection: Vue.config.devtools ? `http://${window.location.hostname}:5001` : window.location.origin,
}))

import PrettyCheckbox from 'pretty-checkbox-vue';
Vue.use(PrettyCheckbox)

new Vue({
  render: h => h(App),
}).$mount('#app')
