<template>
	<div :class="{chat:true, chat_spectators:spectators > 0}" :style="`${collapsed?'min-width:0':''}`">
		<div class="chat-header">
			<div style="display:flex;align-items: center;max-height: 20pt;">
				<h3>{{$t("chat.chat")}}</h3>
				<button class="btn" @click="collapsed = !collapsed" style="max-height:20pt;">{{collapsed?">>":"X"}}</button>
			</div>
			<h4 v-if="spectators > 0" style="margin:0">{{$tc("chat.spectators", spectators)}}</h4>
		</div>
		<div :class="{cont:true, cont_spectators:spectators > 0}">
			<transition-group name="message" tag="div" id="chatbox" :style="`${collapsed?'display:none':''}`">
				<p style="margin:1pt;" class="chat-message" v-for="(msg, i) in messages" v-bind:key="`${i}-c`" :style="`color:${msg.color};background:${msg.bgcolor}${msg.bgcolor?';border-left: medium solid '+msg.color+';padding-left:2pt;':''}`">
					<JsonViewer v-if="msg.type == 'json'" :value="msg.json"/>
					<span v-else-if="msg.parts" v-for="(part, i) in msg.parts" v-bind:key="`${i}-p`" :style="`${i%2!=0?'font-weight: bold;':''}${part.desc?'text-decoration: dotted underline':''}`" class="msg-part" :title="part.desc">{{part.text}}</span>
					<span v-else class="msg-text">{{msg.text}}</span>
				</p>
				<p class="end" key="end" style="color:#0000">.</p>
			</transition-group>
			<div v-if="commandSuggestion.length > 0">
				<p style="margin:1pt 15pt;cursor:pointer;" class="chat-message" v-for="(msg, i) in commandSuggestion" v-bind:key="`${i}-c`" :style="`color:orange`"
						@click="fillCmd(msg.cmd)">{{msg.cmd}} <i class="std-text" style="font-size:8pt;">{{msg.help}}</i></p>
			</div>
			<form @submit="sendChatMessage" id="msg-form">
				<input id="my-msg" autocomplete="off" v-model="text" style="flex-grow:2;"/>
				<input id="submit-message" type="submit" class="btn" :value="$t('submit')"/>
			</form>
		</div>
		<transition-group name="message" tag="div" id="toast-chatbox">
			<p style="margin:1pt;" class="chat-message" v-for="msg in toasts" v-bind:key="`${msg.text}-c`" :style="`width:fit-content;color:${msg.color};background:${msg.bgcolor}${msg.bgcolor?';border-left: medium solid '+msg.color+';padding-left:2pt;padding-right:4pt;':''}`">{{msg.text}}</p>
		</transition-group>
	</div>
</template>

<script>
import message_sfx from '@/assets/sounds/message.mp3'
import notification_sfx from '@/assets/sounds/actionlog.mp3'
import dynamite_sfx from '@/assets/sounds/dynamite.mp3'
import prison_sfx from '@/assets/sounds/prison.mp3'
import turn_sfx from '@/assets/sounds/turn.mp3'
import death_sfx from '@/assets/sounds/death.mp3'
import cash_sfx from '@/assets/sounds/cash.mp3'
import JsonViewer from 'vue-json-viewer'

export default {
	name: 'Chat',
	props: {
		username: String
	},
	components: {
		JsonViewer
	},
	data: () => ({
		messages: [],
		toasts: [],
		text: '',
		spectators: 0,
		commands: [{cmd:'/debug', help:'Toggles the debug mode'}],
		collapsed: false,
	}),
	computed: {
		commandSuggestion() {
			this.text;
			if (this.text.length < 1) {
				return [];
			}
			return this.commands.filter(x => x.cmd.slice(0, this.text.length) == this.text);
		},
	},
	sockets: {
		chat_message(msg) {
			if ((typeof msg === "string" && msg.indexOf('_') === 0) || (msg.color != null && msg.text.indexOf('_') === 0)) {
				let t_color = null
				let bg_color = null
				if (msg.color != null) {
					t_color = msg.color
					bg_color = msg.bgcolor
					msg = msg.text
				}
				let desc = undefined
				let params = msg.split('|')
				let type = params.shift().substring(1)
				if (["flipped", "respond", "play_card", "play_card_against", "play_card_for", "spilled_beer", "diligenza", "wellsfargo", "saloon", "special_calamity", 'won'].indexOf(type) !== -1){
					params[1] = this.$t(`cards.${params[1]}.name`)
					desc = this.$t(`cards.${params[1]}.desc`)
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
					this.messages.push({color:t_color, bgcolor: bg_color, text:false, parts:this.$t(`chat.${type}`, params).split(';').map(x=>({text:x}))});
				} else {
					this.messages.push({text:false, parts: this.$t(`chat.${type}`, params).split(';').map((x, i)=>({text:x, desc:(i===3&&desc?desc:null)}))});
				}
				if (type == 'turn' && params[0] == this.username) {
					(new Audio(turn_sfx)).play();
				} else if (type == 'died_role') {
					(new Audio(death_sfx)).play();
				} else if (type == 'explode') {
					(new Audio(dynamite_sfx)).play();
				} else if (type == 'prison_turn') {
					(new Audio(prison_sfx)).play();
				} else if (type == 'purchase_card') {
					(new Audio(cash_sfx)).play();
				} else {
					(new Audio(notification_sfx)).play();
				}
			} else { // a chat message
				(new Audio(message_sfx)).play();
				this.messages.push(msg);
				if (msg.type && msg.type === 'json') {
					msg.json = JSON.parse(msg.text);
				}
				if (this.collapsed || window.innerWidth < 1000) {
					this.toasts.push(msg);
					setTimeout(() => this.toasts.shift(), 5000);
				}
			}
			let container = this.$el.querySelector("#chatbox");
			container.scrollTop = container.scrollHeight;
		},
		spectators(val) {
			this.spectators = val
		},
		commands(list) {
			this.commands = list;
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
		fillCmd(cmd) {
			this.text = cmd;
			document.getElementById('my-msg').focus();
		}
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
.std-text {
	color: var(--font-color);
}
.chat, .cont {
	display: flex;
	flex-direction: column;
	max-height: 90vh;
}
.chat_spectators, .cont_spectators {
	max-height: 84vh;
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
	.chat-header {
		margin-left: 10pt;
	}
	.chat, .cont { 
		height: 88vh;
		margin-left: 10pt;
	}	
	.chat_spectators, .cont_spectators {
		max-height: 84vh;
	}
	#submit-message {
		margin-left: 6pt;
		margin-right: -5pt;
	}
}
#toast-chatbox {
	position: fixed;
	bottom: 30pt;
	left: 0;
	background: --var(--bg-color);
}
@media only screen and (max-width:1000px) {
	#msg-form {
		flex-direction: column;
		margin-bottom: 50pt;
	}
	#submit-message {
		margin-top: 6pt;
	}
	#chatbox {
		max-height:150px;
	}
}
</style>