<template>
	<div id="overlay" class="center-stuff">
		<h1>{{text}}</h1>
		<div>
		<transition-group name="list" tag="div">
				<Card v-for="(c, i) in cards" v-bind:key="c.name ? (c.name+c.number) : i" :card="c" @click.native="select(c)"	@pointerenter.native="showDesc(c)" @pointerleave.native="desc=''"/>
		</transition-group>
		</div>
		<p v-if="hintText">{{hintText}}</p>
		<div style="margin-top:6pt;" class="button center-stuff" v-if="showCancelBtn" @click="cancel"><span>{{realCancelText}}</span></div>
		<p v-if="desc" style="bottom:10pt;right:0;left:0;position:absolute;margin:16pt;font-size:18pt">{{desc}}</p>
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
		cancel: Function,
		cancelText: {
			type: String,
			default: '',
		},
		text: String,
		hintText: String,
	},
	data: () => ({
		desc: '',
		realCancelText: ''
	}),
	computed: {
		showCancelBtn() {
			if (this.cancel)
				return true
			return false
		}
	},
	methods: {
		showDesc(card) {
			if (card.desc)
				this.desc = (this.$i18n.locale=='it'?card.desc:card.desc_eng)
			else
				this.desc = this.$t(`cards.${card.name}.desc`)
		}
	},
	mounted() {
		this.realCancelText = this.cancelText
		if (this.realCancelText == '') {
			this.realCancelText = this.$t('cancel')
		}
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
	background-color: rgba(0,0,0,0.7); /* Black background with opacity */
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
	flex-wrap: wrap;
}
.card {
	width: 72pt;
	min-width:72pt;
	height: 120pt;
}
.card:hover {
	transform: translate(0, -5px) scale(1.05, 1.05);
}
.button {
	background-color: #0000;
	color: white;
	border: 2px solid white;
	transition-duration: 0.2s;
	width: 100pt;
	height: 24pt;
	border-radius: 12pt;
	cursor: pointer;
}

.button:hover {
	background-color: white; /* Green */
	color: black;
}
</style>
