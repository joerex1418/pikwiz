function gcd(a, b) {
    return b === 0 ? a : gcd(b, a % b);
}

function getImageRatio(width, height) {
    let divisor = gcd(width, height);
    let ratioWidth = width / divisor;
    let ratioHeight = height / divisor;

    return `${ratioWidth}:${ratioHeight}`;
}

function calculateHeight(width, ratio) {
    let rl = ratio.split(":");
    
    let numerator = parseInt(rl[0])
    let denominator = parseInt(rl[1])

    width = parseInt(width);
    
    let factor = parseFloat(width / numerator);

    let height = parseInt(parseFloat(denominator * factor));
    return height
}

function calculateWidth(height, ratio) {
    let rl = ratio.split(":");
    
    let numerator = parseInt(rl[0])
    let denominator = parseInt(rl[1])

    height = parseInt(height);
    
    let factor = parseFloat(height / denominator);

    let width = parseInt(parseFloat(numerator * factor));
    
    return width
}

function getWidth() { 
    return parseInt(document.querySelector("#width .detail-value").value);
}

function getHeight() { 
    return parseInt(document.querySelector("#height .detail-value").value);
}

function setInputWidth(value) {
    document.querySelector("#width .detail-value").value = value;
}

function setInputHeight(value) {
    document.querySelector("#height .detail-value").value = value;
}