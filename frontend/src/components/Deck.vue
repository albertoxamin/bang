<template>
	<div>
		<div class="deck">
			<card v-if="endTurnAction && isPlaying" v-show="pending_action == 2" :card="endTurnCard" class="end-turn" @click.native="endTurnAction"/>
			<div v-if="eventCard" style="position:relative">
				<div class="card fistful-of-cards" style="position:relative; bottom:-3pt;right:-3pt;"/>
				<div class="card fistful-of-cards" style="position:absolute; bottom:-1.5pt;right:-1.5pt;"/>
				<card :card="eventCard" :key="eventCard.name" :class="eventClasses" @click.native="event"/>
			</div>
			<div style="position:relative">
				<div class="card back" style="position:absolute; bottom:-3pt;right:-3pt;"/>
				<div class="card back" style="position:absolute; bottom:-1.5pt;right:-1.5pt;"/>
				<card :card="card" :class="{back:true, pick:pending_action === 0, draw:pending_action === 1}" @click.native="action"/>
			</div>
			<div style="position:relative;">
				<card v-if="previousScrap" :card="previousScrap" style="top: 1.5pt;right: -1.5pt;"/>
				<card v-else :card="card" class="back" style="opacity:0"/>
				<card v-if="lastScrap" :card="lastScrap" :key="lastScrap.name+lastScrap.number" class="last-scrap" @click.native="action('scrap')"
							@pointerenter.native="desc=($i18n.locale=='it'?lastScrap.desc:lastScrap.desc_eng)" @pointerleave.native="desc=''" />
			</div>
		</div>
		<transition name="list">
			<p v-if="eventCard" class="center-stuff"><i>{{($i18n.locale=='it'?eventCard.desc:eventCard.desc_eng)}}</i></p>
		</transition>
		<transition name="list">
			<p v-if="desc" class="center-stuff"><i>{{desc}}</i></p>
		</transition>
	</div>
</template>

<script>
import Card from '@/components/Card.vue'

export default {
	name: 'Deck',
	props: {
		endTurnAction: Function
	},
	components: {
		Card,
	},
	data: () => ({
		card: {
			name: 'PewPew!',
			icon: '💥',
		},
		lastScrap: null,
		eventCard: null,
		previousScrap: null,
		pending_action: false,
		isPlaying: true,
		desc: '',
	}),
	sockets: {
		self(self){
			self = JSON.parse(self)
			this.isPlaying = self.lives > 0 || self.is_ghost
			this.pending_action = self.pending_action
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
		}
	},
	methods: {
		action(pile) {
			if (this.pending_action !== false && this.pending_action < 2) {
				console.log('action')
				if (this.pending_action == 0)
					this.$socket.emit('pick')
				else if (this.pending_action == 1)
					this.$socket.emit('draw', pile)
			}
		},
		event() {
			if (this.pending_action !== false) {
				this.$socket.emit('draw', 'event')
			}
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
		0 0 0 6pt white,
		0 0 5pt 6pt #aaa !important;
}
@media (prefers-color-scheme: dark) {
	.end-turn {
		box-shadow: 0 0 0 3pt rgb(138, 12, 12), 0 0 0 6pt #181a1b, 0 0 5pt 6pt #aaa !important;
	}
}
</style>