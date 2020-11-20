<template>
	<div>
		<h1>Lobby: {{ lobbyName }}</h1>
		<h3>Giocatori</h3>
		<div style="display:flex">
			<Card v-if="startGameCard" :card="startGameCard" @click.native="startGame"/>
			<Card v-for="p in players" v-bind:key="p" :card="getPlayerCard(p)"/>
		</div>
		<h3>Chat</h3>
		<div id="chatbox" style="max-height:200px; overflow:auto;">
			<p style="margin:1pt;" v-for="msg in messages" v-bind:key="msg">{{msg}}</p>
		</div>
		<form @submit="sendChatMessage">
			<input v-model="text"/>
			<input type="submit"/>
		</form>
		<Chooser v-if="showChooser" :cards="availableCharacters" :select="setCharacter"/>
	</div>
</template>

<script>
import Card from '@/components/Card.vue'
import Chooser from './Chooser.vue'

export default {
	name: 'Lobby',
	components: {
		Card,
		Chooser,
	},
	props: {
		username: String
	},
	data: () => ({
		lobbyName: '',
		started: false,
		players: [],
		messages: [],
		availableCharacters: [],
		text: ''
	}),
	sockets: {
		room(data) {
			console.log(data)
			this.lobbyName = data.name
			this.started = data.started
			this.players = data.players
		},
		chat_message(msg) {
			this.messages.push(msg)
			let container = this.$el.querySelector("#chatbox");
			container.scrollTop = container.scrollHeight;
		},
		characters(data){
			this.availableCharacters = JSON.parse(data)
		},
	},
	computed: {
		startGameCard() {
			if (!this.started && this.players.length > 2 && this.players[0] == this.username) {
				return {
					name: 'Start',
					icon: '▶️',
					is_equipment: true,
					number: `${this.players.length}🤠`
				}
			}
			return null;
		},
		showChooser() {
			return this.availableCharacters.length > 0;
		}
	},
	methods: {
		sendChatMessage(e) {
			if (this.text.trim().length > 0){
				this.$socket.emit('chat_message', this.text.trim())
				this.text = ''
			}
			e.preventDefault();
		},
		getPlayerCard(username) {
			return {
				name: username,
				number: (this.username == username) ? 'YOU' : (this.players[0] == username) ? 'OWNER' :'',
				icon: '🤠',
				is_character: true,
			}
		},
		startGame() {
			this.started = true;
			this.$socket.emit('start_game')
		},
		setCharacter(char) {
			this.availableCharacters = []
			this.$socket.emit('set_character', char.name)
		},
	},
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
