<template>
	<div>
		<p v-if="instruction && (lives > 0 || is_ghost)" class="center-stuff">{{instruction}}</p>
		<!-- <button v-if="canEndTurn" @click="end_turn">Termina Turno</button> -->
		<div class="equipment-slot">
			<Card v-if="my_role" :card="my_role" class="back" style="transform:rotate(-2deg)"
					@pointerenter.native="desc=($i18n.locale=='it'?my_role.goal:my_role.goal_eng)" @pointerleave.native="desc=''"/>
			<Card v-if="character" :card="character" style="margin-left: -30pt;margin-right: 0pt;"
					@pointerenter.native="setDesc(character)" @pointerleave.native="desc=''"/>
			<transition-group name="list" tag="div" style="display: flex;flex-direction:column; justify-content: space-evenly; margin-left: 12pt;margin-right:-10pt;">
				<span v-for="(n, i) in (max_lives-lives)" v-bind:key="`${i}-sk`" :alt="i">💀</span>
				<span v-for="(n, i) in lives" v-bind:key="i" :alt="i">❤️</span>
			</transition-group>
			<div v-if="gold_nuggets > 0" style="position:relative;left:-90pt;top:65pt;justify-content: space-evenly;width: 25pt;">
				<h3 style="background:gold;border-radius:15pt;padding:2pt 2pt;color:black;text-align:center"> 💵️ {{ gold_nuggets }} </h3>
			</div>
			<transition-group v-if="lives > 0 || is_ghost" name="list" id="equipment" tag="div" style="margin: 0 0 0 10pt; display:flex;">
				<Card v-for="card in equipmentComputed" v-bind:key="card.name+card.number" :card="card" 
					@pointerenter.native="setDesc(card)" @pointerleave.native="desc=''"
					@click.native="play_card(card, true)" :class="{'cant-play':((eventCard && eventCard.name == 'Lazo') || (!card.can_be_used_now && !card.is_equipment))}"/>
			</transition-group>
		</div>
		<transition name="list">
			<p v-if="desc"><i>{{desc}}</i></p>
		</transition>
		<div style="margin-bottom:6pt;margin-bottom: 6pt;display: flex;flex-direction: column;">
			<button :class="{'btn': true, 'cant-play':(pending_action != 2)}" :disabled="pending_action != 2" v-if="!(eventCard && eventCard.name == 'Sbornia') && is_my_turn && character.name === 'Sid Ketchum' && lives < max_lives && hand.length > 1" @click="sidWantsScrapForHealth=true">{{$t('special_ability')}}</button>
			<button :class="{'btn': true, 'cant-play':(pending_action != 2)}" :disabled="pending_action != 2" v-if="!(eventCard && eventCard.name == 'Sbornia') && is_my_turn && character.name === 'Chuck Wengam' && lives > 1" @click="()=>{$socket.emit('special', {})}">{{$t('special_ability')}}</button>
			<button :class="{'btn': true, 'cant-play':(pending_action != 2)}" :disabled="pending_action != 2" v-if="!(eventCard && eventCard.name == 'Sbornia') && is_my_turn && character.name === 'José Delgado' && special_use_count < 2 && hand.filter(x => x.is_equipment).length > 0" @click="joseScrap=true">{{$t('special_ability')}}</button>
			<button :class="{'btn': true, 'cant-play':(pending_action != 2)}" :disabled="pending_action != 2" v-if="!(eventCard && eventCard.name == 'Sbornia') && is_my_turn && character.name === 'Doc Holyday' && special_use_count < 1 && hand.length > 1" @click="holydayScrap=true">{{$t('special_ability')}}</button>
			<button :class="{'btn': true, 'cant-play':(pending_action != 2)}" :disabled="pending_action != 2" v-if="!(eventCard && eventCard.name == 'Sbornia') && is_my_turn && character.name === 'Jacky Murieta' && gold_nuggets >=2" @click="()=>{$socket.emit('special', {})}">{{$t('special_ability')}}</button>
			<button :class="{'btn': true, 'cant-play':(pending_action != 2)}" :disabled="pending_action != 2" v-if="!(eventCard && eventCard.name == 'Sbornia') && is_my_turn && character.name === 'Josh McCloud' && gold_nuggets >=2" @click="()=>{$socket.emit('special', {})}">{{$t('special_ability')}}</button>
			<button :class="{'btn': true, 'cant-play':(pending_action != 2)}" :disabled="pending_action != 2" v-if="!(eventCard && eventCard.name == 'Sbornia') && is_my_turn && character.name === 'Raddie Snake' && special_use_count < 2 && gold_nuggets >=1" @click="()=>{$socket.emit('special', {})}">{{$t('special_ability')}}</button>
			<button :class="{'btn': true, 'cant-play':(pending_action != 2)}" :disabled="pending_action != 2" v-if="!(eventCard && eventCard.name == 'Sbornia') && is_my_turn && character.name === 'Der Spot Burst Ringer' && special_use_count < 1" @click="()=>{$socket.emit('special', {})}">{{$t('special_ability')}}</button>
			<button :class="{'btn': true, 'cant-play':(pending_action != 2)}" :disabled="pending_action != 2" v-if="!(eventCard && eventCard.name == 'Sbornia') && is_my_turn && character.name === 'Black Flower' && special_use_count < 1" @click="()=>{$socket.emit('special', {})}">{{$t('special_ability')}}</button>
			<button :class="{'btn': true, 'cant-play':(pending_action != 2)}" :disabled="pending_action != 2" v-if="!(eventCard && eventCard.name == 'Sbornia') && is_my_turn && character.name === 'Flint Westwood' && special_use_count < 1" @click="()=>{$socket.emit('special', {})}">{{$t('special_ability')}}</button>
			<button :class="{'btn': true, 'cant-play':(pending_action != 2)}" :disabled="pending_action != 2" v-if="!(eventCard && eventCard.name == 'Sbornia') && is_my_turn && character.name === 'Lee Van Kliff' && special_use_count < 1" @click="()=>{$socket.emit('special', {})}">{{$t('special_ability')}}</button>
		</div>
		<div v-if="lives > 0 || is_ghost" style="position:relative">
			<span id="hand_text">{{$t('hand')}}</span>
			<span id="hand_text" style="bottom:40pt;">{{hand.length}}/{{maxHandLength()}}</span>
			<transition-group name="list" tag="div" :class="{hand:true, 'play-cards':pending_action===2}">
				<Card v-for="card in handComputed" v-bind:key="card.name+card.number+card.suit" :card="card" 
					@click.native="play_card(card, false)"
					@pointerenter.native="setHint(card)" @pointerleave.native="hint=''"
					:class="{'cant-play':card.cantBePlayed}"/>
			</transition-group>
		</div>
		<transition name="list">
			<p v-if="hint"><i>{{hint}}</i></p>
		</transition>
		<Chooser v-if="is_my_turn && pending_action == 4 && (lives > 0 || is_ghost) && !(emporioCards && emporioCards.cards && emporioCards.cards.length > 0)" :text="$t('wait')" :cards="[]"/>
		<Chooser v-if="card_against" :text="$t('card_against')" :hint-text="visiblePlayers.length === 0 ? $t('no_players_in_range'):''" :cards="visiblePlayers" :select="selectAgainst" :cancel="card_against.number !== 42 ? cancelCardAgainst : null"/>
		<Chooser v-if="pending_action == 3" :text="respondText" :cards="respondCards" :select="respond" :playAudio="true" :timer="30"/>
		<Chooser v-if="shouldChooseCard" :text="$t(choose_text)" :cards="available_cards" :select="choose" :playAudio="true" :timer="30"/>
		<Chooser v-if="lives <= 0 && max_lives > 0 && !is_ghost && !spectator" :text="$t('you_died')" :cancelText="$t('spectate')" :cancel="()=>{max_lives = 0; spectator = true}"/>
		<Chooser v-if="win_status !== undefined" :text="win_status?$t('you_win'):$t('you_lose')" />
		<Chooser v-if="show_role" :text="$t('you_are')" :cards="[my_role]" :hintText="($i18n.locale=='it'?my_role.goal:my_role.goal_eng)" :select="() => {show_role=false}" :cancel="() => {show_role=false}" :cancelText="$t('ok')"/>
		<Chooser v-if="notifycard" :key="notifycard.card" :text="`${notifycard.player} ${$t('did_pick_as')}:`" :cards="[notifycard.card]" :hintText="$t(notifycard.message)" class="turn-notify-4s"/>
		<Chooser v-if="cantplaycard" :key="cantplaycard" :text="`${$t('cantplaycard')}`" class="turn-notify-4s"/>
		<Chooser v-if="!show_role && is_my_turn && pending_action < 2" :text="$t('play_your_turn')" :key="is_my_turn" class="turn-notify" />
		<Chooser v-if="!show_role && availableCharacters.length > 0" :text="$t('choose_character')" :cards="availableCharacters" :select="setCharacter" :timer="45"/>
		<Chooser v-if="hasToPickResponse" :playAudio="true" :text="`${$t('pick_a_card')} ${attacker?($t('to_defend_from')+' '+attacker):''}`" :key="hasToPickResponse" class="turn-notify" />
		<Chooser v-if="!card_against && card_with" :text="`${$t('choose_scarp_card_to')} ${card_with.name.toUpperCase()}`" :cards="handComputed.filter(x => x !== card_with && (x.name.indexOf(card_with.need_with_only) > -1))" :select="selectWith" :cancel="()=>{card_with = null}"/>
		<Chooser v-if="showScrapScreen" :text="`${$t('discard')} ${hand.length}/${maxHandLength()}`" :cards="hand" :select="scrap"  :cancel="cancelEndingTurn"/>
		<Chooser v-if="sidWantsScrapForHealth && scrapHand.length < 2" :text="`${$t('discard')} ${2 - scrapHand.length} ${$t('to_regain_1_hp')}`"
							:cards="notScrappedHand" :select="sidScrap" :cancel="() => {sidWantsScrapForHealth = false;scrapHand=[]}"/>
		<Chooser v-if="joseScrap" :text="`${$t('discard')}`"
							:cards="hand.filter(x => x.is_equipment)" :select="(card) => {joseScrap=false;scrap(card)}" :cancel="() => {joseScrap=false}"/>
		<Chooser v-if="holydayScrap && scrapHand.length < 2" :text="`${$t('discard')} ${2 - scrapHand.length}`"
							:cards="notScrappedHand" :select="holydayScrapAdd" :cancel="() => {holydayScrap = false;scrapHand=[]}"/>
		<Chooser v-if="holydayScrap && scrapHand.length == 2" :text="$t('card_against')" :cards="visiblePlayers" :select="holydayScrapBang" :cancel="() => {holydayScrap = false;scrapHand=[]}"/>
		<Chooser style="filter: grayscale(1);" v-if="emporioCards && emporioCards.cards && emporioCards.cards.length > 0 && (pending_action === 4 || pending_action === null)" :text="$t('emporio_others', [emporioCards.name])" :cards="emporioCards.cards"/>
		<div style="position: fixed;width: 100%;height: 100%;background: #ff000070;top: 0;left: 0;" v-if="hurt" class="hurt-notify"/>
	</div>
</template>

<script>
import Card from '@/components/Card.vue'
import Chooser from '@/components/Chooser.vue'

export default {
	name: 'Player',
	props: {
		chooseCardFromPlayer: Function,
		cancelChooseCardFromPlayer: Function,
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
		gold_rush_equipment: [],
		hand: [],
		lives: 0,
		max_lives: 0,
		hint: '',
		pending_action: 4,
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
		sight_extra: 1,
		norangecard: false,
		can_target_sheriff: true,
		show_role: false,
		attacker: undefined,
		attacking_card: undefined,
		notifycard: null,
		desc: '',
		scrapHand: [],
		sidWantsScrapForHealth: false,
		choose_text: '',
		joseScrap: false,
		holydayScrap: false,
		special_use_count: 0,
		mancato_needed: 0,
		is_ghost: false,
		name: '',
		eventCard: false,
		emporioCards: {},
		spectator: false,
		noStar: false,
		committed_suit_manette: null,
		gold_nuggets: 0,
		cantplaycard: false,
		avatar: '',
		hurt: false,
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
		emporio(cards) {
			this.emporioCards = JSON.parse(cards)
		},
		self(self) {
			self = JSON.parse(self)
			this.name = self.name
			this.avatar = self.avatar
			this.pending_action = self.pending_action
			this.character = self.character
			if (this.character != null) {
				this.character.is_character = true
			}
			this.hand = self.hand
			this.equipment = self.equipment
			this.gold_rush_equipment = self.gold_rush_equipment
			this.lives = self.lives
			this.max_lives = self.max_lives
			this.has_played_bang = self.has_played_bang
			this.special_use_count = self.special_use_count
			this.choose_text = self.choose_text.split('|')[0]
			this.is_my_turn = self.is_my_turn
			this.committed_suit_manette = self.committed_suit_manette
			if (this.is_my_turn) document.title = this.$t('your_turn')+' | PewPew!'
			else if (this.pending_action == 3) document.title = this.$t('your_response')+' | PewPew!'
			else if (this.pending_action == 5) document.title = this.$t('your_choose')+' | PewPew!'
			else document.title = 'PewPew!'
			if ((this.live > 0 || this.is_ghost) && this.spectator) this.spectator = false
			this.expected_response = self.expected_response
			this.available_cards = self.available_cards
			this.win_status = self.win_status
			this.sight = self.sight
			this.sight_extra = self.sight_extra
			this.attacker = self.attacker
			this.attacking_card = self.attacking_card
			this.mancato_needed = self.mancato_needed
			this.is_ghost = self.is_ghost
			if (this.pending_action == 5 && self.target_p) {
				this.chooseCardFromPlayer(self.target_p)
			} else if (this.pending_action == 5) {
				this.shouldChooseCard = true
			} else {
				this.cancelChooseCardFromPlayer()
				this.shouldChooseCard = false
			}
			this.noStar = self.noStar
			this.gold_nuggets = self.gold_nuggets
			let mustplay = this.handComputed.filter(x => x.number == 42);
			if (mustplay.length > 0) {
				this.play_card(mustplay[0], false)
			}
		},
		self_vis(vis) {
			// console.log('received visibility update')
			// console.log(vis)
			this.playersDistances = JSON.parse(vis)
		},
		notify_card(mess) {
			this.notifycard = mess
			setTimeout(function(){
					this.notifycard = null
				}.bind(this), 4000)
		},
		hurt() {
			this.hurt = true
			setTimeout(function(){
					this.hurt = false
			}.bind(this), 500)
		},
		cant_play_card() {
			this.cantplaycard = true
			setTimeout(function(){
					this.cantplaycard = false
				}.bind(this), 1000)
		},
		event_card(card) {
			this.eventCard = card
		},
	},
	computed:{
		respondText() {
			let attCard = this.attacking_card ? ' ('+this.$t('cards.'+this.attacking_card+'.name')+')' : '';
			return `${this.$t('choose_response')}${this.attacker?(this.$t('choose_response_to')+this.attacker+attCard):''}${(this.mancato_needed>1)?(` (${this.$t('choose_response_needed')} ` + this.mancato_needed + ')'):''}`
		},
		showScrapScreen() {
			return this.isEndingTurn && !this.canEndTurn && this.is_my_turn;
		},
		notScrappedHand() {
			return this.hand.filter((x, i) => (this.scrapHand.indexOf(i) === -1))
		},
		otherPlayers() {
			let vis = this.playersDistances.filter(x => {
					return x.name !== this.name
				}).map(player => {
				return {
					name: player.name,
					number: player.dist !== undefined ? `${player.dist}⛰` : '',
					icon: this.noStar ? player.icon : player.is_sheriff ? '⭐' : '🤠',
					avatar: player.avatar,
					is_character: true,
					is_player: true
				}})
			return vis
		},
		visiblePlayers() {
			this.range;
			let vis = this.playersDistances.filter(x => {
					if (!this.can_target_sheriff && x.is_sheriff)
						return false
					else
						//console.log(x.name +" dist:" +x.dist +" range:" +this.range +" sight:" +this.sight +" sight_extra:" +this.sight_extra)
						if (this.norangecard)
							return x.dist <= this.range
						else
							return x.dist <= this.range + this.sight_extra
				}).map(player => {
				return {
					name: player.name,
					number: player.dist !== undefined ? `${player.dist}⛰` : '',
					icon: this.noStar ? player.icon : player.is_sheriff ? '⭐' : '🤠',
					alt_text: Array(player.lives+1).join('❤️')+Array(player.max_lives-player.lives+1).join('💀'),
					avatar: player.avatar,
					is_character: true,
					is_player: true
				}})
			if (this.card_against && this.card_against.can_target_self && (this.equipment.length > 0 || this.card_against.name === 'Tequila')) {
				vis.push({
					name: this.name,
					number: '0⛰',
					alt_text: this.$t('you'),
					avatar: this.avatar,
					icon: '🤳',
					is_character: true,
					is_player: true
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
			return (this.pending_action == 2 && this.hand.length <= this.maxHandLength())
		},
		respondCards() {
			let cc = [{
					name: this.$t('take_dmg'),
					icon: '❌',
					is_equipment: true,
					noDesc: true,
				}]
			let expectedBangResponse = this.expected_response.indexOf('Bang!') !== -1
			let sborniaEvent = this.eventCard && this.eventCard.name == "Sbornia"
			this.hand.filter(x => (x.can_be_used_now && this.expected_response.indexOf(x.name) !== -1) || (!expectedBangResponse && this.character.name === "Elena Fuente" && !sborniaEvent)).forEach(x=>{
				cc.push(x)
			})
			this.equipment.filter(x => x.usable_next_turn && x.can_be_used_now && this.expected_response.indexOf(x.name) !== -1).forEach(x=>{
				cc.push(x)
			})
			return cc
		},
		equipmentComputed() {
			let eq = []
			this.equipment.forEach(x => eq.push(x));
			this.gold_rush_equipment.forEach(x => eq.push(x));
			return eq
		},
		handComputed() {
			return this.hand.map(x => {
				let cantBePlayed = false
				let calamity_special = (x.name === 'Mancato!' && this.character.name === 'Calamity Janet')
				let cant_play_bang = (this.has_played_bang && this.equipment.filter(x => x.name == 'Volcanic').length == 0)
				if ((x.name == 'Bang!' || x.name == 'Sventagliata' || (calamity_special && x.name=='Mancato!')) && (cant_play_bang || (this.eventCard && this.eventCard.name == "Sermone"))) cantBePlayed = true;
				else if (this.eventCard && this.eventCard.name == "Il Giudice" && (x.is_equipment || !x.can_be_used_now)) cantBePlayed = true;
				else if (this.eventCard && this.eventCard.name == "Il Reverendo" && (x.name == "Birra")) cantBePlayed = true;
				else if (this.need_with && this.hand.length === 1) cantBePlayed = true;
				else if (this.committed_suit_manette !== null && this.committed_suit_manette !== x.suit) cantBePlayed = true;
				return {
					...x,
					cantBePlayed: cantBePlayed
				}
			})
		}
	},
	methods: {
		maxHandLength() {
			return (this.character.name === "Sean Mallory" && !(this.eventCard && this.eventCard.name == "Sbornia")?10:(this.gold_rush_equipment.filter(x => x.name == 'Cinturone').length>0?8:this.lives))
		},
		setCharacter(char) {
			this.availableCharacters = []
			this.$socket.emit('set_character', char.name)
		},
		sidScrap(c) {
			this.scrapHand.push(this.hand.indexOf(c))
			if (this.scrapHand.length == 2) {
				let x = [this.scrapHand[0], this.scrapHand[1]].sort().reverse()
				this.$socket.emit('scrap', x[0])
				this.$socket.emit('scrap', x[1])
				this.scrapHand = []
				this.sidWantsScrapForHealth = false
			}
		},
		setDesc(card) {
			if (card.desc)
				this.desc = (this.$i18n.locale=='it'?card.desc:card.desc_eng)
			else
				this.desc = this.$t(`cards.${card.name}.desc`)
		},
		setHint(card) {
			if (card.desc)
				this.hint = (this.$i18n.locale=='it'?card.desc:card.desc_eng)
			else
				this.hint = this.$t(`cards.${card.name}.desc`)
		},
		holydayScrapAdd(c) {
			this.scrapHand.push(this.hand.indexOf(c))
		},
		holydayScrapBang(other) {
			this.$socket.emit('special', {
				cards : [this.scrapHand[0], this.scrapHand[1]],
				against: other.name
			})
			this.scrapHand = []
			this.holydayScrap = false
		},
		end_turn(){
			// console.log('ending turn')
			this.cancelEndingTurn()
			this.$socket.emit('end_turn')
		},
		scrap(c) {
			this.$socket.emit('scrap', this.hand.indexOf(c))
		},
		play_card(card, from_equipment) {
			console.log('play ' + card.name)
			if (from_equipment && ((!card.can_be_used_now && !card.name == 'Lemat') || (this.eventCard && this.eventCard.name == "Lazo"))) return;
			else if (card.usable_next_turn && !card.can_be_used_now) return this.really_play_card(card, null);
			let calamity_special = (card.name === 'Mancato!' && this.character.name === 'Calamity Janet')
			let cant_play_bang = (this.has_played_bang && card.number !==42 && this.equipment.filter(x => x.name == 'Volcanic').length == 0)
			if (this.pending_action == 2) {
				this.can_target_sheriff = (card.name !== 'Prigione')
				if (card.need_with && !this.card_with) {
					this.card_with = card
				} else if ((card.need_target || calamity_special) && !((card.name == 'Bang!' || (calamity_special && card.name=='Mancato!')) && cant_play_bang)) {
						if (card.name == 'Bang!' || card.name == "Pepperbox" || calamity_special) {
							this.range = this.sight
							this.norangecard = true
						} else {
							this.range = card.range
							this.norangecard = false
						}
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
				this.norangecard = false
				this.card_with = card
			} else {
				let card_data	 = {
					index: this.handComputed.indexOf(this.card_with),
					against: null,
					with: this.handComputed.indexOf(card),
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
			let res = this.handComputed.indexOf(card)
			if (res === -1) {
				res = this.equipmentComputed.indexOf(card)
				if (res !== -1) res += this.hand.length
			}
			let card_data	 = {
				index: res,
				against: against,
				with: this.handComputed.indexOf(this.card_with) > -1 ? this.handComputed.indexOf(this.card_with):null,
			}
			this.card_with = null
			// console.log(card_data)
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
	border: 2px dashed var(--muted-color);
	padding: 10pt 40pt 0pt 40pt;
	overflow:auto;
	border-radius: 4pt;
	min-height: 122pt;
}
@media not all and (min-resolution:.001dpcm)
{ @supports (-webkit-appearance:none) and (stroke-color:transparent) {
	.hand {
		border-radius: 0;
	}
}}

.hand>.card{
	margin-left: -30pt;
}
.hand>.card:hover {
	transform: translateY(-15px) translateX(-15px) rotate(-2deg);
	z-index: 1;
}
.hand>.card:nth-child(1):hover, .hand>.card:last-child:hover {
	transform: translateY(-15px) translateX(0) rotate(2deg);
	z-index: 1;
}
#hand_text{
	color: var(--muted-color);
	position: absolute;
	font-size: xxx-large;
	font-size: -webkit-xxx-large;
	font-weight: 300;
	bottom: 0;
	right: 10pt;
}
.equipment-slot {
	display:flex;
	margin: 10pt 0pt;
	overflow:auto;
}
#equipment .card:nth-child(even) {
	transform: rotate(1deg);
}
#equipment .card:nth-child(odd) {
	transform: rotate(-1deg);
}
.hurt-notify {
	pointer-events: none;
	animation: disappear 0.5s ease-in forwards;
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
/* @keyframes play-cards {
	50% {
		background: rgba(204, 204, 204, 0.3);
	}
}
.play-cards {
	animation: play-cards;
	animation-duration: 3s;
	animation-iteration-count: infinite;
} */
</style>