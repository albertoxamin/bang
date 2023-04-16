<template>
	<div >
		<div class="deck">
			<div class="deck" :style="`position:relative;${goldRushShopOpen?'border: 2px dashed #6a6a6a42;border-radius:8pt':''}`" v-if="goldRushCards.length > 0" >
				<card @pointerenter.native="()=>{setGoldRushDesc(goldRushCards[0])}" @pointerleave.native="goldRushDesc=null" :style="goldRushShopOpen?``:`position:absolute; top:0; right:0; transform: rotate(95deg) translate(30px, -40px) scale(0.6)`" v-if="goldRushCards.length > 0" :key="goldRushCards[0].name" :card="goldRushCards[0]" :class="{'shop-open':goldRushShopOpen, 'cant-play': pending_action !==2 || gold_nuggets < goldRushCards[0].number - gold_rush_discount}" @click.native="() => {buy_gold_rush_card(0)}"/>
				<card @pointerenter.native="()=>{setGoldRushDesc(goldRushCards[1])}" @pointerleave.native="goldRushDesc=null" :style="goldRushShopOpen?``:`position:absolute; top:0; right:0; transform: rotate(90deg)  translate(0, -40px) scale(0.6)`" v-if="goldRushCards.length > 1" :key="goldRushCards[1].name" :card="goldRushCards[1]" :class="{'shop-open':goldRushShopOpen, 'cant-play': pending_action !==2 || gold_nuggets < goldRushCards[1].number - gold_rush_discount}" @click.native="() => {buy_gold_rush_card(1)}"/>
				<card @pointerenter.native="()=>{setGoldRushDesc(goldRushCards[2])}" @pointerleave.native="goldRushDesc=null" :style="goldRushShopOpen?``:`position:absolute; top:0; right:0; transform: rotate(85deg) translate(-30px, -40px) scale(0.6)`" v-if="goldRushCards.length > 2" :key="goldRushCards[2].name" :card="goldRushCards[2]" :class="{'shop-open':goldRushShopOpen, 'cant-play': pending_action !==2 || gold_nuggets < goldRushCards[2].number - gold_rush_discount}" @click.native="() => {buy_gold_rush_card(2)}"/>
				<div style="position:relative">
					<div class="card gold-rush back" style="position:relative; bottom:-3pt;right:-3pt;"/>
					<div class="card gold-rush back" style="position:absolute; bottom:-1.5pt;right:-1.5pt;"/>
					<card :card="goldRushCardBack" :donotlocalize="true" class="gold-rush back last-event" @click.native="goldRushShopOpen = !goldRushShopOpen"/>
				</div>
			</div>
			<div v-if="current_stations.length > 0" class="deck" :style="`position:relative;border: 2px dashed #6a6a6a42;border-radius:8pt;align-items: flex-end;`" >
				<station-card v-for="station, i in current_stations" :key="station.name" :card="station" :price="station.price" :trainPiece="
					i == 2 ? {
						name: 'Iron House',
						icon: '🚂',
						back: true,
					} : i > 2 ? {
						name: 'Passenger Car',
						icon: '🚃',
						back: true,
					} : undefined
				"/>
			</div>
			<div v-if="eventCard" style="position:relative">
				<div class="card fistful-of-cards" style="position:relative; bottom:-3pt;right:-3pt;"/>
				<div class="card fistful-of-cards" style="position:absolute; bottom:-1.5pt;right:-1.5pt;"/>
				<card :card="eventCard" :key="eventCard.name" :class="eventClasses" @click.native="() => event('event')"/>
			</div>
			<div v-if="eventCardWildWestShow" style="position:relative">
				<div class="card wild-west-show back" style="position:relative; bottom:-3pt;right:-3pt;"/>
				<div class="card wild-west-show back" style="position:absolute; bottom:-1.5pt;right:-1.5pt;"/>
				<card :card="eventCardWildWestShow" :key="eventCardWildWestShow.name" :class="eventWwsClasses" @click.native="() => event('event_wildwestshow')"/>
			</div>
			<div style="position:relative" class="deck">
				<div style="position:relative" id="actual-deck">
					<div class="card back" style="position:absolute; bottom:-3pt;right:-3pt;"/>
					<div class="card back" style="position:absolute; bottom:-1.5pt;right:-1.5pt;"/>
					<card :card="card" :donotlocalize="true" :class="{back:true, pick:pending_action === 0, draw:pending_action === 1}" @click.native="action"/>
				</div>
				<div style="position:relative;" id="actual-scrap">
					<card v-if="previousScrap" :card="previousScrap" style="top: 1.5pt;right: -1.5pt;"/>
					<card v-else :card="card" class="back" style="opacity:0"/>
					<card v-if="lastScrap" :card="lastScrap" :key="lastScrap.name+lastScrap.number" class="last-scrap" @click.native="action('scrap')"
								@pointerenter.native="setdesc" @pointerleave.native="desc=''" />
				</div>
				<card v-if="endTurnAction && isPlaying" :donotlocalize="true" v-show="pending_action == 2" :card="endTurnCard" class="end-turn" @click.native="endTurnAction"/>
			</div>
		</div>
		<transition name="list">
			<p v-if="eventCard" class="center-stuff"><b>{{eventDesc}}</b></p>
		</transition>
		<transition name="list">
			<p v-if="eventCardWildWestShow && !eventCardWildWestShow.back" class="center-stuff">🎪 <b>{{eventDescWildWestShow}}</b> 🎪</p>
		</transition>
		<transition name="list">
			<div v-if="goldRushDesc">
				<p class="center-stuff">🤑️ <i>{{$t(`cards.${goldRushDesc.name}.desc`)}}</i> 🤑️</p>
				<p class="center-stuff">🤑️ <b>{{goldRushDesc.number - gold_rush_discount}} 💵️</b> 🤑️</p>
			</div>
		</transition>
		<div style="margin-bottom:6pt;margin-bottom: 6pt;display: flex;flex-direction: column;">
			<button class="btn" v-if="pending_action == 2 && can_gold_rush_discard" @click="$socket.emit('gold_rush_discard')">{{$t('gold_rush_discard')}}</button>
		</div>
		<transition name="list">
			<p v-if="desc" class="center-stuff"><i>{{desc}}</i></p>
		</transition>
	</div>
</template>

<script>
import Card from '@/components/Card.vue'
import StationCard from '@/components/StationCard.vue'

export default {
	name: 'Deck',
	props: {
		endTurnAction: Function
	},
	components: {
		Card,
		StationCard
	},
	data: () => ({
		card: {
			name: 'PewPew!',
			icon: '💥',
		},
		goldRushCardBack: {
			name: 'GoldRush!',
			icon: '🤑️',
		},
		lastScrap: null,
		eventCard: null,
		eventCardWildWestShow: null,
		previousScrap: null,
		pending_action: false,
		isPlaying: true,
		desc: '',
		goldRushShopOpen: true,
		goldRushCards: [],
		gold_nuggets: 0,
		goldRushDesc: null,
		can_gold_rush_discard: false,
		gold_rush_discount: 0,
		current_stations: [],
	}),
	sockets: {
		self(self){
			self = JSON.parse(self)
			this.isPlaying = self.lives > 0 || self.is_ghost
			this.pending_action = self.pending_action
			this.gold_nuggets = self.gold_nuggets
			this.can_gold_rush_discard = self.can_gold_rush_discard
			this.gold_rush_discount = self.gold_rush_discount
		},
		scrap(card) {
			this.lastScrap = card
		},
		event_card(card) {
			this.eventCard = card == false ? {
				name: 'PewPew!',
				icon: '🎲',
				back: true,
				expansion: 'fistful-of-cards',
			} : card
		},
		event_card_wildwestshow(card) {
			this.eventCardWildWestShow = card == false ? {
				name: 'Wild West Show',
				icon: '🎪',
				back: true,
				expansion: 'wild-west-show',
			} : card
		},
		gold_rush_shop(cards) {
			console.log('GOLD RUSH:'+ cards)
			this.goldRushCards = JSON.parse(cards)
		},
		stations(stations) {
			this.current_stations = JSON.parse(stations)
		},
	},
	computed: {
		endTurnCard() {
			return {
				name: this.$t('end_turn'),
				icon: '⛔️'
			}
		},
		eventClasses() {
			let classes = {
				'last-event':true,
				'back':this.eventCard.back
			}
			classes[this.eventCard.expansion] = true
			return classes
		},
		eventWwsClasses() {
			let classes = {
				'last-event':true,
				'back':this.eventCardWildWestShow.back,
				'wild-west-show':true,
			}
			return classes
		},
		eventDesc() {
			this.eventCard;
			if (this.eventCard.name !== 'PewPew!'){
				return this.$t(`cards.${this.eventCard.name}.desc`)
			}
			return ""
		},
		eventDescWildWestShow() {
			this.eventCardWildWestShow;
			if (this.eventCardWildWestShow.name !== 'PewPew!'){
				return this.$t(`cards.${this.eventCardWildWestShow.name}.desc`)
			}
			return ""
		},
	},
	methods: {
		action(pile) {
			if (this.pending_action !== false && this.pending_action < 2) {
				// console.log('action')
				if (this.pending_action == 0)
					this.$socket.emit('pick')
				else if (this.pending_action == 1)
					this.$socket.emit('draw', pile)
			}
		},
		buy_gold_rush_card(index) {
			this.$socket.emit('buy_gold_rush_card', index)
		},
		event(pile='event') {
			if (this.pending_action !== false) {
				this.$socket.emit('draw', pile)
			}
		},
		setdesc() {
			if (this.lastScrap.desc)
				this.desc = (this.$i18n.locale=='it'?this.lastScrap.desc:this.lastScrap.desc_eng)
			else
				this.desc = this.$t(`cards.${this.lastScrap.name}.desc`)
		},
		setGoldRushDesc(card) {
			this.goldRushDesc = card
		},
	},
	mounted() {
		if (window.innerWidth < 1000) {
			this.goldRushShopOpen = false;
		}
	},
	watch: {
		lastScrap(newVal, old) {
			this.previousScrap = old
			newVal;
		}
	}
}
</script>
<style scoped>
.deck {
	display:flex;
	margin:0;
	align-items: center;
	justify-content: center;
	flex-direction: row-reverse;
	flex-wrap: wrap-reverse;
}
.last-scrap {
	position: absolute;
	top: 0;
	animation-duration: 0.8s;
	animation-name: slidein;
}
.last-scrap:hover {
	opacity: 0.8;
	transform: translateY(-10px);
}
.gold-rush:not(.back) {
	animation-duration: 0.8s;
	animation-name: slidein;
}
@keyframes slidein {
	from {
		transform: translate(-100px, 10px) scale(1.3) rotate(-10deg);
	}
	to {
		transform: translate(0, 0) scale(1);
	}
}
.last-event {
	position: absolute;
	top: 0;
	animation-duration: 0.8s;
	animation-name: slidein;
}
@keyframes slidein {
	from {
		transform: translate(30px, 20px) scale(1.3) rotate(-10deg);
	}
	to {
		transform: translate(0, 0) scale(1);
	}
}
@keyframes pick {
	0% {
		transform: translate(0,0);
		z-index: 1;
	}
	50% {
		transform: translate(-10px,0);
		z-index: 1;
	}
	100% {
		transform: translate(0,0);
		z-index: 1;
	}
}
@keyframes draw {
	0% {
		transform: translate(0,0);
		z-index: 1;
	}
	50% {
		transform: translate(0,10px);
		z-index: 1;
	}
	100% {
		transform: translate(0,0);
		z-index: 1;
	}
}
.pick {
	animation-duration: 2s;
	animation-name: pick;
	animation-iteration-count: infinite;
}
.draw {
	animation-duration: 2s;
	animation-name: draw;
	animation-iteration-count: infinite;
}
.pick:hover {
	transform: translate(-10px,0);
	z-index: 1;
}
.draw:hover {
	transform: translate(0,10px);
	z-index: 1;
}
.end-turn {
	box-shadow: 
		0 0 0 3pt  rgb(138, 12, 12),
		0 0 0 6pt var(--bg-color),
		0 0 5pt 6pt #aaa !important;
}

</style>