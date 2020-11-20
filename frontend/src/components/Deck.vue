<template>
	<div class="deck">
		<!-- <div v-if="lastScrap != null" :class="{ card:true, equipment: lastScrap.is_equipment }">
			<h3>{{lastScrap.name}}</h3>
			<emoji>{{lastScrap.icon}}</emoji>
			<span>{{lastScrap.number}}{{lastScrap.suit}}</span>
		</div> -->
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
		pending_action: false,
	}),
	sockets: {
		self(self){
			self = JSON.parse(self)
			this.pending_action = self.pending_action
		}
	},
	methods: {
		action() {
			if (this.pending_action && this.pending_action < 2) {
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