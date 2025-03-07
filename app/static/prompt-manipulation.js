const positivePromptElem = document.querySelector("#positive-prompt textarea");
const negativePromptElem = document.querySelector("#negative-prompt textarea");

positivePromptElem.addEventListener("keydown", function(e) {
    // if (e.ctrlKey & e.shiftKey) {
    if ((e.ctrlKey & e.shiftKey) | (e.shiftKey)) {
        switch (e.key) {
            case "ArrowLeft":
                moveTagLeft(positivePromptElem); break;
            case "ArrowRight":
                moveTagRight(positivePromptElem); break;
            case "ArrowUp":
                increaseWeight(positivePromptElem); break;
            case "ArrowDown":
                decreaseWeight(positivePromptElem); break;
        }
        e.preventDefault();
    }
});

negativePromptElem.addEventListener("keydown", function(e) {
    // if (e.ctrlKey & e.shiftKey) {
    if ((e.ctrlKey & e.shiftKey) | (e.shiftKey)) {
        switch (e.key) {
            case "ArrowLeft":
                moveTagLeft(negativePromptElem); break;
            case "ArrowRight":
                moveTagRight(negativePromptElem); break;
            case "ArrowUp":
                increaseWeight(negativePromptElem); break;
            case "ArrowDown":
                decreaseWeight(negativePromptElem); break;
        }
        e.preventDefault();
    }
});





function moveTagLeft(promptElem) {
    let selectionStart = promptElem.selectionStart;

    if (selectionStart) {
        /* Check if selected tag is the LEFTMOST tag */
        if (promptElem.value.slice(0, selectionStart).indexOf(",") == -1) {
            promptElem.setSelectionRange(0, promptElem.value.indexOf(","));
            // No need to do anything
            console.log("No movement needed")
            return;
        }

        /* Check if selected tag is immediately to the RIGHT of the LEFTMOST tag */
        if ( (promptElem.value.slice(0, selectionStart).split(",").length - 1) == 1 ) {
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

    if (selectionStart) {
        /* Check if selected tag is the RIGHTMOST tag */
        if (promptElem.value.slice(selectionStart).indexOf(",") == -1) {
            promptElem.setSelectionRange(promptElem.value.lastIndexOf(",") + 1, promptElem.value.length);
            // No need to do anything
            console.log("No movement needed")
            return;
        }
        /* Check if selected tag is immediately to the LEFT of the RIGHTMOST tag */
        // ...wait, lol. This is only needs to be checked in the 'moveTagRight()' function
        
        // else if ( (promptElem.value.slice(selectionStart).split(",").length - 1) == 1 ) {
        //     let endIndex = promptElem.value.slice(selectionStart).indexOf(",") - 1;
        //     let startIndex = promptElem.value.slice(0, selectionStart).lastIndexOf(",") + 1;
        //     let primaryTagString = promptElem.value.slice(startIndex, endIndex + 1);

        // } 
        else {
            // let endCommaIndex = promptElem.value.indexOf(",", selectionStart);
            // let startCommaIndex = promptElem.value.slice(0, endCommaIndex).lastIndexOf(",");
            // let primaryTagString = promptElem.value.slice(startCommaIndex + 1, endCommaIndex).trim()
            
            // let rightTagEndCommaIndex = promptElem.value.slice(endCommaIndex + 1).indexOf(",") + endCommaIndex + 1
            // let rightTagString = promptElem.value.slice(endCommaIndex + 1, rightTagEndCommaIndex).trim()
    
            // let untouchedLeftSide = promptElem.value.slice(0, startCommaIndex).trim()
            // let untouchedRightSide = promptElem.value.slice(rightTagEndCommaIndex + 1).trim()
            
            let endIndex = promptElem.value.indexOf(",", selectionStart) - 1;
            let startIndex = promptElem.value.slice(0, endIndex + 1).lastIndexOf(",") + 1;
            let primaryTagString = promptElem.value.slice(startIndex, endIndex + 1).trim()
            
            let rightTagStartIndex = endIndex + 2
            let rightTagEndIndex = promptElem.value.slice(rightTagStartIndex).indexOf(",") + rightTagStartIndex - 1;
            let rightTagString = promptElem.value.slice(rightTagStartIndex, rightTagEndIndex + 1).trim()
    
            let untouchedLeftSide = promptElem.value.slice(0, startIndex - 1).trim()
            let untouchedRightSide = promptElem.value.slice(rightTagEndIndex + 2).trim()

            console.log("untouchedLeftSide:\t", untouchedLeftSide)
            console.log("rightTagString:\t", rightTagString)
            console.log("rightTagStartIndex:\t", rightTagStartIndex)
            console.log("rightTagEndIndex:\t", rightTagEndIndex)
            console.log("primaryTagString:\t", primaryTagString)
            console.log("untouchedRightSide:\t", untouchedRightSide)
    
            let newString = untouchedLeftSide + ", " + rightTagString + ", " + primaryTagString + ", " + untouchedRightSide;
            
            let newPrimaryTagStartIndex = newString.indexOf(primaryTagString);
            let newPrimaryTagEndIndex = newPrimaryTagStartIndex + primaryTagString.length;
            
            promptElem.value = newString;
    
            promptElem.setSelectionRange(newPrimaryTagStartIndex, newPrimaryTagEndIndex);
        }
    }
}

function increaseWeight(promptElem) {

}