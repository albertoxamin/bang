<template>
	<div>
		<div class="equipment-slot">
			<Card v-if="my_role" :card="my_role" class="back"/>
			<Card v-if="character" :card="character"/>
			<transition-group name="list" tag="equ">
				<Card v-for="card in equipment" v-bind:key="card.name+card.number" :card="card" />
			</transition-group>
		</div>
		<div class="hand">
			<i>Mano</i>
			<Card v-for="card in hand" v-bind:key="card.name+card.number" :card="card" />
		</div>
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
	}),
	sockets: {
		role(role) {
			this.my_role = JSON.parse(role)
		},
		self(self) {
			self = JSON.parse(self)
			this.character = self.character
			this.character.is_character = true
			this.hand = self.hand
			this.equipment = self.equipment
			this.lives = self.lives
			this.max_lives = self.max_lives
		}
	},
	methods: {
		
	},
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
.equipment-slot, .equipment-slot>equ {
	display:flex;
	margin:0;
}
</style>