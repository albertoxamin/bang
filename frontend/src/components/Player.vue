<template>
	<div>
		<p v-if="instruction">⏯ {{instruction}}</p>
		<button v-if="canEndTurn" @click="end_turn">Termina Turno</button>
		<div class="equipment-slot">
			<Card v-if="my_role" :card="my_role" class="back"/>
			<Card v-if="character" :card="character"/>
			<transition-group name="list" tag="div" >
				<Card v-for="card in equipment" v-bind:key="card.name+card.number" :card="card" />
			</transition-group>
		</div>
		<div>
			<span>Mano</span>
			<transition-group name="list" tag="div" class="hand">
				<Card v-for="card in hand" v-bind:key="card.name+card.number" :card="card" 
					@click.native="play_card(card)"
					@mouseover.native="hint=card.desc" @mouseleave.native="hint=''"/>
			</transition-group>
		</div>
		<p>{{hint}}</p>
	</div>
</template>

<script>
import Card from '@/components/Card.vue'

export default {
	name: 'Player',
	components: {
		Card
	},
	data: () => ({
		my_role: null,
		character: null,
		equipment: [],
		hand: [],
		lives: 0,
		max_lives: 0,
		hint: '',
		pending_action: null
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
		}
	},
	computed:{
		instruction() {
			if (this.pending_action == null)
				return ''
			let x = ['Estrai una carta', 'Pesca le tue carte', 'Gioca le tue carte', 'Rispondi alla carta', 'Attendi']
			return x[this.pending_action]
		},
		canEndTurn() {
			return (this.pending_action == 2 && this.hand.length <= this.lives)
		},
	},
	methods: {
		end_turn(){
			console.log('ending turn')
			this.$socket.emit('end_turn')
		},
		play_card(card) {
			if (this.pending_action == 2) {
				let card_data = {
					index: this.hand.indexOf(card),
					against: null
				}
				console.log(card_data)
				this.$socket.emit('play_card', card_data)
			}
		},
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