<script setup>
import { useDataStore } from '../DataStore';
import { onMounted, ref } from 'vue';
import { Button } from 'primevue';
import ConceptListItem from '../components/ConceptListItem.vue';

import * as CDEHelper from '../CDEHelper';
import { Jimin } from '../Jimin';
onMounted(() => {
    console.log('* mounted grandReviewView');
});

const store = useDataStore();

function countReviewedConcept(concept) {
    if (concept == null) {
        return 0;
    }

    let count = 0;

    const concept_id = concept.concept_id;

    store.grand_review_data.forEach(review => {
        review.mappings.forEach(mapping => {
            if (mapping.concept_id == concept_id) {
                count++;
            }
        });
    });

    return count;
}
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
                    <div class="flex">
                        <div class="flex-col">
                            <div class="text-lg font-bold">
                                <i class="fa-solid fa-cubes"></i>
                                CDE Mappings result list
                                <span v-if="store.working_concept">
                                    for 
                                    <i>{{ store.working_concept?.term }}</i>
                                </span>
                            </div>
                            <div class="panel-subtitle text-sm">
                                <template v-if="countReviewedConcept(store.working_concept) > 0">
                                    <b>{{ countReviewedConcept(store.working_concept)}}</b>
                                    reviewed results for this concept
                                </template>
                                <template v-else>
                                    &nbsp;
                                </template>
                            </div>
                        </div>
                    </div>
                </div>
            </template>
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
</style>