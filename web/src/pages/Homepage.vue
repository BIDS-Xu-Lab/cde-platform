<script setup>
import { RouterLink } from 'vue-router';
</script>

<template>
<div id="homepage">
    <div style="font-size: 4rem;">
        CDE 2.0
    </div>
    <div style="font-size: 1rem; font-style: italic;">
        Create, share, and visualize Common Data Elements (CDEs) in a collaborative environment!
    </div>
<RouterLink to="/main">
    Get Started!
</RouterLink>
</div>
</template>

<style scoped>
#homepage {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100vh;
    font-size: 20px;
    font-weight: bold;
}
</style>