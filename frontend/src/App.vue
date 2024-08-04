<script setup lang="ts">
import { createSQLiteHTTPPool } from 'sqlite-wasm-http';
import { Ref, ref } from 'vue';
// https://fuzzy-pancake-97q4x4pxgv6hxp59-5173.app.github.dev/node_modules/sqlite-wasm-http/dist/sqlite-worker.js?worker_file&type=classic

let services: Ref<string[]> = ref([])
let locations: Ref<string[]> = ref([])
console.log("start")
setTimeout(async () => {
  try {
    const remoteURL = '/test_new.sqlite';
    const pool = await createSQLiteHTTPPool({ workers: 4 });
    await pool.open(remoteURL);

    const servicesResult = await pool.exec('SELECT id, name  FROM azure_services');
    services.value = servicesResult.map(r => r.row[1] as string)

    const locationsResult = await pool.exec('SELECT id, name  FROM azure_locations');
    locations.value = locationsResult.map(r => r.row[1] as string)



    // await pool.close();
  } catch(e){
    console.log(e)
  }
}, 0);

const selectService = ref('')
const selectLocation = ref('')

</script>

<template>
  <div>
    <h1>
      Hi!
    </h1>
    <div>Selected: {{ selectService }}</div>

    <select v-model="selectService">
      <option disabled value="">Please select one</option>
      <option v-for="item in services">{{ item }}</option>
    </select>

    <div>Selected: {{ selectLocation }}</div>

    <select v-model="selectLocation">
      <option disabled value="">Please select one</option>
      <option v-for="item in locations">{{ item }}</option>
    </select>
  </div>
</template>

<style scoped>

</style>
