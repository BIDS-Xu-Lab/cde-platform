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
                v-tooltip.right="'Add a new member to your team.'"
                @click="onClickSave">
                <i class="fa-solid fa-user-plus menu-icon"></i>
                <span>
                    Add Member
                </span>
            </Button>
            <Button text
                class="menu-button"
                v-tooltip.bottom="'Update member list.'"
                @click="onClickSave">
                <i class="fa-solid fa-users menu-icon"></i>
                <span>
                    Update List
                </span>
            </Button>
        </div>
        <div class="menu-group-title">
            Team
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

<Panel class="h-full team-panel">
    <template #header>
        <div class="w-full flex justify-between">
            <div class="flex">
                <div class="flex-col">
                    <div class="text-lg font-bold">
                        <i class="fa-solid fa-users"></i>
                        Team Members
                    </div>
                    <div class="panel-subtitle text-sm">
                    </div>
                </div>
            </div>
            <div>

            </div>
        </div>
    </template>
</Panel>
</div>


</template>

<style scoped>
.team-panel {
    width: 400px;
}
</style>