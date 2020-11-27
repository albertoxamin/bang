<template>
	<div class="deck">
		<card v-if="endTurnAction && isPlaying" v-show="pending_action == 2" :card="endTurnCard" class="end-turn" @click.native="endTurnAction"/>
		<div style="position:relative">
			<div class="card back" style="position:absolute; bottom:-3pt;right:-3pt;"/>
			<div class="card back" style="position:absolute; bottom:-1.5pt;right:-1.5pt;"/>
			<card :card="card" :class="{back:true, pick:pending_action === 0, draw:pending_action === 1}" @click.native="action"/>
		</div>
		<div style="position:relative;">
			<card v-if="previousScrap" :card="previousScrap"/>
			<card v-else :card="card" class="back" style="opacity:0"/>
			<card v-if="lastScrap" :card="lastScrap" :key="lastScrap" class="last-scrap" @click.native="action('scrap')"/>
		</div>
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
		endTurnCard: {
			name: this.$t('end_turn'),
			icon: '⛔️'
		},
		lastScrap: null,
		previousScrap: null,
		pending_action: false,
		isPlaying: true,
	}),
	sockets: {
		self(self){
			self = JSON.parse(self)
			this.isPlaying = self.lives > 0
			this.pending_action = self.pending_action
		},
		scrap(card) {
			this.lastScrap = card
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
@keyframes slidein {
	from {
		transform: translate(-100px, 10px) scale(1.3) rotate(-10deg);
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