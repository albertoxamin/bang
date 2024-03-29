<template>
	<div id="app" class="dark-mode">
		<div v-if="!isInLobby" id="logo" class="center-stuff" style="margin-bottom:10pt">
			<h1 style="margin-bottom:0pt;">PewPew!</h1>
			<p id="tip" style="margin-top: auto; color:darkorange">{{$t(randomTip)}}</p>
			<p style="transform: scale(0.7);margin-top: auto;">v-{{version}}</p>
			<div style="display:flex;justify-content: space-evenly;;min-height:140pt;">
				<span style="font-size:48pt;transform:scaleX(-1) translateY(25%);">🔫️</span>
				<TinyHand :ncards="5" :ismyturn="true" style="position:none;transform:scale(1);bottom:none;width:120pt;"/>
				<span style="font-size:48pt;transform:translateY(25%);">🔫️</span>
			</div>
			<i style="font-size: x-small;">{{$t("trademark")}}</i>
		</div>
		<div>
			<div v-if="!didSetUsername">
				<p id="choose_username">{{$t("choose_username")}}</p>
				<form @submit="setUsername" class="form" style="display:flex">
					<input id="_username" v-model="username" />
					<input type="submit" class="btn" :value="$t('submit')"/>
					<input type="button" class="btn" @click="discordLogin" value="Login with Discord"/>
				</form>
				<p v-if="onlinePlayers > 0">{{$t("online_players")}}{{onlinePlayers}}</p>
			</div>
			<div v-else>
				<div v-if="!isInLobby" >
					<p>{{$t("online_players")}}{{onlinePlayers}}</p>
					<Card :card="getSelfCard" :donotlocalize="true" style="position:absolute; top:10pt; left: 10pt;"/>
					<h2>{{$t("create_lobby")}}</h2>
					<form @submit="createLobby" class="form" style="display:flex">
						<p>{{$t("lobby_name")}}</p>
						<input id="lobbyname" v-model="lobbyName"/>
						<input type="submit" class="btn" :value="$t('submit')"/>
					</form>
					<h2>{{$t("available_lobbies")}}</h2>
					<div style="display: flex">
						<Card v-for="lobby in openLobbies" v-bind:key="lobby.name" :card="getLobbyCard(lobby)" @click.native="joinLobby(lobby)"/>
						<p v-if="noLobbyAvailable">{{$t("no_lobby_available")}}</p>
					</div>
					<h2>{{$t("spectate_lobbies")}}</h2>
					<div style="display: flex">
						<Card v-for="lobby in spectateLobbies" v-bind:key="lobby.name" :card="getSpectateLobbyCard(lobby)" @click.native="joinLobby(lobby)"/>
						<p v-if="noSpectateLobbyAvailable">{{$t("no_lobby_available")}}</p>
					</div>
				</div>
			</div>
		</div>
		<label for="_username" style="opacity:0">Username</label>
		<label for="lobbyname" style="opacity:0">Lobby Name</label>
		<div>
			Still new to the game? Read the rules <a href="./help">here</a> or press the question mark in the bottom right corner anytime during your matches.
		</div>
	</div>
</template>

<script>
// import Vue from 'vue'
import Card from '@/components/Card.vue'
import TinyHand from '@/components/TinyHand.vue'
// import Lobby from './components/Lobby.vue'
import { datadogRum } from '@datadog/browser-rum';
import { emojiMap } from '@/utils/emoji-map.js'

export default {
	name: 'App',
	components: {
		Card,
		TinyHand,
		// Lobby,
	},
	data: () => ({
		isConnected: false,
		didSetUsername: false,
		username: '',
		openLobbies: [],
		spectateLobbies: [],
		lobbyName: '',
		isInLobby: false,
		onlinePlayers: 0,
		randomTip: '',
		discordPic: '',
	}),
	computed: {
		redirectUrl() {
			return 'https://discordapp.com/api/oauth2/authorize?client_id=1059452581027532880&response_type=code&scope=identify&redirect_uri=' + window.location.origin;
		},
		noLobbyAvailable() {
			return this.openLobbies && this.openLobbies.length == 0
		},
		noSpectateLobbyAvailable() {
			return this.spectateLobbies && this.spectateLobbies.length == 0
		},
		getSelfCard() {
			return {
				name: this.username,
				number: this.$t('you'),
				icon: '🤠',
				is_character: true,
				avatar: this.discordPic,
				is_player: true
			}
		},
		version() {
			return document.getElementsByTagName("html")[0].getAttribute("data-build-timestamp-utc").replace(/[-|:|T]/g,'.').substring(0,16)
		}
	},
	sockets: {
		lobbies(data) {
			this.openLobbies = data;
		},
		spectate_lobbies(data) {
			this.spectateLobbies = data;
		},
		room(data) {
			this.isInLobby = true;
			this.$router.push({path:'game', query: { code: data.name }})
		},
		players(num) {
			this.onlinePlayers = num;
			// console.log('PLAYERS:' + num)
		},
		discord_auth_succ(data) {
			if (data.access_token) {
				localStorage.setItem('discord_token', data.access_token)
				this.login()
			}
		},
	},
	methods: {
		setUsername(e){
			if (this.username.trim().length > 0){
				this.didSetUsername = true
				localStorage.setItem('username', this.username)
				this.$socket.emit('set_username', {name:this.username})
				datadogRum.setUser({name: localStorage.getItem('username')})
				e.preventDefault();
			}
		},
		discordLogin() {
			window.location = this.redirectUrl;
		},
		getLobbyCard(lobby) {
			return {
				name: lobby.name,
				icon: "💥",
				number: `${lobby.players-lobby.bots}🤠${lobby.bots > 0 ? ' '+lobby.bots+'🤖':''} ${lobby.locked?'🔐':''}`,
				alt_text: lobby.expansions?.map(e => emojiMap[e]).join(''),
				is_equipment: true,
			}
		},
		getSpectateLobbyCard(lobby) {
			return {
				name: lobby.name,
				icon: "👁️",
				number: `${lobby.players-lobby.bots}🤠${lobby.bots > 0 ? ' '+lobby.bots+'🤖':''} ${lobby.locked?'🔐':''}`,
				alt_text: lobby.expansions?.map(e => emojiMap[e]).join(''),
				usable_next_turn: true,
			}
		},
		createLobby(e) {
			if (this.lobbyName.trim().length > 0) {
				this.$socket.emit('create_room', this.lobbyName)
			}
			e.preventDefault();
		},
		joinLobby(lobby) {
			let password = lobby.locked ? prompt(this.$t("room_password_prompt"), "") : '';
			this.$socket.emit('join_room', {name:lobby.name,password:password})
		},
		init() {
			location.reload();
		},
		login() {
			fetch('https://discordapp.com/api/users/@me', {
				headers: {
					'Authorization': 'Bearer ' + localStorage.getItem('discord_token')
				}
			})
			.then((res) => {
				if (res.status !== 200) throw new Error(res.status)
				return res
			})
			.then(response => response.json())
			.then(data => {
				console.log(data)
				this.username = data.username
				this.didSetUsername = true
				this.discordPic = `https://cdn.discordapp.com/avatars/${data.id}/${data.avatar}.png`
				localStorage.setItem('username', this.username)
				this.$socket.emit('set_username', {name: this.username, discord_token: localStorage.getItem('discord_token')})
			}).catch(err => {
				console.error(err)
				localStorage.removeItem('discord_token')
				this.$router.replace({query: []})
			})
		}
	},
	mounted() {
		if (localStorage.getItem('discord_token')) {
			this.login()
		} else if (this.$route.query.code) {
			this.$socket.emit('discord_auth', {code:this.$route.query.code, origin:window.location.origin})
			this.$router.replace({query: []})
		}
		this.randomTip = `tip_${1+Math.floor(Math.random() * 10)}`
		if (localStorage.getItem('username'))
			this.username = localStorage.getItem('username')
		else {
			let names = ['player', 'cowboy', 'madman', 'horseshoe', 'mustang', '🤠️', 'dog lover', 'random', 'cows', 'seagull', 'pewneer', 'pioneer', 'django', 'tarantined', 'horse', 'cinnamom', 'toast', 'notPewDiePie', 'username', 'caveman', 'cat', 'gold', 'chicken', 'nugget', 'bullet', 'fire', 'scott', 'emiliano', 'apple', 'pear', 'pencil', 'youtuber', 'hi mom', 'discord guy', '🥰️', 'somebody', 'AAAAA', 'BBBB', 'pain', 'help?', 'gg', 'gigi', 'lmao', 'yikes', 'you?', 'kid', 'cowgirl', 'bite', 'hungry', 'joe', 'limbo', 'leeeroy', 'jenkins', 'batman', 'spiderman', 'luke skywalker', 'nemo', 'zemo', 'ironman', 'butterman', 'postman', 'father', 'son', 'sven', 'mike', 'straw', 'saaay', 'whaaaat', 'rick', 'morty', 'wubbalubbadubdub']
			this.username = names[Math.floor(Math.random() * names.length)]
		}
		this.$socket.emit('get_online_players')
	},
}
</script>

<style>
@media only screen and (max-width:1000px) {
	.form {
		flex-direction: column;
	}
	.form > input, .form>p{
		font-size: 20pt;
	}
	#choose_username{
		font-size: 20pt;
	}
}
#tip {
	animation-name: zoom;
	animation-duration: 2s;
	animation-iteration-count: infinite;
}
@keyframes zoom {
	0% {
		transform: scale(1);
	}
	50% {
		transform: scale(0.95);
	}
	100% {
		transform: scale(1);
	}
}
</style>
