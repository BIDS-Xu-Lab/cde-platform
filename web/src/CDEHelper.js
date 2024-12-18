export const hasResults = function(term) {
    return term.results && term.results.length > 0;
}

export const hasSelectedResult = function(term) {
    return term.activeIndex >= 0;
}

export const getSelectedResult = function(term) {
    if (!term.results || term.activeIndex < 0) {
        return null;
    }
    return term.results[term.activeIndex];
}

export const makeSampleData = function() {
    const concepts = [];
    for (let i = 0; i < 25; i++) {
        let concept = {
            "_id": "675cee40077e19647d1e9c02" + i,
            "element": "Hospital transport type " + i,
            "description": "Type of transport to hospital from home/scene " + i + " (e.g. Mobile Stroke Unit, EMS, private transportation, unknown, other) and other details",
            "values": "Mobile Stroke Unit |  EMS from home/scene |  Private transportation/taxi/other from home/scene |  Unknown |  Other, specify",
            "user_id": "kp_c541b01bc33e4c5d8f4a2f70184f993a",
            "file_id": "7ee9f754-d2fe-4439-84e1-34a56755fbc8",
            "id": i,
            "mappedValues": {},
            "term": "Hospital transport type",
            "activeIndex": i % 5 - 1,
            "results": []
        }

        // add some results
        for (let j=0; j<10; j++) {
            concept['results'].push({
                "score": 125.087036 - j,
                "conceptId": "z3jbnCdyaqE" + j,
                "conceptCode": "z3jbnCdyaqE" + j,
                "conceptSource": "NINDS",
                "standardConcept": "Hospital transport type " + i + '-' + j,
                "description": "Type of transportation from injury scene to hospital" + i + '-' + j,
                "valueDomain": {
                    "identifiers": [],
                    "ids": [],
                    "datatype": "Value List",
                    "permissibleValues": [
                        {
                            "permissibleValue": "Ground ambulance with physician",
                            "valueMeaningName": "Ground ambulance with physician",
                            "valueMeaningDefinition": "Ground ambulance with physician"
                        },
                    ]
                },
                "index": j
            })
        }

        if (concept.activeIndex < 0) {
            // set some to empty
            concept['results'] = [];
        }

        concepts.push(concept);
    }
    return concepts;
}

export const convertConceptToQueryByFile = function(concept, definition) {
    // get the column of the term
    let col_term = definition.term;
    let col_description = definition.description;
    let col_value = definition.value;

    return {
        term: concept[col_term],
        description: concept[col_description],
        value: concept[col_value]
    }
}