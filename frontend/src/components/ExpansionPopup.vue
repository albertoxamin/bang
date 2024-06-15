<template>
  <div class="popup-overlay" v-if="show" @click="handleOverlayClick">
    <div class="popup-content" @click.stop>
      <button class="close-button" @click="close">×</button>
      <h2>{{ expansion.name }}</h2>
      <div  v-for="section in expansion.cards" :key="section.type" class="section">
        <h3>{{ section.type }}</h3>
        <div class="cards-container flexy-cards-wrapper">
          <div v-for="card in section.cards" :key="card.name"  class="flexy-cards">
            <Card :card="card" v-if="section.type !== 'stations'" :class="getClass(expansion, section)"/>
            <StationCard :card="card" :price="card.price" v-else-if="section.type === 'stations'"/>
            <div style="margin-left:6pt;">
              <p>{{$t(`cards.${card.name}.desc`)}}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Card from '@/components/Card.vue';
import StationCard from './StationCard.vue';

export default {
  props: {
    show: Boolean,
    expansion: Object, // Expecting an object with id, name, and cards
  },
  components: {
    Card,
    StationCard,
  },
  methods: {
    close() {
      this.$emit('close');
    },
    handleOverlayClick() {
      this.close();
    },
    getClass(expansion, section) {
      let classes = ''
      if (section.type == 'events') {
        classes += 'last-event';
      }
      if (expansion.id == 'fistful_of_cards') {
        classes += ' fistful-of-cards';
      } else if (expansion.id == 'high_noon') {
        classes += ' high-noon';
      } else if (expansion.id == 'gold_rush') {
        classes += ' gold-rush';
      } else if (expansion.id == 'train_robbery') {
        classes += ' train-robbery';
      } else if (expansion.id == 'the_valley_of_shadows') {
        classes += ' valley-of-shadows';
      } else if (expansion.id == 'wild_west_show') {
        classes += ' wild-west-show';
      }
      console.log(classes);
      return classes;
    }
  },
};
</script>

<style scoped>
.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}
.popup-content {
  position: relative;
  background: white;
  padding: 20px;
  border-radius: 5px;
  max-width: 80%;
  max-height: 80%;
  overflow-y: auto;
}
.close-button {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
}
.section {
  margin-bottom: 20px;
}
.cards-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.card {
  box-sizing: border-box;
  margin-bottom: 10px;
}
.flexy-cards-wrapper {
	display: flex;
	flex-flow: wrap;
}
.flexy-cards {
	flex: 30%;
	display:flex;
}
</style>