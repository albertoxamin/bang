<template>
	<div id="app" class="dark-mode">
		<div v-if="isConnected">
			<router-view></router-view>
		</div>
		<div v-else class="center-stuff">
			<h2>{{$t("warning")}}</h2>
			<p>{{$t("connection_error")}}</p>
		</div>
		<select id="lang" style="position:fixed;bottom:4pt;right:4pt;" v-model="$i18n.locale" @change="storeLangPref">
			<option
				v-for="(lang, i) in ['it.🇮🇹.Italiano', 'en.🇬🇧.English']"
				:key="`lang-${i}`"
				:value="lang.split('.')[0]">
					{{lang.split('.')[1]}} {{lang.split('.')[2]}}
			</option>
		</select>
		<label for="lang" style="opacity:0" >Language</label>
		<div v-if="showUpdateUI" style="position: fixed;bottom: 0;z-index: 1;background: rgba(0,0,0,0.5);padding: 20pt;" class="center-stuff">
			<p class="update-dialog__content">
				A new version is available. Refresh to load it?
			</p>
			<div class="update-dialog__actions">
				<button @click="update">Update</button>
				<button @click="showUpdateUI = false">Cancel</button>
			</div>
		</div>
	</div>
</template>

<script>
// import Vue from 'vue'

export default {
	name: 'App',
	data: () => ({
		isConnected: false,
		c: false,
		showUpdateUI: false,
	}),
	computed: {
	},
	sockets: {
		connect() {
			this.isConnected = true;
			document.title = 'PewPew!'
		},
		disconnect() {
			this.isConnected = false;
		},
		room(data) {
			this.isInLobby = true;
			if (data.password)
				this.$router.replace({path:'game', query: { code: data.name, pwd: data.password }})
			else
				this.$router.replace({path:'game', query: { code: data.name }})
		},
	},
	methods: {
		storeLangPref() {
			localStorage.setItem('lang', this.$i18n.locale)
		},
		async update() {
			this.showUpdateUI = false;
			await this.$workbox.messageSW({ type: "SKIP_WAITING" });
		}
	},
	mounted() {
		if (localStorage.getItem('lang'))
			this.$i18n.locale = localStorage.getItem('lang')
	},
	created() {
		if (this.$workbox) {
			this.$workbox.addEventListener("waiting", () => {
				this.showUpdateUI = true;
			});
		}
	}
}
</script>

<style>
@import '../node_modules/pretty-checkbox/dist/pretty-checkbox.css';
#app {
	-webkit-font-smoothing: antialiased;
	-moz-osx-font-smoothing: grayscale;
	color: #2c3e50;
	margin: 16pt;
	-webkit-user-select: none;  /* Chrome all and Safari all */
	-moz-user-select: none;     /* Firefox all */
	-ms-user-select: none;      /* Internet Explorer 10 and later */
	user-select: none;          /* Likely future */
}
.selectable {
	-webkit-user-select: text !important;  /* Chrome all and Safari all */
	-moz-user-select: text !important;     /* Firefox all */
	-ms-user-select: text !important;      /* Internet Explorer 10 and later */
	user-select: text !important;          /* Likely future */
}
#logo {
	margin-top: 60pt;
	margin-bottom: 60pt !important;
}
@media only screen and (max-width:600px) {
	#app {
		margin: 4pt;
		margin-top: -16pt;
		zoom: 0.8;
	}
}
h1,h2,h3,h4,p,span,b,label{
	font-family: Avenir, Helvetica, Arial, sans-serif;
}
.center-stuff {
	margin-left: auto;
	margin-right: auto;
	left: 0;
	right: 0;
	text-align: center;
}
.list-enter-active, .list-leave-active {
	transition: all 0.5s;
}
.list-enter, .list-leave-to /* .list-leave-active below version 2.1.8 */ {
	opacity: 0;
	transform: translateY(30px);
}
.fade-enter-active, .fade-leave-active {
	transition: opacity 0.25s ease-out;
}

.fade-enter, .fade-leave-to {
	opacity: 0;
}

.bounce-enter-active, .bounce-leave-active {
	animation: bounce-in .5s;
}

.fade-enter, .bounce-leave-to {
	animation: bounce-out .5s;
}
@keyframes bounce-in {
	0% {
		transform: scale(0);
	}
	50% {
		transform: scale(1.2);
	}
	100% {
		transform: scale(1);
	}
}
@keyframes bounce-out {
	0% {
		transform: scale(1);
	}
	50% {
		transform: scale(1.1);
	}
	100% {
		transform: scale(0);
	}
}
input, select {
	border: 2px solid;
	border-radius: 4px;
	font-size: 1rem;
	margin: 0.25rem;
	min-width: 125px;
	padding: 0.5rem;
	transition: border-color 0.5s ease-out;
}
input:disabled {
	opacity: 0.5;
}
@media (prefers-color-scheme: dark) {
	:root, #app, input, select {
		background-color: #181a1b;
		color: rgb(174, 194, 211);
	}
}
</style>
