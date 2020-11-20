<template>
	<div>
		<h3>Chat</h3>
		<div id="chatbox">
			<p style="margin:1pt;" v-for="msg in messages" v-bind:key="msg">{{msg}}</p>
		</div>
		<form @submit="sendChatMessage" style="width:100%; padding:0">
			<input v-model="text" style="width:80%;"/>
			<input type="submit" style="width:18%;"/>
		</form>
	</div>
</template>

<script>
export default {
	name: 'Chat',
	data: () => ({
		messages: [],
		text: ''
	}),
	sockets: {
		chat_message(msg) {
			this.messages.push(msg)
			let container = this.$el.querySelector("#chatbox");
			container.scrollTop = container.scrollHeight;
		},
	},
	methods: {
		sendChatMessage(e) {
			if (this.text.trim().length > 0){
				this.$socket.emit('chat_message', this.text.trim())
				this.text = ''
			}
			e.preventDefault();
		},
	},
}
</script>
<style >
#chatbox {
	width:100%;
	max-height:150px;
	overflow:auto;
	border: 1pt solid #ccc;
	border-radius: 2pt;
}
</style>