<template>
	<div style="max-width: 350pt;">
		<h3>Chat</h3>
		<div id="chatbox">
			<p style="margin:1pt;" class="chat-message" v-for="msg in messages" v-bind:key="msg">{{msg}}</p>
			<p class="end">.</p>
		</div>
		<form @submit="sendChatMessage" style="width:100%; padding:0; display:flex;">
			<input v-model="text" style="flex-grow:2;"/>
			<input type="submit"/>
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
			// let container = this.$el.querySelector("#chatbox");
			// container.scrollTop = container.scrollHeight;
			const el = this.$el.getElementsByClassName('end')[0];
			if (el) {
				el.scrollIntoView();
			}
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
<style scoped>
#chatbox {
	width:100%;
	max-height:150px;
	overflow-y: auto;
	overflow-x: hidden;
	overflow-wrap: break-word;
	overflow-wrap: normal;
	border: 1pt solid #ccc;
	border-radius: 2pt;
}
/* .chat-message:nth-last-of-type(1) {
	margin-bottom: 50pt !important;
} */
</style>