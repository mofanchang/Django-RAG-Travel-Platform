import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

export default function TripList() {
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTrips();
  }, []);

  const fetchTrips = async () => {
    try {
      setLoading(true);
      // 這裡可以根據需要調用不同的端點
      // 選項1: 獲取所有行程（需要實作）
      // 選項2: 使用 RAG 搜尋（暫時使用這個）
      const response = await fetch('http://localhost:5000/api/chat/recommend?query=推薦行程');
      
      if (!response.ok) {
        throw new Error('獲取行程失敗');
      }

      const data = await response.json();
      setTrips(data.recommendedTrips  []);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('獲取行程失敗:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = async (tripId) => {
    const token = localStorage.getItem('token');
    
    if (!token) {
      alert('請先登入');
      window.location.href = '/login';
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/api/cart/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          tripId: tripId,
          quantity: 1
        })
      });

      if (response.ok) {
        alert('已加入購物車！');
        // 觸發導覽列更新購物車數量
        window.dispatchEvent(new Event('cartUpdated'));
      } else {
        const data = await response.json();
        alert(data.message  '加入購物車失敗');
      }
    } catch (error) {
      console.error('加入購物車失敗:', error);
      alert('加入購物車失敗，請稍後再試');
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto mt-8 text-center">
        <p className="text-xl">載入中...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto mt-8 text-center">
        <p className="text-xl text-red-600">錯誤: {error}</p>
        <button 
          onClick={fetchTrips}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          重新載入
        </button>
      </div>
    );
  }

  return (
    <div className="container mx-auto mt-8">
      <h2 className="text-2xl font-bold mb-4">所有行程</h2>
      
      {trips.length === 0 ? (
        <p className="text-gray-600">目前沒有行程。</p>
      ) : (
        <ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {trips.map((trip) => (
            <li key={trip.id} className="bg-white rounded shadow p-4">
              {trip.image && (
                <img 
                  src={trip.image} 
                  alt={trip.name}
                  className="w-full h-48 object-cover rounded mb-3"
                />
              )}
              
              <h3 className="text-xl font-semibold mb-2">
                <Link 
                  to={`/trips/${trip.id}`} 
                  className="text-blue-600 hover:underline"
                >
                  {trip.name}
                </Link>
              </h3>
              
              <div className="mb-2 text-sm text-gray-600">
                <span>{trip.country}</span>
                {trip.city && <span> · {trip.city}</span>}
                {trip.duration && <span> · {trip.duration}天</span>}
              </div>
              
              <p className="mb-2 text-gray-700 line-clamp-2">
                {trip.description}
              </p>
              
              <p className="mb-2">
                價格：<span className="font-bold text-lg text-blue-600">
                  NT$ {trip.price?.toLocaleString()}
                </span>
              </p>
              
              {trip.keywords && (
                <div className="mb-3">
                  {trip.keywords.split(',').map((keyword, idx) => (
                    <span 
                      key={idx}
                      className="inline-block bg-gray-200 text-gray-700 text-xs px-2 py-1 rounded mr-1 mb-1"
                    >
                      {keyword.trim()}
                    </span>
                  ))}
                </div>
              )}
              
              <div className="flex space-x-2">
                <Link 
                  to={`/trips/${trip.id}`}
                  className="flex-1 text-center px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  查看詳情
                </Link>
                
                <button
                  onClick={() => handleAddToCart(trip.id)}
                  className="flex-1 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                >
                  加入購物車
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
