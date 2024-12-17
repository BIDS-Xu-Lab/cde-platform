<!-- <script setup>
import { useDataStore } from "../DataStore";
import { onMounted, ref } from "vue";

const store = useDataStore();

onMounted(() => {
    console.log('* mounted Add File');
});
</script>

<template>
    <div class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
        <div class="bg-surface-50 dark:bg-surface-950 p-10 rounded-lg shadow-lg">
            <div class="bg-surface-0 dark:bg-surface-900 p-6 shadow rounded-border">
                <div class="text-3xl font-medium text-surface-900 dark:text-surface-0 mb-2">Add File</div>
                <div class="projec-selection">
                    <Select v-model="store.mapping.selected_sources" 
                                    :options="store.mapping.sources" 
                                    variant="in"
                                    filter 
                                    optionLabel="name" 
                                    placeholder="Select a data source" 
                                    class="select-sources">
                        <template #header>
                            <div class="font-bold px-3">Available Collections</div>
                        </template>
                    </Select>
                </div>

                <div class="h-[150px] border-2 border-dashed border-surface" />
            </div>
        </div>
    </div>
</template> -->
<script setup>
import { useDataStore } from "../DataStore";
import { onMounted, ref } from "vue";

const store = useDataStore();
const showModal = ref(true);

onMounted(() => {
    console.log('* mounted Add File');
});

const closeModal = () => {
    showModal.value = false;
};

const handleClickOutside = (event) => {
    if (!event.target.closest('.modal-content')) {
        closeModal();
    }
};

onMounted(() => {
    document.addEventListener('click', handleClickOutside);
});

</script>

<template>
    <div class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
        <div class="bg-surface-50 dark:bg-surface-950 p-10 rounded-lg shadow-lg modal-content">
            <div class="bg-surface-0 dark:bg-surface-900 p-6 shadow rounded-border">
                <div class="text-3xl font-medium text-surface-900 dark:text-surface-0 mb-2">Add File</div>
                <div class="projec-selection">
                    <Select v-model="store.mapping.selected_sources" 
                                    :options="store.mapping.sources" 
                                    variant="in"
                                    filter 
                                    optionLabel="name" 
                                    placeholder="Select a data source" 
                                    class="select-sources">
                        <template #header>
                            <div class="font-bold px-3">Available Collections</div>
                        </template>
                    </Select>
                </div>

                <div class="h-[150px] border-2 border-dashed border-surface" />
            </div>
        </div>
    </div>
</template>