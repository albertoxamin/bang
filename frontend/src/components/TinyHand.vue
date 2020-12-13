<template>
	<div style="position:absolute;transform:scale(0.4);bottom:52pt;">
		<div :class="{card:true, back:true, delay:ismyturn}" v-for="(n, i) in ncards" 
		:style="`position:absolute; transform:rotate(${(i-ncards/2)*2}deg) translate(${i*15}px,0); animation-delay:${0.1*i}s`"
		v-bind:key="n" :alt="i">
			<h4 v-if="n==ncards">PewPew!</h4>
			<div class="emoji" v-if="n==ncards">💥</div>
		</div>
	</div>
</template>

<script>
export default {
	name: 'TinyHand',
	props: {
		ncards: Number,
		ismyturn: Boolean
	},
}
</script>
<style scoped>
.delay {
	animation-name: updown;
	animation-duration: 2s;
	animation-iteration-count: infinite;
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