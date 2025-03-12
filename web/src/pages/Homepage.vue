<script setup>
import { RouterLink, useRouter } from 'vue-router';
const router = useRouter();

</script>

<template>
<div id="homepage">
    <div style="font-size: 4rem;">
        <i class="fa fa-edit"></i>
        CDEMapper 2.0
    </div>
    <div style="font-size: 1rem; font-style: italic;">
        Create, share, and visualize Common Data Elements (CDEs) in a collaborative environment
    </div>

    <div class="py-3">
        <Button class="p-button-primary" @click="router.push('/main')">
            <font-awesome-icon icon="fa-solid fa-arrow-right" class="mr-2" />
            Get Started!
        </Button>
    </div>
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