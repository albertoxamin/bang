<template>
	<div>
		<a v-if="!inGame" href=".."><p>Home</p></a>
		<h1 id="help">{{$t('help.title')}}</h1>
		<a href="#thecards"><p>{{$t('help.gotocards')}}</p></a>
		<a href="#highnooncards"><p>{{$t('help.gotohighnoon')}}</p></a>
		<a href="#foccards"><p>{{$t('help.gotofoc')}}</p></a>
		<a href="#goldrushcards"><p>{{$t('help.gotogoldrush')}}</p></a>
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
		<p>{{$t('help.drawinstructions')}}</p>
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
		<h2 id="thecards">{{$t('help.thecards')}}</h2>
		<div class="flexy-cards-wrapper">
			<div v-for="(c, i) in cards" v-bind:key="c.name ? (c.name+c.number) : i" class="flexy-cards">
				<Card :card="c" @pointerenter.native="''" @pointerleave.native="''"/>
				<div style="margin-left:6pt;">
					<p>{{$t(`cards.${c.name}.desc`)}}</p>
					<p v-if="c.is_equipment"><b>{{$t('help.equipment')}}</b></p>
					<p v-if="c.is_weapon"><b>{{$t('help.weapon')}}</b></p>
					<p v-if="c.expansion"><b>{{c.expansion}}</b></p>
				</div>
			</div>
		</div>
		<h2 id="basecharacters">{{$t('help.allcharacters')}}</h2>
		<div class="flexy-cards-wrapper">
			<div v-for="(c, i) in characters" v-bind:key="c.name ? (c.name+c.number) : i" class="flexy-cards">
				<Card :card="c" @pointerenter.native="''" @pointerleave.native="''"/>
				<div style="margin-left:6pt;">
					<p>{{$t(`cards.${c.name}.desc`)}}</p>
					<p v-if="c.expansion"><b>{{c.expansion}}</b></p>
				</div>
			</div>
		</div>
		<h2 id="highnooncards">{{$t('help.highnooncards')}}</h2>
		<div class="flexy-cards-wrapper">
			<div v-for="(c, i) in highnooncards" v-bind:key="c.name ? (c.name+c.number) : i" class="flexy-cards">
				<Card :card="c" :class="'high-noon last-event'" @pointerenter.native="''" @pointerleave.native="''"/>
				<div style="margin-left:6pt;">
					<p>{{$t(`cards.${c.name}.desc`)}}</p>
				</div>
			</div>
		</div>
		<h2 id="foccards">{{$t('help.foccards')}}</h2>
		<div class="flexy-cards-wrapper">
			<div v-for="(c, i) in foccards" v-bind:key="c.name ? (c.name+c.number) : i" class="flexy-cards">
				<Card :card="c" :class="'fistful-of-cards last-event'" @pointerenter.native="''" @pointerleave.native="''"/>
				<div style="margin-left:6pt;">
					<p>{{$t(`cards.${c.name}.desc`)}}</p>
				</div>
			</div>
		</div>
		<h2 id="goldrushcards">{{$t('help.goldrushcards')}}</h2>
		<div class="flexy-cards-wrapper">
			<div v-for="(c, i) in goldrushcards" v-bind:key="c.name ? (c.name+c.number) : i" class="flexy-cards">
				<Card :card="c" class="gold-rush" @pointerenter.native="''" @pointerleave.native="''"/>
				<div style="margin-left:6pt;">
					<p>{{$t(`cards.${c.name}.desc`)}}</p>
				</div>
			</div>
		</div>
		<h2 id="valleyofshadowscards">{{$t('help.valleyofshadowscards')}}</h2>
		<div class="flexy-cards-wrapper">
			<div v-for="(c, i) in valleyofshadowscards" v-bind:key="c.name ? (c.name+c.number) : i" class="flexy-cards">
				<Card :card="c" class="valley-of-shadows" @pointerenter.native="''" @pointerleave.native="''"/>
				<div style="margin-left:6pt;">
					<p>{{$t(`cards.${c.name}.desc`)}}</p>
				</div>
			</div>
		</div>
		<h2 id="wildwestshowcards">{{$t('help.wildwestshowcards')}}</h2>
		<div class="flexy-cards-wrapper">
			<div v-for="(c, i) in wildwestshowcards" v-bind:key="c.name ? (c.name+c.number) : i" class="flexy-cards">
				<Card :card="c" class="wild-west-show" @pointerenter.native="''" @pointerleave.native="''"/>
				<div style="margin-left:6pt;">
					<p>{{$t(`cards.${c.name}.desc`)}}</p>
				</div>
			</div>
		</div>
		<h2 id="trainrobberycards">{{$t('help.trainrobberycards')}}</h2>
		<div class="flexy-cards-wrapper">
			<div v-for="(c, i) in trainrobberycards" v-bind:key="c.name ? (c.name+c.number) : i" class="flexy-cards">
				<Card :card="c" class="train-robbery" @pointerenter.native="''" @pointerleave.native="''"/>
				<div style="margin-left:6pt;">
					<p>{{$t(`cards.${c.name}.desc`)}}</p>
				</div>
			</div>
			<div v-for="(c, i) in trainrobberystations" v-bind:key="c.name ? (c.name+c.number) : i" class="flexy-cards">
				<StationCard :card="c" class="train-robbery" @pointerenter.native="''" @pointerleave.native="''" :price="c.price"/>
				<div style="margin-left:6pt;">
					<p>{{$t(`cards.${c.name}.desc`)}}</p>
				</div>
			</div>
		</div>
	</div>
</template>
<script>
import Card from '@/components/Card.vue'
import StationCard from './StationCard.vue'

export default {
	name: 'Help',
	components: {
		Card,
		StationCard,
	},
	props: {
		inGame: Boolean
	},
	data:()=>({
		cardBack: {
			name: 'PewPew!',
			icon: '💥',
		},
		cards: [],
		characters: [],
		highnooncards: [],
		foccards: [],
		goldrushcards: [],
		valleyofshadowscards: [],
		wildwestshowcards: [],
		trainrobberycards: [],
		trainrobberystations: [],
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
		highnooncards_info(cardsJson) {
			this.highnooncards = JSON.parse(cardsJson).map(x=>({
				...x,
			}))
		},
		foccards_info(cardsJson) {
			this.foccards = JSON.parse(cardsJson).map(x=>({
				...x,
			}))
		},
		goldrushcards_info(cardsJson) {
			this.goldrushcards = JSON.parse(cardsJson).map(x=>({
				...x,
			}))
		},
		valleyofshadows_info(cardsJson) {
			this.valleyofshadowscards = JSON.parse(cardsJson).map(x=>({
				...x,
			}))
		},
		wwscards_info(cardsJson) {
			this.wildwestshowcards = JSON.parse(cardsJson).map(x=>({
				...x,
			}))
		},
		trainrobberycards_info(cardsJson) {
			this.trainrobberycards = JSON.parse(cardsJson).cards.map(x=>({
				...x,
			}))
			this.trainrobberystations = JSON.parse(cardsJson).stations.map(x=>({
				...x,
			}))
		},
	},
	mounted() {
		this.$socket.emit('get_cards')
		this.$socket.emit('get_characters')
		this.$socket.emit('get_highnooncards')
		this.$socket.emit('get_foccards')
		this.$socket.emit('get_goldrushcards')
		this.$socket.emit('get_valleyofshadowscards')
		this.$socket.emit('get_wildwestshowcards')
		this.$socket.emit('get_trainrobberycards')
		document.getElementById('help').scrollIntoView();
	}
}
</script>
<style scoped>
.flexy-cards-wrapper {
	display: flex;
	flex-flow: wrap;
}
.flexy-cards {
	flex: 30%;
	display:flex;
}
@media only screen and (max-width:500px) {
	.flexy-cards {
		flex: 100%;
	}
}
@media only screen and (max-width:800px) {
	.flexy-cards {
		flex: 50%;
	}
}
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