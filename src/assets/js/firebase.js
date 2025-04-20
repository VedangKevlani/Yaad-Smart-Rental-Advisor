import { initializeApp } from 'firebase/app';
import { getAuth, signOut } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyCmvC6bBCJLMkZ5L4EGVFWw_BaHx6cQLT4",
  authDomain: "yaad-smart-rental-advisor.firebaseapp.com",
  projectId: "yaad-smart-rental-advisor",
  storageBucket: "yaad-smart-rental-advisor.appspot.com",
  messagingSenderId: "837879500073",
  appId: "1:837879500073:web:9e8693eefc420a78b9fb38",
  measurementId: "G-6QXJZ4L3T1"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

export { auth, db, signOut };