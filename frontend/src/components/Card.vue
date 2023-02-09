<template>
	<div :class="{ card: true, avatarred:card.avatar, equipment: card.is_equipment, character:card.is_character, back:card.is_back, 'usable-next-turn':card.usable_next_turn, 'must-be-used':card.must_be_used, 'gold-rush': card.expansion === 'gold_rush', 'brown':card.kind === 0, 'black':card.kind === 1,}">
		<h4>{{cardName}}</h4>
		<div v-if="card.avatar" class="avatar" :style="`background-image: url(${card.avatar});`"></div>
		<div :class="{emoji:true, bottomed:card.avatar}">{{emoji}}</div>
		<div class="alt_text">{{card.alt_text}}</div>
		<div class="suit">{{number}}<span :style="`${(card.suit !== undefined && card.suit%2 === 0)? 'color:red':''}`">{{suit}}</span></div>
		<div class="expansion" v-if="card.expansion_icon">{{card.expansion_icon}}</div>
	</div>
</template>

<script>
export default {
	name: 'Card',
	props: {
		card: Object,
		donotlocalize: Boolean
	},
	computed: {
		cardName(){
			// console.log(this.$t(`cards.${this.card.name}.name`))
			if (!this.donotlocalize && this.$t(`cards.${this.card.name}.name`) !== `cards.${this.card.name}.name`) {
				return this.$t(`cards.${this.card.name}.name`)
			}
			if (this.card.name == "you") {
				return this.$t('you')
			}
			return this.card.name
		},
		emoji(){
			return this.card.icon != "you" ? this.card.icon : this.$t('you')
		},
		suit() {
			if (this.card && !isNaN(this.card.suit)) {
				let x = ['♦️','♣️','♥️','♠️','🤑']
				return x[this.card.suit];
			} else if (this.card.suit) {
				return this.card.suit;
			}
			return '';
		},
		number() {
			if (isNaN(this.card.suit))
				return this.card.number
			if (this.card.number === 1) return 'A'
			else if (this.card.number === 11) return 'J'
			else if (this.card.number === 12) return 'Q'
			else if (this.card.number === 13) return 'K'
			else return this.card.number
		}
	}
}
</script>

<style>
.card {
	cursor: pointer;
	width: 60pt;
	min-width:60pt;
	height: 100pt;
	margin: 12pt;
	background: var(--bg-color);
	box-shadow: 
		0 0 0 3pt #987e51,
		0 0 0 6pt var(--bg-color),
		0 0 5pt 6pt #aaa;
	border-radius: 6pt;
	position: relative;
	transition: all 0.5s ease-in-out;
	color: var(--font-color);
	/* overflow: hidden; */
	text-overflow: ellipsis;
	word-wrap: normal;
	/* word-wrap: break-word; */
}
.avatarred {
	display: flex;
	align-items: center;
	justify-content: center;
	flex-wrap: wrap;
}
.card.back{
	color:white;
	background: repeating-linear-gradient(
		45deg,
		#987e51,
		#987e51 5px,
		#816b45 5px,
		#816b45 10px
	);
}
.card:not(.back,.fistful-of-cards,.high-noon,.gold-rush):before{
	content: "";
	background-image: radial-gradient(var(--bg-color) 13%, #0000 5%),
				radial-gradient(var(--bg-color) 14%, transparent 5%),
				radial-gradient(var(--bg-color) 8%, transparent 5%);
	background-position: -12px 0, 12px 14px, 0 -12pt;
	background-size: 50px 50px;
	position: absolute;
	top: -10px;
	left: -10px;
	bottom: -4px;
	right: -4px;
}
.card.equipment {
	box-shadow: 
		0 0 0 3pt #5c5e83,
		0 0 0 6pt var(--bg-color),
		0 0 5pt 6pt #aaa;
}
.card.character {
	box-shadow: 
		0 0 0 3pt #7c795b,
		0 0 0 6pt var(--bg-color),
		0 0 5pt 6pt #aaa;
}
.card.usable-next-turn {
	box-shadow: 
		0 0 0 3pt  #6aa16e, 0 0 0 6pt var(--bg-color), 0 0 5pt 6pt #aaa
}
.card.high-noon{
	box-shadow: 0 0 0pt 4pt var(--bg-color), 0 0 5pt 4pt #aaa;
	border: 2pt dotted rgb(198 78 45);
}
.card.fistful-of-cards{
	box-shadow: 0 0 0pt 4pt var(--bg-color), 0 0 5pt 4pt #aaa;
	border: 2pt dashed rgb(50 122 172);
}
.card.back.fistful-of-cards{
	color:var(--bg-color);
	background: repeating-linear-gradient(
		45deg,
		rgb(50 122 172),
		rgb(50 122 172) 5px,
		rgb(30 102 152) 5px,
		rgb(30 102 152) 10px
	);
	border: 2pt solid rgb(50 122 172);
}
.avatar {
	position: absolute;
	width: 36pt;
	margin: auto;
	top: 25%;
	background-position: center;
	background-size: contain;
	background-repeat: no-repeat;
	border-radius: 36pt;
	height: 36pt;
}
.card.brown.gold-rush {
	box-shadow: 0 0 0pt 4pt var(--bg-color), 0 0 5pt 4pt #aaa;
	border: 2pt dotted #9C7340;
}
.card.black.gold-rush {
	box-shadow: 0 0 0pt 4pt var(--bg-color), 0 0 5pt 4pt #aaa;
	border: 2pt dotted #000;
}
.card.back.gold-rush {
	background: repeating-linear-gradient(347deg, #ffb32f, #987e51 );
}
.card h4 {
	position: absolute;
	text-align: center;
	width: 100%;
	top: -10pt;
	font-size: 11pt;
}
.card .emoji {
	position: absolute;
	text-align: center;
	width: 100%;
	font-size:26pt;
	top: 35%;
} 
.emoji.bottomed {
	top: 45%;
	left: 8pt;
}
.card.must-be-used {
	filter: drop-shadow(0 0 5px red);
}
.fistful-of-cards .emoji, .high-noon .emoji{
	top:auto !important;
	bottom:15% !important;
}
.card .suit {
	position: absolute;
	bottom: 3pt;
	left:3pt;
}
.card.character .suit {
	font-size: small;
	right: 3pt;
	text-align: center;
}
.alt_text {
	right: 3pt;
	text-align: center;
	position: absolute;
	font-size: small;
	bottom: 20pt;
	left: 3pt;
}
.cant-play {
	filter: brightness(0.5);
}
.expansion {
	position: absolute;
	bottom: -5pt;
	right: -5pt;
	background: var(--bg-color);
	border-radius: 100%;
	transform: scale(0.8);
}

</style>