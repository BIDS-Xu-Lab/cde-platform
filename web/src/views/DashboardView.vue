<script setup>
import { useDataStore } from '../DataStore';
const store = useDataStore();

function onClickNewFile() {
    console.log('* clicked New file ');
}

</script>

<template>
<div class="menu">
    <div class="menu-group">
        <div class="menu-group-box">
            <Button text
                class="menu-button"
                v-tooltip.right="'Import a new data file.'"
                @click="onClickNewFile">
                <i class="fa-regular fa-file menu-icon"></i>
                <span>
                    New File
                </span>
            </Button>
        </div>
        <div class="menu-group-title">
            Data Files
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