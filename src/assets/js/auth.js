import { ref } from 'vue';
import { auth, signOut as firebaseSignOut } from './firebase';
import { onAuthStateChanged } from 'firebase/auth';


export const currentUser = ref(null);

onAuthStateChanged(auth, (user) => {
    currentUser.value = user;
});


export const logout = async () => {
  try {
    await firebaseSignOut(auth); 
    localStorage.removeItem('hasWelcomed'); 
    currentUser.value = null; 
  } catch (error) {
    console.error('Error logging out:', error);
  }
};
