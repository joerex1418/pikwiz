
document.getElementById("image-display-container").addEventListener("click", function() {
    document.getElementById("photo-upload").click();
})

function handleUpload(e) {
    const photoUploadInput = document.getElementById("photo-upload");
    const imageWrapperDiv = document.getElementById("image-display-container");
    const imgElement = imageWrapperDiv.querySelector("img");
    // let imageUploaded = false;

    let url = ""
    if (e.dataTransfer) {
        url = e.dataTransfer.getData("text/uri-list");
        document.getElementById("imageurl").querySelector(".detail-text").value = url;
    } else {
        document.getElementById("imageurl").querySelector(".detail-text").value = "";
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
        } else {
            updateImageDisplayUI(false)
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

    document.getElementById("imageurl").querySelector(".detail-text").value = "";
    document.getElementById("model-checkpoint").querySelector(".detail-text").value = ""
    document.getElementById("vae").querySelector(".detail-text").value = ""
    document.getElementById("positive-prompt").querySelector(".detail-text").value = ""
    document.getElementById("negative-prompt").querySelector(".detail-text").value = ""
    // document.getElementById("loras")
    // document.getElementById("weighted-tags")
    document.getElementById("steps").querySelector(".detail-text").value = ""
    document.getElementById("sampler").querySelector(".detail-text").value = ""
    document.getElementById("schedule-type").querySelector(".detail-text").value = ""
    document.getElementById("cfg-scale").querySelector(".detail-text").value = ""
    document.getElementById("seed").querySelector(".detail-text").value = ""

}

document.getElementById("clear-btn").addEventListener("click", clearAll)

// Enable drag-and-drop
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
    // const imgElem = document.getElementById("image-display-container").querySelector("img");
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
        document.getElementById("model-checkpoint").querySelector(".detail-text").value = data["generation"]["settings"]["model"]
        
        if (!data["generation"]["settings"]["vae"]) data["generation"]["settings"]["vae"] = ""
        document.getElementById("vae").querySelector(".detail-text").value = data["generation"]["settings"]["vae"]

        document.getElementById("positive-prompt").querySelector(".detail-text").value = data["generation"]["positive"]
        document.getElementById("negative-prompt").querySelector(".detail-text").value = data["generation"]["negative"]
        // document.getElementById("loras")
        // document.getElementById("weighted-tags")
        
        document.getElementById("steps").querySelector(".detail-text").value = data["generation"]["settings"]["steps"]
        
        if (!data["generation"]["settings"]["sampler"]) data["generation"]["settings"]["sampler"] = ""
        document.getElementById("sampler").querySelector(".detail-text").value = data["generation"]["settings"]["sampler"]
        if (!data["generation"]["settings"]["schedule-type"]) data["generation"]["settings"]["schedule_type"] = ""
        document.getElementById("schedule-type").querySelector(".detail-text").value = data["generation"]["settings"]["schedule_type"]

        document.getElementById("cfg-scale").querySelector(".detail-text").value = data["generation"]["settings"]["cfg_scale"]
        
        document.getElementById("seed").querySelector(".detail-text").value = data["generation"]["settings"]["seed"]
    })
    .catch(error => console.log("ERROR:", error))

})

function getGenerationData(randomSeed=true) {

    let positivePrompt = document.getElementById("positive-prompt").querySelector(".detail-text").value;
    let negativePrompt = document.getElementById("negative-prompt").querySelector(".detail-text").value;
    let steps = document.getElementById("steps").querySelector(".detail-text").value;
    let cfgScale = document.getElementById("cfg-scale").querySelector(".detail-text").value;
    let sampler = document.getElementById("sampler").querySelector(".detail-text").value;
    let scheduleType = document.getElementById("schedule-type").querySelector(".detail-text").value;

    let samplerSched = `${sampler} ${scheduleType}`

    let modelCheckpoint = document.getElementById("model-checkpoint").querySelector(".detail-text").value;
    let vaeModel = document.getElementById("vae").querySelector(".detail-text").value;
    let seed = document.getElementById("seed").querySelector(".detail-text").value;
    if (randomSeed == true) {
        seed = "-1";
    }

    // document.getElementById("loras")
    // document.getElementById("weighted-tags")

    let string = `
${positivePrompt}
Negative prompt: ${negativePrompt}
Steps: ${steps}, CFG scale: ${cfgScale}, Sampler: ${samplerSched}, Seed: ${seed}
    `
    // let string = `${positivePrompt}\nNegative prompt: ${negativePrompt}\nSteps: ${steps}, CFG scale: ${cfgScale}, Sampler: ${samplerSched}, Seed: ${seed}`

    return string
}

document.getElementById("copy-raw").addEventListener("click", function(e) {
    let generationDataString = getGenerationData(true)
    navigator.clipboard.writeText(generationDataString.trim())
})

document.getElementById("copy-raw-with-seed").addEventListener("click", function(e) {
    let generationDataString = getGenerationData(false)
    navigator.clipboard.writeText(generationDataString.trim())
})



