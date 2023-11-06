const { initializeApp } = require('firebase/app');
const { getAuth, signInWithCustomToken } = require('firebase/auth');

const firebaseConfig = {
  apiKey: "AIzaSyAE2UmE-hWp_oujziTOLvFiRiB0z_o3yKI",
  authDomain: "user-management-system-994a9.firebaseapp.com",
  projectId: "user-management-system-994a9",
  storageBucket: "user-management-system-994a9.appspot.com",
  messagingSenderId: "461428496319",
  appId: "1:461428496319:web:ddcf836146a32aeb5f730a",
  measurementId: "G-G444JCL1VB"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
var user = "";

signInWithCustomToken(auth, process.argv.slice(2)[0])
  .then((userCredential) => {
    // Signed in
    user = userCredential.user;
    console.log(user);
  })
  .catch((error) => {
    const errorCode = error.code;
    const errorMessage = error.message;
  });