import Vue from 'vue'
import App from './App.vue'
import { registerSW } from 'virtual:pwa-register'

registerSW({ immediate: true })

Vue.config.productionTip = false
import VueSocketIO from 'bang-vue-socket.io'
if (window.localStorage.getItem('connect-dev')) {
	Vue.use(new VueSocketIO({
		debug: true,
		connection: window.localStorage.getItem('connect-dev'),
	}))
}	else {
	Vue.use(new VueSocketIO({
		debug: Vue.config.devtools,
		connection: (Vue.config.devtools) ? `http://${window.location.hostname}:5001` : window.location.origin,
	}))
}

import PrettyCheckbox from 'pretty-checkbox-vue';
Vue.use(PrettyCheckbox)
import VueClipboard from 'vue-clipboard2'
Vue.use(VueClipboard)

Vue.directive('focus', {
	inserted: function (el) {
			el.focus()
	}
})

import VueI18n from 'vue-i18n'
Vue.use(VueI18n)

import { languages, defaultLocale, fallbackLocale } from './i18n';
import router from './router'
const messages = Object.assign(languages)

const i18n = new VueI18n({
  locale: defaultLocale,
	messages,
	fallbackLocale: fallbackLocale
})

new Vue({
  i18n,
  router,
  render: h => h(App)
}).$mount('#app')
