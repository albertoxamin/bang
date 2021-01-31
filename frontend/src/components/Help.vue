<template>
	<div>
		<h1>Come giocare</h1>
		<h2>Personaggi</h2>
			<p>Ogni personaggio ha delle abilità speciali e un numero di vite che lo rendono unico.
			Le vite sono il numero di punti vita che puoi perdere prima di morire e indicano anche il numero massimo di carte che puoi tenere in mano.</p>
			<input type="button" value="Visualizza tutti i personaggi"/>
		<h2>Ruoli</h2>
		<ul>
			<li><p>Sceriffo ⭐️</p></li>
			<li><p>Fuorilegge 🐺️</p></li>
			<li><p>Rinnegato 🦅️</p></li>
			<li><p>Vice 🎖️</p></li>
		</ul>
		<h2>Turni</h2>
		<p>Si inizia sempre dallo Sceriffo ⭐️, e il gioco prosegue in senso orario, i turni sono divisi in 3 fasi.</p>
		<ol>
			<li><p>Pesca 2 carte ⏬️</p></li>
			<li><p>Gioca un numero qualsiasi di carte ▶️</p></li>
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
		<p>Puoi giocare le tue carte per te oppure per recare danno agli altri giocatori cercando di eliminarli.</p>
		<p>Puoi giocare le carte solo nel tuo turno. Ad eccezzione delle carte usate come risposta tipo i mancato 😅️.</p>
		<p><b>Non sei obblicato a giocare carte.</b></p>
		<p>Ci sono solo 3 limitazioni:</p>
		<ul>
			<li><p>Puoi giocare 1 solo Bang! per turno (si riferisce solo alle carte con nome Bang!)</p></li>
			<li><p>Non puoi avere 2 carte con lo stesso nome equipaggiate.</p></li>
			<li><p>Puoi avere solo 1 arma equipaggiata.</p></li>
		</ul>
		<h3>Scartare</h3>
		<p>Quando hai terminato di giocare le tue carte, ovvero quando non vuoi o non puoi giocare altre carte, devi scartare le carte che eccedono il tuo numero di vite attuali.
		Dopodichè passi il turno al giocatore successivo cliccando su termina turno.</p>
		<card :card="endTurnCard" class="end-turn" @click.native="alert('')"/>
		<h3>Distanza</h3>
		<p>La distanza viene calcolata automaticamente dal gioco e corrisponde al percorso minimo tra la sinistra e la destra del giocatore.</p>
		<h3>La morte di un giocatore</h3>
		<p>Quando perdi l'ultimo punto vita e non hai una birra 🍺️ in mano, muori. Le tue carte vengono scartate e il tuo ruolo rivelato a tutti.</p>
		<h3>Penalità e ricompense</h3>
		<ul>
			<li><p>Se lo sceriffo ⭐️ uccide un vice perde tutte le carte in mano e in gioco davanti a se.</p></li>
			<li><p>Chiunque uccida un fuorilegge 🐺️ pesca 3 carte dal mazzo (anche altri fuorilegge 🐺️).</p></li>
		</ul>
		<h2>Fine del gioco</h2>
		<p>Il gioco termina quando una delle seguenti condizioni si verifica:</p>
		<ul>
			<li><p>Lo sceriffo ⭐️ muore. Se il rinnegato 🦅️ è l'ultimo giocatore in vita vince, altrimenti vincono i fuorilegge.</p></li>
			<li><p>Tutti i fuorilegge 🐺️ e i rinnegati 🦅️ sono morti. In tal caso vincono lo sceriffo ⭐️ e i vice 🎖️.</p></li>
		</ul>
		<h2>Le carte</h2>
		<input type="button" value="Visualizza tutte le carte"/>
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