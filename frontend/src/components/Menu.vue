<template>
	<div id="app" class="dark-mode">
		<div v-if="!isInLobby" id="logo" class="center-stuff" style="margin-bottom:10pt;">
			<h1 style="margin-bottom:0pt;">PewPew!</h1>
			<i style="font-size: x-small;">{{$t("trademark")}}</i>
		</div>
		<div>
			<div v-if="!didSetUsername">
				<p>{{$t("choose_username")}}</p>
				<form @submit="setUsername">
					<input v-model="username" />
					<input type="submit" :value="$t('submit')"/>
				</form>
				<p>{{$t("online_players")}}{{onlinePlayers}}</p>
			</div>
			<div v-else>
				<div v-if="!isInLobby" >
					<p>{{$t("online_players")}}{{onlinePlayers}}</p>
					<Card :card="getSelfCard" style="position:absolute; top:10pt; left: 10pt;"/>
					<h2>{{$t("available_lobbies")}}</h2>
					<div style="display: flex">
						<Card v-for="lobby in openLobbies" v-bind:key="lobby.name" :card="getLobbyCard(lobby)" @click.native="joinLobby(lobby)"/>
						<p v-if="noLobbyAvailable">{{$t("no_lobby_available")}}</p>
					</div>
					<form @submit="createLobby">
						<h2>{{$t("create_lobby")}}</h2>
						<p>{{$t("lobby_name")}}</p>
						<input v-model="lobbyName"/>
						<input type="submit" :value="$t('submit')"/>
					</form>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
// import Vue from 'vue'
import Card from '@/components/Card.vue'
// import Lobby from './components/Lobby.vue'

export default {
	name: 'App',
	components: {
		Card,
		// Lobby,
	},
	data: () => ({
		isConnected: false,
		didSetUsername: false,
		username: '',
		openLobbies: [],
		lobbyName: '',
		isInLobby: false,
		onlinePlayers: 0,
	}),
	computed: {
		noLobbyAvailable() {
			return this.openLobbies && this.openLobbies.length == 0
		},
		getSelfCard() {
			return {
				name: this.username,
				number: this.$t('you'),
				icon: '🤠',
				is_character: true,
			}
		},
	},
	sockets: {
		lobbies(data) {
			this.openLobbies = data;
		},
		room(data) {
			this.isInLobby = true;
			this.$router.push({path:'game', query: { code: data.name }})
		},
		players(num) {
			this.onlinePlayers = num;
		}
	},
	methods: {
		setUsername(e){
			if (this.username.trim().length > 0){
				this.didSetUsername = true
				localStorage.setItem('username', this.username)
				this.$socket.emit('set_username', this.username)
				e.preventDefault();
			}
		},
		getLobbyCard(lobby) {
			return {
				name: lobby.name,
				icon: "💥",
				number: `${lobby.players}🤠 ${lobby.locked?'🔐':''}`,
				is_equipment: true,
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
	},
	mounted() {
		if (localStorage.getItem('username'))
			this.username = localStorage.getItem('username')
	},
}
</script>

<style>
</style>