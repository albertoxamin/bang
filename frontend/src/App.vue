<template>
	<div id="app">
		<div v-if="isConnected">
			<router-view></router-view>
		</div>
		<div v-else class="center-stuff">
			<h2>{{$t("warning")}}</h2>
			<p>{{$t("connection_error")}}</p>
		</div>
		<help v-if="showHelp"/>
		<div style="position:fixed;bottom:4pt;right:4pt;display:flex;">
			<input type="button" class="btn" value="Discord" style="min-width:28pt;cursor:pointer;" @click="joinDiscord"/>
			<input type="button" class="btn" :value="(showHelp?'X':'?')" style="min-width:28pt;border-radius:100%;cursor:pointer;" @click="getHelp"/>
			<select id="theme" class="btn" v-model="theme">
				<option
					v-for="(theme, i) in ['light.☀️.Light', 'dark.🌙️.Dark', 'sepia..Sepia', 'grayscale..Grayscale']"
					:key="`theme-${i}`"
					:value="theme.split('.')[0]">
						{{theme.split('.')[1]}} {{theme.split('.')[2]}}
				</option>
			</select>
			<select id="lang" class="btn" v-model="$i18n.locale" @change="storeLangPref">
				<option
					v-for="(lang, i) in ['it.🇮🇹.Italiano', 'en.🇬🇧.English']"
					:key="`lang-${i}`"
					:value="lang.split('.')[0]">
						{{lang.split('.')[1]}} {{lang.split('.')[2]}}
				</option>
			</select>
		</div>
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
import Help from './components/Help.vue';
// import Vue from 'vue'

export default {
  components: { Help },
	name: 'App',
	data: () => ({
		isConnected: false,
		c: false,
		showUpdateUI: false,
		showHelp:false,
		theme: 'light',
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
				this.$router.replace({path:'game', query: { code: data.name, pwd: data.password }}).catch(()=>{});
			else
				this.$router.replace({path:'game', query: { code: data.name }}).catch(()=>{});
		},
	},
	methods: {
		getHelp() {
			this.showHelp = !this.showHelp
			// window.open(`${window.location.origin}/help`, '_blank')
		},
		storeLangPref() {
			localStorage.setItem('lang', this.$i18n.locale);
			document.documentElement.lang = this.$i18n.locale;
		},
		async update() {
			this.showUpdateUI = false;
			await this.$workbox.messageSW({ type: "SKIP_WAITING" });
		},
		detectColorScheme() {
			if(localStorage.getItem("theme")){
				this.theme = localStorage.getItem("theme")
				console.log("Found theme preference: " + this.theme)
			} else if(!window.matchMedia) {
				console.log("Auto theme not supported")
			} else if(window.matchMedia("(prefers-color-scheme: dark)").matches) {
				console.log("Prefers dark mode")
				this.theme = "dark";
			}
		},
		joinDiscord() {
			window.open('https://discord.gg/Dr58dZ2na8', '_blank');
		}
	},
	watch: {
		theme() {
			document.documentElement.setAttribute("data-theme", this.theme);
			localStorage.setItem('theme', this.theme)
		}
	},
	mounted() {
		if (localStorage.getItem('lang')) {
			this.$i18n.locale = localStorage.getItem('lang');
			document.documentElement.lang = this.$i18n.locale;
		}
		this.detectColorScheme()
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
html {
	scroll-behavior: smooth;
}
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
		zoom: 0.75;
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
:root {
	--font-color: #2c3e50;
	--bg-color: white;
	--muted-color: #ccc;
}
[data-theme="dark"] {
	--font-color: rgb(174, 194, 211);
	--bg-color: #181a1b;
}
[data-theme="sepia"] {
	--font-color: rgb(54, 43, 33);
	--bg-color: #e7d6bb;
	--muted-color: rgba(54, 43, 33, 0.5);
}
[data-theme="grayscale"] {
	--font-color: rgb(66, 66, 66);
	--bg-color: #e2e0e0;
	--muted-color: rgba(66, 66, 66, 0.5);
}
html, #app, input, select {
	background-color: var(--bg-color);
	color: var(--font-color);
}

.btn {
	background-color: var(--bg-color);
	color: var(--font-color);
	border: 2px solid var(--font-color);
	border-radius: 12pt;
	cursor: pointer;
	transition: all 0.13s ease-in-out;
	-webkit-appearance: none;
	-moz-appearance: none;
	appearance: none;
}
.btn:hover:not([disabled]) {
	background-color: var(--font-color); /* Green */
	color: var(--bg-color);
}
.btn:disabled {
	cursor: not-allowed;
}
</style>
