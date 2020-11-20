<template>
	<div id="app">
		<div id="logo" class="center-stuff" style="margin-bottom:10pt;">
			<h1 style="margin-bottom:0pt;">PewPew!</h1>
			<i style="font-size: x-small;">Bang! è un marchio registrato DVGiochi</i>
		</div>
		<div v-if="isConnected">
			<div v-if="!didSetUsername">
				Scegli un username:
				<form @submit="setUsername">
					<input v-model="username" />
					<input type="submit"/>
				</form>
			</div>
			<div v-else>
				<div v-if="!isInLobby" >
					<Card :card="getSelfCard"/>
					<form @submit="createLobby">
						<h2>Crea una lobby:</h2>
						Nome: <input v-model="lobbyName"/>
						<input type="submit" />
					</form>
					<h2>Lobby disponibili:</h2>
					<div style="display: flex">
						<Card v-for="lobby in openLobbies" v-bind:key="lobby.name" :card="getLobbyCard(lobby)" @click.native="joinLobby(lobby)"/>
						<p v-if="noLobbyAvailable">Nessuna lobby disponibile</p>
					</div>
				</div>
				<Lobby :username="username" v-else/>
			</div>
		</div>
		<div v-else class="center-stuff">
			<h2>Attenzione!</h2>
			<p>Connessione al server assente.</p>
		</div>
	</div>
</template>

<script>
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
		},
		disconnect() {
			this.isConnected = false;
		},
		lobbies(data) {
			this.openLobbies = data;
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
				number: lobby.players,
				suit: '🤠',
				is_equipment: true,
			}
		},
		createLobby(e) {
			if (this.lobbyName.trim().length > 0) {
				this.$socket.emit('create_room', this.lobbyName)
				this.isInLobby = true; 
			}
			e.preventDefault();
		},
		joinLobby(lobby) {
			this.$socket.emit('join_room', lobby.name)
			this.isInLobby = true;
		},
		// room() {
		// },
	}
}
</script>

<style>
#app {
	font-family: Avenir, Helvetica, Arial, sans-serif;
	-webkit-font-smoothing: antialiased;
	-moz-osx-font-smoothing: grayscale;
	color: #2c3e50;
	margin: 60px;
}
.center-stuff {
	margin-left: auto;
	margin-right: auto;
	left: 0;
	right: 0;
	text-align: center;
}
</style>
