<template>
	<div id="app" class="dark-mode">
		<div v-if="!isInLobby" id="logo" class="center-stuff" style="margin-bottom:10pt;">
			<h1 style="margin-bottom:0pt;">PewPew!</h1>
			<i style="font-size: x-small;">Bang! è un marchio registrato DVGiochi</i>
		</div>
		<div v-if="isConnected">
			<div v-if="!didSetUsername">
				<p>Scegli un username:</p>
				<form @submit="setUsername">
					<input v-model="username" />
					<input type="submit"/>
				</form>
				<p>Giocatori online: {{onlinePlayers}}</p>
			</div>
			<div v-else>
				<div v-if="!isInLobby" >
					<p>Giocatori online: {{onlinePlayers}}</p>
					<Card :card="getSelfCard" style="position:absolute; bottom:10pt; right: 10pt;"/>
					<h2>Lobby disponibili:</h2>
					<div style="display: flex">
						<Card v-for="lobby in openLobbies" v-bind:key="lobby.name" :card="getLobbyCard(lobby)" @click.native="joinLobby(lobby)"/>
						<p v-if="noLobbyAvailable">Nessuna lobby disponibile</p>
					</div>
					<form @submit="createLobby">
						<h2>Crea una lobby:</h2>
						<p>Nome:</p>
						<input v-model="lobbyName"/>
						<input type="submit" />
					</form>
				</div>
				<Lobby v-show="isInLobby" :username="username" />
			</div>
		</div>
		<div v-else class="center-stuff">
			<h2>Attenzione!</h2>
			<p>Connessione al server assente.</p>
		</div>
	</div>
</template>

<script>
import Vue from 'vue'
import Card from './components/Card.vue'
import Lobby from './components/Lobby.vue'

export default {
	name: 'App',
	components: {
		Card,
		Lobby,
	},
	data: () => ({
		isConnected: false,
		didSetUsername: false,
		username: '',
		openLobbies: [],
		lobbyName: '',
		isInLobby: false,
		onlinePlayers: 0,
	}),
	computed: {
		noLobbyAvailable() {
			return this.openLobbies && this.openLobbies.length == 0
		},
		getSelfCard() {
			return {
				name: this.username,
				number: 'YOU',
				icon: '🤠',
				is_character: true,
			}
		},
	},
	sockets: {
		connect() {
			this.isConnected = true;
			document.title = 'PewPew!'
			if (Vue.config.devtools) {
				setTimeout(function(){
					this.username =(1+Math.random() * 100 % 100).toFixed(2).toString();
					this.setUsername();
				}.bind(this), 1000)
			}
		},
		disconnect() {
			this.isConnected = false;
		},
		lobbies(data) {
			this.openLobbies = data;
		},
		room() {
			this.isInLobby = true;
		},
		players(num) {
			this.onlinePlayers = num;
		}
	},
	methods: {
		setUsername(e){
			this.didSetUsername = true
			this.$socket.emit('set_username', this.username)
			e.preventDefault();
		},
		getLobbyCard(lobby) {
			return {
				name: lobby.name,
				icon: "💥",
				number: `${lobby.players}🤠`,
				is_equipment: true,
			}
		},
		createLobby(e) {
			if (this.lobbyName.trim().length > 0) {
				this.$socket.emit('create_room', this.lobbyName)
			}
			e.preventDefault();
		},
		joinLobby(lobby) {
			this.$socket.emit('join_room', lobby.name)
		},
		init() {
			location.reload();
		},
	}
}
</script>

<style>
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
h1,h2,h3,h4,p,span{
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
input {
  border: 2px solid;
  border-radius: 4px;
  font-size: 1rem;
  margin: 0.25rem;
  min-width: 125px;
  padding: 0.5rem;
  transition: border-color 0.5s ease-out;
}
@media (prefers-color-scheme: dark) {
	:root, #app, input {
    background-color: #181a1b;
    color: rgb(174, 194, 211);
  }
}
</style>
