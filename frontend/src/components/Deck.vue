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
			<card :card="card" class="back"/>
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
	}),
	sockets: {

	},
	methods: {
		
	},
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