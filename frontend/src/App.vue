<script setup lang="ts">
import { createSQLiteHTTPPool } from 'sqlite-wasm-http';
// https://fuzzy-pancake-97q4x4pxgv6hxp59-5173.app.github.dev/node_modules/sqlite-wasm-http/dist/sqlite-worker.js?worker_file&type=classic

console.log("start")
setTimeout(async () => {
  try {
    const remoteURL = 
      '/test.sqlite';
  
    const pool = await createSQLiteHTTPPool({ workers: 8 });
    await pool.open(remoteURL);
    // This will automatically use a free thread from the pool
    const queryResult = await pool.exec('SELECT serviceName FROM prices_azure');
    console.log(queryResult[0].row);
    // This shutdowns the pool
    await pool.close();
  } catch(e){
    console.log(e)
  }
}, 0);

</script>

<template>
  <div>
    <h1>
      Hi!
    </h1>
  </div>
</template>

<style scoped>

</style>
