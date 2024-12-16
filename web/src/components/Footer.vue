<script setup>
import { useDataStore } from "../DataStore";
import { onMounted, ref } from "vue";
const store = useDataStore();

onMounted(() => {
    console.log('* mounted Footer');
});
</script>

<template>
<div class="footer">
<div class="footer-left">
    <i class="fa fa-edit"></i>
    CDE Reviewer

    {{ store.version }}
</div>

<div class="footer-right">
    <div>
        <i class="fa-brands fa-github"></i>
    </div>
</div>
</div>


</template>