
const WHO_TOPIC = "iotdemo.who";
const LED_TOPIC = "iotdemo.ledmessage";
const IMAGES_TOPIC = "iotdemo.images";
var newGuestID = "";

/* --------------------------- */
const ws = new WebSocket("ws://localhost:8000/ws");
// add listener for the 'beforeunload' event
window.addEventListener('beforeunload', function (event) {
// close the WebSocket connection
    ws.close();
    console.log('Socket closed.');
});
ws.onmessage = (event) => {
    // console.log(event.data);
    let dataObject = JSON.parse(event.data);

    if (WHO_TOPIC in dataObject) {
        let whoData = dataObject[WHO_TOPIC];
        let domElem = document.getElementById(WHO_TOPIC);
        // domElem.innerHTML = "";

        for(let i = 0; i < whoData.length; i++) {
            let timestamp = whoData[i]["timestamp"];
            let payload = whoData[i]["payload"];
            
            let haveChild = false;
            for(let j = 0; j < domElem.children.length; j++) {
                if (domElem.children[j].getAttribute("timestamp") == timestamp) {
                    haveChild = true;
                    break;
                }
            }

            if (!haveChild)
            {
                let myPara = document.createElement('p');
                myPara.setAttribute("timestamp", timestamp);
                myPara.textContent = payload;
                domElem.appendChild(myPara);
            }
        }
    }
    
    if (LED_TOPIC in dataObject) {
        let ledData = dataObject[LED_TOPIC];
        let domElem = document.getElementById(LED_TOPIC);
        domElem.textContent = ledData["payload"];
    }

    if (IMAGES_TOPIC in dataObject) {
        let imageData = dataObject[IMAGES_TOPIC];
        let domElem = document.getElementById(IMAGES_TOPIC);
        domElem.src = "data:image/png;base64," + imageData["payload"]["image"];

        let inputNewGuest = document.getElementById("inputNewGuest");
        let submitNewGuest = document.getElementById("submitNewGuest");

        if (imageData["payload"]["name"].includes(".jpg")) {
            inputNewGuest.disabled = false;
            submitNewGuest.disabled = false;
            newGuestID = imageData["payload"]["name"];
        } else {
            inputNewGuest.disabled = true;
            submitNewGuest.disabled = true;
        }
    }
};

/* --------------------------- */
const myScrollBox = document.getElementById(WHO_TOPIC);
function scrollToBottom() {
    myScrollBox.scrollTop = myScrollBox.scrollHeight - myScrollBox.clientHeight;
}
// call the scrollToBottom function after new data is added to the scroll box
myScrollBox.addEventListener('DOMNodeInserted', scrollToBottom);
// manually scroll to the bottom on page load
scrollToBottom();

/* --------------------------- */
// JavaScript
let myInput = document.getElementById("inputLEDM");
let myButton = document.getElementById("submitLEDM");
let outputDiv = document.getElementById("outputLEDM");

// Event listener for button click
myButton.addEventListener("click", function() {
    let inputValue = myInput.value;
    if (inputValue == "") {
        outputDiv.textContent = "";
        return;
    }
    inputValue = inputValue.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    // outputDiv.textContent = "Your message: " + inputValue;

    // Send an HTTP POST request to the FastAPI API endpoint with the user input data.
    fetch('/api/postLEDMessage', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            data: inputValue
        })
    })
    .then(response => response.json())
    .then(data => {
        outputDiv.textContent = "Response from server: " + JSON.stringify(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
});


/* ---------------------------- */
let inputNewGuest = document.getElementById("inputNewGuest");
let submitNewGuest = document.getElementById("submitNewGuest");
submitNewGuest.addEventListener("click", function() {
    let inputValue = inputNewGuest.value;
    if (inputValue == "") {
        return;
    }
    inputValue = inputValue.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    // outputDiv.textContent = "Your message: " + inputValue;

    // Send an HTTP POST request to the FastAPI API endpoint with the user input data.
    fetch('/api/postNewGuest', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: inputValue,
            id: newGuestID
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Response from server: " + JSON.stringify(data));
        inputNewGuest.textContent = "";
        inputNewGuest.disabled = true;
        submitNewGuest.disabled = true;
    })
    .catch(error => {
        console.error('Error:', error);
    });
});