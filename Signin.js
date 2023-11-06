const { initializeApp } = require('firebase/app');
const { getAuth, signInWithCustomToken } = require('firebase/auth');

const firebaseConfig = {
  //''' your firebase configuration
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