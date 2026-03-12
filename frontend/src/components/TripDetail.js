import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

export default function TripDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [trip, setTrip] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // 注意：目前 .NET API 沒有單一行程端點
    // 這裡使用 RAG 搜尋作為替代方案
    fetchTripDetail();
  }, [id]);

  const fetchTripDetail = async () => {
    try {
      setLoading(true);
      // TODO: 需要在 .NET API 實作 GET /api/trips/{id}
      // 暫時使用搜尋結果
      const response = await fetch(`http://localhost:5000/api/chat/recommend?query=行程`);
      
      if (!response.ok) {
        throw new Error('獲取行程失敗');
      }

      const data = await response.json();
      const foundTrip = data.recommendedTrips?.find(t => t.id === parseInt(id));
      
      if (foundTrip) {
        setTrip(foundTrip);
      } else {
        setError('找不到此行程');
      }
    } catch (err) {
      setError(err.message);
      console.error('獲取行程詳情失敗:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = async () => {
    const token = localStorage.getItem('token');
    
    if (!token) {
      alert('請先登入');
      navigate('/login');
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
          tripId: parseInt(id),
          quantity: 1
        })
      });

      if (response.ok) {
        alert('已加入購物車！');
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

  if (error  !trip) {
    return (
      <div className="container mx-auto mt-8 text-center">
        <p className="text-xl text-red-600">{error  '找不到此行程'}</p>
        <button 
          onClick={() => navigate('/trips')}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          返回行程列表
        </button>
      </div>
    );
  }

  return (
    <div className="container mx-auto mt-8">
      <div className="max-w-4xl mx-auto bg-white rounded shadow p-6">
        <h2 className="text-3xl font-bold mb-4">{trip.name}</h2>
        
        {trip.image && (
          <img 
            src={trip.image} 
            alt={trip.name}
            className="w-full h-96 object-cover rounded mb-6"
          />
        )}
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <h3 className="text-xl font-semibold mb-3">行程資訊</h3>
            <div className="space-y-2">
              <p>
                <span className="font-semibold">國家：</span>
                {trip.country}
              </p>
              {trip.city && (
                <p>
                  <span className="font-semibold">城市：</span>
                  {trip.city}
                </p>
              )}
              {trip.duration && (
                <p>
                  <span className="font-semibold">天數：</span>
                  {trip.duration} 天
                </p>
              )}
              {trip.startDate && (
                <p>
                  <span className="font-semibold">出發日：</span>
                  {new Date(trip.startDate).toLocaleDateString()}
                </p>
              )}
              {trip.endDate && (
                <p>
                  <span className="font-semibold">結束日：</span>
                  {new Date(trip.endDate).toLocaleDateString()}
                </p>
              )}
              {trip.availableSeats !== undefined && (
                <p>
                  <span className="font-semibold">剩餘名額：</span>
                  <span className={trip.availableSeats < 5 ? 'text-red-600' : ''}>
                    {trip.availableSeats} 位
                  </span>
                </p>
              )}
            </div>
          </div>
          
          <div>
            <h3 className="text-xl font-semibold mb-3">價格</h3>
            <p className="text-4xl font-bold text-blue-600 mb-4">
              NT$ {trip.price?.toLocaleString()}
            </p>
            
            {trip.keywords && (
              <div className="mb-4">
                <h4 className="font-semibold mb-2">標籤</h4>
                <div className="flex flex-wrap gap-2">
                  {trip.keywords.split(',').map((keyword, idx) => (
                    <span 
                      key={idx}
                      className="bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full"
                    >
                      {keyword.trim()}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
        
        <div className="mb-6">
          <h3 className="text-xl font-semibold mb-3">行程描述</h3>
          <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
            {trip.description}
          </p>
        </div>
        
        <div className="flex space-x-4">
          <button
            onClick={handleAddToCart}
            className="flex-1 px-8 py-3 bg-green-600 text-white text-lg rounded hover:bg-green-700 font-semibold"
            disabled={trip.availableSeats === 0}
          >
            {trip.availableSeats === 0 ? '已售完' : '加入購物車'}
          </button>
          
          <button
            onClick={() => navigate('/trips')}
            className="px-8 py-3 bg-gray-500 text-white rounded hover:bg-gray-600"
          >
            返回列表
          </button>
        </div>
      </div>
    </div>
  );
}
