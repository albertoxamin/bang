<template>
	<div class="lobby">
		<div style="flex-grow: 4;">
			<div style="position:relative;">
				<h2 v-if="!started">{{$t('room')}}{{ lobbyName }}</h2>
				<input style="position:absolute;top:0;right:0;max-height:100pt" v-if="!started" type="button" @click="leaveRoom" :value="$t('leave_room')"/>
			</div>
			<h3>{{$t('room_players', {username:username})}}</h3>
			<div v-if="debug" style="position: absolute;top: 6pt;right: 6pt;">
				<p style="padding:0 10px;background:red;color:white;border-radius:12pt;">DEBUG ON</p>
			</div>
			<div v-if="!started">
				<PrettyCheck v-if="isRoomOwner" class="p-switch p-fill" v-model="privateRoom" style="margin-top:5px; margin-bottom:3px;">{{$t("private_room")}}</PrettyCheck>
				<label v-if="password !== ''">{{$t('password')}}<b class="selectable" style="font-size:larger;">{{ password }}</b></label>
				<input type="button" style="margin-left: 10pt;" v-clipboard:copy="inviteLink" :value="$t('copy')"/>
			</div>
			
			<!-- <div class="players-table"> -->
				<!-- <div style="position: relative;width:260pt;height:400pt;"> -->
			<transition-group name="list" tag="div" class="players-table">
				<Card v-if="startGameCard" key="_start_game_" :donotlocalize="true" :card="startGameCard" @click.native="startGame"/>
				<div v-for="p in playersTable" v-bind:key="p.card.name" style="position:relative;">
					<transition-group v-if="p.max_lives && !p.is_ghost" name="list" tag="div" class="tiny-health">
						<span v-for="(n, i) in p.lives" v-bind:key="i" :alt="i">❤️</span>
						<span v-for="(n, i) in (p.max_lives-p.lives)" v-bind:key="`${i}-sk`" :alt="i">💀</span>
					</transition-group>
					<div v-else-if="p.is_ghost" class="tiny-health">
						<span>👻</span>
					</div>
					<Card :card="p.card" @click.native="drawFromPlayer(p.name)"  :donotlocalize="true" :class="{is_my_turn:p.is_my_turn}"/>
					<Card v-if="p.character" :card="p.character" class="character tiny-character" @click.native="selectedInfo = [p.character]"/>
					<Card v-if="p.character && p.character.name !== p.real_character.name" style="transform:scale(0.5) translate(-90px, -50px);" :card="p.character" class="character tiny-character" @click.native="selectedInfo = [p.character]"/>
					<tiny-hand :ncards="p.ncards" @click.native="drawFromPlayer(p.name)" :ismyturn="p.pending_action === 2"/>
					<span style="position:absolute;top:10pt;" class="center-stuff">{{getActionEmoji(p)}}</span>
					<div class="tiny-equipment">
						<Card v-for="(card, i) in p.equipment" v-bind:key="card.name+card.number"
									:card="card" @click.native="selectedInfo = p.equipment"
									:style="`margin-top: ${i<1?10:-(Math.min((p.equipment.length+1)*12,80))}pt`"/>
					</div>
					<div v-if="p.is_bot" style="position:absolute;bottom:57%;" class="center-stuff">
						<span>🤖</span>
					</div>
				</div>
			</transition-group>
					<!-- :style="p.style"/> -->
				<!-- </div> -->
			<!-- </div> -->
			<div v-if="!started">
				<p v-if="players.length < 3" class="center-stuff" style="min-height: 19px;">{{$t('minimum_players')}}</p>
				<p v-else style="min-height: 19px;"> </p>
				<h3>{{$t("expansions")}}</h3>
				<div v-for="ex in expansionsStatus" v-bind:key="ex.id">
					<PrettyCheck @click.native="toggleExpansions(ex.id)" :disabled="!isRoomOwner" :checked="ex.enabled" class="p-switch p-fill" style="margin-top:5px; margin-bottom:3px;">{{ex.name}}</PrettyCheck>
					<br>
				</div>
				<h3>{{$t('mods')}}</h3>
				<PrettyCheck @click.native="toggleCompetitive" :disabled="!isRoomOwner" v-model="is_competitive" class="p-switch p-fill" style="margin-top:5px; margin-bottom:3px;">{{$t('mod_comp')}}</PrettyCheck>
				<h3>{{$t('bots')}}</h3>
				<input type="button" :value="$t('add_bot')" :disabled="!isRoomOwner || players.length > 7" @click="()=>{this.$socket.emit('chat_message', '/addbot')}"/>
				<input type="button" style="margin-left: 10pt;" :value="$t('remove_bot')" :disabled="!isRoomOwner || !isThereAnyBot" @click="()=>{this.$socket.emit('chat_message', '/removebot')}"/>
				<!-- <br> -->
				<!-- <PrettyCheck @click.native="toggleReplaceWithBot" :disabled="!isRoomOwner" v-model="disconnect_bot" class="p-switch p-fill" style="margin-top:5px; margin-bottom:3px;">{{$t('disconnect_bot')}}</PrettyCheck> -->
			</div>
			<div v-if="started">
				<deck :endTurnAction="()=>{wantsToEndTurn = true}"/>
				<player :isEndingTurn="wantsToEndTurn" :cancelEndingTurn="()=>{wantsToEndTurn = false}" :chooseCardFromPlayer="choose" :cancelChooseCardFromPlayer="()=>{hasToChoose=false}"/>
			</div>
		</div>
		<chat :username="username"/>
		<Chooser v-if="selectedInfo" :text="$t('details')" :cards="selectedInfo" :cancelText="$t('ok')" :cancel="()=>{selectedInfo = null}" :select="()=>{selectedInfo = null}"/>
		<transition name="bounce">
			<Chooser v-show="hasToChoose" :text="`${$t('choose_card')}${target_p?$t('choose_card_from') + target_p:''}`" :cards="chooseCards" :select="chooseCard"/>
			<full-screen-input v-if="!started && hasToSetUsername" :defaultValue="storedUsername" :text="$t('choose_username')" :val="username" :cancel="setUsername" :cancelText="$t('ok')"/>
		</transition>
	</div>
</template>

<script>
import Vue from 'vue'
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
		hasToChoose: false,
		target_p: '', 
		chooseCards: [],
		wantsToEndTurn: false,
		selectedInfo: null,
		privateRoom: false,
		password: '',
		togglable_expansions: [],
		expansions: [],
		hasToSetUsername: false,
		is_competitive: false,
		disconnect_bot: false,
		debug: false,
	}),
	sockets: {
		room(data) {
			this.lobbyName = data.name
			if (!data.started) {
				document.title = this.lobbyName +' | PewPew!'
			}	else if (data.started && !this.started) {
				document.title = 'PewPew!'
			}
			this.started = data.started
			this.password = data.password
			this.privateRoom = data.password !== ''
			this.is_competitive = data.is_competitive
			this.disconnect_bot = data.disconnect_bot
			this.togglable_expansions = data.available_expansions
			this.expansions = data.expansions
			this.debug = data.debug
			this.players = data.players.map(x => {
				return {
					name: x.name,
					ready: x.ready,
					is_bot: x.is_bot,
					ncards: 0,
				}
			})
		},
		start() {
			this.started = true;
		},
		players_update(data) {
			if (Vue.config.devtools)
				console.log(data)
			this.players = data
		},
		me(username) {
			if (username.error) { 
				alert(username.error)
				this.$router.push('/')
			}
			this.username = username
			// this.$socket.emit('get_cards', 'dodge_city')
		},
		// cards_info(data) {
		// 	data = JSON.parse(data)
		// 	let bigthing = {}
		// 	let bigthing_eng = {}
		// 	data.forEach(x => {
		// 		bigthing[x.name] = {
		// 			name:x.name,
		// 			desc:x.desc,
		// 		}
		// 		bigthing_eng[x.name] = {
		// 			name:x.name,
		// 			desc:x.desc_eng,
		// 		}
		// 	})
		// 	console.log(JSON.stringify(bigthing))
		// 	console.log(JSON.stringify(bigthing_eng))
		// },
		change_username() {
			this.hasToSetUsername = true
		},
	},
	computed: {
		inviteLink() {
			return `${window.location.origin}/game?code=${encodeURIComponent(this.lobbyName)}${this.password?`&pwd=${this.password}`:''}`
		},
		isThereAnyBot() {
			return this.players.filter(x => x.is_bot).length > 0;
		},
		expansionsStatus() { 
			return this.togglable_expansions.map(x=>{
				return {
					id: x,
					name: x.replace(/(^|_)([a-z])/g, function($0,$1,$2) {return ' ' + $2.toUpperCase()}),
					enabled: this.expansions.indexOf(x) !== -1
				}
			})
		},
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
			if (Vue.config.devtools)
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
		is_toggled_expansion(ex) {
			if (Vue.config.devtools)
				console.log(ex+' '+ this.expansions+ (this.expansions.indexOf(ex) !== -1))
			return this.expansions.indexOf(ex) !== -1
		},
		leaveRoom() {
			window.location.replace(window.location.origin)
			document.title = 'PewPew!'
		},
		toggleExpansions(name) {
			if (!this.isRoomOwner) return;
			this.$socket.emit('toggle_expansion', name)
		},
		toggleCompetitive() {
			if (!this.isRoomOwner) return;
			this.$socket.emit('toggle_comp')
		},
		toggleReplaceWithBot() {
			if (!this.isRoomOwner) return;
			this.$socket.emit('toggle_replace_with_bot')
		},
		getActionEmoji(p) {
			if (p.is_my_turn === undefined || p.pending_action === undefined) return '';
			if (p.pending_action != 4) {
				return ['↙️', '⏬', '▶️', '↩️', '4', '🔽'][p.pending_action]
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
			if (Vue.config.devtools)
				console.log('choose from' + player_name)
			this.target_p = player_name
			let pl = this.players.filter(x=>x.name === player_name)[0]
			if (Vue.config.devtools)
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
			if (Vue.config.devtools)
				console.log(card + ' ' + this.chooseCards.indexOf(card))
			this.chooseCards = []
			this.hasToChoose = false
			this.target_p = ''
		},
		drawFromPlayer(name) {
			if (Vue.config.devtools)
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
		privateRoom(old, _new) {
			if (this.isRoomOwner && old !== _new)
				this.$socket.emit('private')
		}
	},
	mounted() {
		if (Vue.config.devtools)
			console.log('mounted lobby')
		if (!this.$route.query.code)
			return this.$router.push('/')
		this.$socket.emit('get_me', {name:this.$route.query.code, password:this.$route.query.pwd, username: localStorage.getItem('username')})
	},
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style >
.is_my_turn {
	box-shadow: 0 0 0 3pt rgb(138, 12, 12), 0 0 0 6pt var(--bg-color), 0 0 5pt 6pt #aaa !important;
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
		transform: scale(1.02);
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
	top: 10pt;
}
.tiny-health {
	display: flex;
	justify-content: space-evenly;
	transform: scale(0.8);
	margin-bottom: -4pt;
}
.tiny-equipment .card:hover {
	transform: translateY(10px) scale(1.1);
	z-index: 1;
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
		min-width: 25vw;
		max-width: 25vw;
	}
}
</style>
