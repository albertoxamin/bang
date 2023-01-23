<template>
	<div id="overlay" class="center-stuff">
		<h1>{{text}}</h1>
		<div>
			<Card v-if="playerCard" :card="playerCard" />
			<Card v-if="playerRole" :card="playerRole" class="back"/>
		</div>
	</div>
</template>

<script>
import Card from '@/components/Card.vue'

export default {
	name: 'DeadRoleNotification',
	components: {
		Card,
	},
	props: {
		playerCard: Object,
		playerRole: Object
	},
	data: () => ({

	}),
	computed: {
	},
	methods: {
	},
	mounted() {
	}
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
#overlay {
	position: fixed; /* Sit on top of the page content */
	width: 100%; /* Full width (cover the whole page) */
	height: 100%; /* Full height (cover the whole page) */
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background-color: rgba(0,0,0,0.7); /* Black background with opacity */
	z-index: 2; /* Specify a stack order in case you're using a different order for other elements */
	/* display: flex; */
	color: white;
	justify-content: center;
	text-align: center;
}

#overlay>div {
	margin:auto;
	position: relative;
	top:35%;
	text-align: center;
	width: 72pt;
	transform: scale(1.5);
}
.card {
	width: 72pt;
	min-width:72pt;
	height: 120pt;
	position: absolute;
}
.card.avatarred{
	animation: slide-in-fwd-bottom 2s ease, puff-out-center 1s ease 2s, make-invisible 10s step-start 3s;
}
.card.back {
	animation: make-visible 3s step-end, wobble-ver-left 2s ease 3s;
}
@keyframes make-invisible {
	0% {
		opacity: 1;
	}
	100% {
		opacity: 0;
	}
}
@keyframes make-visible {
	0% {
		opacity: 0;
	}
	100% {
		opacity: 1;
	}
}
@keyframes wobble-ver-left {
		0% {
			transform:translateY(0) rotate(0);
			transform-origin:50% 50%;
		}
		15% {
			transform:translateY(-30px) rotate(-6deg);
		}
		30% {
			transform:translateY(15px) rotate(6deg);
		}
		45% {
			transform:translateY(-15px) rotate(-3.6deg);
		}
		60% {
			transform:translateY(9px) rotate(2.4deg);
		}
		75% {
			transform:translateY(-6px) rotate(-1.2deg);
		}
		100% {
			transform:translateY(0) rotate(0);
			transform-origin:50% 50%;
		}
	}
@keyframes slide-in-fwd-bottom {
		0% {
			transform:translateZ(-1400px) translateY(800px);
			opacity:0;
		}
		100% {
			transform:translateZ(0) translateY(0);
			opacity:1;
		}
	}
@keyframes puff-out-center {
			
		0% {
			transform:scale(1);
			filter:blur(0);
			opacity:1;
		}
		100% {
			transform:scale(2);
			filter:blur(4px);
			opacity:0;
		}
	}

.button {
	background-color: #0000;
	color: white;
	border: 2px solid white;
	transition-duration: 0.2s;
	width: 100pt;
	height: 24pt;
	border-radius: 12pt;
	cursor: pointer;
}

.button:hover {
	background-color: white; /* Green */
	color: black;
}
</style>
