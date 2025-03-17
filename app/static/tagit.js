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

document.querySelector("#load-dir-btn").addEventListener("click", function(e) {
    document.querySelector("input[name='image_dir']").click();
})

document.querySelector("input[name='image_dir']").addEventListener("change", function(e) {
    const galleryElem = document.getElementById("gallery");
    
    if (e.target.files > 0) {
        galleryElem.innerHTML = "";
    }

    // let count = 1;
    for (let index = 0; index < e.target.files.length; index++) {
        const file = e.target.files[index];
        if (file.type.startsWith("image/")) {
            // console.log(file.webkitRelativePath)

            let imgWrapper = document.createElement("div");
            imgWrapper.classList.add("img-wrapper");
            
            let imgElem = document.createElement("img");
            let blobUrl = URL.createObjectURL(file);
            imgElem.src = blobUrl;
            imgElem.dataset["og_name"] = file.name;
            imgElem.onload = () => URL.revokeObjectURL(blobUrl);
            
            let promptWrapper = document.createElement("div");
            promptWrapper.classList.add("prompt-wrapper");
            
            let textArea = document.createElement("textarea");
            textArea.dataset["og_name"] = file.name;
            textArea.autocapitalize = "off"
            textArea.autocomplete = "off"
            textArea.ariaAutoComplete = "none"
            
            imgWrapper.appendChild(imgElem)
            promptWrapper.appendChild(textArea)

            galleryElem.appendChild(imgWrapper)
            galleryElem.appendChild(promptWrapper)
        }
    }

    const formData = new FormData();

    for (const file of e.target.files) {
        if (file.type.startsWith("image/")) {
            formData.append("images", file, file.name);
        }
    }

    fetch("/tagit", {
        method: "POST",
        body: formData
    })
    .then( response => {return response.json()} )
    .then( data => {
        for (const item of data) {
            const textArea = document.querySelector(`textarea[data-og_name="${item['filename']}"]`);
            textArea.textContent = item["tagtext"];
        }
    } )


})


// positivePromptElem.addEventListener("keydown", function(e) {
//     // if (e.ctrlKey & e.shiftKey) {
//     if ((e.ctrlKey & e.shiftKey)) {
//         switch (e.key) {
//             case "ArrowLeft":
//                 moveTagLeft(positivePromptElem); 
//                 break;
//             case "ArrowRight":
//                 moveTagRight(positivePromptElem); 
//                 break;
//             case "ArrowUp":
//                 changeWeight(positivePromptElem, "up"); 
//                 break;
//             case "ArrowDown":
//                 changeWeight(positivePromptElem, "down"); 
//                 break;
//         }
//         e.preventDefault();
//     }
// });