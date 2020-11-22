<template>
	<div>
		<p v-if="instruction">⏯ {{instruction}}</p>
		<button v-if="canEndTurn" @click="end_turn">Termina Turno</button>
		<div class="equipment-slot">
			<Card v-if="my_role" :card="my_role" class="back"/>
			<Card v-if="character" :card="character"/>
			<transition-group name="list" tag="div" style="margin: 0 0 0 10pt;">
				<Card v-for="card in equipment" v-bind:key="card.name+card.number" :card="card" />
			</transition-group>
		</div>
		<transition-group name="list" tag="div" style="display: flex; justify-content: space-evenly;">
			<span v-for="(n, i) in lives" v-bind:key="n" :alt="i">❤️</span>
			<span v-for="(n, i) in (max_lives-lives)" v-bind:key="n" :alt="i">💀</span>
		</transition-group>
		<div>
			<span>Mano</span>
			<transition-group name="list" tag="div" class="hand">
				<Card v-for="card in hand" v-bind:key="card.name+card.number" :card="card" 
					@click.native="play_card(card)"
					@mouseover.native="hint=card.desc" @mouseleave.native="hint=''"/>
			</transition-group>
		</div>
		<p>{{hint}}</p>
		<Chooser v-if="card_against" text="Contro chi vuoi giocare la carta" :cards="visiblePlayers" :select="selectAgainst"/>
		<Chooser v-if="pending_action == 3" text="Scegli come rispondere" :cards="respondCards" :select="respond"/>
		<Chooser v-if="lives <= 0 && max_lives > 0" text="SEI MORTO" />
	</div>
</template>

<script>
import Card from '@/components/Card.vue'
import Chooser from '@/components/Chooser.vue'

export default {
	name: 'Player',
	props: {
		chooseCardFromPlayer: Function
	},
	components: {
		Card,
		Chooser,
	},
	data: () => ({
		my_role: null,
		character: null,
		equipment: [],
		hand: [],
		lives: 0,
		max_lives: 0,
		hint: '',
		pending_action: null,
		card_against: null,
		has_played_bang: false,
		visiblePlayers: []
	}),
	sockets: {
		role(role) {
			this.my_role = JSON.parse(role)
		},
		self(self) {
			self = JSON.parse(self)
			this.pending_action = self.pending_action
			this.character = self.character
			this.character.is_character = true
			this.hand = self.hand
			this.equipment = self.equipment
			this.lives = self.lives
			this.max_lives = self.max_lives
			this.has_played_bang = self.has_played_bang
			if (this.pending_action == 5) {
				this.chooseCardFromPlayer(self.target_p)
			}
		},
		self_vis(vis) {
			console.log('received visibility update')
			console.log(vis)
			this.visiblePlayers = JSON.parse(vis).map(player => {
				return {
					name: player.name,
					number: player.dist !== undefined ? `${player.dist}⛰` : '',
					icon: '🤠',
					is_character: true,
				}})
		},
	},
	computed:{
		instruction() {
			if (this.pending_action == null)
				return ''
			let x = ['Estrai una carta', 'Pesca le tue carte', 'Gioca le tue carte', 'Rispondi alla carta', 'Attendi', 'Scegli una carta']
			return x[this.pending_action]
		},
		canEndTurn() {
			return (this.pending_action == 2 && this.hand.length <= this.lives)
		},
		respondCards() {
			let cc = [{
					name: 'Prendi Danno',
					icon: '❌',
					is_equipment: true,
				}]
			this.hand.filter(x => x.name == 'Mancato!').forEach(x=>{
				cc.push(x)
			})
			return cc
		}
	},
	methods: {
		end_turn(){
			console.log('ending turn')
			this.$socket.emit('end_turn')
		},
		play_card(card) {
			if (this.pending_action == 2) {
				if (card.need_target &&
					!(card.name == 'Bang!' && (this.has_played_bang && this.equipment.filter(x => x.name == 'Volcanic').length == 0))) {
					this.card_against = card
				} else {
					this.really_play_card(card, null)
				}
			}
		},
		respond(card) {
			this.$socket.emit('respond', this.hand.indexOf(card))
		},
		selectAgainst(player) {
			this.really_play_card(this.card_against, player.name)
			this.card_against = null
		},
		really_play_card(card, against) {
			let card_data	 = {
				index: this.hand.indexOf(card),
				against: against
			}
			console.log(card_data)
			this.$socket.emit('play_card', card_data)
		}
	},
	mounted() {
		this.$socket.emit('refresh')
	}
}
</script>
<style scoped>
.hand>i {
	position: absolute;
	top: 0;
	left: 0;
	font-weight: bold;
	text-transform: uppercase;
	opacity: 0.5;
}
.hand {
	margin-top: -16pt;
	position: relative;
	display:flex;
	border: 1px solid #ccc;
	padding: 10pt 40pt 0pt 40pt;
	overflow:auto;
	border-radius: 4pt;
	min-height: 20pt;
}
.hand>.card{
	margin-left: -30pt;
}
.hand>.card:hover {
	margin-right:35pt;
	margin-top:-0.5pt;
}
.equipment-slot, .equipment-slot>div {
	display:flex;
	margin: 10pt 0pt;
}
</style>