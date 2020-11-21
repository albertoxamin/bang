<template>
	<div>
		<h1>Lobby: {{ lobbyName }}</h1>
		<h3>Giocatori (tu sei {{username}})</h3>
		<div style="display:flex">
			<Card v-if="startGameCard" :card="startGameCard" @click.native="startGame"/>
			<!-- <div style="position: relative;width:260pt;height:400pt;"> -->
			<div v-for="p in playersTable" v-bind:key="p.card.name" style="position:relative;">
				<Card :card="p.card"/>
				<tiny-hand :ncards="p.ncards"/>
			</div>
				<!-- :style="p.style"/> -->
			<!-- </div> -->
		</div>
		<div v-if="started">
			<deck/>
			<player/>
		</div>
		<chat/>
		<transition name="bounce">
			<Chooser v-if="showChooser" text="Scegli il tuo personaggio" :cards="availableCharacters" :select="setCharacter"/>
		</transition>
	</div>
</template>

<script>
import Card from '@/components/Card.vue'
import Chooser from './Chooser.vue'
import Chat from './Chat.vue'
import Player from './Player.vue'
import Deck from './Deck.vue'
import TinyHand from './TinyHand.vue'

export default {
	name: 'Lobby',
	components: {
		Card,
		Chooser,
		Chat,
		Player,
		Deck,
		TinyHand,
	},
	props: {
		username: String
	},
	data: () => ({
		lobbyName: '',
		started: false,
		players: [],
		messages: [],
		distances: {},
		availableCharacters: [],
		self: {},
	}),
	sockets: {
		room(data) {
			this.lobbyName = data.name
			this.started = data.started
			this.players = data.players.map(x => {
				return {
					name: x,
					ncards: 0,
				}
			})
		},
		characters(data) {
			this.availableCharacters = JSON.parse(data)
		},
		start() {
			this.started = true;
		},
		players_update(data) {
			console.log(data)
			this.players = data
		},
		// self_vis(vis) {
		// 	console.log('received visibility update')
		// 	console.log(vis)
		// 	this.players = JSON.parse(vis)
		// },
	},
	computed: {
		startGameCard() {
			if (!this.started && this.players.length > 2 && this.players[0].name == this.username) {
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
			console.log('update players')
			return this.players.map((x,i) => {
				let offsetAngle = 360.0 / this.players.length
				let rotateAngle = (i) * offsetAngle
				let size = 130
				return {
					card:this.getPlayerCard(x),
					style: `position:absolute;transform: rotate(${rotateAngle}deg) translate(0, -${size}pt) rotate(-${rotateAngle}deg) translate(${size}pt,${size}pt)`,
					...x
				}
			})
		}
	},
	methods: {
		getPlayerCard(player) {
			return {
				name: player.name,
				number: ((this.username == player.name) ? 'YOU' : (this.players[0].name == player.name) ? 'OWNER' :'') + (player.dist ? `${player.dist}⛰` : ''),
				icon: (player.lives === undefined || player.lives > 0) ? '🤠' : '☠️',
				alt_text: player.lives !== undefined ? Array(player.lives).join('❤️')+Array(player.max_lives-player.lives).join('💀') : '',
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
