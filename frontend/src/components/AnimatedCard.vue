<template>
	<Card v-if="card" :card="card" :class="{back:card.back}" :style="style"/>
</template>

<script>
import Card from '@/components/Card.vue'

export default {
	name: 'AnimatedCard',
	components: {
		Card,
	},
	props: {
		card: Object,
		startPosition: Object,
		midPosition: Object,
		endPosition: Object,
	},
	data: () => ({
		style: ''
	}),
	computed: {
	},
	methods: {
	},
	mounted() {
		this.style = `position: absolute;top:${this.startPosition.top}px;left: ${this.startPosition.left}px`
		if (this.midPosition) {
			setTimeout(() => {
				this.style = `position: absolute;top:${this.midPosition.top}px;left: ${this.midPosition.left}px;transform: scale(0.5);`
			}, 200)
			setTimeout(() => {
				this.style = `position: absolute;top:${this.endPosition.top}px;left: ${this.endPosition.left}px;transform: scale(0.5);`
			}, 800)
		}
		else {
			setTimeout(() => {
				this.style = `position: absolute;top:${this.endPosition.top}px;left: ${this.endPosition.left}px;transform: scale(0.5);`
			}, 200)
		}
		setTimeout(() => {
			this.style = `display:none;`
		}, this.midPosition ? 1600 : 800)
	}
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.card {
	position: absolute;
}
</style>
