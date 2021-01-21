<template>
	<div class="chat">
		<h4 v-if="spectators > 0">{{$tc("chat.spectators", spectators)}}</h4>
		<h3>{{$t("chat.chat")}}</h3>
		<div id="chatbox">
			<p style="margin:1pt;" class="chat-message selectable" v-for="(msg, i) in messages" v-bind:key="`${i}-c`" :style="`color:${msg.color}`">{{msg.text}}</p>
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
		text: '',
		spectators: 0,
	}),
	sockets: {
		chat_message(msg) {
			console.log(msg)
			if ((typeof msg === "string") && msg.indexOf('_') === 0) {
				let params = msg.split('|')
				let type = params.shift().substring(1)
				this.messages.push({text:this.$t(`chat.${type}`, params)})
			}else {
				this.messages.push(msg)
			}
			let container = this.$el.querySelector("#chatbox");
			container.scrollTop = container.scrollHeight;
		},
		spectators(val) {
			this.spectators = val
		}
	},
	methods: {
		sendChatMessage(e) {
			let msg = this.text.trim()
			if (msg.length > 0){
				if (msg.indexOf('/addbot') !== -1 && msg.split(' ').length > 1){
					for (let i = 0; i < parseInt(msg.split(' ')[1]); i++) {
						this.$socket.emit('chat_message', msg.split(' ')[0])
					}
				}else{
					this.$socket.emit('chat_message', msg)
				}
				this.text = ''
			}
			e.preventDefault();
		},
	},
}
</script>
<style scoped>
#chatbox {
	flex: 1;
	width:100%;
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
.chat {
	display: flex;
	flex-direction: column;
}
#msg-form {
	width:100%;
	padding:0;
	display:flex;
}
@media only screen and (min-width:1000px) {
	.chat { 
		height: 90vh;
		margin-left: 10pt;
	}
}
@media only screen and (max-width:1000px) {
	#msg-form {
		flex-direction: column;
	}
	#chatbox {
		max-height:150px;
	}
}
</style>