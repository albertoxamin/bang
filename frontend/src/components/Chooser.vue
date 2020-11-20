<template>
	<div id="overlay" class="center-stuff">
		<h1>{{text}}</h1>
		<div>
			<Card v-for="c in cards" v-bind:key="c" :card="c" @click.native="select(c)"/>
		</div>
	</div>
</template>

<script>
import Card from '@/components/Card.vue'

export default {
	name: 'Chooser',
	components: {
		Card,
	},
	props: {
		cards: Array,
		select: Function,
		text: String,
	},
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
#overlay {
	position: fixed; /* Sit on top of the page content */
	width: 100%; /* Full width (cover the whole page) */
	height: 100%; /* Full height (cover the whole page) */
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background-color: rgba(0,0,0,0.8); /* Black background with opacity */
	z-index: 2; /* Specify a stack order in case you're using a different order for other elements */
	display: flex;
	color: white;
	flex-direction: column;
	justify-content: center;
}
#overlay div {
	display: flex;
	align-items: center;
	justify-content: center;
}

.card {
	width: 72pt;
	min-width:72pt;
	height: 120pt;
}
.card:hover {
	transform: translate(0, -5px) scale(1.05, 1.05);
}
</style>
