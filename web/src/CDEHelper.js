export const hasResults = function(term) {
    return term.results && term.results.length > 0;
}

export async function onClickRefreshListGetSources() {
    console.log('* clicked Refresh List');

    // load source data
    let sources = await Jimin.getSources();

    store.msg('Loaded ' + sources.length + ' sources.');

    // update store
    store.mapping.sources = sources.map((item) => {
        return {
            name: item,
            code: item
        };
    });
}

export function checkSubmitAndFinalStatus(){
    if (store.working_concept?.final) {
        return true;
    }
    for (const mapping of Object.values(store.working_mappings)) {
        if (mapping.status === "mapped" || mapping.status === "reviewed") {
            return true;
        }
    }
    return false;
}