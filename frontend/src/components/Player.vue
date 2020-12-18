<template>
	<div>
		<p v-if="instruction" class="center-stuff">{{instruction}}</p>
		<!-- <button v-if="canEndTurn" @click="end_turn">Termina Turno</button> -->
		<div class="equipment-slot">
			<Card v-if="my_role" :card="my_role" class="back"
					@pointerenter.native="desc=($i18n.locale=='it'?my_role.goal:my_role.goal_eng)" @pointerleave.native="desc=''"/>
			<Card v-if="character" :card="character" style="margin-left: -30pt;margin-right: 0pt;"
					@pointerenter.native="desc=($i18n.locale=='it'?character.desc:character.desc_eng)" @pointerleave.native="desc=''"/>
			<transition-group name="list" tag="div" style="display: flex;flex-direction:column; justify-content: space-evenly; margin-left: 12pt;margin-right:-10pt;">
				<span v-for="(n, i) in lives" v-bind:key="n" :alt="i">❤️</span>
				<span v-for="(n, i) in (max_lives-lives)" v-bind:key="n" :alt="i">💀</span>
			</transition-group>
			<transition-group v-if="lives > 0" name="list" tag="div" style="margin: 0 0 0 10pt; display:flex;">
				<Card v-for="card in equipment" v-bind:key="card.name+card.number" :card="card" 
					@pointerenter.native="desc=($i18n.locale=='it'?card.desc:card.desc_eng)" @pointerleave.native="desc=''"
					@click.native="play_card(card, true)" />
			</transition-group>
		</div>
		<transition name="list">
			<p v-if="desc"><i>{{desc}}</i></p>
		</transition>
		<button v-if="is_my_turn && character.name === 'Sid Ketchum'" @click="sidWantsScrapForHealth=true">{{$t('special_ability')}}</button>
		<button v-if="is_my_turn && character.name === 'Chuck Wengam' && lives > 1" @click="chuckSpecial">{{$t('special_ability')}}</button>
		<div v-if="lives > 0" style="position:relative">
			<span id="hand_text">{{$t('hand')}}</span>
			<transition-group name="list" tag="div" class="hand">
				<Card v-for="card in hand" v-bind:key="card.name+card.number" :card="card" 
					@click.native="play_card(card, false)"
					@pointerenter.native="hint=($i18n.locale=='it'?card.desc:card.desc_eng)" @pointerleave.native="hint=''"/>
			</transition-group>
		</div>
		<transition name="list">
			<p v-if="hint"><i>{{hint}}</i></p>
		</transition>
		<Chooser v-if="is_my_turn && pending_action == 4" :text="$t('wait')" :cards="[]"/>
		<Chooser v-if="card_against" :text="$t('card_against')" :cards="visiblePlayers" :select="selectAgainst" :cancel="cancelCardAgainst"/>
		<Chooser v-if="pending_action == 3" :text="respondText" :cards="respondCards" :select="respond"/>
		<Chooser v-if="shouldChooseCard" :text="$t('choose_card_to_get')" :cards="available_cards" :select="choose"/>
		<Chooser v-if="lives <= 0 && max_lives > 0" :text="$t('you_died')" :cancelText="$t('spectate')" :cancel="()=>{max_lives = 0}"/>
		<Chooser v-if="win_status !== undefined" :text="win_status?$t('you_win'):$t('you_lose')" />
		<Chooser v-if="show_role" :text="$t('you_are')" :cards="[my_role]" :hintText="($i18n.locale=='it'?my_role.goal:my_role.goal_eng)" :select="() => {show_role=false}" :cancel="() => {show_role=false}" :cancelText="$t('ok')" />
		<Chooser v-if="notifycard" :key="notifycard.card" :text="`${notifycard.player} ${$t('did_pick_as')}:`" :cards="[notifycard.card]" :hintText="$t(notifycard.message)" class="turn-notify-4s"/>
		<Chooser v-if="!show_role && is_my_turn && pending_action < 2" :text="$t('play_your_turn')" :key="is_my_turn" class="turn-notify" />
		<Chooser v-if="!show_role && availableCharacters.length > 0" :text="$t('choose_character')" :cards="availableCharacters" :select="setCharacter"/>
		<Chooser v-if="hasToPickResponse" :text="`${$t('pick_a_card')} ${attacker?($t('to_defend_from')+' '+attacker):''}`" :key="hasToPickResponse" class="turn-notify" />
		<Chooser v-if="!card_against && card_with" :text="`${$t('choose_scarp_card_to')} ${card_with.name.toUpperCase()}`" :cards="hand.filter(x => x !== card_with)" :select="selectWith" :cancel="()=>{card_with = null}"/>
		<Chooser v-if="showScrapScreen" :text="`${$t('discard')} ${hand.length}/${lives}`" :cards="hand" :select="scrap"  :cancel="cancelEndingTurn"/>
		<Chooser v-if="sidWantsScrapForHealth && sidScrapForHealth.length < 2" :text="`${$t('discard')} ${2 - sidScrapForHealth.length} ${$t('to_regain_1_hp')}`"
							:cards="sidScrapHand" :select="sidScrap" :cancel="() => {sidWantsScrapForHealth = false;sidScrapForHealth=[]}"/>
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
		availableCharacters: [],
		equipment: [],
		hand: [],
		lives: 0,
		max_lives: 0,
		hint: '',
		pending_action: null,
		card_against: null,
		card_with: null,
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
		mancato_needed: 0,
		name: '',
	}),
	sockets: {
		role(role) {
			this.my_role = JSON.parse(role)
			this.my_role.is_back = true
			this.show_role = true
		},
		characters(data) {
			this.availableCharacters = JSON.parse(data)
		},
		self(self) {
			self = JSON.parse(self)
			this.name = self.name
			this.pending_action = self.pending_action
			this.character = self.character
			this.character.is_character = true
			this.hand = self.hand
			this.equipment = self.equipment
			this.lives = self.lives
			this.max_lives = self.max_lives
			this.has_played_bang = self.has_played_bang
			this.is_my_turn = self.is_my_turn
			if (this.is_my_turn) document.title = this.$t('your_turn')+' | PewPew!'
			else if (this.pending_action == 3) document.title = this.$t('your_response')+' | PewPew!'
			else if (this.pending_action == 5) document.title = this.$t('your_choose')+' | PewPew!'
			else document.title = 'PewPew!'
			this.expected_response = self.expected_response
			this.available_cards = self.available_cards
			this.win_status = self.win_status
			this.sight = self.sight
			this.attacker = self.attacker
			this.mancato_needed = self.mancato_needed
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
			setTimeout(function(){
					this.notifycard = null
				}.bind(this), 4000)
		}
	},
	computed:{
		respondText() {
			return `${this.$t('choose_response')}${this.attacker?(this.$t('choose_response_to')+this.attacker):''}${(this.mancato_needed>1)?(` (${this.$t('choose_response_needed')} ` + this.mancato_needed + ')'):''}`
		},
		showScrapScreen() {
			return this.isEndingTurn && !this.canEndTurn && this.is_my_turn;
		},
		sidScrapHand() {
			return this.hand.filter((x, i) => (this.sidScrapForHealth.indexOf(i) === -1))
		},
		visiblePlayers() {
			this.range;
			let vis = this.playersDistances.filter(x => {
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
			if (this.card_against && this.card_against.can_target_self) {
				vis.push({
					name: this.name,
					number: 0,
					icon: this.$t('you'),
					is_character: true,
				})
			}
			return vis
		},
		hasToPickResponse() {
			return !this.is_my_turn && this.pending_action == 0
		},
		instruction() {
			if (this.pending_action == null)
				return ''
			let x = [this.$t('flip_card'), this.$t('draw_cards'), this.$t('play_cards'), this.$t('respond_card'), this.$t('wait'), this.$t('choose_cards')]
			return x[this.pending_action]
		},
		canEndTurn() {
			return (this.pending_action == 2 && this.hand.length <= (this.character.name === "Sean Mallory"?10:this.lives))
		},
		respondCards() {
			let cc = [{
					name: this.$t('take_dmg'),
					icon: '❌',
					is_equipment: true,
				}]
			this.hand.filter(x => x.can_be_used_now && this.expected_response.indexOf(x.name) !== -1).forEach(x=>{
				cc.push(x)
			})
			this.equipment.filter(x => x.usable_next_turn && x.can_be_used_now && this.expected_response.indexOf(x.name) !== -1).forEach(x=>{
				cc.push(x)
			})
			return cc
		}
	},
	methods: {
		setCharacter(char) {
			this.availableCharacters = []
			this.$socket.emit('set_character', char.name)
		},
		sidScrap(c) {
			this.sidScrapForHealth.push(this.hand.indexOf(c))
			if (this.sidScrapForHealth.length == 2) {
				this.$socket.emit('scrap', this.hand.indexOf(this.sidScrapForHealth[0]))
				this.$socket.emit('scrap', this.hand.indexOf(this.sidScrapForHealth[1]))
				this.sidScrapForHealth = []
				this.sidWantsScrapForHealth = false
			}
		},
		chuckSpecial(){
			this.$socket.emit('chuck_lose_hp_draw')
		},
		end_turn(){
			console.log('ending turn')
			this.cancelEndingTurn()
			this.$socket.emit('end_turn')
		},
		scrap(c) {
			this.$socket.emit('scrap', this.hand.indexOf(c))
		},
		play_card(card, from_equipment) {
			if (from_equipment && (!card.usable_next_turn || !card.can_be_used_now)) return;
			else if (card.usable_next_turn && !card.can_be_used_now) return this.really_play_card(card, null);
			let calamity_special = (card.name === 'Mancato!' && this.character.name === 'Calamity Janet')
			let cant_play_bang = (this.has_played_bang && this.equipment.filter(x => x.name == 'Volcanic').length == 0)
			if (this.pending_action == 2) {
				if (card.need_with && !this.card_with) {
					this.card_with = card
				} else if ((card.need_target || calamity_special) && !((card.name == 'Bang!' || (calamity_special && card.name=='Mancato!')) && cant_play_bang)) {
						if (card.name == 'Bang!' || card.name == "Pepperbox" || calamity_special)
							this.range = this.sight
						else
							this.range = card.range
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
			let res = this.hand.indexOf(card)
			if (res === -1) {
				res = this.equipment.indexOf(card)
				if (res !== -1) res += this.hand.length
			}
			this.$socket.emit('respond', res)
		},
		selectAgainst(player) {
			this.really_play_card(this.card_against, player.name)
			this.card_against = null
		},
		selectWith(card) {
			if (this.card_with.need_target) {
				this.card_against = this.card_with
				this.range = this.card_against.range
				this.card_with = card
			} else {
				let card_data	 = {
					index: this.hand.indexOf(this.card_with),
					against: null,
					with: this.hand.indexOf(card),
				}
				this.card_with = null
				this.$socket.emit('play_card', card_data)
			}
		},
		cancelCardAgainst() {
			this.card_against = null
			this.card_with = null
		},
		really_play_card(card, against) {
			let res = this.hand.indexOf(card)
			if (res === -1) {
				res = this.equipment.indexOf(card)
				if (res !== -1) res += this.hand.length
			}
			let card_data	 = {
				index: res,
				against: against,
				with: this.hand.indexOf(this.card_with) > -1 ? this.hand.indexOf(this.card_with):null,
			}
			this.card_with = null
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
	position: relative;
	display:flex;
	border: 2px dashed #ccc;
	padding: 10pt 40pt 0pt 40pt;
	overflow:auto;
	border-radius: 4pt;
	min-height: 40pt;
}
.hand>.card{
	margin-left: -30pt;
}
.hand>.card:hover {
	margin-right:35pt;
	transform: translateY(-15px);
}
#hand_text{
	color: #ccc;
	position: absolute;
	font-size: xxx-large;
	font-weight: 300;
	bottom: 0;
	right: 10pt;
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