<template>
	<div class="chat">
		<h3>{{$t("chat.chat")}}</h3>
		<div id="chatbox">
			<p style="margin:1pt;" class="chat-message" v-for="msg in messages" v-bind:key="msg">{{msg}}</p>
			<p class="end">.</p>
		</div>
		<form @submit="sendChatMessage" id="msg-form">
			<input v-model="text" style="flex-grow:2;"/>
			<input type="submit" :value="$t('submit')"/>
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
			if (msg.indexOf('_') === 0) {
				let params = msg.split('|')
				let type = params.shift().substring(1)
				this.messages.push(this.$t(`chat.${type}`, params))
			}else {
				this.messages.push(msg)
			}
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
<style scoped>
#chatbox {
	width:100%;
	max-height:150px;
	overflow-y: auto;
	overflow-x: hidden;
	overflow-wrap: break-word;
	overflow-wrap: normal;
	border: 2pt solid #ccc;
	border-radius: 4pt;
}
input {
	margin:0;
}
.end {
	height: 0pt;
	margin-top: -1.5pt;
}
#msg-form {
	width:100%;
	padding:0;
	display:flex;
}
@media only screen and (max-width:1000px) {
	#msg-form {
		flex-direction: column;
	}
}
</style>