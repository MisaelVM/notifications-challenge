importScripts(
  "https://www.gstatic.com/firebasejs/12.17.1/firebase-app-compat.js",
);
importScripts(
  "https://www.gstatic.com/firebasejs/12.17.1/firebase-messaging-compat.js",
);

firebase.initializeApp({
  apiKey: "AIzaSyC_likyA_fN8wAh6llHYwXCB1GSjRCffUU",
  authDomain: "test-project-a9235.firebaseapp.com",
  projectId: "test-project-a9235",
  storageBucket: "test-project-a9235.firebasestorage.app",
  messagingSenderId: "358837086105",
  appId: "1:358837086105:web:1cbd20af2a6e71e7d81508",
});

const messaging = firebase.messaging();

/*
import { initializeApp } from "https://www.gstatic.com/firebasejs/12.17.1/firebase-app.js";
import { getMessaging } from "https://www.gstatic.com/firebasejs/12.17.1/firebase-messaging.js";

const firebaseApp = initializeApp({
  apiKey: "AIzaSyC_likyA_fN8wAh6llHYwXCB1GSjRCffUU",
  authDomain: "test-project-a9235.firebaseapp.com",
  projectId: "test-project-a9235",
  storageBucket: "test-project-a9235.firebasestorage.app",
  messagingSenderId: "358837086105",
  appId: "1:358837086105:web:1cbd20af2a6e71e7d81508",
});

const messaging = getMessaging(firebaseApp);
*/

messaging.onBackgroundMessage(function (payload) {
  console.log(
    "[firebase-messaging-sw.js] Received background message ",
    payload,
  );
  // Customize notification here
  const notificationTitle = "Background Message Title";
  const notificationOptions = {
    body: "Background Message body.",
    icon: "/firebase-logo.png",
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});
