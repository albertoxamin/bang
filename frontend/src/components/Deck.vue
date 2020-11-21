<template>
	<div class="deck">
		<card v-if="lastScrap" :card="lastScrap" />
		<div style="position:relative">
			<div class="card back" style="position:absolute; bottom:-3pt;right:-2pt;"/>
			<div class="card back" style="position:absolute; bottom:-1pt;right:-1pt;"/>
			<card :card="card" class="back" @click.native="action"/>
		</div>
	</div>
</template>

<script>
import Card from '@/components/Card.vue'

export default {
	name: 'Deck',
	components: {
		Card,
	},
	data: () => ({
		card: {
			name: 'PewPew!',
			icon: '💥',
		},
		lastScrap: null,
		pending_action: false,
	}),
	sockets: {
		self(self){
			self = JSON.parse(self)
			this.pending_action = self.pending_action
		},
		scrap(card) {
			this.lastScrap = card
		}
	},
	methods: {
		action() {
			if (this.pending_action !== false && this.pending_action < 2) {
				console.log('action')
				if (this.pending_action == 0)
					this.$socket.emit('pick')
				else if (this.pending_action == 1)
					this.$socket.emit('draw')
			}
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
}
</style>