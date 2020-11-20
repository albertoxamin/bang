<template>
	<div>
		<h1>Lobby: {{ lobbyName }}</h1>
		<h3>Giocatori</h3>
		<div style="display:flex">
			<div style="position: relative;width:260pt;height:400pt;">
				<Card v-for="p in playersTable" v-bind:key="p" :card="p.card" :style="p.style"/>
			</div>
			<Card v-if="startGameCard" :card="startGameCard" @click.native="startGame"/>
		</div>
		<div v-if="started">
			<deck/>
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
import Deck from './Deck.vue'

export default {
	name: 'Lobby',
	components: {
		Card,
		Chooser,
		Chat,
		Player,
		Deck,
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
		},
		playersTable() {
			return this.players.map((x,i) => {
				let offsetAngle = 360.0 / this.players.length
				let rotateAngle = (i) * offsetAngle
				let size = 130
				return {card:this.getPlayerCard(x), style: `position:absolute;transform: rotate(${rotateAngle}deg) translate(0, -${size}pt) rotate(-${rotateAngle}deg) translate(${size}pt,${size}pt)`}
			})
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
