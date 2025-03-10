const positivePromptElem = document.querySelector("#positive-prompt textarea");
const negativePromptElem = document.querySelector("#negative-prompt textarea");

positivePromptElem.addEventListener("keydown", function(e) {
    // if (e.ctrlKey & e.shiftKey) {
    if ((e.ctrlKey & e.shiftKey)) {
        switch (e.key) {
            case "ArrowLeft":
                moveTagLeft(positivePromptElem); 
                break;
            case "ArrowRight":
                moveTagRight(positivePromptElem); 
                break;
            case "ArrowUp":
                changeWeight(positivePromptElem, "up"); 
                break;
            case "ArrowDown":
                changeWeight(positivePromptElem, "down"); 
                break;
        }
        e.preventDefault();
    }
});

negativePromptElem.addEventListener("keydown", function(e) {
    // if (e.ctrlKey & e.shiftKey) {
    if ((e.ctrlKey & e.shiftKey)) {
        switch (e.key) {
            case "ArrowLeft":
                moveTagLeft(negativePromptElem); 
                break;
            case "ArrowRight":
                moveTagRight(negativePromptElem); 
                break;
            case "ArrowUp":
                changeWeight(negativePromptElem, "up"); 
                break;
            case "ArrowDown":
                changeWeight(negativePromptElem, "down"); 
                break;
        }
        e.preventDefault();
    }
});





function moveTagLeft(promptElem) {
    let selectionStart = promptElem.selectionStart;

    if (selectionStart >=0) {
        let tagList = promptElem.value.split(",");

        /* Check if less than 3 tags */
        if (tagList.length < 3) {
            if (tagList.length == 2) {
                let selectedTagSide = promptElem.value.slice(selectionStart).indexOf(",") == -1 ? "right" : "left"
                
                let selectedTagString = tagList[0].trim();
                let secondaryTagString = tagList[1].trim();
                
                if (selectedTagSide == "right") {
                    selectedTagString = tagList[1].trim();
                    secondaryTagString = tagList[0].trim();
                }

                let newString = selectedTagString + ", " + secondaryTagString;

                let newSelectedTagStartIndex = newString.indexOf(selectedTagString);
                let newSelectedTagEndIndex = newSelectedTagStartIndex + selectedTagString.length;
                
                promptElem.value = newString;
                promptElem.setSelectionRange(newSelectedTagStartIndex, newSelectedTagEndIndex);
            } else {
                promptElem.setSelectionRange(0, promptElem.value.length)
            }
        }
        /* Check if selected tag is the LEFTMOST tag */
        else if (promptElem.value.slice(0, selectionStart).indexOf(",") == -1) {
            // No need to do anything
            // console.log("No movement needed")
            promptElem.setSelectionRange(0, promptElem.value.indexOf(","));
            return;
        }

        /* Check if selected tag is immediately to the RIGHT of the LEFTMOST tag */
        else if ( (promptElem.value.slice(0, selectionStart).split(",").length - 1) == 1 ) {
            let endIndex = promptElem.value.indexOf(",", selectionStart) - 1;
            let startIndex = promptElem.value.slice(0, endIndex + 1).lastIndexOf(",") + 1;
            let primaryTagString = promptElem.value.slice(startIndex, endIndex + 1).trim()
            
            let leftTagString = promptElem.value.slice(0, startIndex - 1).trim()

            let untouchedRightSide = promptElem.value.slice(endIndex + 2).trim()
            
            let newString = primaryTagString + ", " + leftTagString + ", " + untouchedRightSide;
            
            let newPrimaryTagStartIndex = newString.indexOf(primaryTagString);
            let newPrimaryTagEndIndex = newPrimaryTagStartIndex + primaryTagString.length;
            
            promptElem.value = newString;
    
            promptElem.setSelectionRange(newPrimaryTagStartIndex, newPrimaryTagEndIndex);

        } 

        /* Check if selected tag is the RIGHTMOST tag */
        else if (promptElem.value.slice(selectionStart).indexOf(",") == -1 ) {
            let endIndex = promptElem.value.length - 1;
            let startIndex = promptElem.value.lastIndexOf(",") + 1;
            let primaryTagString = promptElem.value.slice(startIndex);

            let leftTagStartIndex = promptElem.value.slice(0, startIndex - 1).lastIndexOf(",") + 1;
            let leftTagString = promptElem.value.slice(leftTagStartIndex, startIndex - 1).trim();

            let untouchedLeftSide = promptElem.value.slice(0, leftTagStartIndex - 1).trim();
            
            let newString = untouchedLeftSide + ", " + primaryTagString + ", " + leftTagString;

            let newPrimaryTagStartIndex = newString.indexOf(primaryTagString);
            let newPrimaryTagEndIndex = newPrimaryTagStartIndex + primaryTagString.length;
            
            promptElem.value = newString;
    
            promptElem.setSelectionRange(newPrimaryTagStartIndex, newPrimaryTagEndIndex);
        }
        else {
            let endIndex = promptElem.value.indexOf(",", selectionStart) - 1;
            let startIndex = promptElem.value.slice(0, endIndex + 1).lastIndexOf(",") + 1;
            let primaryTagString = promptElem.value.slice(startIndex, endIndex + 1).trim();
            
            let leftTagStartIndex = promptElem.value.slice(0, startIndex - 1).lastIndexOf(",") + 1;
            let leftTagString = promptElem.value.slice(leftTagStartIndex, startIndex - 1).trim();
    
            let untouchedLeftSide = promptElem.value.slice(0, leftTagStartIndex - 1).trim();
            let untouchedRightSide = promptElem.value.slice(endIndex + 2).trim();
    
            let newString = untouchedLeftSide + ", " + primaryTagString + ", " + leftTagString + ", " + untouchedRightSide;
            
            let newPrimaryTagStartIndex = newString.indexOf(primaryTagString);
            let newPrimaryTagEndIndex = newPrimaryTagStartIndex + primaryTagString.length;
            
            promptElem.value = newString;
    
            promptElem.setSelectionRange(newPrimaryTagStartIndex, newPrimaryTagEndIndex);
        }

    }
}

function moveTagRight(promptElem) {
    let selectionStart = promptElem.selectionStart;

    if (selectionStart >= 0) {
        let tagList = promptElem.value.split(",")
        /* Check if less than 3 tags */
        if (tagList.length < 3) {
            if (tagList.length == 2) {
                let primaryTagSide = promptElem.value.slice(selectionStart).indexOf(",") == -1 ? "right" : "left"
                
                let primaryTagString = tagList[0].trim();
                let secondaryTagString = tagList[1].trim();
                
                if (primaryTagSide == "right") {
                    primaryTagString = tagList[1].trim();
                    secondaryTagString = tagList[0].trim();
                }

                let newString = secondaryTagString + ", " + primaryTagString;

                let newPrimaryTagStartIndex = newString.indexOf(primaryTagString);
                let newPrimaryTagEndIndex = newPrimaryTagStartIndex + primaryTagString.length;
                
                promptElem.value = newString;
                promptElem.setSelectionRange(newPrimaryTagStartIndex, newPrimaryTagEndIndex);
            } else {
                promptElem.setSelectionRange(0, promptElem.value.length)
            }
        }
        /* Check if selected tag is the RIGHTMOST tag */
        else if (promptElem.value.slice(selectionStart).indexOf(",") == -1) {
            // No need to do anything
            // console.log("Selected TAG is RIGHTMOST tag")
            promptElem.setSelectionRange(promptElem.value.lastIndexOf(",") + 1, promptElem.value.length);
        }
        /* Check if selected tag is immediately to the LEFT of the RIGHTMOST tag */
        else if ( (promptElem.value.slice(selectionStart).split(",").length - 1) == 1 ) {
            // console.log("Selected TAG is immediately to the LEFT of the RIGHTMOST tag")
            let endIndex = promptElem.value.indexOf(",", selectionStart) - 1;
            let startIndex = promptElem.value.slice(0, selectionStart).lastIndexOf(",") + 1;
            let primaryTagString = promptElem.value.slice(startIndex, endIndex + 1).trim();

            let rightTagStartIndex = promptElem.value.lastIndexOf(",") + 1;
            let rightTagString = promptElem.value.slice(rightTagStartIndex).trim();

            let untouchedLeftSide = promptElem.value.slice(0, startIndex - 1).trim();

            let newString = untouchedLeftSide + ", " + rightTagString + ", " + primaryTagString;

            let newPrimaryTagStartIndex = newString.indexOf(primaryTagString);
            let newPrimaryTagEndIndex = newPrimaryTagStartIndex + primaryTagString.length;
            
            promptElem.value = newString;
    
            promptElem.setSelectionRange(newPrimaryTagStartIndex, newPrimaryTagEndIndex);

        } 
        /* Check if selected tag is the LEFTMOST tag */
        else if ( (promptElem.value.slice(0, selectionStart).indexOf(",") == -1) || (selectionStart == 0)) {
            // console.log("Selected TAG is the LEFTMOST tag")
            let endIndex = promptElem.value.indexOf(",") - 1;
            let primaryTagString = promptElem.value.slice(0, endIndex + 1).trim();

            let rightTagStartIndex = endIndex + 2;
            let rightTagEndIndex = promptElem.value.indexOf(",", rightTagStartIndex) - 1;
            let rightTagString = promptElem.value.slice(rightTagStartIndex, rightTagEndIndex + 1).trim();

            let untouchedRightSide = promptElem.value.slice(rightTagEndIndex + 2).trim();

            let newString = rightTagString + ", " + primaryTagString + ", " + untouchedRightSide;
            
            let newPrimaryTagStartIndex = newString.indexOf(primaryTagString);
            let newPrimaryTagEndIndex = newPrimaryTagStartIndex + primaryTagString.length;
            
            promptElem.value = newString;
    
            promptElem.setSelectionRange(newPrimaryTagStartIndex, newPrimaryTagEndIndex);   
        }
        else {
            // console.log("Selected TAG is surrounded by other tags")
            let endIndex = promptElem.value.indexOf(",", selectionStart) - 1;
            let startIndex = promptElem.value.slice(0, endIndex + 1).lastIndexOf(",") + 1;
            let primaryTagString = promptElem.value.slice(startIndex, endIndex + 1).trim()
            
            let rightTagStartIndex = endIndex + 2
            let rightTagEndIndex = promptElem.value.slice(rightTagStartIndex).indexOf(",") + rightTagStartIndex - 1;
            let rightTagString = promptElem.value.slice(rightTagStartIndex, rightTagEndIndex + 1).trim()
    
            let untouchedLeftSide = promptElem.value.slice(0, startIndex - 1).trim()
            let untouchedRightSide = promptElem.value.slice(rightTagEndIndex + 2).trim()
    
            let newString = untouchedLeftSide + ", " + rightTagString + ", " + primaryTagString + ", " + untouchedRightSide;
            
            let newPrimaryTagStartIndex = newString.indexOf(primaryTagString);
            let newPrimaryTagEndIndex = newPrimaryTagStartIndex + primaryTagString.length;
            
            promptElem.value = newString;
    
            promptElem.setSelectionRange(newPrimaryTagStartIndex, newPrimaryTagEndIndex);
        }
    }
}

function changeWeight(promptElem, direction) {
    let selectionStart = promptElem.selectionStart;

    if (selectionStart >= 0) {
        let tagList = promptElem.value.split(",");
        let location = null;

        let startIndex = null;
        let endCommaIndex = null;

        if ((selectionStart < promptElem.value.indexOf(",")) || (tagList.length < 2)) {
            location = "start";
            if (promptElem.value.indexOf(",") == -1) {
                startIndex = 0;
                endCommaIndex = promptElem.value.length;
            } else {
                startIndex = 0;
                endCommaIndex = promptElem.value.indexOf(",");
            }
        }
        else if ((promptElem.value.indexOf(",") < selectionStart) && (selectionStart < promptElem.value.lastIndexOf(","))) {
            location = "middle";
            startIndex = promptElem.value.slice(0, selectionStart).lastIndexOf(",") + 1;
            endCommaIndex = promptElem.value.slice(selectionStart).indexOf(",") + selectionStart;
        } 
        else if (selectionStart > promptElem.value.lastIndexOf(",")) {
            location = "end";
            startIndex = promptElem.value.lastIndexOf(",") + 1;
            endCommaIndex = promptElem.value.length;
        } else {
            console.log("idk man")
            return;
        }
        
        // console.log("location:", location)
        
        let tagString = promptElem.value.slice(startIndex, endCommaIndex);

        let tagData = parseTag(tagString)
        
        let newWeight = direction == "up" ? tagData["weight"] + 0.05 : tagData["weight"] - 0.05;
        // let newWeightString = newWeight >= 0 ? newWeight.toFixed(2) : "0";
        let newWeightString = undefined;
        if (newWeight > 0) {
            newWeightString = newWeight.toFixed(2)
        } else {
            newWeightString = "0"
        }

        if (newWeightString.split(".")[1] == "00" || newWeightString.split(".")[1] == "0") {
            newWeightString = newWeightString.split(".")[0]
        } 
        else if (newWeightString.charAt(newWeightString.length - 1) == "0") {
            newWeightString = newWeight.toFixed(1)
        }

        newWeightString = parseFloat(newWeightString) < 0 ? "0" : newWeightString;

        let bracketOpenChar = null;
        let bracketCloseChar = null;
        if (tagData["display"].indexOf("(") != -1) {
            bracketOpenChar = "("
            bracketCloseChar = ")"
        } else if (tagData["display"].indexOf("[")) {
            bracketOpenChar = "["
            bracketCloseChar = "]"
        }

        let newTagString = tagData["tag"];
        let openBracketCount = tagData["display"].split(bracketOpenChar).length - 1;
        let closeBracketCount = tagData["display"].split(bracketCloseChar).length - 1


        // ---- Generate new tag representation ---- //
        // If the weight is '1', we can just display the tag without any weight syntax
        if (newWeightString == "1") {
            newTagString = tagData["tag"];
        }
        else if (tagData["type"] == "explicit") {
            newTagString = `(${tagData['tag']}:${newWeightString})`
        }
        else if (tagData["type"] == "implicit") {
            // Ensure same number of parentheses on both sides
            if (openBracketCount == closeBracketCount) {
                /* Explicit weight syntax will be favored for tags enclosed in only 1 pair of brackets 
                NOTE: This could be customizeable though. */
                if (openBracketCount == 1) {
                    newTagString = `(${tagData['tag']}:${newWeightString})`
                } else {
                    let newBracketCount = direction == "up" ? openBracketCount + 1 : openBracketCount - 1;
                    newTagString = `${bracketOpenChar.repeat(newBracketCount)}${tagData['tag']}${bracketCloseChar.repeat(newBracketCount)}`
                }
            }
        }
        else if (tagData["type"] == "default") {
            newTagString = `(${tagData['tag']}:${newWeightString})`
        }

        // Build new prompt string
        let newPromptString = undefined;
        let newStartIndex = undefined;
        let newEndCommaIndex = undefined;
        if (location == "start") {
            newStartIndex = 0;
            let rightSide = promptElem.value.slice(endCommaIndex + 1).trim();
            
            if (rightSide == "") {
                newPromptString = newTagString;
            } else {
                newPromptString = `${newTagString}, ${rightSide}`;
                newEndCommaIndex = newPromptString.indexOf(",");
            }

            promptElem.value = newPromptString;

            if (newEndCommaIndex) {
                promptElem.setSelectionRange(newStartIndex, newEndCommaIndex);
            } else {
                promptElem.setSelectionRange(newStartIndex, promptElem.value.length);
            }
        } 
        else if (location == "middle") {
            newPromptString = `${promptElem.value.slice(0, startIndex - 1)}, ${newTagString}, ${promptElem.value.slice(endCommaIndex + 1).trim()}`;
            newStartIndex = newPromptString.indexOf(newTagString);
            newEndCommaIndex = newPromptString.indexOf(",", newStartIndex);
            
            promptElem.value = newPromptString;
            promptElem.setSelectionRange(newStartIndex, newEndCommaIndex);
        }
        else if (location == "end") {
            newPromptString = `${promptElem.value.slice(0, startIndex - 1).trim()}, ${newTagString}`;
            newStartIndex = newPromptString.indexOf(newTagString);
            
            promptElem.value = newPromptString;
            promptElem.setSelectionRange(newStartIndex, newPromptString.length);
        }




    }
}

/*
TODO: Add button that converts all implicit weights to explicit weights
*/

function parseTag(tag) {
    if (typeof tag !== "string") {
        return {};
    }

    tag = tag.trim();
    const tagInfo = {};

    // Helper function to calculate weight
    function calculateWeight(count, decrease = false) {
        const base = 1.1;
        return decrease ? Math.pow(base, -count) : Math.pow(base, count);
    }

    // Check for explicit weight (e.g., `(cute dress:1.25)`)
    const explicitMatch = tag.match(/^\(([^:()]+):([\d.]+)\)$/);
    if (explicitMatch) {
        const [_, tagName, weight] = explicitMatch;
        tagInfo["tag"] = tagName.trim();
        tagInfo["weight"] = parseFloat(weight);
        tagInfo["type"] = "explicit";
        tagInfo["display"] = tag.trim();
        return tagInfo;
    }

    // Check for implicit weight increase (e.g., `((1girl))`)
    const implicitIncreaseMatch = tag.match(/^(\(+)([^()]+)(\)+)$/);
    if (implicitIncreaseMatch) {
        const [_, openBrackets, tagName] = implicitIncreaseMatch;
        const count = openBrackets.length;
        const weight = parseFloat(calculateWeight(count).toFixed(4));
        tagInfo["tag"] = tagName.trim();
        tagInfo["weight"] = weight;
        tagInfo["type"] = "implicit";
        tagInfo["display"] = tag.trim();
        return tagInfo;
    }

    // Check for implicit weight decrease (e.g., `[grayscale]`)
    const implicitDecreaseMatch = tag.match(/^(\[+)([^\[\]]+)(\]+)$/);
    if (implicitDecreaseMatch) {
        const [_, openBrackets, tagName] = implicitDecreaseMatch;
        const count = openBrackets.length;
        const weight = parseFloat(calculateWeight(count, true).toFixed(4));
        tagInfo["tag"] = tagName.trim();
        tagInfo["weight"] = weight;
        tagInfo["type"] = "implicit";
        tagInfo["display"] = tag.trim();
        return tagInfo;
    }

    // Default case: no weight
    tagInfo["tag"] = tag.trim();
    tagInfo["weight"] = 1.0;
    tagInfo["type"] = "default";
    tagInfo["display"] = tag.trim();
    return tagInfo;
}
