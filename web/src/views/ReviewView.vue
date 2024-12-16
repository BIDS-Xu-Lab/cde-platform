<script setup>
import { useDataStore } from '../DataStore';
const store = useDataStore();

function onClickSave() {
    console.log('* clicked Save');
}
</script>

<template>
<div class="menu">
    <div class="menu-group">
        <div class="menu-group-box">
            <Button text
                class="menu-button"
                v-tooltip.right="'Create a new project.'"
                @click="onClickSave">
                <i class="fa-regular fa-save menu-icon"></i>
                <span>
                    Load All Mappings
                </span>
            </Button>
        </div>
        <div class="menu-group-title">
            Mappings
        </div>
    </div>

    <div class="menu-group">
        <div class="menu-group-box">
            <Button text
                class="menu-button"
                v-tooltip.bottom="'Show the user manual in a new window.'"
                @click="store.showGuide()">
                <i class="fa-solid fa-book menu-icon"></i>
                <span>
                    How-to Guide
                </span>
            </Button>
        </div>
        <div class="menu-group-title">
            Help
        </div>
    </div>

</div>
<div class="main">

</div>

</template>

<style scoped>
</style>