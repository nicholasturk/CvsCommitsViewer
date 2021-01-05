<template>
  <div class="container mt-4">
    <div id="app">
      <router-view :key="$route.path"></router-view>
    </div>
  </div>
</template>

<script>

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

export default {
   name: "App"
};
</script>

<style>

</style>
