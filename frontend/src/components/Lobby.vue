<template>
	<div>
		<h1>Lobby: {{ lobbyName }}</h1>
		<h3>Giocatori</h3>
		<div style="display:flex">
			<Card v-if="startGameCard" :card="startGameCard" @click.native="startGame"/>
			<Card v-for="p in players" v-bind:key="p" :card="getPlayerCard(p)"/>
		</div>
		<div v-if="started">
			<player/>
		</div>
		<chat/>
		<Chooser v-if="showChooser" text="Scegli il tuo personaggio" :cards="availableCharacters" :select="setCharacter"/>
	</div>
</template>

<script>
import Card from '@/components/Card.vue'
import Chooser from './Chooser.vue'
import Chat from './Chat.vue'
import Player from './Player.vue'

export default {
	name: 'Lobby',
	components: {
		Card,
		Chooser,
		Chat,
		Player,
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
		self: {},
	}),
	sockets: {
		room(data) {
			console.log(data)
			this.lobbyName = data.name
			this.started = data.started
			this.players = data.players
		},
		characters(data){
			this.availableCharacters = JSON.parse(data)
		},
		start() {
			this.started = true;
		}
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
<style >
#logo {
	display:none;
}
</style>
