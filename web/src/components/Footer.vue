<script setup>
import { useDataStore } from "../DataStore";
import { onMounted, ref } from "vue";
const store = useDataStore();

const now = ref(new Date().toLocaleString());

onMounted(() => {
    console.log('NaviMenu mounted');

    // update now every second
    setInterval(() => {
        now.value = new Date().toLocaleString();
    }, 1000);
});
</script>

<template>
<div class="footer">
<div class="footer-left">
    <i class="fa fa-edit"></i>
    CDE Manager

    {{ store.version }}
</div>

<div class="footer-right">
    <div>
        {{ now }}
    </div>
</div>
</div>


</template>