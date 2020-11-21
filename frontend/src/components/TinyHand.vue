<template>
	<div style="position:absolute;transform:scale(0.45);bottom:50pt;">
		<div class="card back" v-for="(n, i) in ncards" :style="`position:absolute; transform:rotate(${(i-ncards/2)*2}deg) translate(${i*15}px,0);`" v-bind:key="n" :alt="i">
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
	},
}
</script>
<style>

</style>