<template>
	<div id="app">
		<div v-if="isConnected">
			<div v-if="!didSetUsername">
				Scegli un username:
				<div>
					<input v-model="username"/>
					<input type="submit" @click="setUsername"/>
				</div>
			</div>
			<div v-else>
				<div v-if="!isInLobby" >
					<h2>Crea una lobby:</h2>
					Nome: <input v-model="lobbyName"/>
					<input type="submit" @click="createLobby"/>
				</div>
				<Card v-for="lobby in openLobbies" v-bind:key="lobby" :card="lobby"/>
			</div>
		</div>
		<div v-else>
			<h2>Attenzione!</h2>
			<p>Connessione al server assente.</p>
		</div>
	</div>
</template>

<script>
import Card from './components/Card.vue'

export default {
	name: 'App',
	components: {
		Card
	},
	data: () => ({
		card: {
			name: "Bang!",
			icon: "🔫",
			number: 2,
			suit: '♠',
			is_equipment: false,
		},
		isConnected: false,
		didSetUsername: false,
		username: '',
		openLobbies: [],
		lobbyName: '',
		isInLobby: false,
	}),
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
		setUsername(){
			this.didSetUsername = true
			this.$socket.emit('set_username', this.username)
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
		createLobby() {
			if (this.lobbyName.trim().length > 0) {
				this.$socket.emit('create_room', this.lobbyName)
				this.isInLobby = true; 
			}
		}
	}
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
