<template>
	<div>
		<h1>Lobby: {{ lobbyName }}</h1>
		<h3>Giocatori</h3>
		<div style="display:flex">
			<Card v-if="startGameCard" :card="startGameCard"/>
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
	</div>
</template>

<script>
import Card from '@/components/Card.vue'

export default {
	name: 'Lobby',
	components: {
		Card,
	},
	props: {
		username: String
	},
	data: () => ({
		lobbyName: '',
		started: false,
		players: [],
		messages: [],
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
	},
	computed: {
		startGameCard() {
			if (this.players.length > 2 && this.players[0] == this.username) {
				return {
					name: 'Start',
					icon: '▶️',
					is_equipment: true,
					number: `${this.players.length}🤠`
				}
			}
			return null;
		}
	}
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
