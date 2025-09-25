import { getFirestore, collection, addDoc, getDocs, doc, updateDoc, deleteDoc, query, orderBy, serverTimestamp } from 'firebase/firestore';
import { getAuth } from 'firebase/auth';
import { app } from '@/firebase.js';

export const dashboardService = {
  async saveDashboard(dashboardData) {
    try {
      const auth = getAuth(app);
      const user = auth.currentUser;
      
      if (!user) {
        throw new Error('User must be logged in to save dashboards');
      }

      const db = getFirestore(app);
      const dashboardsRef = collection(db, 'users', user.uid, 'dashboards');

      // Add timestamp and user info
      const dashboardWithMeta = {
        ...dashboardData,
        createdAt: serverTimestamp(),
        updatedAt: serverTimestamp(),
        userId: user.uid,
        userName: user.displayName || user.email
      };

      const docRef = await addDoc(dashboardsRef, dashboardWithMeta);
      return { id: docRef.id, ...dashboardWithMeta };
    } catch (error) {
      console.error('Error saving dashboard:', error);
      throw error;
    }
  },

  async getDashboards() {
    try {
      const auth = getAuth(app);
      const user = auth.currentUser;
      
      if (!user) {
        throw new Error('User must be logged in to fetch dashboards');
      }

      const db = getFirestore(app);
      const dashboardsRef = collection(db, 'users', user.uid, 'dashboards');
      const q = query(dashboardsRef, orderBy('updatedAt', 'desc'));
      const snapshot = await getDocs(q);
      
      return snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
    } catch (error) {
      console.error('Error fetching dashboards:', error);
      throw error;
    }
  },

  async updateDashboard(dashboardId, updates) {
    try {
      const auth = getAuth(app);
      const user = auth.currentUser;
      
      if (!user) {
        throw new Error('User must be logged in to update dashboards');
      }

      const db = getFirestore(app);
      const dashboardRef = doc(db, 'users', user.uid, 'dashboards', dashboardId);
      
      await updateDoc(dashboardRef, {
        ...updates,
        updatedAt: serverTimestamp()
      });
    } catch (error) {
      console.error('Error updating dashboard:', error);
      throw error;
    }
  },

  async deleteDashboard(dashboardId) {
    try {
      const auth = getAuth(app);
      const user = auth.currentUser;
      
      if (!user) {
        throw new Error('User must be logged in to delete dashboards');
      }

      const db = getFirestore(app);
      const dashboardRef = doc(db, 'users', user.uid, 'dashboards', dashboardId);
      
      await deleteDoc(dashboardRef);
    } catch (error) {
      console.error('Error deleting dashboard:', error);
      throw error;
    }
  }
};
