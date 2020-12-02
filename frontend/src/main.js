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
import VueClipboard from 'vue-clipboard2'
Vue.use(VueClipboard)

import VueI18n from 'vue-i18n'
Vue.use(VueI18n)

import { languages, defaultLocale } from './i18n';
import './registerServiceWorker'
import router from './router'
const messages = Object.assign(languages)

const i18n = new VueI18n({
  locale: defaultLocale,
  messages
})

new Vue({
  i18n,
  router,
  render: h => h(App)
}).$mount('#app')
