<script setup>
import { useDataStore } from '../DataStore';
import { onMounted, ref } from 'vue';
onMounted(() => {
    console.log('* mounted GrantReviewView');
});

</script>

<template>
<div class="menu">
    <div class="menu-group">
        <div class="menu-group-box">
            <Button text
                class="menu-button"
                >
                <font-awesome-icon icon="fa-solid fa-rotate" class="menu-icon" />
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
                >
                <font-awesome-icon icon="fa-solid fa-book" class="menu-icon" />
                <span>
                    How-to Guide
                </span>
            </Button>
        </div>
        <div class="menu-group-title">
            Help
        </div>
    </div>
    <div class="main flex-row">
    <!-- concept list -->
     <ConceptListItem :view_mode="'grant_review'"/>
    </div>

</div>
</template>

<style>

</style>