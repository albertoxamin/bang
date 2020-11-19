<template>
	<div :class="{ card: true, equipment: card.is_equipment }" @click="equip(card)">
		<h3>{{card.name}}</h3>
		<emoji>{{card.icon}}</emoji>
		<span>{{card.number}}{{card.suit}}</span>
	</div>
</template>

<script>
export default {
	name: 'HelloWorld',
	props: {
    card: Object
  },
}
</script>

<style>
.card {
  cursor: pointer;
  width: 60pt;
  min-width:60pt;
  height: 100pt;
	margin: 12pt;
  background: white;
  box-shadow: 
    0 0 0 3pt #987e51,
    0 0 0 6pt white,
    0 0 5pt 6pt #aaa;
  border-radius: 6pt;
  position: relative;
  transition: all 0.5s ease-in-out;
}
.card.back{
  color:white;
  background: #987e51;
}
.card.back::before{
  background:red;
}

.card.equipment {
  box-shadow: 
    0 0 0 3pt #5c5e83,
    0 0 0 6pt white,
    0 0 5pt 6pt #aaa;
}
.card.character {
  box-shadow: 
    0 0 0 3pt #7c795b,
    0 0 0 6pt white,
    0 0 5pt 6pt #aaa;
}
.card h3 {
	position: absolute;
  text-align: center;
  width: 100%;
  top: -10pt;
} 
.card emoji {
	position: absolute;
  text-align: center;
  width: 100%;
  font-size:26pt;
  top: 35%;
} 
.card span {
	position: absolute;
  bottom: 3pt;
  left:3pt;
}
</style>