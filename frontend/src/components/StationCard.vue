<template>
  <div>
    <div class="stationcard">
      <h4>{{ cardName }}</h4>
      <div :class="{ emoji: true, bottomed: card.avatar }">{{ emoji }}</div>
      <div class="alt_text">{{ card.alt_text }}</div>
      <div class="price">
        <card v-for="c, i in price" :key="i" :card="c"/>
      </div>
    </div>
    <card v-if="trainPiece" class="train-piece" :card="trainPiece" />
  </div>
</template>

<script>
import Card from '@/components/Card.vue'

export default {
  name: "StationCard",
  props: {
    card: Object,
    price: Array,
    trainPiece: Object,
    donotlocalize: Boolean,
  },
  components: {
    Card
  },
  computed: {
    cardName() {
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

<style scoped>
.stationcard {
  cursor: pointer;
  width: 60pt;
  min-width: 60pt;
  height: 60pt;
  margin: 6pt;
  border-radius: 16pt 16pt 2pt 2pt;
  position: relative;
  transition: all 0.5s ease-in-out;
  text-overflow: ellipsis;
  word-wrap: normal;
  color: white;
  background: repeating-linear-gradient(
    0deg,
    rgb(198 78 45),
    rgb(198 78 45) 5px,
    rgb(178 58 25) 5px,
    rgb(178 58 25) 10px
  );
  border: 2pt solid rgb(198 78 45);
  box-shadow: 0 0 0pt 2pt var(--font-color), 0 0 5pt 2pt #aaa;
}
.stationcard h4 {
  position: absolute;
  text-align: center;
  width: 100%;
  top: -15pt;
  font-size: 10pt;
}
.alt_text {
  right: 3pt;
  text-align: center;
  position: absolute;
  font-size: small;
  bottom: 20pt;
  left: 3pt;
}
.stationcard .price {
  justify-content: center;
  /* left: -12pt; */
  margin-top: -20pt;
  /* left: 0; */
  display: flex;
  width: 60pt;
  transform: scale(0.3);
}
.price .card {
  transform:  rotate(14deg);
}
.train-piece {
  margin: 6pt;
}
</style>