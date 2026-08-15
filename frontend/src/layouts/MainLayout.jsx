import React from 'react';
import Navbar from '../components/Navbar';

export default function MainLayout({ children }) {
  return (
    <div className="main-layout">
      <Navbar />
      <main className="content-container">
        {children}
      </main>
    </div>
  );
}
