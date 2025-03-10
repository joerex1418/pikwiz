let allowAutoHeight = false;
let allowAutoWidth = false;

document.getElementById("image-display-container").addEventListener("click", function() {
    document.getElementById("photo-upload").click();
})

function resetScaleAdjust() {
    // document.querySelector("#scale-original-wrapper .detail-value").value = 1.0
}

function handleUpload(e) {
    const photoUploadInput = document.getElementById("photo-upload");
    const imageWrapperDiv = document.getElementById("image-display-container");
    const imgElement = imageWrapperDiv.querySelector("img");
    // let imageUploaded = false;

    let url = ""
    if (e.dataTransfer) {
        url = e.dataTransfer.getData("text/uri-list");
        document.getElementById("imageurl").querySelector(".detail-value").value = url;
    } else {
        document.getElementById("imageurl").querySelector(".detail-value").value = "";
    }

    // Handle drag and drop from the web
    if (url.startsWith("http")) {
        fetch(url)
            .then(response => {
                // console.log(response.headers);
                return response.blob()
            })
            .then(blob => {
                if (blob.type.startsWith("image/")) {
                    const file = new File([blob], "temp." + blob.type.slice(5), { type: blob.type });
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(file)

                    imgElement.src = URL.createObjectURL(file);
                    photoUploadInput.files = dataTransfer.files;
                    updateImageDisplayUI(true)
                    resetScaleAdjust();
                }
            })
            .catch( error => {
                // updateImageDisplayUI(false)
                console.log("Error Fetching image:", error)
            })
    } else {
        const files = e.target?.files || e.dataTransfer?.files;
        if (files.length) {
            // Assign new file to the input element
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(files[0]); // Ensure only one file is stored
            photoUploadInput.files = dataTransfer.files;
        
            const file = photoUploadInput.files[0];
            imgElement.src = URL.createObjectURL(file);
            updateImageDisplayUI(true);
            resetScaleAdjust();
        } else {
            updateImageDisplayUI(false)
            resetScaleAdjust();
        }
        
    }
}

function updateImageDisplayUI(imageUploaded) {
    const imageWrapperDiv = document.getElementById("image-display-container");
    const imgElement = imageWrapperDiv.querySelector("img");
    if (imageUploaded == true) {
        imgElement.style.width = "auto";
        imgElement.style.height = "auto";
        imgElement.style.maxWidth = imageWrapperDiv.clientWidth.toString() + "px";
        imgElement.style.maxHeight = imageWrapperDiv.clientHeight.toString() + "px";
        imageWrapperDiv.classList.add("populated")
    } else {
        imageWrapperDiv.classList.remove("populated")
    }
}

document.getElementById("photo-upload").addEventListener("change", handleUpload)

function clearAll() {
    const photoUploadInput = document.getElementById("photo-upload");
    const imageWrapperDiv = document.getElementById("image-display-container");
    const imgElement = imageWrapperDiv.querySelector("img");

    photoUploadInput.value = "";
    imageWrapperDiv.classList.remove("populated")
    imgElement.src = ""

    document.getElementById("imageurl").querySelector(".detail-value").value = "";
    document.getElementById("model-checkpoint").querySelector(".detail-value").value = ""
    document.getElementById("vae").querySelector(".detail-value").value = ""
    document.getElementById("positive-prompt").querySelector(".detail-value").value = ""
    document.getElementById("negative-prompt").querySelector(".detail-value").value = ""
    // document.getElementById("loras")
    // document.getElementById("weighted-tags")
    document.getElementById("steps").querySelector(".detail-value").value = ""
    document.getElementById("sampler").querySelector(".detail-value").value = ""
    document.getElementById("schedule-type").querySelector(".detail-value").value = ""
    document.getElementById("cfg-scale").querySelector(".detail-value").value = ""
    document.getElementById("seed").querySelector(".detail-value").value = ""
    document.getElementById("width").querySelector(".detail-value").value = ""
    document.getElementById("height").querySelector(".detail-value").value = ""

}

document.getElementById("clear-btn").addEventListener("click", clearAll)

// ----------------------------- //
// Implement drag-and-drop
// ----------------------------- //
const displayContainer = document.getElementById("image-display-container");

displayContainer.addEventListener("dragover", function (e) {
    e.preventDefault();
    displayContainer.classList.add("dragging"); // Optional visual feedback
});

displayContainer.addEventListener("dragleave", function () {
    displayContainer.classList.remove("dragging"); // Remove feedback
});

displayContainer.addEventListener("drop", function (e) {
    e.preventDefault(); // Prevent default behavior (open file in new tab)
    displayContainer.classList.remove("dragging"); // Remove feedback

    handleUpload(e)
});

document.getElementById("extract-prompt-btn").addEventListener("click", function() {
    const photoUploadInput = document.getElementById("photo-upload");
    
    if (photoUploadInput.files[0] == 0) return;

    const file = photoUploadInput.files[0];
    const formData = new FormData();
    
    formData.append("image", file);
    
    fetch("/extract-prompt", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        let baseModel = null;
        let checkpointId = null;
        let checkpointVersionId = null;
        let checkpointName = data["generation"]["settings"]["model"];
        let checkpointVersionName = null;

        let civitaiResources = data["generation"]["civitai_resources"];
        civitaiResources = civitaiResources ? civitaiResources : []
        for (let index = 0; index < civitaiResources.length; index++) {
            const resource = civitaiResources[index];
            if (resource["type"] == "checkpoint") {
                baseModel = resource["base_model"];
                checkpointId = resource["model_id"];
                
                // checkpointVersionId = resource["modelVersionId"];
                // checkpointVersionName = resource["modelVersionName"];

                if (resource["modelName"] == undefined) {
                    if (resource["model_name"]) {
                        checkpointName = resource["model_name"];
                    }
                } else {
                    checkpointName = resource["modelName"];
                }

                if (resource["modelVersionId"] == undefined) {
                    if (resource["model_version_id"]) {
                        checkpointVersionId = resource["model_name"];
                    }
                } else {
                    checkpointVersionId = resource["modelVersionId"];
                }

                if (resource["modelVersionName"] == undefined) {
                    if (resource["model_version_name"]) {
                        checkpointVersionName = resource["model_version_name"];
                    }
                } else {
                    checkpointVersionName = resource["modelVersionName"];
                }

                break;
            }
        }
        let checkpointInputElem = document.getElementById("model-checkpoint").querySelector(".detail-value")
        checkpointInputElem.value = checkpointName;
        checkpointInputElem.dataset["checkpointId"] = checkpointId;
        checkpointInputElem.dataset["checkpointVersionId"] = checkpointVersionId;
        checkpointInputElem.dataset["checkpointVersionName"] = checkpointVersionName;


        if (!data["generation"]["settings"]["vae"]) data["generation"]["settings"]["vae"] = ""
        document.getElementById("vae").querySelector(".detail-value").value = data["generation"]["settings"]["vae"]

        document.getElementById("positive-prompt").querySelector(".detail-value").value = data["generation"]["positive"]
        document.getElementById("negative-prompt").querySelector(".detail-value").value = data["generation"]["negative"]
        // document.getElementById("loras")
        // document.getElementById("weighted-tags")
        
        document.getElementById("steps").querySelector(".detail-value").value = data["generation"]["settings"]["steps"]
        
        if (!data["generation"]["settings"]["sampler"]) data["generation"]["settings"]["sampler"] = ""
        if (!data["generation"]["settings"]["schedule_type"]) data["generation"]["settings"]["schedule_type"] = ""

        document.getElementById("sampler").querySelector(".detail-value").value = data["generation"]["settings"]["sampler"]
        document.getElementById("schedule-type").querySelector(".detail-value").value = data["generation"]["settings"]["schedule_type"]

        document.getElementById("cfg-scale").querySelector(".detail-value").value = data["generation"]["settings"]["cfg_scale"]
        
        document.getElementById("seed").querySelector(".detail-value").value = data["generation"]["settings"]["seed"]
        
        let size = data["generation"]["settings"]["size"];
        let width = parseInt(size.split("x")[0]);
        let height = parseInt(size.split("x")[1]);
        let imageRatio = getImageRatio(width, height);

        document.getElementById("width").querySelector(".detail-value").value = width;
        document.querySelector("#width .detail-value").dataset["originalValue"] = width;

        document.getElementById("height").querySelector(".detail-value").value = height;
        document.querySelector("#height .detail-value").dataset["originalValue"] = height;

        if (document.querySelector(`.size-value[data-dimensions="${size}"]`)) {
            document.querySelector(`.size-value[data-dimensions="${size}"]`).classList.add("selected")
        }

        // Reset scale adjustment to 1.00 by default
        resetScaleAdjust();

    })
    .catch(error => console.log("ERROR:", error))

})

// ----------------------------- //
// Handling Image Size/Res
// ----------------------------- //
document.getElementById("swap-orientation-btn").addEventListener("click", function() {
    let width = getWidth();
    let height = getHeight();

    setInputHeight(width)
    setInputWidth(height)
})


// ----------------------------- //
// Select Resolution Dropdown
// ----------------------------- //
const selectResDropdown = document.getElementById("select-resolution");
const selectResBtn = document.getElementById("select-resolution-btn");

selectResBtn.addEventListener("click", function(e) {
    selectResDropdown.classList.toggle("hidden")
    
})

document.body.addEventListener("click", function(e) {
    if ( !e.target.closest("#select-resolution") && !e.target.closest("#select-resolution-btn") ) {
        selectResDropdown.classList.add("hidden")
    }
})

selectResDropdown.addEventListener("click", function(e) {
    if ( e.target.closest(".size-value") ) {
        const selectedElem = e.target.closest(".size-value");
        const orientation = selectedElem.closest(".resolution-group").dataset["orientation"];
        
        let dimensions = selectedElem.dataset["dimensions"];
        let width = dimensions.split("x")[0];
        let height = dimensions.split("x")[1];
        let ratio = selectedElem.dataset["ratio"];

        document.querySelector("#width .detail-value").value = parseInt(width);
        document.querySelector("#height .detail-value").value = parseInt(height);

        selectResDropdown.classList.add("hidden");

        document.querySelectorAll(".size-value").forEach(elem => {
            if (elem == selectedElem) {
                elem.classList.add("selected");
            } else {
                elem.classList.remove("selected");
            }
        })

    }
})



// ----------------------------- //
// Copying data to clipboard
// ----------------------------- //
function genDataToRawString(randomSeed=true) {
    let positivePrompt = document.getElementById("positive-prompt").querySelector(".detail-value").value;
    let negativePrompt = document.getElementById("negative-prompt").querySelector(".detail-value").value;
    let steps = document.getElementById("steps").querySelector(".detail-value").value;
    let cfgScale = document.getElementById("cfg-scale").querySelector(".detail-value").value;
    let sampler = document.getElementById("sampler").querySelector(".detail-value").value;
    let scheduleType = document.getElementById("schedule-type").querySelector(".detail-value").value;

    let samplerSched = `${sampler} ${scheduleType}`.trim()

    let modelCheckpoint = document.getElementById("model-checkpoint").querySelector(".detail-value").value;
    let vaeModel = document.getElementById("vae").querySelector(".detail-value").value;
    let seed = document.getElementById("seed").querySelector(".detail-value").value;
    
    if (randomSeed == true) {
        seed = "-1";
    }

    // document.getElementById("loras")
    // document.getElementById("weighted-tags")

    let string = `${positivePrompt}\nNegative prompt: ${negativePrompt}\nSteps: ${steps}, CFG scale: ${cfgScale}, Sampler: ${samplerSched}, Seed: ${seed}`

    return string
}

document.getElementById("copy-raw").addEventListener("click", function(e) {
    let generationDataString = genDataToRawString(true)
    navigator.clipboard.writeText(generationDataString.trim())
})

document.getElementById("copy-raw-with-seed").addEventListener("click", function(e) {
    let generationDataString = genDataToRawString(false)
    navigator.clipboard.writeText(generationDataString.trim())
})


// ----------------------------- //
// 
// ----------------------------- //
document.getElementById("hide-image-btn").addEventListener("click", function() {
    let imgElem = document.querySelector("#image-preview img");
    if (imgElem.classList.contains("discreet")) {
        imgElem.classList.remove("discreet")
        document.getElementById("hide-image-btn").textContent = "Hide"
    } else {
        imgElem.classList.add("discreet")
        document.getElementById("hide-image-btn").textContent = "Show"
    }
})