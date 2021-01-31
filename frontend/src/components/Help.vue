<template>
	<div>
		<h1>Come giocare</h1>
		<h2>Personaggi</h2>
			<p>Ogni personaggio ha delle abilità speciali e un numero di vite che lo rendono unico.
			Le vite sono il numero di punti vita che puoi perdere prima di morire e indicano anche il numero massimo di carte che puoi tenere in mano.</p>
			<input type="button" value="Visualizza tutti i personaggi"/>
		<h2>Ruoli</h2>
		<ul>
			<li>Sceriffo</li>
			<li>Fuorilegge</li>
			<li>Rinnegato</li>
			<li>Vice</li>
		</ul>
		<h2>Turni</h2>
		<p>Si inizia sempre dallo Sceriffo, e il gioco prosegue in senso orario, i turni sono divisi in 3 fasi.</p>
		<ol>
			<li><p>Pesca 2 carte</p></li>
			<li><p>Gioca un numero qualsiasi di carte</p></li>
			<li><p>Scarta le carte in eccesso</p></li>
		</ol>
		<h3>Pescare le carte</h3>
		<p>Per pescare le carte dovrai cliccare sul mazzo quando vedi questa animazione.<p>
		<div style="display:flex" class="center-stuff">
			<div style="position:relative">
				<div class="card back" style="position:absolute; bottom:-3pt;right:-3pt;"/>
				<div class="card back" style="position:absolute; bottom:-1.5pt;right:-1.5pt;"/>
				<card :card="cardBack" :class="{back:true, draw:true}" @click.native="action"/>
			</div>
		</div>
		<h3>Giocare le carte</h3>
Now you may play cards to help yourself or hurt the other players, trying
to eliminate them. You can only play cards during your turn (exception:
Missed! and Beer, see below). You are not forced to play cards during this
phase. You can play any number of cards; there are only three limitations:
•	 you can play only 1 BANG! card per turn;
(this applies only to BANG! cards, not to cards with the symbol )
•	 you can have only 1 copy of any one card in play;
(one card is a copy of another if they have the same name)
•	 you can have only 1 weapon in play.
(when you play a new weapon, discard the one you have in play)
Example. If you put a Barrel in play, you cannot play another one, since you
would end up having two copies of the same card in front of you.
There are two types of cards: brown-bordered cards (= play and discard) and
blue-bordered cards (= weapons and other objects).
Brown-bordered cards are played by putting
them directly into the discard pile and applying
the effect described with text or with symbols on
the cards (illustrated in the next paragraphs).
Blue-bordered cards are played face up in front
of you (exception: Jail). Blue cards in front of
you are hence defined to be “in play”. The effect
of these cards lasts until they are discarded or
removed somehow (e.g. through the play of a Cat
Balou), or a special event occurs (e.g. in the case of Dynamite). There
is no limit on the cards you can have in front of you provided that they do
not share the same name.
<h3>Scartare</h3>
<p>Quando hai terminato di giocare le tue carte, ovvero quando non vuoi o non puoi giocare altre carte, devi scartare le carte che eccedono il tuo numero di vite attuali.
Dopodichè passi il turno al giocatore successivo cliccando su termina turno.</p>
		<card :card="endTurnCard" class="end-turn" @click.native="alert('')"/>
	</div>
</template>
<script>
import Card from './Card'
export default {
	name: 'Help',
	components: {
		Card,
	},
	data:()=>({
		cardBack: {
			name: 'PewPew!',
			icon: '💥',
		},
	}),
	computed: {
		endTurnCard() {
			return {
				name: this.$t('end_turn'),
				icon: '⛔️'
			}
		},
	},
}
</script>
<style scoped>
@keyframes pick {
	0% {
		transform: translate(0,0);
		z-index: 1;
	}
	50% {
		transform: translate(-10px,0);
		z-index: 1;
	}
	100% {
		transform: translate(0,0);
		z-index: 1;
	}
}
@keyframes draw {
	0% {
		transform: translate(0,0);
		z-index: 1;
	}
	50% {
		transform: translate(0,10px);
		z-index: 1;
	}
	100% {
		transform: translate(0,0);
		z-index: 1;
	}
}
.pick {
	animation-duration: 2s;
	animation-name: pick;
	animation-iteration-count: infinite;
}
.draw {
	animation-duration: 2s;
	animation-name: draw;
	animation-iteration-count: infinite;
}
.end-turn {
	box-shadow: 
		0 0 0 3pt  rgb(138, 12, 12),
		0 0 0 6pt white,
		0 0 5pt 6pt #aaa !important;
}
</style>