import { initializeApp } from "https://www.gstatic.com/firebasejs/12.17.1/firebase-app.js";
import {
  getMessaging,
  onMessage,
  onRegistered,
  register,
} from "https://www.gstatic.com/firebasejs/12.17.1/firebase-messaging.js";

const firebaseConfig = {
  apiKey: "AIzaSyC_likyA_fN8wAh6llHYwXCB1GSjRCffUU",
  authDomain: "test-project-a9235.firebaseapp.com",
  projectId: "test-project-a9235",
  storageBucket: "test-project-a9235.firebasestorage.app",
  messagingSenderId: "358837086105",
  appId: "1:358837086105:web:1cbd20af2a6e71e7d81508",
};

const app = initializeApp(firebaseConfig);
const vapidKey =
  "BH1m3PzZKUYNWCORF5nTos04VSZsbuOAKdjuUNMIjIsVYU-AH263wsa6w99yvGOQX_yw9ovDwkAjUF1dzhR1QtI";

const messaging = getMessaging(app);

const tokenDivId = "token_div";
const permissionDivId = "permission_div";

onRegistered(messaging, (installationId) => {
  console.log("Registered installation ID:", installationId);
  updateUIForPushEnabled(installationId);
});

onMessage(messaging, (payload) => {
  console.log("Message received. ", payload);
  const { notification } = payload;

  new Notification(notification.title, {
    body: notification.body,
  });
  console.log("Notification extracted. ", notification);
  appendNotification(notification);
});

function requestPermission() {
  console.log("Requesting permission...");
  Notification.requestPermission().then((permission) => {
    if (permission === "granted") {
      console.log("Notification permission granted.");
      resetUI();
    } else {
      console.log("Unable to get permission to notify.");
    }
  });
}

function showToken(currentToken) {
  const tokenElement = document.querySelector("#token");
  tokenElement.textContent = currentToken ?? "Loading...";
}

function showHideDiv(divId, show) {
  const div = document.querySelector("#" + divId);
  if (show) {
    div.style.display = "block";
  } else {
    div.style.display = "none";
  }
}

function resetUI() {
  clearMessages();
  showToken("Loading...");

  register(messaging, { vapidKey })
    .then(() => {})
    .catch((error) => {
      console.error("An error occurred while registering", error);
      showToken("Error retrieving Installation ID.");
    });
}

function updateUIForPushEnabled(currentToken) {
  showHideDiv(tokenDivId, true);
  showHideDiv(permissionDivId, false);
  showToken(currentToken);
}

function appendNotification(notification) {
  const messagesElement = document.querySelector("#notifications");
  const dataHeaderElement = document.createElement("h5");
  const dataElement = document.createElement("pre");
  dataElement.style.overflowX = "hidden;";
  dataHeaderElement.textContent = "Received notification:";
  dataElement.textContent = JSON.stringify(notification, null, 2);
  messagesElement.appendChild(dataHeaderElement);
  messagesElement.appendChild(dataElement);
}

function clearMessages() {
  const messagesElement = document.querySelector("#notifications");
  while (messagesElement.hasChildNodes()) {
    messagesElement.removeChild(messagesElement.lastChild);
  }
}

document
  .getElementById("request-permission-button")
  .addEventListener("click", requestPermission);

resetUI();
