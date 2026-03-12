import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

export default function Navbar() {
  const [user, setUser] = useState(null);
  const [cartCount, setCartCount] = useState(0);

  useEffect(() => {
    // 檢查是否已登入
    const token = localStorage.getItem('token');
    if (token) {
      fetchUserProfile(token);
      fetchCartCount(token);
    }
  }, []);

  const fetchUserProfile = async (token) => {
    try {
      const response = await fetch('http://localhost:5000/api/accounts/profile', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setUser(data);
      }
    } catch (error) {
      console.error('獲取使用者資料失敗:', error);
    }
  };

  const fetchCartCount = async (token) => {
    try {
      const response = await fetch('http://localhost:5000/api/cart', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setCartCount(data.totalItems  0);
      }
    } catch (error) {
      console.error('獲取購物車數量失敗:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setCartCount(0);
    window.location.href = '/';
  };

  return (
    <nav className="bg-blue-600 text-white p-4">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/" className="font-bold text-xl hover:text-blue-200">
          旅遊網站
        </Link>
        
        <div className="flex items-center space-x-4">
          <Link to="/trips" className="hover:underline">
            所有行程
          </Link>
          
          {user ? (
            <>
              <Link to="/cart" className="hover:underline relative">
                購物車
                {cartCount > 0 && (
                  <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    {cartCount}
                  </span>
                )}
              </Link>
              <Link to="/bookings" className="hover:underline">
                我的訂單
              </Link>
              <Link to="/profile" className="hover:underline">
                {user.username  user.email}
              </Link>
              <button 
                onClick={handleLogout}
                className="hover:underline bg-blue-700 px-3 py-1 rounded"
              >
                登出
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="hover:underline">
                登入
              </Link>
              <Link to="/register" className="hover:underline bg-blue-700 px-3 py-1 rounded">
                註冊
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
