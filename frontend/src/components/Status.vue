<template>
	<div>
		<h1 id="status">PewPew! Server Status</h1>
		<h2>Rooms {{rooms.length}}</h2>
		<button @click="refresh">reload</button>
		<ul>
			<li v-for="r in rooms" :key="r">
				<p style="margin:0"><b>name:</b> {{r.name}}</p>
				<p style="margin:0"><b>hidden:</b> {{r.hidden}}</p>
				<button @click="hide(r.name)">toggle hide</button>
				<p style="margin:0"><b>password:</b> {{r.password}}</p>
				<p style="margin:0"><b>mods:</b> {{r.expansions}}</p>
				<p style="margin:0"><b>started:</b> {{r.started}}</p>
				<p style="margin:0"><b>turn:</b> {{r.current_turn}}</p>
				<p style="margin:0"><b>incremental_turn:</b> {{r.incremental_turn}}</p>
				<p style="margin:0"><b>debug:</b> {{r.debug}}</p>
				<p style="margin:0"><b>spectators:</b> {{r.spectators}}</p>
				<p style="margin:0"><b>players:</b></p>
				<ul style="margin:0">
					<li v-for="p in r.players" :key="p">
						<p style="margin:0"><b>name:</b> {{p.name}}</p>
						<p style="margin:0"><b>is_bot:</b> {{p.bot}}</p>
						<p style="margin:0"><b>health:</b> {{p.health}}</p>
						<button v-if="!p.bot" @click="kick(p.sid)">Kick</button>
					</li>
				</ul>
				<br>
			</li>
		</ul>
	</div>
</template>
<script>
export default {
	name: 'Help',
	components: {
	},
	data:()=>({
		rooms: [],
		deploy_key: ''
	}),
	computed: {
	},
	sockets: {
		all_rooms(data) {
			this.rooms = data;
		},
	},
	mounted() {
		if (this.deploy_key == "")
			this.deploy_key = prompt('Write the key');
		this.refresh();
	},
	methods: {
		refresh(){
			this.$socket.emit('get_all_rooms', this.deploy_key)
		},
		hide(room_name){
			this.$socket.emit('hide_toogle', {'key':this.deploy_key, 'room':room_name})
			setTimeout((()=>{
				this.refresh()
			}).bind(this), 500)
		},
		kick(sid){
			this.$socket.emit('kick', {'key':this.deploy_key, 'sid':sid})
			setTimeout((()=>{
				this.refresh()
			}).bind(this), 500)
		}
	}
}
</script>
<style scoped>
</style>