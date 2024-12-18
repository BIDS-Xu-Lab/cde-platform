export const hasResults = function(term) {
    return term.results && term.results.length > 0;
}

export const convertConceptToQueryByFile = function(concept, definition) {
    // get the column of the term
    let col_term = definition.term;
    let col_description = definition.description;
    let col_value = definition.value;

    return {
        concept_id: concept.concept_id,
        term: concept[col_term],
        description: concept[col_description],
        value: concept[col_value]
    }
}