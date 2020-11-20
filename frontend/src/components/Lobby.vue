<template>
	<div>
		<h1>Lobby: {{ lobbyName }}</h1>
		<h3>Giocatori</h3>
		<div style="display:flex">
			<Card v-for="p in players" v-bind:key="p" :card="getPlayerCard(p)"/>
		</div>
		<h3>Chat</h3>
		<div id="chatbox" style="max-height:300px; overflow:auto;">
			<p v-for="msg in messages" v-bind:key="msg">{{msg}}</p>
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
				number: (this.username == username) ? 'YOU' : '',
				icon: '🤠',
				is_character: true,
			}
		},
	},
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
