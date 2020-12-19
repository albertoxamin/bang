<template>
	<div :class="{ card: true, equipment: card.is_equipment, character:card.is_character, back:card.is_back, 'usable-next-turn':card.usable_next_turn}">
		<h4>{{card.name}}</h4>
		<div class="emoji">{{card.icon}}</div>
		<div class="alt_text">{{card.alt_text}}</div>
		<div class="suit">{{number}}{{suit}}</div>
	</div>
</template>

<script>
export default {
	name: 'Card',
	props: {
		card: Object
	},
	computed: {
		suit() {
			if (this.card && !isNaN(this.card.suit)) {
				let x = ['♦️','♣️','♥️','♠️']
				return x[this.card.suit];
			}
			return '';
		},
		number() {
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
	background: white;
	box-shadow: 
		0 0 0 3pt #987e51,
		0 0 0 6pt white,
		0 0 5pt 6pt #aaa;
	border-radius: 6pt;
	position: relative;
	transition: all 0.5s ease-in-out;
	color: #333;
	overflow: hidden;
	text-overflow: ellipsis;
	word-wrap: normal;
	/* word-wrap: break-word; */
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
.card.equipment {
	box-shadow: 
		0 0 0 3pt #5c5e83,
		0 0 0 6pt white,
		0 0 5pt 6pt #aaa;
}
.card.character {
	box-shadow: 
		0 0 0 3pt #7c795b,
		0 0 0 6pt white,
		0 0 5pt 6pt #aaa;
}
.card.usable-next-turn {
	box-shadow: 
		0 0 0 3pt  #6aa16e, 0 0 0 6pt white, 0 0 5pt 6pt #aaa
}
.card.high-noon{
	box-shadow: 0 0 0pt 4pt white, 0 0 5pt 4pt #aaa;
	border: 2pt dotted rgb(198 78 45);
}
.card.fistful-of-cards{
	box-shadow: 0 0 0pt 4pt white, 0 0 5pt 4pt #aaa;
	border: 2pt dashed rgb(50 122 172);
}
.card h4 {
	position: absolute;
	text-align: center;
	width: 100%;
	top: -10pt;
} 
.card .emoji {
	position: absolute;
	text-align: center;
	width: 100%;
	font-size:26pt;
	top: 35%;
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
	font-size: x-small;
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
@media (prefers-color-scheme: dark) {
	:root, #app {
    background-color: #181a1b;
    color: rgb(174, 194, 211);
  }
	.card {
		background-color: #181a1b;
    color: rgb(174, 194, 211);
		box-shadow: 
			0 0 0 3pt #987e51,
			0 0 0 6pt #181a1b,
			0 0 5pt 6pt #aaa;
	}
	.card.back{
		color:#181a1b;
	}
	.card.equipment {
		box-shadow: 
			0 0 0 3pt #5c5e83,
			0 0 0 6pt #181a1b,
			0 0 5pt 6pt #aaa;
	}
	.card.character {
		box-shadow: 
			0 0 0 3pt #7c795b,
			0 0 0 6pt #181a1b,
			0 0 5pt 6pt #aaa;
	}
	.card.usable-next-turn {
		box-shadow: 
			0 0 0 3pt #6aa16e, 0 0 0 6pt #181a1b, 0 0 5pt 6pt #aaa
	}
	.card.high-noon{
		box-shadow: 0 0 0pt 4pt #181a1b, 0 0 5pt 4pt #aaa;
	}
	.card.fistful-of-cards{
		box-shadow: 0 0 0pt 4pt #181a1b, 0 0 5pt 4pt #aaa;
	}
}
</style>