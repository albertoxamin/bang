<template>
	<div>
		<p v-if="instruction" class="center-stuff">{{instruction}}</p>
		<!-- <button v-if="canEndTurn" @click="end_turn">Termina Turno</button> -->
		<div class="equipment-slot">
			<Card v-if="my_role" :card="my_role" class="back"
					@pointerenter.native="desc=my_role.goal" @pointerleave.native="desc=''"/>
			<Card v-if="character" :card="character" style="margin-left: -30pt;margin-right: 0pt;"
					@pointerenter.native="desc=character.desc" @pointerleave.native="desc=''"/>
			<transition-group name="list" tag="div" style="margin: 0 0 0 10pt; display:flex;">
				<Card v-for="card in equipment" v-bind:key="card.name+card.number" :card="card" @pointerenter.native="desc=card.desc" @pointerleave.native="desc=''" />
			</transition-group>
		</div>
		<p v-if="desc">{{desc}}</p>
		<transition-group name="list" tag="div" style="display: flex; justify-content: space-evenly; margin-bottom:2pt;">
			<span v-for="(n, i) in lives" v-bind:key="n" :alt="i">❤️</span>
			<span v-for="(n, i) in (max_lives-lives)" v-bind:key="n" :alt="i">💀</span>
		</transition-group>
		<div>
			<span>Mano</span>
			<transition-group name="list" tag="div" class="hand">
				<Card v-for="card in hand" v-bind:key="card.name+card.number" :card="card" 
					@click.native="play_card(card)"
					@pointerenter.native="hint=card.desc" @pointerleave.native="hint=''"/>
			</transition-group>
		</div>
		<p>{{hint}}</p>
		<Chooser v-if="card_against" text="Contro chi vuoi giocare la carta" :cards="visiblePlayers" :select="selectAgainst" :cancel="cancelCardAgainst"/>
		<Chooser v-if="pending_action == 3" :text="`Scegli come rispondere ${attacker?('a '+attacker):''}`" :cards="respondCards" :select="respond"/>
		<Chooser v-if="shouldChooseCard" text="Scegli che carta pescare" :cards="available_cards" :select="choose"/>
		<Chooser v-if="lives <= 0 && max_lives > 0" text="SEI MORTO" />
		<Chooser v-if="win_status !== undefined" :text="win_status?'HAI VINTO':'HAI PERSO'" />
		<Chooser v-if="show_role" text="Tu sei" :cards="[my_role]" :hintText="my_role.goal" :select="() => {show_role=false}" :cancel="() => {show_role=false}" cancelText="OK" />
		<Chooser v-if="notifycard" :text="`${notifycard.player} ha pescato come seconda carta:`" :cards="[notifycard.card]" hintText="Se la carta è cuori o quadri ne pesca un'altra" class="turn-notify-4s"/>
		<Chooser v-if="!show_role && is_my_turn" text="GIOCA IL TUO TURNO" :key="is_my_turn" class="turn-notify" />
		<Chooser v-if="hasToPickResponse" :text="`ESTRAI UNA CARTA ${attacker?('PER DIFENDERTI DA '+attacker):''}`" :key="hasToPickResponse" class="turn-notify" />
		<Chooser v-if="showScrapScreen" :text="`SCARTA ${hand.length}/${lives}`" :cards="hand" :select="scrap"  :cancel="cancelEndingTurn"/>
		<Chooser v-if="sidWantsScrapForHealth && sidScrapForHealth.length < 2" :text="`SCARTA ${2 - sidScrapForHealth.length} PER RECUPERARE 1 VITA`"
							:cards="sidScrapHand" :select="sidScrap" :cancel="() => {sidWantsScrapForHealth = false;sidScrapForHealth=[]}"/>
		<button v-if="is_my_turn && character.name === 'Sid Ketchum'" @click="sidWantsScrapForHealth=true">ABILITÀ SPECIALE</button>
	</div>
</template>

<script>
import Card from '@/components/Card.vue'
import Chooser from '@/components/Chooser.vue'

export default {
	name: 'Player',
	props: {
		chooseCardFromPlayer: Function,
		isEndingTurn: Boolean,
		cancelEndingTurn: Function,
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
		playersDistances: [],
		is_my_turn: false,
		expected_response: null,
		shouldChooseCard: false,
		available_cards: [],
		win_status: undefined,
		range: 1,
		sight: 1,
		can_target_sheriff: true,
		show_role: false,
		attacker: undefined,
		notifycard: null,
		desc: '',
		sidScrapForHealth: [],
		sidWantsScrapForHealth: false,
	}),
	sockets: {
		role(role) {
			this.my_role = JSON.parse(role)
			this.my_role.is_back = true
			this.show_role = true
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
			this.is_my_turn = self.is_my_turn
			if (this.is_my_turn) document.title = 'È il tuo turno! | PewPew!'
			else document.title = 'PewPew!'
			this.expected_response = self.expected_response
			this.available_cards = self.available_cards
			this.win_status = self.win_status
			this.sight = self.sight
			this.attacker = self.attacker
			if (this.pending_action == 5 && self.target_p) {
				this.chooseCardFromPlayer(self.target_p)
			} else if (this.pending_action == 5) {
				this.shouldChooseCard = true
			}
		},
		self_vis(vis) {
			console.log('received visibility update')
			console.log(vis)
			this.playersDistances = JSON.parse(vis)
		},
		notify_card(mess) {
			this.notifycard = mess
		}
	},
	computed:{
		showScrapScreen() {
			return this.isEndingTurn && !this.canEndTurn && this.is_my_turn;
		},
		sidScrapHand() {
			return this.hand.filter((x, i) => (this.sidScrapForHealth.indexOf(i) === -1))
		},
		visiblePlayers() {
			this.range;
			return this.playersDistances.filter(x => {
					if (!this.can_target_sheriff && x.is_sheriff)
						return false
					else
						return x.dist <= this.range
				}).map(player => {
				return {
					name: player.name,
					number: player.dist !== undefined ? `${player.dist}⛰` : '',
					icon: player.is_sheriff ? '⭐' : '🤠',
					is_character: true,
				}})
		},
		hasToPickResponse() {
			return !this.is_my_turn && this.pending_action == 0
		},
		instruction() {
			if (this.pending_action == null)
				return ''
			let x = ['▶️ Estrai una carta', '▶️ Pesca le tue carte', '▶️ Gioca le tue carte', '▶️ Rispondi alla carta', '⏸ Attendi', '▶️ Scegli una carta']
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
			this.hand.filter(x => this.expected_response.indexOf(x.name) !== -1).forEach(x=>{
				cc.push(x)
			})
			return cc
		}
	},
	methods: {
		sidScrap(c) {
			this.sidScrapForHealth.push(this.hand.indexOf(c))
			if (this.sidScrapForHealth.length == 2) {
				this.$socket.emit('scrap', this.hand.indexOf(this.sidScrapForHealth[0]))
				this.$socket.emit('scrap', this.hand.indexOf(this.sidScrapForHealth[1]))
				this.sidScrapForHealth = []
				this.sidWantsScrapForHealth = false
			}
		},
		end_turn(){
			console.log('ending turn')
			this.cancelEndingTurn()
			this.$socket.emit('end_turn')
		},
		scrap(c) {
			this.$socket.emit('scrap', this.hand.indexOf(c))
		},
		play_card(card) {
			let calamity_special = (card.name === 'Mancato!' && this.character.name === 'Calamity Janet')
			let cant_play_bang = (this.has_played_bang && this.equipment.filter(x => x.name == 'Volcanic').length == 0)
			if (this.pending_action == 2) {
				if ((card.need_target || calamity_special) && !((card.name == 'Bang!' || !calamity_special) && cant_play_bang)) {
						if (card.name == 'Panico!' || (card.name == 'Bang!' && cant_play_bang))
							this.range = 1
						else if (card.name == 'Bang!' || calamity_special)
							this.range = this.sight
						else
							this.range = 999
						this.can_target_sheriff = (card.name !== 'Prigione')
					if (this.visiblePlayers.length == 0 && this.hand.length > this.lives) {
						this.really_play_card(card, null)
					}
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
		cancelCardAgainst() {
			this.card_against = null
		},
		really_play_card(card, against) {
			let card_data	 = {
				index: this.hand.indexOf(card),
				against: against
			}
			console.log(card_data)
			this.$socket.emit('play_card', card_data)
		},
		choose(card) {
			this.$socket.emit('choose', this.available_cards.indexOf(card))
			this.available_cards = []
			this.shouldChooseCard = false
		},
	},
	mounted() {
		this.$socket.emit('refresh')
	},
	watch: {
		isEndingTurn(val) {
			if (val && this.canEndTurn) {
				this.end_turn()
			}
		},
		canEndTurn(val) {
			if (val && this.isEndingTurn) {
				this.end_turn()
			}
		},
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
	transform: translateY(-15px);
}
.equipment-slot {
	display:flex;
	margin: 10pt 0pt;
	overflow:auto;
}
.turn-notify {
	pointer-events: none;
	animation: disappear 2s ease-in forwards;
}
.turn-notify-4s {
	pointer-events: none;
	animation: disappear 4s ease-in forwards;
}
@keyframes disappear {
	0% {
		opacity: 1;
	}
	100% {
		opacity: 0;
		visibility: hidden;
	}
}
</style>