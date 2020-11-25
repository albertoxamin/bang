<template>
	<div class="lobby">
		<div style="flex-grow: 4;">
			<h2 v-if="!started">Lobby: {{ lobbyName }}</h2>
			<h3>Giocatori (tu sei {{username}})</h3>
			<div v-if="startGameCard">
				<div class="pretty p-switch p-fill">
					<input type="checkbox" />
					<div class="state">
							<label>Stanza Privata</label>
					</div>
				</div>
			</div>
			<div class="players-table">
				<Card v-if="startGameCard" :card="startGameCard" @click.native="startGame"/>
				<!-- <div style="position: relative;width:260pt;height:400pt;"> -->
				<div v-for="p in playersTable" v-bind:key="p.card.name" style="position:relative;">
					<transition-group v-if="p.max_lives" name="list" tag="div" class="tiny-health">
						<span v-for="(n, i) in p.lives" v-bind:key="n" :alt="i">❤️</span>
						<span v-for="(n, i) in (p.max_lives-p.lives)" v-bind:key="n" :alt="i">💀</span>
					</transition-group>
					<Card :card="p.card" :class="{is_my_turn:p.is_my_turn}"/>
					<Card v-if="p.character" :card="p.character" class="character tiny-character" @click.native="selectedInfo = [p.character]"/>
					<tiny-hand :ncards="p.ncards" @click.native="drawFromPlayer(p.name)"/>
					<span style="position:absolute;top:0;" class="center-stuff">{{getActionEmoji(p)}}</span>
					<div class="tiny-equipment">
						<Card v-for="card in p.equipment" v-bind:key="card.name+card.number" :card="card" @click.native="selectedInfo = p.equipment"/>
					</div>
				</div>
					<!-- :style="p.style"/> -->
				<!-- </div> -->
			</div>
			<div v-if="started">
				<deck :endTurnAction="()=>{wantsToEndTurn = true}"/>
				<player :isEndingTurn="wantsToEndTurn" :cancelEndingTurn="()=>{wantsToEndTurn = false}" :chooseCardFromPlayer="choose"/>
			</div>
		</div>
		<chat/>
		<Chooser v-if="selectedInfo" text="Dettagli" :cards="selectedInfo"  cancelText="OK" :cancel="()=>{selectedInfo = null}" :select="()=>{selectedInfo = null}"/>
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
		wantsToEndTurn: false,
		selectedInfo: null,
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
		getActionEmoji(p) {
			if (p.is_my_turn === undefined || p.pending_action === undefined) return '';
			if (p.pending_action != 4) {
				return '▶️'
			} else if (p.is_my_turn) {
				return '⏸'
			} else {
				return ''
			}
		},
		getPlayerCard(player) {
			return {
				name: player.name,
				number: ((this.username == player.name) ? 'YOU' : (this.players[0].name == player.name) ? 'OWNER' :'') + (player.dist ? `${player.dist}⛰` : ''),
				icon: (player.lives === undefined || player.lives > 0) ? (player.is_sheriff ? '⭐' : player.icon || '🤠' ) : '☠️',
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
		drawFromPlayer(name) {
			console.log(name)
			this.$socket.emit('draw', name)
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
@media (prefers-color-scheme: dark) {
	.is_my_turn {
		box-shadow: 0 0 0 3pt rgb(138, 12, 12), 0 0 0 6pt #181a1b, 0 0 5pt 6pt #aaa !important;
	}
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
.tiny-health {
	position: absolute;
	display: flex;
	justify-content: space-evenly;
	top: -16pt;
	transform: scale(0.8);
	right: 0;
	left: 0;
}
.tiny-equipment .card:nth-child(n+2) {
	margin-top: -60pt;
}
.tiny-character {
	position: absolute;
	transform: scale(0.6) translate(-80px, -50px);
	top: 0;
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
	.chat {
		max-width: 350pt;
	}
}
</style>
