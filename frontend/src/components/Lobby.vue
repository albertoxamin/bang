<template>
  <div class="lobby">
    <div style="flex-grow: 4">
      <div style="position: relative">
        <h2 v-if="!started">{{ $t("room") }}{{ lobbyName }}</h2>
        <input
          style="position: absolute; top: 0; right: 0; max-height: 100pt"
          v-if="!started"
          type="button"
          class="btn"
          @click="leaveRoom"
          :value="$t('leave_room')"
        />
      </div>
      <h3>{{ $t("room_players", { username: username }) }}</h3>
      <div v-if="debug_mode" style="position: absolute; top: 6pt; right: 6pt">
        <p
          style="
            padding: 0 10px;
            background: red;
            color: white;
            border-radius: 12pt;
          "
        >
          DEBUG ON
        </p>
      </div>
      <div v-if="!started">
        <PrettyCheck
          v-if="isRoomOwner"
          class="p-switch p-fill"
          v-model="privateRoom"
          style="margin-top: 5px; margin-bottom: 3px"
          >{{ $t("private_room") }}</PrettyCheck
        >
        <label v-if="password !== ''"
          >{{ $t("password")
          }}<b class="selectable" style="font-size: larger">{{
            password
          }}</b></label
        >
        <input
          type="button"
          class="btn"
          style="margin-left: 10pt"
          v-clipboard:copy="inviteLink"
          :value="$t('copy')"
        />
      </div>
      <div style="position: relative">
        <div
          v-if="showTurnFlow"
          id="turn-indicator"
          :class="{ reversed: turnReversed }"
        />
        <transition-group name="list" tag="div" class="players-table">
          <Card
            v-if="startGameCard"
            key="_start_game_"
            :donotlocalize="true"
            :card="startGameCard"
            @click.native="startGame"
            style="margin-top: 36pt;"
          />
          <div
            v-for="p in playersTable"
            v-bind:key="p.card.name"
            :id="p.card.name"
            style="position: relative"
            class="player-in-table"
          >
            <transition-group
              v-if="p.max_lives && !p.is_ghost"
              name="list"
              tag="div"
              class="tiny-health"
            >
              <span v-for="(n, i) in p.lives" v-bind:key="i" :alt="i">
                {{(!p.is_sheriff || i !== (p.max_lives-1))?'❤️':'💛'}}</span>
              <span
                v-for="(n, i) in p.max_lives - p.lives"
                v-bind:key="`${i}-sk`"
                :alt="i"
                >💀</span
              >
            </transition-group>
            <div v-else-if="p.is_ghost" class="tiny-health">
              <span>👻</span>
            </div>
            <Card
              :card="p.card"
              @click.native="drawFromPlayer(p.name)"
              :donotlocalize="true"
              :class="{ is_my_turn: p.is_my_turn }"
            />
            <Card
              v-if="p.character"
              :card="p.character"
              class="character tiny-character"
              @click.native="selectedInfo = [p.character]"
            />
            <Card
              v-if="p.character && p.character.name !== p.real_character.name"
              style="transform: scale(0.5) translate(-90px, -50px)"
              :card="p.character"
              class="character tiny-character"
              @click.native="selectedInfo = [p.character]"
            />
            <div
              v-if="p.gold_nuggets && p.gold_nuggets > 0"
              style="position: absolute; top: 45pt; left: -5pt; font-size: 9pt;"
            >
              <h3 style="background:gold;border-radius:15pt;padding:0pt 2pt;color:black"> 💵️ {{ p.gold_nuggets }} </h3>
            </div>
            <tiny-hand
              :id="p.name + '-hand'"
              :ncards="p.ncards"
              :cards="p.hand_cards"
              @click.native="drawFromPlayer(p.name)"
              :ismyturn="p.pending_action === 2"
            />
            <span style="position: absolute; top: 3pt" class="center-stuff">{{
              getActionEmoji(p)
            }}</span>
            <div class="tiny-equipment">
              <Card
                v-for="(card, i) in p.equipment"
                v-bind:key="card.name + card.number"
                :card="card"
                @click.native="selectedInfo = p.equipment"
                :style="`margin-top: ${
                  i < 1
                    ? 10
                    : -Math.min(
                        (p.equipment.length +
                          p.gold_rush_equipment.length +
                          1) *
                          12,
                        80
                      )
                }pt;`"
              />
              <Card
                v-for="(card, i) in p.gold_rush_equipment"
                v-bind:key="card.name + card.number"
                :card="card"
                @click.native="selectedInfo = p.gold_rush_equipment"
                :style="`margin-top: ${
                  i + p.equipment.length < 1
                    ? 10
                    : -Math.min(
                        (p.equipment.length +
                          p.gold_rush_equipment.length +
                          1) *
                          12,
                        80
                      )
                }pt`"
              />
            </div>
            <button
              v-if="is_replay"
              style="position: absolute"
              @click="replayPlayer(p.name)"
            >
              {{ $t("spectate_player") }}
            </button>
            <div
              v-if="p.is_bot"
              style="position: absolute; bottom: 57%; width: 20pt"
              class="center-stuff"
            >
              <span>🤖</span>
            </div>
          </div>
          <Card
            v-if="startGameCard"
            key="_shuffle_players_"
            :donotlocalize="true"
            :card="shufflePlayersCard"
            @click.native="shufflePlayers"
            style="margin-top: 36pt;"
            class="fistful-of-cards"
          />
        </transition-group>
      </div>
      <div v-if="!started">
        <p
          v-if="players.length < 3"
          class="center-stuff"
          style="min-height: 19px"
        >
          {{ $t("minimum_players") }}
        </p>
        <p v-else style="min-height: 19px"></p>
        <h3>{{ $t("expansions") }}</h3>
        <div class="players-table" style="justify-content: flex-start">
          <card
            v-for="ex in expansionsStatus"
            v-bind:key="ex.id"
            :id="ex.id"
            :card="ex.card"
            :class="{
              'cant-play': !ex.enabled,
              ...ex.card.classes,
            }"
            :donotlocalize="true"
            @click.native="toggleExpansions(ex.id)"
          />
        </div>
        <p v-if="isRoomOwner">{{ $t("click_to_toggle") }}</p>
        <h3>{{ $t("mods") }}</h3>
        <PrettyCheck
          @click.native="toggleCompetitive"
          :disabled="!isRoomOwner"
          v-model="is_competitive"
          class="p-switch p-fill"
          style="margin-top: 5px; margin-bottom: 3px"
          >{{ $t("mod_comp") }}</PrettyCheck
        >
        <br/>
        <br/>
        <span>{{$t("characters_to_distribute")}}</span>
        <input
          type="button"
          :class="{btn:true, 'small-btn':true, active: characters_to_distribute === 1}"
          :value="1"
          :disabled="!isRoomOwner"
          @click="
            (e) => {
              this.$socket.emit('chat_message', '/set_chars 1');
              e.preventDefault();
            }
          "
        />
        <input
          type="button"
          :class="{btn:true, 'small-btn':true, active: characters_to_distribute === 2}"
          :value="2"
          :disabled="!isRoomOwner"
          @click="
            (e) => {
              this.$socket.emit('chat_message', '/set_chars 2');
              e.preventDefault();
            }
          "
        />
        <input
          type="button"
          :class="{btn:true, 'small-btn':true, active: characters_to_distribute === 3}"
          :value="3"
          :disabled="!isRoomOwner"
          @click="
            (e) => {
              this.$socket.emit('chat_message', '/set_chars 3');
              e.preventDefault();
            }
          "
        />
        <input
          type="button"
          :class="{btn:true, 'small-btn':true, active: characters_to_distribute === 4}"
          :value="4"
          :disabled="!isRoomOwner"
          @click="
            (e) => {
              this.$socket.emit('chat_message', '/set_chars 4');
              e.preventDefault();
            }
          "
        />
        <h3>{{ $t("bots") }}</h3>
        <input
          type="button"
          class="btn"
          :value="$t('add_bot')"
          :disabled="!isRoomOwner || players.length > 7"
          @click="
            (e) => {
              this.$socket.emit('chat_message', '/addbot');
              e.preventDefault();
            }
          "
        />
        <input
          type="button"
          class="btn"
          style="margin-left: 10pt"
          :value="$t('remove_bot')"
          :disabled="!isRoomOwner || !isThereAnyBot"
          @click="
            (e) => {
              this.$socket.emit('chat_message', '/removebot');
              e.preventDefault();
            }
          "
        />
        <!-- <br> -->
        <!-- <PrettyCheck @click.native="toggleReplaceWithBot" :disabled="!isRoomOwner" v-model="disconnect_bot" class="p-switch p-fill" style="margin-top:5px; margin-bottom:3px;">{{$t('disconnect_bot')}}</PrettyCheck> -->
      </div>
      <AnimatedCard
        v-for="c in cardsToAnimate"
        v-bind:key="c.key"
        :card="c.card"
        :startPosition="c.startPosition"
        :midPosition="c.midPosition"
        :endPosition="c.endPosition"
      />
      <AnimatedEffect
        v-for="c in fullScreenEffects"
        v-bind:key="c.key"
        :text="c.text"
        :startPosition="c.startPosition"
      />
      <div v-if="started">
        <deck
          :endTurnAction="
            () => {
              wantsToEndTurn = true;
            }
          "
        />
        <player
          :isEndingTurn="wantsToEndTurn"
          :cancelEndingTurn="
            () => {
              wantsToEndTurn = false;
            }
          "
          :chooseCardFromPlayer="choose"
          :cancelChooseCardFromPlayer="
            () => {
              hasToChoose = false;
            }
          "
        />
      </div>
    </div>
    <chat :username="username" />
    <Chooser
      v-if="selectedInfo"
      :text="$t('details')"
      :cards="selectedInfo"
      :cancelText="$t('ok')"
      :cancel="
        () => {
          selectedInfo = null;
        }
      "
      :select="
        () => {
          selectedInfo = null;
        }
      "
    />
    <transition name="bounce">
      <Chooser
        v-show="hasToChoose"
        :text="`${$t('choose_card')}${
          target_p ? $t('choose_card_from') + target_p : ''
        }`"
        :cards="chooseCards"
        :select="chooseCard"
      />
    </transition>
    <transition name="bounce">
      <full-screen-input
        v-if="!started && hasToSetUsername"
        :defaultValue="storedUsername"
        :text="$t('choose_username')"
        :val="username"
        :send="setUsername"
        :sendText="$t('ok')"
      />
    </transition>
    <transition name="bounce">
      <div v-if="displayAdminStatus" id="admin-status">
        <input
          type="button"
          @click="displayAdminStatus = false"
          value="close"
        />
        <Status deploy_key="ok" :onpage="false" />
      </div>
    </transition>
    <transition name="bounce">
      <DeadRoleNotification
        v-if="deadRoleData"
        :key="deadRoleData.name"
        :playerCard="deadRoleData"
        :playerRole="deadRoleData.role"
      />
    </transition>
  </div>
</template>

<script>
import Vue from "vue";
import PrettyCheck from "pretty-checkbox-vue/check";
import Card from "@/components/Card.vue";
import Chooser from "./Chooser.vue";
import Chat from "./Chat.vue";
import Player from "./Player.vue";
import Deck from "./Deck.vue";
import TinyHand from "./TinyHand.vue";
import FullScreenInput from "./FullScreenInput.vue";
import Status from "./Status.vue";
import DeadRoleNotification from "./DeadRoleNotification.vue";
import AnimatedCard from "./AnimatedCard.vue";
import { emojiMap } from "@/utils/emoji-map.js";
import { expansionsMap } from "@/utils/expansions-map.js";
import AnimatedEffect from './AnimatedEffect.vue';

const cumulativeOffset = function (element) {
  var top = 0,
    left = 0;
  do {
    top += element.offsetTop || 0;
    left += element.offsetLeft || 0;
    element = element.offsetParent;
  } while (element);
  return {
    top: top,
    left: left - Math.floor(Math.random() * 20) + 10,
  };
};

export default {
  name: "Lobby",
  components: {
    Card,
    Chooser,
    Chat,
    Player,
    Deck,
    TinyHand,
    PrettyCheck,
    FullScreenInput,
    Status,
    DeadRoleNotification,
    AnimatedCard,
    AnimatedEffect,
  },
  data: () => ({
    username: "",
    lobbyName: "",
    started: false,
    players: [],
    messages: [],
    distances: {},
    hasToChoose: false,
    target_p: "",
    chooseCards: [],
    wantsToEndTurn: false,
    selectedInfo: null,
    privateRoom: false,
    password: "",
    togglable_expansions: [],
    expansions: [],
    hasToSetUsername: false,
    is_competitive: false,
    disconnect_bot: false,
    debug_mode: false,
    showTurnFlow: false,
    turnReversed: false,
    displayAdminStatus: false,
    is_replay: false,
    turn: -1,
    deadRoleData: false,
    cardsToAnimate: [],
    characters_to_distribute: 2,
    fullScreenEffects: [],
  }),
  sockets: {
    room(data) {
      this.lobbyName = data.name;
      if (!data.started) {
        document.title = this.lobbyName + " | PewPew!";
      } else if (data.started && !this.started) {
        document.title = "PewPew!";
      }
      this.started = data.started;
      this.password = data.password;
      this.privateRoom = data.password !== "";
      this.is_competitive = data.is_competitive;
      this.disconnect_bot = data.disconnect_bot;
      this.togglable_expansions = data.available_expansions;
      this.expansions = data.expansions;
      this.is_replay = data.is_replay;
      this.characters_to_distribute = data.characters_to_distribute;
      this.players = data.players.map((x) => {
        return {
          name: x.name,
          ready: x.ready,
          is_bot: x.is_bot,
          avatar: x.avatar,
          ncards: 0,
        };
      });
    },
    notify_dead_role(data) {
      this.deadRoleData = data;
      setTimeout(() => {
        this.deadRoleData = false;
      }, 4000);
    },
    debug(data) {
      this.debug_mode = data;
    },
    start() {
      this.started = true;
    },
    players_update(data) {
      if (Vue.config.devtools) console.log(data);
      this.players = data;
    },
    me(username) {
      if (username.error) {
        alert(username.error);
        this.$router.push("/");
      }
      this.username = username;
    },
    card_drawn(data) {
      let from = data.pile === "deck" ? "actual-deck" : `${data.pile}-hand`;
      let decel = document.getElementById(from);
      if (!decel) return;
      let decelOffset = cumulativeOffset(decel);
      let phand = document.getElementById(`${data.player}-hand`);
      if (!phand) return;
      let playerOffset = cumulativeOffset(phand);
      playerOffset.top -= 30;
      playerOffset.left += 10;
      let key = Math.random();
      this.cardsToAnimate.push({
        key: key,
        card: {
          name: "PewPew!",
          icon: "💥",
          back: true,
        },
        startPosition: decelOffset,
        endPosition: playerOffset,
      });
      setTimeout(() => {
        this.cardsToAnimate = this.cardsToAnimate.filter((x) => x.key !== key);
      }, 900);
    },
    card_against(data) {
      let target = document.getElementById(`${data.target}-hand`);
      let targetOffset = cumulativeOffset(target.parentElement);
      let decel = document.getElementById("actual-scrap");
      let decelOffset = cumulativeOffset(decel);
      let phand = document.getElementById(`${data.player}-hand`);
      let playerOffset = cumulativeOffset(phand);
      playerOffset.top -= 30;
      playerOffset.left += 10;
      let key = data.card.name + data.card.number + data.player;
      this.cardsToAnimate.push({
        key: key,
        card: data.card,
        startPosition: playerOffset,
        midPosition: targetOffset,
        endPosition: decelOffset,
      });
      setTimeout(() => {
        this.cardsToAnimate = this.cardsToAnimate.filter((x) => x.key !== key);
      }, 1800);
    },
    chat_message(msg) {
      if (typeof msg !== "string") {
        let key = Math.random();
        let username = msg.text.substring(1, msg.text.indexOf(":")-1);
        setTimeout(() => {
            this.fullScreenEffects.push({
              key: key,
              text: '💬',
              startPosition: cumulativeOffset(document.getElementById(username)),
            });
          }, 50);
          setTimeout(() => {
            this.fullScreenEffects = this.fullScreenEffects.filter(
                (x) => x.key !== key
            );
          }, 3000);
        return;
      }
      let params = msg.split('|')
      let type = params.shift().substring(1)
      let messageMap = {
        prison_turn: '⛓️;🔒;⏭️',
        explode: '💥;🧨',
        purchase_card: '🛒;💸',
        prison_free: '🆓;🔑',
        snake_bit: '🐍;🩸',
        beer_save: '🍺;😇',
        sheriff: '⭐',
        spilled_beer: '🍺;😭',
        use_special: '🔝;✨',
        died: '💀;👻;😭;☠️;🪦;F',
        died_role: '💀;👻;😭;☠️;🪦;F',
      }
      if (messageMap[type]) {
        let key = Math.random();
        let avail = messageMap[type].split(';');
        for (let i = 0; i < 5; i++) {
          setTimeout(() => {
            this.fullScreenEffects.push({
              key: key+i,
              text: avail[Math.floor(Math.random() * avail.length)],
              startPosition: cumulativeOffset(document.getElementById(params[0])),
            });
          }, 50 * i);
          setTimeout(() => {
            this.fullScreenEffects = this.fullScreenEffects.filter(
                (x) => x.key !== key+i
            );
          }, 3000);
        }
      }
    },
    suggest_expansion(expansionName) {
      if (this.expansions.includes(expansionName)) return;
      let key = Math.random();
      let decel = document.getElementById(expansionName);
      if (!decel) return;
      let decelOffset = cumulativeOffset(decel);
      for (let i = 0; i < 6; i++) {
        setTimeout(() => {
          this.fullScreenEffects.push({
            key: key+i,
            text: i == 0 ? '🤠' : i == 5 ? '💭' : emojiMap[expansionName],
            startPosition: decelOffset,
          });
        }, 50 * i);
        setTimeout(() => {
          this.fullScreenEffects = this.fullScreenEffects.filter(
            (x) => x.key !== key+i
          );
        }, 3000);
      }
    },
    card_scrapped(data) {
      let decel = document.getElementById("actual-scrap");
      if (!decel) {
        console.log("card_scrapped no deck");
        return;
      }
      let phand = document.getElementById(`${data.player}-hand`);
      if (data.pile == "train_robbery") {
        decel = phand
        phand = document.getElementById("train-robbery-deck");
      } else if (data.pile == "gold_rush") {
        decel = phand
        phand = document.getElementById("gold-rush-deck");
      }
      let decelOffset = cumulativeOffset(decel);
      if (!phand) {
        console.log("card_scrapped no phand");
        return;
      }
      let playerOffset = cumulativeOffset(phand);
      playerOffset.top -= 30;
      playerOffset.left += 10;
      console.log("card_scrapped" + decelOffset + " " + playerOffset);
      let key = data.card.name + data.card.number + data.player;
      this.cardsToAnimate.push({
        key: key,
        card: data.card,
        startPosition: playerOffset,
        endPosition: decelOffset,
      });
      setTimeout(() => {
        this.cardsToAnimate = this.cardsToAnimate.filter((x) => x.key !== key);
      }, 900);
    },
    mount_status() {
      this.displayAdminStatus = true;
    },
    change_username() {
      this.hasToSetUsername = true;
    },
    kicked() {
      window.location.replace(window.location.origin);
      document.title = "PewPew!";
    },
  },
  computed: {
    inviteLink() {
      return `${window.location.origin}/game?code=${encodeURIComponent(
        this.lobbyName
      )}${this.password ? `&pwd=${this.password}` : ""}`;
    },
    isThereAnyBot() {
      return this.players.filter((x) => x.is_bot).length > 0;
    },
    expansionsStatus() {
      return this.togglable_expansions.map((x) => {
        return {
          id: x,
          name: x.replace(/(^|_)([a-z])/g, function ($0, $1, $2) {
            return " " + $2.toUpperCase();
          }),
          enabled: this.expansions.indexOf(x) !== -1,
          emoji: emojiMap[x],
          card: this.getExpansionCard(x),
        };
      });
    },
    storedUsername() {
      if (localStorage.getItem("username"))
        return localStorage.getItem("username");
      return "";
    },
    isRoomOwner() {
      if (this.players.length > 0) {
        let pls = this.players.filter((x) => !x.is_bot);
        return pls.length > 0 && pls[0].name == this.username;
      }
      return false;
    },
    startGameCard() {
      if (!this.started && this.players.length > 2 && this.isRoomOwner) {
        return {
          name: this.$t("start_game"),
          icon: "▶️",
          is_equipment: true,
          number: `${this.players.length}🤠`,
        };
      }
      return null;
    },
    shufflePlayersCard() {
      if (!this.started && this.players.length > 2 && this.isRoomOwner) {
        return {
          name: this.$t("shuffle_players"),
          icon: "🔀",
          is_equipment: true,
        };
      }
      return null;
    },
    playersTable() {
      if (Vue.config.devtools) console.log("update players");
      return this.players.map((x, i) => {
        let offsetAngle = 360.0 / this.players.length;
        let rotateAngle = i * offsetAngle;
        let size = 130;
        return {
          card: this.getPlayerCard(x),
          style: `position:absolute;transform: rotate(${rotateAngle}deg) translate(0, -${size}pt) rotate(-${rotateAngle}deg) translate(${size}pt,${size}pt)`,
          ...x,
        };
      });
    },
  },
  methods: {
    getExpansionCard(id) {
      let ex = expansionsMap[id];
      ex.classes = {
        back: true,
        "exp-pack": true,
      };
      if (ex.status) ex.classes[ex.status] = true;
      ex.classes[ex.expansion] = true;
      return ex;
    },
    is_toggled_expansion(ex) {
      if (Vue.config.devtools)
        console.log(
          ex + " " + this.expansions + (this.expansions.indexOf(ex) !== -1)
        );
      return this.expansions.indexOf(ex) !== -1;
    },
    replayPlayer(player) {
      this.$socket.emit("chat_message", `/replaypov ${player}`);
    },
    leaveRoom() {
      window.location.replace(window.location.origin);
      document.title = "PewPew!";
    },
    toggleExpansions(name) {
      if (!this.isRoomOwner) return this.$socket.emit("toggle_expansion", `suggest;${name}`);
      this.$socket.emit("toggle_expansion", name);
    },
    toggleCompetitive() {
      if (!this.isRoomOwner) return;
      this.$socket.emit("toggle_comp");
    },
    toggleReplaceWithBot() {
      if (!this.isRoomOwner) return;
      this.$socket.emit("toggle_replace_with_bot");
    },
    getActionEmoji(p) {
      if (p.is_my_turn === undefined || p.pending_action === undefined)
        return "";
      if (p.pending_action != 4) {
        return ["↙️", "⏬", "▶️", "↩️", "4", "🔽"][p.pending_action];
      } else if (p.is_my_turn) {
        return "⏸";
      } else {
        return "";
      }
    },
    getPlayerCard(player) {
      let icon = "";
      let nonBots = this.players.filter((x) => !x.is_bot);
      let isOwner = nonBots.length > 0 && nonBots[0].name == player.name;
      let isMe = this.username == player.name;
      if (!this.started) icon = "🤠";
      else
        icon =
          player.ready !== undefined
            ? player.ready
              ? "👍"
              : "🤔"
            : player.is_sheriff
            ? "⭐"
            : player.icon;
      return {
        name: player.name,
        number:
          (isMe
            ? this.$t("you")
            : isOwner
            ? this.$t("owner")
            : "") + (player.dist ? `${player.dist}⛰` : ""),
        isMe: isMe,
        icon: icon,
        is_character: true,
        avatar: player.avatar,
        is_player: true,
      };
    },
    startGame() {
      this.started = true;
      this.$socket.emit("start_game");
    },
    shufflePlayers() {
      this.$socket.emit("shuffle_players");
    },
    choose(player_name) {
      if (Vue.config.devtools) console.log("choose from" + player_name);
      this.target_p = player_name;
      let pl = this.players.filter((x) => x.name === player_name)[0];
      if (Vue.config.devtools) console.log(pl);
      let arr = [];
      if (this.username != player_name)
        for (let i = 0; i < pl.ncards; i++)
          arr.push({
            name: "PewPew!",
            icon: "💥",
            is_back: true,
          });
      pl.equipment.forEach((x) => arr.push(x));
      this.chooseCards = arr;
      this.hasToChoose = true;
    },
    chooseCard(card) {
      let index = this.chooseCards.indexOf(card);
      if (!this.debug_mode) {
        let pl = this.players.filter((x) => x.name === this.target_p)[0];
        if (index < pl.ncards) {
          index = Math.floor(Math.random() * pl.ncards);
        }
      }
      this.$socket.emit("choose", index);
      if (Vue.config.devtools) console.log(card + " " + index);
      this.chooseCards = [];
      this.hasToChoose = false;
      this.target_p = "";
    },
    drawFromPlayer(name) {
      if (Vue.config.devtools) console.log(name);
      this.$socket.emit("draw", name);
    },
    setUsername(name) {
      if (name.trim().length > 0) {
        localStorage.setItem("username", name);
        this.hasToSetUsername = false;
        this.$socket.emit("set_username", { name: name });
      }
    },
  },
  watch: {
    privateRoom(old, _new) {
      if (this.isRoomOwner && old !== _new) this.$socket.emit("private");
    },
    players(_, _new) {
      let x = _new.findIndex((x) => x.is_my_turn);
      if (x !== -1 && x !== this.turn) {
        this.turnReversed = x + 1 === this.turn;
        this.showTurnFlow = true;
        setTimeout(() => {
          this.showTurnFlow = false;
        }, 1000);
        this.turn = x;
      }
    },
  },
  mounted() {
    if (Vue.config.devtools) console.log("mounted lobby");
    if (!this.$route.query.code && !this.$route.query.replay)
      return this.$router.push("/");
    this.$socket.emit("get_me", {
      name: this.$route.query.code,
      password: this.$route.query.pwd,
      username: localStorage.getItem("username"),
      discord_token: localStorage.getItem("discord_token"),
      replay: this.$route.query.replay,
      ffw: this.$route.query.ffw,
    });
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style >
.is_my_turn {
  box-shadow: 0 0 0 3pt rgb(138, 12, 12), 0 0 0 6pt var(--bg-color),
    0 0 5pt 6pt #aaa !important;
  animation-name: turn-animation;
  animation-duration: 2s;
  animation-iteration-count: infinite;
}

@keyframes turn-animation {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.02);
  }
  100% {
    transform: scale(1);
  }
}
.tiny-equipment {
  position: absolute;
  display: flex;
  flex-direction: column;
  right: -35pt;
  transform: scale(0.45);
  transform-origin: 50% 0%;
  top: 4pt;
}
.tiny-health {
  display: flex;
  justify-content: space-evenly;
  transform: scale(0.8);
  margin-top: -16pt;
  position: absolute;
  z-index: 1;
  top: 0;
  left: 0;
  right: 0;
}
.tiny-equipment .card {
  transform: rotate(2deg);
}
.tiny-equipment .card:nth-child(odd) {
  transform: rotate(-2deg);
}
.tiny-equipment .card:hover {
  transform: translateY(10px) scale(1.2);
  z-index: 1;
}
.tiny-character {
  position: absolute;
  transform: translate(-30pt, -30pt) scale(0.5);
  top: 0;
}
.players-table {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-evenly;
  margin-bottom: 12pt;
}
.small-btn {
  min-width: 28pt;
}
.small-btn.active {
  color: var(--bg-color);
  background: var(--font-color);
}
#admin-status {
  position: absolute;
  width: 100%;
  height: 100%;
  overflow: auto;
  background: var(--bg-color);
  opacity: 0.8;
}
#turn-indicator {
  position: absolute;
  width: 100%;
  height: 100%;
  background-image: linear-gradient(135deg, #cbcbcb33 25%, transparent 25%),
    linear-gradient(45deg, #cbcbcb33 25%, transparent 25%);
  background-size: 80px 200px;
  background-position: 0 100px;
  background-position-x: 0;
  opacity: 0;
  background-repeat: repeat;
  animation-name: next-turn-animation;
  animation-duration: 1s;
  animation-iteration-count: 3;
  animation-timing-function: linear;
}
#turn-indicator.reversed {
  background-image: linear-gradient(225deg, #cbcbcb33 25%, transparent 25%),
    linear-gradient(315deg, #cbcbcb33 25%, transparent 25%);
}

@keyframes next-turn-animation {
  0% {
    background-position-x: 0;
    opacity: 1;
  }
  50% {
    background-position-x: 80px;
  }
  100% {
    opacity: 0;
    background-position-x: 160px;
  }
}
.lobby {
  display: flex;
  flex-direction: column;
}
@media only screen and (min-width: 1000px) {
  .lobby {
    flex-direction: row;
  }
  .chat {
    min-width: 25vw;
    max-width: 25vw;
  }
  .player-in-table {
    transition: all 0.2s ease-in-out;
    margin-top: 26pt;
  }
  .player-in-table:hover {
    transform: translateY(-5px) scale(1.05);
  }
}
@media only screen and (max-width: 500pt) {
  .players-table {
    border-bottom: dashed #ccc2;
  }
}
</style>
