<template>
	<div style="position:absolute;transform:scale(0.4);bottom:52pt;">
		<div v-if="!(cards && cards.length >0)">
			<div :class="{card:true, back:true, delay:ismyturn}" v-for="(n, i) in ncards" 
			:style="`position:absolute; transform:rotate(${(i-ncards/2)*2}deg) translate(${i*15}px,0); animation-delay:${0.1*i}s`"
			v-bind:key="n" :alt="i">
				<h4 v-if="n==ncards">PewPew!</h4>
				<div class="emoji" v-if="n==ncards">💥</div>
			</div>
		</div>
		<div v-else>
			<card :card="c" :key="c" v-for="(c, i) in cards"
			:class="{delay:ismyturn, zoomable:true}"
			:style="`position:absolute; transform:rotate(${(i-ncards/2)*5}deg) translate(${(i-ncards/3)*40}px,0); animation-delay:${0.1*i}s`"/>
		</div>
	</div>
</template>

<script>
import Card from './Card.vue'
export default {
  components: { Card },
	name: 'TinyHand',
	props: {
		ncards: Number,
		cards: Array,
		ismyturn: Boolean,
	},
}
</script>
<style scoped>
.delay {
	animation-name: updown;
	animation-duration: 2s;
	animation-iteration-count: infinite;
}
.zoomable:hover {
	z-index: 1;
}
@keyframes updown {
	0% {
		top: 0;
	}
	50% {
		top:10pt;
	}
	100% {
		top: 0;
	}
}
</style>