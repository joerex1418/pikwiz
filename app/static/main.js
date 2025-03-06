let allowAutoHeight = false;
let allowAutoWidth = false;

document.getElementById("image-display-container").addEventListener("click", function() {
    document.getElementById("photo-upload").click();
})

function resetScaleAdjust() {
    document.querySelector("#scale-original-wrapper .detail-value").value = 1.0
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
        document.getElementById("model-checkpoint").querySelector(".detail-value").value = data["generation"]["settings"]["model"]
        
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
        let imageRatio = getImageRatio(width, height)
        document.getElementById("width").querySelector(".detail-value").value = width;
        document.querySelector("#width .detail-value").dataset["originalValue"] = width;

        document.getElementById("height").querySelector(".detail-value").value = height;
        document.querySelector("#height .detail-value").dataset["originalValue"] = height;

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
// Scale Event
// ----------------------------- //
document.querySelector("#scale-original-wrapper .detail-value").addEventListener("change", function(e) {
    const widthElem = document.querySelector("#width .detail-value");
    const heightElem = document.querySelector("#height .detail-value");

    if (widthElem.value && heightElem.value) {
        let scaleFactor = parseFloat(document.querySelector("#scale-original-wrapper .detail-value").value)
        let originalWidth = widthElem.dataset["originalValue"];
        let originalHeight = heightElem.dataset["originalValue"];

        widthElem.value = originalWidth * scaleFactor;
        heightElem.value = originalHeight * scaleFactor;

    }
})

// ----------------------------- //
// Select Resize Method
// ----------------------------- //
document.getElementById("resize-tool-select-btn-bar").addEventListener("click", function(e) {
    const resizeToolsWrapper = document.getElementById("resize-tools-wrapper");

    if (e.target.classList.contains("tool-select-btn")) {
        let selectedPrefix = e.target.dataset["prefix"];
        
        resizeToolsWrapper.querySelector(`.btn[data-prefix="${selectedPrefix}"]`).classList.add("active");
        resizeToolsWrapper.querySelector(`.btn:not([data-prefix="${selectedPrefix}"])`).classList.remove("active");

        resizeToolsWrapper.querySelector(`.detail-wrapper[data-prefix="${selectedPrefix}"]`).classList.add("active");
        resizeToolsWrapper.querySelector(`.detail-wrapper:not([data-prefix="${selectedPrefix}"])`).classList.remove("active");
    }
})

// ----------------------------- //
// Select Orientation
// ----------------------------- //
document.getElementById("orientation-selection-btn-bar").addEventListener("click", function(e) {
    const orientationBtnBar = document.getElementById("orientation-selection-btn-bar");

    if (e.target.classList.contains("orientation-btn")) {
        let selectedOrientation = e.target.dataset["orientation"]
        
        document.querySelectorAll(".orientation-btn").forEach(oriBtn => {
            if (oriBtn == e.target) {
                oriBtn.classList.add("active")
            } else {
                oriBtn.classList.remove("active")
            }
        })

        if (selectedOrientation == "square") {
            // Change Resolution Buttons
            document.querySelectorAll(`.res-btn[data-orientation="square"]`).forEach(resBtn => {
                resBtn.classList.add("active")
            })
            document.querySelectorAll(`.res-btn[data-orientation="portrait"], .res-btn[data-orientation="landscape"]`).forEach(resBtn => {
                resBtn.classList.remove("active")
            })
        } else {
            // Change Resolution Buttons
            document.querySelectorAll(`.res-btn[data-orientation="square"]`).forEach(resBtn => {
                resBtn.classList.remove("active")
            })
            document.querySelectorAll(`.res-btn[data-orientation="portrait"], .res-btn[data-orientation="landscape"]`).forEach(resBtn => {
                resBtn.classList.add("active")
                resBtn.dataset["orientation"] = selectedOrientation
                resBtn.textContent = resBtn.dataset[selectedOrientation]
            })
        }

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

    let samplerSched = `${sampler} ${scheduleType}`

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