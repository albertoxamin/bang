<template>
	<p class="animated" :style="style">{{text}}</p>
</template>

<script>
export default {
	name: 'AnimatedEffect',
	props: {
		text: String,
		startPosition: Object,
	},
	data: () => ({
		style: ''
	}),
	computed: {
	},
	methods: {
	},
	mounted() {
		let startPosition = {
			top: this.startPosition.top + Math.random() * 100 - 50,
			left: this.startPosition.left + Math.random() * 100 - 25,
		}
		let endPosition = {
			top: startPosition.top + Math.random() * 50 - 25,
			left: startPosition.left + Math.random() * 50 - 25,
		}
		this.style = `position: absolute;top:${startPosition.top}px;left: ${startPosition.left}px;`
		setTimeout(() => {
			this.style = `position:absolute;;top:${endPosition.top}px;left:${endPosition.left}px;`
		}, 400)
		setTimeout(() => {
			this.style = `position:absolute;;top:${endPosition.top}px;left:${endPosition.left}px;opacity:0;`
		}, 900)
		setTimeout(() => {
			this.style = `display:none;`
		}, 1500)
	}
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.animated {
	position: absolute;
	font-size: 26pt;
	transition: all 0.5s;
}
</style>
