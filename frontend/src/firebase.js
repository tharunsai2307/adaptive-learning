// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics, isSupported } from "firebase/analytics";

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBdfSML-wUEhVkbthANeL9y0CzLWIDssW4",
  authDomain: "smart-waste-f7004.firebaseapp.com",
  databaseURL: "https://smart-waste-f7004-default-rtdb.firebaseio.com",
  projectId: "smart-waste-f7004",
  storageBucket: "smart-waste-f7004.firebasestorage.app",
  messagingSenderId: "1049334460388",
  appId: "1:1049334460388:web:25e8faf5fa017f396d21f1",
  measurementId: "G-CKZ12BL1E1"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Analytics conditionally to prevent issues in environments where analytics is not supported
let analytics = null;
if (typeof window !== "undefined") {
  isSupported().then((supported) => {
    if (supported) {
      analytics = getAnalytics(app);
    }
  }).catch((err) => {
    console.warn("Firebase Analytics not supported in this environment:", err);
  });
}

export { app, analytics, firebaseConfig };
export default app;
