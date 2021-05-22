<template>
	<div>
		<h1 id="help">{{$t('help.title')}}</h1>
		<h2>{{$t('help.character')}}</h2>
		<p>{{$t('help.characters_special')}}</p>
		<a href="#basecharacters"><p>{{$t('help.gotoallcharacters')}}</p></a>
		<h2>{{$t('help.roles')}}</h2>
		<div style="display:flex;">
			<card :card="{name:$t('help.sheriff'), icon:'⭐️'}" :class="{back:true}"/>
			<card :card="{name:$t('help.outlaw'), icon:'🐺️'}" :class="{back:true}"/>
			<card :card="{name:$t('help.renegade'), icon:'🦅️'}" :class="{back:true}"/>
			<card :card="{name:$t('help.vice'), icon:'🎖️'}" :class="{back:true}"/>
		</div>
		<h2>{{$t('help.turns')}}</h2>
		<p>{{$t('help.turnstart')}}</p>
		<ol>
			<li><p>{{$t('help.turndraw')}} ⏬️</p></li>
			<li><p>{{$t('help.turnplay')}} ▶️</p></li>
			<li><p>{{$t('help.turndiscard')}}</p></li>
		</ol>
		<h3>{{$t('help.drawthecards')}}</h3>
		<p>{{$t('help.drawinstructions')}}<p>
		<div style="display:flex" class="center-stuff">
			<div style="position:relative">
				<div class="card back" style="position:absolute; bottom:-3pt;right:-3pt;"/>
				<div class="card back" style="position:absolute; bottom:-1.5pt;right:-1.5pt;"/>
				<card :card="cardBack" :class="{back:true, draw:true}" @click.native="action"/>
			</div>
		</div>
		<h3>{{$t('help.playingcards')}}</h3>
		<p>{{$t('help.playingdmg')}}</p>
		<p>{{$t('help.playingduringturn')}}</p>
		<p><b>{{$t('help.playingifyouwant')}}</b></p>
		<p>{{$t('help.playlimit')}}</p>
		<ul>
			<li><p>{{$t('help.playonlyonebang')}}</p></li>
			<li><p>{{$t('help.maxtwocardsequip')}}</p></li>
			<li><p>{{$t('help.justoneweapon')}}</p></li>
		</ul>
		<h3>{{$t('help.discard')}}</h3>
		<p>{{$t('help.endingturn')}}</p>
		<card :card="endTurnCard" class="end-turn" @click.native="alert('')"/>
		<h3>{{$t('help.distance')}}</h3>
		<p>{{$t('help.distancecalc')}}</p>
		<h3>{{$t('help.playerdeath')}}</h3>
		<p>{{$t('help.deathnobeer')}}</p>
		<h3>{{$t('help.rewardspen')}}</h3>
		<ul>
			<li><p>{{$t('help.sheriffkillsvice')}}</p></li>
			<li><p>{{$t('help.outlawreward')}}</p></li>
		</ul>
		<h2>{{$t('help.endgame')}}</h2>
		<p>{{$t('help.endgameconditions')}}</p>
		<ul>
			<li><p>{{$t('help.endgameshriffdeath')}}</p></li>
			<li><p>{{$t('help.endgamesheriffwin')}}</p></li>
		</ul>
		<h2>{{$t('help.thecards')}}</h2>
		<div>
			<div v-for="(c, i) in cards" v-bind:key="c.name ? (c.name+c.number) : i" style="display:flex">
				<Card :card="c" @pointerenter.native="''" @pointerleave.native="''"/>
				<div style="margin-left:6pt;">
					<p>{{$t(`cards.${c.name}.desc`)}}</p>
					<p v-if="c.is_equipment"><b>{{$t('help.equipment')}}</b></p>
					<p v-if="c.is_weapon"><b>{{$t('help.weapon')}}</b></p>
				</div>
			</div>
		</div>
		<h2 id="basecharacters">{{$t('help.allcharacters')}}</h2>
		<div>
			<div v-for="(c, i) in characters" v-bind:key="c.name ? (c.name+c.number) : i" style="display:flex">
				<Card :card="c" @pointerenter.native="''" @pointerleave.native="''"/>
				<div style="margin-left:6pt;">
					<p>{{$t(`cards.${c.name}.desc`)}}</p>
				</div>
			</div>
		</div>
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
		cards: [],
		characters: [],
	}),
	computed: {
		endTurnCard() {
			return {
				name: this.$t('end_turn'),
				icon: '⛔️'
			}
		},
	},
	sockets: {
		cards_info(cardsJson) {
			this.cards = JSON.parse(cardsJson)
		},
		characters_info(cardsJson) {
			this.characters = JSON.parse(cardsJson).map(x=>({
				...x,
				is_character:true,
			}))
		},
	},
	mounted() {
		this.$socket.emit('get_cards')
		this.$socket.emit('get_characters')
		document.getElementById('help').scrollIntoView();
	}
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
		0 0 0 6pt var(--bg-color),
		0 0 5pt 6pt #aaa !important;
}
</style>