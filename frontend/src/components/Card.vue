<template>
  <div
    :class="{
      card: true,
      avatarred: card.avatar,
      equipment: card.is_equipment,
      character: card.is_character,
      back: card.is_back,
      'usable-next-turn': card.usable_next_turn,
      'must-be-used': card.must_be_used,
      'gold-rush': card.expansion === 'gold_rush',
      brown: card.kind === 0,
      black: card.kind === 1,
    }"
  >
    <h4>{{ cardName }}</h4>
    <div
      v-if="card.avatar"
      class="avatar"
      :style="`background-image: url(${card.avatar});`"
    ></div>
    <div :class="{ emoji: true, bottomed: card.avatar }">{{ emoji }}</div>
    <div v-if="card.isMe" :class="{ emoji: true, bottomed: card.avatar, isMe: true }"></div>
    <div class="alt_text">{{ card.alt_text }}</div>
    <div class="suit">
      {{ number
      }}<span
        :style="`${
          card.suit !== undefined && card.suit % 2 === 0 ? 'color:red' : ''
        }`"
        >{{ suit }}</span
      >
    </div>
    <div class="expansion" v-if="card.expansion_icon">
      {{ card.expansion_icon }}
    </div>
  </div>
</template>

<script>
export default {
  name: "Card",
  props: {
    card: Object,
    donotlocalize: Boolean,
  },
  computed: {
    cardName() {
      // console.log(this.$t(`cards.${this.card.name}.name`))
      if (
        !this.donotlocalize &&
        this.$t(`cards.${this.card.name}.name`) !==
          `cards.${this.card.name}.name`
      ) {
        return this.$t(`cards.${this.card.name}.name`);
      }
      if (this.card.name == "you") {
        return this.$t("you");
      }
      return this.card.name;
    },
    emoji() {
      return this.card.icon != "you" ? this.card.icon : this.$t("you");
    },
    suit() {
      if (this.card && !isNaN(this.card.suit)) {
        let x = ["♦️", "♣️", "♥️", "♠️", "🤑"];
        return x[this.card.suit];
      } else if (this.card.suit) {
        return this.card.suit;
      }
      return "";
    },
    number() {
      if (isNaN(this.card.suit)) return this.card.number;
      if (this.card.number === 1) return "A";
      else if (this.card.number === 11) return "J";
      else if (this.card.number === 12) return "Q";
      else if (this.card.number === 13) return "K";
      else return this.card.number;
    },
  },
};
</script>

<style>
.card {
  cursor: pointer;
  width: 60pt;
  min-width: 60pt;
  height: 100pt;
  margin: 12pt;
  background: var(--bg-color);
  box-shadow: 0 0 0 3pt #987e51, 0 0 0 6pt var(--bg-color), 0 0 5pt 6pt #aaa;
  border-radius: 6pt;
  position: relative;
  transition: all 0.5s ease-in-out;
  color: var(--font-color);
  text-overflow: ellipsis;
  word-wrap: normal;
}
.avatarred {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
}
.card.back {
  color: white;
  background: repeating-linear-gradient(
    45deg,
    #987e51,
    #987e51 5px,
    #816b45 5px,
    #816b45 10px
  );
}
.card:not(.back, .fistful-of-cards, .high-noon, .gold-rush, .train-piece):before {
  content: "";
  background-image: radial-gradient(var(--bg-color) 13%, #0000 5%),
    radial-gradient(var(--bg-color) 14%, transparent 5%),
    radial-gradient(var(--bg-color) 8%, transparent 5%);
  background-position: -12px 0, 12px 14px, 0 -12pt;
  background-size: 50px 50px;
  position: absolute;
  top: -10px;
  left: -10px;
  bottom: -4px;
  right: -4px;
}
.card.equipment {
  box-shadow: 0 0 0 3pt #5c5e83, 0 0 0 6pt var(--bg-color), 0 0 5pt 6pt #aaa;
}
.card.character {
  box-shadow: 0 0 0 3pt #7c795b, 0 0 0 6pt var(--bg-color), 0 0 5pt 6pt #aaa;
}
.card.usable-next-turn {
  box-shadow: 0 0 0 3pt #6aa16e, 0 0 0 6pt var(--bg-color), 0 0 5pt 6pt #aaa;
}
.card.wild-west-show {
  box-shadow: 0 0 0pt 4pt var(--bg-color), 0 0 5pt 4pt #aaa;
  border: 2pt dotted #987e51;
}
.card.high-noon {
  box-shadow: 0 0 0pt 4pt var(--bg-color), 0 0 5pt 4pt #aaa;
  border: 2pt dotted rgb(198 78 45);
}
.card.fistful-of-cards {
  box-shadow: 0 0 0pt 4pt var(--bg-color), 0 0 5pt 4pt #aaa;
  border: 2pt dashed rgb(50 122 172);
}
.card.back.fistful-of-cards {
  background: repeating-linear-gradient(
    45deg,
    rgb(50 122 172),
    rgb(50 122 172) 5px,
    rgb(30 102 152) 5px,
    rgb(30 102 152) 10px
  );
  border: 2pt solid rgb(50 122 172);
}
.card.back.high-noon {
  background: repeating-linear-gradient(
    45deg,
    rgb(198 78 45),
    rgb(198 78 45) 5px,
    rgb(178 58 25) 5px,
    rgb(178 58 25) 10px
  );
  border: 2pt solid rgb(198 78 45);
}
.card.back.the-valley-of-shadows {
  background: repeating-linear-gradient(
    45deg,
    rgb(98 88 85),
    rgb(98 88 85) 5px,
    rgb(78 68 65) 5px,
    rgb(78 68 65) 10px
  );
  border: 2pt solid rgb(98 88 85);
  box-shadow: 0 0 0pt 4pt var(--bg-color), 0 0 5pt 4pt #aaa;
}
.card.back.wild-west-show {
  color: white;
  background: repeating-linear-gradient(
    90deg,
    #816b45,
    #816b45 3px,
    #987e51 3px,
    #987e51 6px
  );
  border: 2pt solid #987e51;
}
.card.back.dodge-city {
  color: white;
  border: 2pt solid #987e51;
  box-shadow: 0 0 0pt 4pt var(--bg-color), 0 0 5pt 4pt #aaa;
}
.card.back.cant-play {
  transform: scale(0.9);
  filter: grayscale(1);
  opacity: 0.5;
}
.card.back.cant-play:hover {
  transform: scale(0.95);
  filter: grayscale(0.6);
  opacity: 0.8;
}
.beta::after {
  content: "Beta";
  position: absolute;
  bottom: -12pt;
  right: -12pt;
  background: red;
  font-size: 10pt;
  color: white;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  font-weight: bold;
  padding: 4pt;
  border-radius: 12pt;
}
.alpha::after {
  content: "Alpha";
  position: absolute;
  bottom: -12pt;
  right: -12pt;
  background: red;
  font-size: 10pt;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
  font-weight: bold;
  padding: 4pt;
  border-radius: 12pt;
}
.avatar {
  position: absolute;
  width: 36pt;
  margin: auto;
  top: 25%;
  background-position: center;
  background-size: contain;
  background-repeat: no-repeat;
  border-radius: 36pt;
  height: 36pt;
}
.card.brown.gold-rush {
  box-shadow: 0 0 0pt 4pt var(--bg-color), 0 0 5pt 4pt #aaa;
  border: 2pt dotted #9c7340;
}
.card.black.gold-rush {
  box-shadow: 0 0 0pt 4pt var(--bg-color), 0 0 5pt 4pt #aaa;
  border: 2pt dotted #000;
}
.card.back.gold-rush {
  border: 2pt solid #987e51;
  box-shadow: 0 0 0pt 4pt var(--bg-color), 0 0 5pt 4pt #aaa;
  background: repeating-linear-gradient(347deg, #ffb32f, #987e51);
}
.card h4 {
  position: absolute;
  text-align: center;
  width: 100%;
  top: -10pt;
  font-size: 11pt;
}
.card.back h4 {
  font-size: 12pt;
}
.card .emoji {
  position: absolute;
  text-align: center;
  width: 100%;
  font-size: 26pt;
  top: 35%;
}
.card .emoji.isMe {
  position: absolute;
  text-align: center;
  width: 100%;
  font-size: 16pt;
  top: 52%;
  right: 12pt;
}
.emoji.isMe::after {
  content: "🫵";
  display: block;
}
.card:HOVER .isMe::after {
  content: "👋";
  animation: wave 0.5s infinite;
  will-change: transform;
}
@keyframes wave {
  0% {
    transform: translate(-5px, 0px) rotate(0deg);
  }
  50% {
    transform: translate(-5px, -5px) rotate(25deg);
  }
  100% {
    transform: translate(-5px, 0) rotate(0deg);
  }
}
.emoji.bottomed {
  top: 45%;
  left: 8pt;
}
.emoji.bottomed.emoji.isMe {
  top: 60%;
  left: -5pt;
}
.card.must-be-used {
  filter: drop-shadow(0 0 5px red);
}
.fistful-of-cards .emoji,
.high-noon .emoji,
.card.wild-west-show .emoji,
.exp-pack .emoji {
  top: auto !important;
  bottom: 15% !important;
}
.card .suit {
  position: absolute;
  bottom: 3pt;
  left: 3pt;
}
.card.character .suit {
  font-size: small;
  right: 3pt;
  text-align: center;
}
.alt_text {
  right: 3pt;
  text-align: center;
  position: absolute;
  font-size: small;
  bottom: 20pt;
  left: 3pt;
}
.cant-play {
  filter: brightness(0.5);
}
.expansion {
  position: absolute;
  bottom: -5pt;
  right: -5pt;
  background: var(--bg-color);
  border-radius: 100%;
  transform: scale(0.8);
}
.train-piece {
  background: linear-gradient(180deg, rgba(218,101,64,1) 0%, rgba(217,197,184,1) 13%, rgba(217,197,184,1) 53%, rgba(235,169,95,1) 61%, rgba(158,81,55,1) 91%, rgba(158,81,55,1) 100%);
    box-shadow: 0 0 0pt 2pt var(--font-color), 0 0 5pt 2pt #aaa;
}
.train-piece .emoji {
  transform: scaleX(-1);
  /* filter: grayscale(1); */
}
.train-piece h4 {
  position: absolute;
  text-align: center;
  width: 100%;
  bottom: -10pt;
  top: unset;
  font-size: 11pt;
  color: #FFE27E;
}
</style>