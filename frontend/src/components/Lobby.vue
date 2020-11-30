<template>
	<div class="lobby">
		<div style="flex-grow: 4;">
			<h2 v-if="!started">{{$t('room')}}{{ lobbyName }}</h2>
			<h3>{{$t('room_players', {username:username})}}</h3>
			<div v-if="!started">
				<PrettyCheck v-if="isRoomOwner" class="p-switch p-fill" v-model="privateRoom" style="margin-top:5px; margin-bottom:3px;">{{$t("private_room")}}</PrettyCheck>
				<label v-if="password !== ''">{{$t('password')}}<b class="selectable" style="font-size:larger;">{{ password }}</b></label>
			</div>
			
			<div class="players-table">
				<Card v-if="startGameCard" :card="startGameCard" @click.native="startGame"/>
				<!-- <div style="position: relative;width:260pt;height:400pt;"> -->
				<div v-for="p in playersTable" v-bind:key="p.card.name" style="position:relative;">
					<transition-group v-if="p.max_lives" name="list" tag="div" class="tiny-health">
						<span v-for="(n, i) in p.lives" v-bind:key="n" :alt="i">❤️</span>
						<span v-for="(n, i) in (p.max_lives-p.lives)" v-bind:key="n" :alt="i">💀</span>
					</transition-group>
					<Card :card="p.card" :class="{is_my_turn:p.is_my_turn}"/>
					<Card v-if="p.character" :card="p.character" class="character tiny-character" @click.native="selectedInfo = [p.character]"/>
					<tiny-hand :ncards="p.ncards" @click.native="drawFromPlayer(p.name)"/>
					<span style="position:absolute;top:10pt;" class="center-stuff">{{getActionEmoji(p)}}</span>
					<div class="tiny-equipment">
						<Card v-for="card in p.equipment" v-bind:key="card.name+card.number" :card="card" @click.native="selectedInfo = p.equipment"/>
					</div>
				</div>
					<!-- :style="p.style"/> -->
				<!-- </div> -->
			</div>
			<div v-if="!started">
				<h3>{{$t("expansions")}}</h3>
				<PrettyCheck @click.native="toggleExpansions('dodge_city')" :disabled="!isRoomOwner" v-model="useDodgeCity" class="p-switch p-fill" style="margin-top:5px; margin-bottom:3px;">Dodge City</PrettyCheck>
			</div>
			<div v-if="started">
				<deck :endTurnAction="()=>{wantsToEndTurn = true}"/>
				<player :isEndingTurn="wantsToEndTurn" :cancelEndingTurn="()=>{wantsToEndTurn = false}" :chooseCardFromPlayer="choose"/>
			</div>
		</div>
		<chat/>
		<Chooser v-if="selectedInfo" :text="$t('details')" :cards="selectedInfo" :cancelText="$t('ok')" :cancel="()=>{selectedInfo = null}" :select="()=>{selectedInfo = null}"/>
		<transition name="bounce">
			<Chooser v-if="hasToChoose" :text="`${$t('choose_card')}${target_p?$t('choose_card_from') + target_p:''}`" :cards="chooseCards" :select="chooseCard"/>
			<full-screen-input v-if="!started && hasToSetUsername" :defaultValue="storedUsername" :text="$t('choose_username')" :val="username" :cancel="setUsername" :cancelText="$t('ok')"/>
		</transition>
	</div>
</template>

<script>
import PrettyCheck from 'pretty-checkbox-vue/check'
import Card from '@/components/Card.vue'
import Chooser from './Chooser.vue'
import Chat from './Chat.vue'
import Player from './Player.vue'
import Deck from './Deck.vue'
import TinyHand from './TinyHand.vue'
import FullScreenInput from './FullScreenInput.vue'

export default {
	name: 'Lobby',
	components: {
		Card,
		Chooser,
		Chat,
		Player,
		Deck,
		TinyHand,
		PrettyCheck,
		FullScreenInput
	},
	data: () => ({
		username: '',
		lobbyName: '',
		started: false,
		players: [],
		messages: [],
		distances: {},
		self: {},
		hasToChoose: false,
		target_p: '', 
		chooseCards: [],
		wantsToEndTurn: false,
		selectedInfo: null,
		privateRoom: false,
		password: '',
		useDodgeCity: false,
		hasToSetUsername: false,
	}),
	sockets: {
		room(data) {
			this.lobbyName = data.name
			this.started = data.started
			this.password = data.password
			this.useDodgeCity = data.expansions.indexOf('dodge_city') !== -1
			this.players = data.players.map(x => {
				return {
					name: x.name,
					ready: x.ready,
					ncards: 0,
				}
			})
		},
		start() {
			this.started = true;
		},
		players_update(data) {
			console.log(data)
			this.players = data
		},
		me(username) {
			if (username.error) { 
				alert(username.error)
				this.$router.push('/')
			}
			this.username = username
		},
		change_username() {
			this.hasToSetUsername = true
		}
	},
	computed: {
		storedUsername() {
			if (localStorage.getItem('username'))
				return localStorage.getItem('username')
			return ''
		},
		isRoomOwner() {
			return this.players.length > 0 && this.players[0].name == this.username
		},
		startGameCard() {
			if (!this.started && this.players.length > 2 && this.isRoomOwner) {
				return {
					name: this.$t('start_game'),
					icon: '▶️',
					is_equipment: true,
					number: `${this.players.length}🤠`
				}
			}
			return null;
		},
		playersTable() {
			console.log('update players')
			return this.players.map((x,i) => {
				let offsetAngle = 360.0 / this.players.length
				let rotateAngle = (i) * offsetAngle
				let size = 130
				return {
					card: this.getPlayerCard(x),
					style: `position:absolute;transform: rotate(${rotateAngle}deg) translate(0, -${size}pt) rotate(-${rotateAngle}deg) translate(${size}pt,${size}pt)`,
					...x
				}
			})
		}
	},
	methods: {
		toggleExpansions(name) {
			if (!this.isRoomOwner) return;
			this.$socket.emit('toggle_expansion', name)
		},
		getActionEmoji(p) {
			if (p.is_my_turn === undefined || p.pending_action === undefined) return '';
			if (p.pending_action != 4) {
				return '▶️'
			} else if (p.is_my_turn) {
				return '⏸'
			} else {
				return ''
			}
		},
		getPlayerCard(player) {
			let icon = ''
			if (!this.started) icon = '🤠'
			else icon = player.ready !== undefined ? ((player.ready)?'👍': '🤔') : (player.is_sheriff ? '⭐' : player.icon)
			return {
				name: player.name,
				number: ((this.username == player.name) ? this.$t('you') : (this.players[0].name == player.name) ? this.$t('owner') :'') + (player.dist ? `${player.dist}⛰` : ''),
				icon: icon,
				is_character: true,
			}
		},
		startGame() {
			this.started = true;
			this.$socket.emit('start_game')
		},
		choose(player_name) {
			console.log('choose from' + player_name)
			this.target_p = player_name
			let pl = this.players.filter(x=>x.name === player_name)[0]
			console.log(pl)
			let arr = []
			for (let i=0; i<pl.ncards; i++)
				arr.push({
					name: 'PewPew!',
					icon: '💥',
					is_back: true,
				})
			pl.equipment.forEach(x=>arr.push(x))
			this.chooseCards = arr
			this.hasToChoose = true
		},
		chooseCard(card) {
			this.$socket.emit('choose', this.chooseCards.indexOf(card))
			console.log(card + ' ' + this.chooseCards.indexOf(card))
			this.chooseCards = []
			this.hasToChoose = false
			this.target_p = ''
		},
		drawFromPlayer(name) {
			console.log(name)
			this.$socket.emit('draw', name)
		},
		setUsername(name){
			if (name.trim().length > 0){
				localStorage.setItem('username', name)
				this.hasToSetUsername = false
				this.$socket.emit('set_username', name)
			}
		},
	},
	watch: {
		privateRoom() {
			this.$socket.emit('private')
		}
	},
	mounted() {
		console.log('mounted lobby')
		this.$socket.emit('get_me', {name:this.$route.query.code, password:this.$route.query.pwd})
	},
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style >
.is_my_turn {
	box-shadow: 0 0 0 3pt rgb(138, 12, 12), 0 0 0 6pt white, 0 0 5pt 6pt #aaa !important;
	animation-name: turn-animation;
  animation-duration: 2s;
  animation-iteration-count: infinite;
}
@media (prefers-color-scheme: dark) {
	.is_my_turn {
		box-shadow: 0 0 0 3pt rgb(138, 12, 12), 0 0 0 6pt #181a1b, 0 0 5pt 6pt #aaa !important;
	}
}
@keyframes turn-animation {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}
.tiny-equipment {
	position: absolute;
	display: flex;
	flex-direction: column;
	right: -35pt;
	transform: scale(0.45);
	transform-origin: 50% 0%;
	top: 0;
}
.tiny-health {
	display: flex;
	justify-content: space-evenly;
	transform: scale(0.8);
	margin-bottom: -4pt;
}
.tiny-equipment .card:nth-child(n+2) {
	margin-top: -60pt;
}
.tiny-character {
	position: absolute;
	transform: scale(0.5) translate(-80px, -40px);
	top: 0;
}
.players-table {
	display: flex;
	flex-wrap: wrap;
	justify-content: space-evenly;
	margin-bottom: 12pt;
}
.lobby {
	display: flex;
	flex-direction: column;
}
@media only screen and (min-width:1000px) {
	.lobby {
		flex-direction: row;
	}
	.chat {
		max-width: 350pt;
	}
}
</style>
