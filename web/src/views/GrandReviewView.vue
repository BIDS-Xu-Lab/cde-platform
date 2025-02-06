<script setup>
import { useDataStore } from '../DataStore';
import { onMounted, ref, computed } from 'vue';
import { Button } from 'primevue';
import ConceptListItem from '../components/ConceptListItem.vue';
import grandReviewResultItem from '../components/grandReviewResultItem.vue';

import * as CDEHelper from '../CDEHelper';
import { Jimin } from '../Jimin';
onMounted(() => {
    console.log('* mounted grandReviewView');
    if (!store.working_mappings) {
        CDEHelper.getGrandReviewData();
    }
});

const store = useDataStore();

const checked = ref(true);

const filteredGrandReviewData = computed(() => {
    if (!store.working_concept) return [];
    console.log('store.grand_review_data:', store.grand_review_data.filter(item => item.concept_id === store.working_concept.concept_id)[0]);
    return store.grand_review_data.filter(item => item.concept_id === store.working_concept.concept_id)[0];
});

const popover_suggestions = ref(null);
const togglePopoverSuggestions = (event) => {
    popover_suggestions.value.toggle(event);
};
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
     <ConceptListItem :view_mode="'grand_review'"/>
     <div class="flex flex-col w-full h-full result-list">
        <Panel class="w-full">
            <template #header>
                <div class="w-full flex justify-between items-center">
                    <div class="flex-col">
                        <div class="text-lg font-bold">
                            <i class="fa-solid fa-cubes"></i>
                            CDE Mappings result list
                            <span v-if="store.working_concept">
                                for 
                                <i>{{ store.working_concept?.term }}</i>
                            </span>
                        </div>
                    </div>
                    <div class="flex justify-end item-center mr-2" v-if="store.working_concept">
                        <span style="font-size: 1.2em; font-weight: bold;">Number of CDE suggestion: {{ filteredGrandReviewData.suggest_cde.length }}</span>
                        <Button 
                            severity="secondary"
                            :disabled="filteredGrandReviewData.suggest_cde.length == 0"
                            size="small"
                            class="ml-2"
                            v-tooltip.bottom="'View suggestions details.'"
                            @click="togglePopoverSuggestions">
                            <font-awesome-icon :icon="['fa', 'list']" />
                           Details
                        </Button>
                        <Popover ref="popover_suggestions">
                            <div class="flex flex-col gap-4 w-[20rem]">
                                <div style="border-bottom: 1px solid var(--bd-color)">
                                    <span class="font-bold">Reviewer List:</span>
                                </div>
                                <li v-for="item in filteredGrandReviewData.suggest_cde" class="flex items-center gap-2 px-2 py-3 rounded-border">
                                    <div>
                                        <span class="text-xl font-bold">Name: {{ item.name}}</span>
                                        <div class="text-sm text-surface-500 dark:text-surface-400">Email: {{ item.email }}</div>
                                    </div>
                                </li>
                            </div>
                        </Popover>
                        <ToggleButton 
                        v-model="checked"
                        :disabled="filteredGrandReviewData.suggest_cde.length == 0"
                        class="ml-2" 
                        onLabel="Accpet" 
                        offLabel="Deaccept" />
                    </div>
                </div>
            </template>
            <div class="result-list-scroller"
                :style="{ height: 'calc(100vh - 19rem)' }">

                <!-- selected list -->
                <template v-if="filteredGrandReviewData.selected_results?.length > 0">
                <div class="selected-results-section">

                    <div class="text-lg font-bold mb-4">
                        <i class="fa-solid fa-magnifying-glass"></i>
                    Reviewed Results
                        ({{ filteredGrandReviewData.selected_results.length }})
                    </div>
                    
                    <template v-for="item, item_idx in filteredGrandReviewData.selected_results">
                        <grandReviewResultItem :item="item" 
                            :item_idx="item_idx" 
                            />
                    </template>

                </div>
                </template>
            </div>
        </Panel>
    </div>
                
    </div>

</div>
</template>

<style scoped>
.result-list {
    width: calc(100% - 500px);
}
.select-sources {
    width: 10rem;
}
.result-list-scroller {
    width: calc(100% + 1rem);
    overflow-y: auto;
}
</style>