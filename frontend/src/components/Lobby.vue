<template>
	<div class="lobby">
		<div style="flex-grow: 4;">
			<h2>Lobby: {{ lobbyName }}</h2>
			<h3>Giocatori (tu sei {{username}})</h3>
			<div class="players-table">
				<Card v-if="startGameCard" :card="startGameCard" @click.native="startGame"/>
				<!-- <div style="position: relative;width:260pt;height:400pt;"> -->
				<div v-for="p in playersTable" v-bind:key="p.card.name" style="position:relative;">
					<Card :card="p.card" :class="{is_my_turn:p.is_my_turn}"/>
					<tiny-hand :ncards="p.ncards"/>
					<div class="tiny-equipment">
						<Card v-for="card in p.equipment" v-bind:key="card.name+card.number" :card="card" />
					</div>
				</div>
					<!-- :style="p.style"/> -->
				<!-- </div> -->
			</div>
			<div v-if="started">
				<deck/>
				<player :chooseCardFromPlayer="choose"/>
			</div>
		</div>
		<chat/>
		<transition name="bounce">
			<Chooser v-if="showChooser" text="Scegli il tuo personaggio" :cards="availableCharacters" :select="setCharacter"/>
			<Chooser v-if="hasToChoose" text="Scegli una carta" :cards="chooseCards" :select="chooseCard"/>
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
		hasToChoose: false,
		chooseCards: [],
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
				icon: (player.lives === undefined || player.lives > 0) ? (player.is_sheriff ? '⭐' : '🤠') : '☠️',
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
		choose(player_name) {
			console.log('choose from' + player_name)
			let pl = this.players.filter(x=>x.name === player_name)[0]
			console.log(pl)
			let arr = []
			for (let i=0; i<pl.ncards; i++)
				arr.push({
					name: 'PewPew!',
					icon: '💥',
					is_back: true,
				})
			pl.equipment.forEach(x=>arr.push(x))
			this.chooseCards = arr
			this.hasToChoose = true
		},
		chooseCard(card) {
			this.$socket.emit('choose', this.chooseCards.indexOf(card))
			console.log(card + ' ' + this.chooseCards.indexOf(card))
			this.chooseCards = []
			this.hasToChoose = false
		},
	},
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style >
.is_my_turn {
	box-shadow: 0 0 0 3pt rgb(138, 12, 12), 0 0 0 6pt white, 0 0 5pt 6pt #aaa !important;
	animation-name: turn-animation;
  animation-duration: 2s;
  animation-iteration-count: infinite;
}
@keyframes turn-animation {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}
.tiny-equipment {
	position: absolute;
	display: flex;
	flex-direction: column;
	right: -35pt;
	transform: scale(0.45);
	transform-origin: 50% 0%;
	top: 0;
}
.tiny-equipment .card:nth-child(n+2) {
	margin-top: -60pt;
}
.players-table {
	display: flex;
	justify-content: space-evenly;
	margin-bottom: 12pt;
}
.lobby {
	display: flex;
	flex-direction: column;
}
@media only screen and (min-width:1000px) {
	.lobby {
		flex-direction: row;
	}
}
</style>
