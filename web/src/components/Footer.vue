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
    <font-awesome-icon :icon="['fa', 'edit']" />
    CDE Reviewer

    {{ store.version }}
</div>

<div class="footer-right flex flex-row items-center">
    <div>
    </div>
    <div>
        <font-awesome-icon :icon="['fab', 'github']" />
        GitHub
    </div>
</div>
</div>


</template>