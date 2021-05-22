<template>
	<div class="chat">
		<h4 v-if="spectators > 0">{{$tc("chat.spectators", spectators)}}</h4>
		<h3>{{$t("chat.chat")}}</h3>
		<transition-group name="message" tag="div" id="chatbox">
		<!-- <div id="chatbox"> -->
			<p style="margin:1pt;" class="chat-message" v-for="(msg, i) in messages" v-bind:key="`${i}-c`" :style="`color:${msg.color}`">{{msg.text}}</p>
			<p class="end" key="end" style="color:#0000">.</p>
		<!-- </div> -->
		</transition-group>
		<form @submit="sendChatMessage" id="msg-form">
			<input v-model="text" style="flex-grow:2;"/>
			<input id="submit-message" type="submit" class="btn" :value="$t('submit')"/>
		</form>
	</div>
</template>

<script>
import message_sfx from '@/assets/sounds/message.mp3'
import notification_sfx from '@/assets/sounds/actionlog.mp3'
import dynamite_sfx from '@/assets/sounds/dynamite.mp3'
import prison_sfx from '@/assets/sounds/prison.mp3'
import turn_sfx from '@/assets/sounds/turn.mp3'
import death_sfx from '@/assets/sounds/death.mp3'
export default {
	name: 'Chat',
	props: {
		username: String
	},
	data: () => ({
		messages: [],
		text: '',
		spectators: 0,
	}),
	sockets: {
		chat_message(msg) {
			// console.log(msg)
			if ((typeof msg === "string" && msg.indexOf('_') === 0) || (msg.color != null && msg.text.indexOf('_') === 0)) {
				let t_color = null
				if (msg.color != null) {
					t_color = msg.color
					msg = msg.text
				}
				let params = msg.split('|')
				let type = params.shift().substring(1)
				if (["flipped", "respond", "play_card", "play_card_against", "play_card_for", "spilled_beer", "diligenza", "wellsfargo", "saloon", "special_calamity"].indexOf(type) !== -1){
					params[1] = this.$t(`cards.${params[1]}.name`)
				} else if (type === "choose_character"){
					params.push(this.$t(`cards.${params[1]}.desc`))
				} else if (type === "allroles") {
					params.forEach((p,i)=>{
						if (i%2 === 0) {
							params[i] = this.$t(`cards.${params[i]}.name`)
						}
					})
					if (params.length <= 6){
						type += "3"
					} else {
						type += "4"
					}
				}
				if (t_color != null) {
					this.messages.push({color:t_color, text:this.$t(`chat.${type}`, params)});
				} else {
					this.messages.push({text:this.$t(`chat.${type}`, params)});
				}
				if (type == 'turn' && params[0] == this.username) {
					(new Audio(turn_sfx)).play();
				} else if (type == 'died_role') {
					(new Audio(death_sfx)).play();
				} else if (type == 'explode') {
					(new Audio(dynamite_sfx)).play();
				} else if (type == 'prison_turn') {
					(new Audio(prison_sfx)).play();
				} else {
					(new Audio(notification_sfx)).play();
				}
			} else { // a chat message
				(new Audio(message_sfx)).play();
				this.messages.push(msg);
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
	border: 2pt solid var(--muted-color);
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
	margin-top: 6pt;
	display:flex;
}
.message-enter-active, .message-leave-active {
  transition: all 1s;
}
.message-enter, .message-leave-to /* .list-leave-active below version 2.1.8 */ {
  opacity: 0;
  transform: translateX(30px);
}
@media only screen and (min-width:1000px) {
	.chat { 
		height: 90vh;
		margin-left: 10pt;
	}
	#submit-message {
		margin-left: 6pt;
		margin-right: -5pt;
	}
}
@media only screen and (max-width:1000px) {
	#msg-form {
		flex-direction: column;
	}
	#submit-message {
		margin-top: 6pt;
	}
	#chatbox {
		max-height:150px;
	}
}
</style>