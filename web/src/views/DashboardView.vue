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
                @click="onClickRefreshList">
                <i class="fa-solid fa-rotate menu-icon"></i>
                <span>
                    Refresh
                </span>
            </Button>
        </div>
        <div class="menu-group-title">
            Data
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


<div class="main flex-row">


</div>

</template>

<style scoped>
</style>