<script setup lang="ts">
import {onMounted, ref } from "vue";
import axios from 'axios';


const dataUrl = "https://fuck-off-abc63-default-rtdb.firebaseio.com/sensor_readings.json?orderBy=\"id\"&limitToLast=1"
const stateUrl = "https://fuck-off-abc63-default-rtdb.firebaseio.com/rpi_state.json"
const rpiData = ref({
  id:null,
  temp:null,
  humidity:null,
  door_open:null,
  alarm_on:null,
  in_test_mode:null
})


const stateValues = ref({
  state_test_mode:false,
  state_alarm:false,
  state_door:false,
  state_temp:0
})


onMounted(async () => {
await getData()
});

onMounted(() => {
  setInterval(() => {
    getData();
  }, 5000);
});


async function getData() {
  await fetch(dataUrl)
  .then((response) => response.json())
  .then((response) => Object.values(response)[0])
  // .then((response) => console.log("ttt", response['alarm_on']))
  .then((data) => (rpiData.value = data));
  // alarm.value = rpiData.value["alarm_on"]
  if (!stateValues.value.state_test_mode) {
    stateValues.value.state_alarm = rpiData.value["alarm_on"] == 1
    stateValues.value.state_door = rpiData.value["door_open"] ==1
    stateValues.value.state_temp = rpiData.value["temp"]
  console.log("update data")

  }

}

async function updateState() {
  await axios.put(stateUrl, stateValues.value);
}
</script>

<template>

    <div class="viewing-data" v-if="stateValues.state_test_mode==false">
      <h1>normal mode</h1>
        <div>
        <label for="test-mode">alarm state</label>
          <br>
        <select disabled :value="rpiData['alarm_on']">
          <!-- <option :value=null>auto</option> -->
          <option :value=1>true</option>
          <option :value=0>false</option>
        </select>
        </div>

        <div>
        <label for="test-mode">in test mode</label>
          <br>
        <select :value="rpiData['in_test_mode']" disabled>
          <!-- <option :value=null>auto</option> -->
          <option :value=1>true</option>
          <option :value=0>false</option>
        </select>
        </div>

        <div>
        <label for="test-mode">door state</label>
          <br>
        <select :value="rpiData['door_open']" disabled>
          <!-- <option :value=null>auto</option> -->
          <option :value=1>open</option>
          <option :value=0>closed</option>
        </select>
        </div>

        <div>
        <label for="test-mode">humidity</label>
          <br>
        <input type="number" v-model="rpiData['humidity']" disabled>
        </div>

        <div>
        <label for="test-mode">temperature</label>
          <br>
        <input type="number" v-model="rpiData['temp']" disabled>
        </div>

        <!-- <div>
        <label for="test-mode">test mode</label>
        <input type="checkbox" :selected="stateValues.state_test_mode == 0" name="test-mode">
        </div> -->
        <br>
        <div>
        <button @click="stateValues.state_test_mode = !stateValues.state_test_mode; updateState()">test mode: {{stateValues.state_test_mode}}</button>
      </div>
      </div>


    <div class="viewing-data" v-else>
      <h1>test mode</h1>

        <div>
        <label for="test-mode">alarm state</label>
          <br>
        <select @change="updateState()" v-model="stateValues.state_alarm">
          <option :value=null>auto</option>
          <option :value=true>on</option>
          <option :value=false>off</option>
        </select>
        </div>


        <div>
        <label for="test-mode">door state</label>
          <br>
        <select @change="updateState()" v-model="stateValues.state_door">
          <option :value=null>auto</option>
          <option :value=true>open</option>
          <option :value=false>closed</option>
        </select>
        </div>

        <div>
        <label for="test-mode">humidity</label>
          <br>
        <input disabled type="number" v-model="rpiData['humidity']">
        </div>
        <div>
        <label for="test-mode">temperature</label>
          <br>
        <input type="number" @change="updateState()" v-model="stateValues.state_temp">
        </div>

<br>

        <!-- <button @click="updateState()" > apply</button> -->
<div>
        <button @click="stateValues.state_test_mode = !stateValues.state_test_mode; updateState()">test mode: {{stateValues.state_test_mode}}</button>
      </div>

    </div>

      <!-- <div>
        <button @click="stateValues.state_test_mode = !stateValues.state_test_mode; updateState()">test mode: {{stateValues.state_test_mode}}</button>
      </div> -->




</template>


<!-- <style scoped>
.form-grid{
  color:white
}
header {
  line-height: 1.5;
  max-height: 100vh;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

nav {
  width: 100%;
  font-size: 12px;
  text-align: center;
  margin-top: 2rem;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }

  nav {
    text-align: left;
    margin-left: -1rem;
    font-size: 1rem;

    padding: 1rem 0;
    margin-top: 1rem;
  }
}
</style> -->
