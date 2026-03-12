import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';

export default function Cart() {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchCart();
  }, []);

  const fetchCart = async () => {
    const token = localStorage.getItem('token');
    
    if (!token) {
      navigate('/login');
      return;
    }

    try {
      setLoading(true);
      const response = await fetch('http://localhost:5000/api/cart', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('獲取購物車失敗');
      }

      const data = await response.json();
      setCart(data);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('獲取購物車失敗:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateQuantity = async (itemId, quantity) => {
    const token = localStorage.getItem('token');

    try {
      const response = await fetch(`http://localhost:5000/api/cart/items/${itemId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ quantity })
      });

      if (response.ok) {
        fetchCart(); // 重新載入購物車
      } else {
        const data = await response.json();
        alert(data.message  '更新數量失敗');
      }
    } catch (error) {
      console.error('更新數量失敗:', error);
      alert('更新數量失敗，請稍後再試');
    }
  };

  const handleRemoveItem = async (itemId) => {
    const token = localStorage.getItem('token');

    if (!window.confirm('確定要移除此商品嗎？')) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:5000/api/cart/items/${itemId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        fetchCart(); // 重新載入購物車
        window.dispatchEvent(new Event('cartUpdated'));
      } else {
        const data = await response.json();
        alert(data.message  '移除商品失敗');
      }
    } catch (error) {
      console.error('移除商品失敗:', error);
      alert('移除商品失敗，請稍後再試');
    }
  };

  const handleClearCart = async () => {
    const token = localStorage.getItem('token');

    if (!window.confirm('確定要清空購物車嗎？')) {
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/api/cart/clear', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        fetchCart(); // 重新載入購物車
        window.dispatchEvent(new Event('cartUpdated'));
      } else {
        const data = await response.json();
        alert(data.message  '清空購物車失敗');
      }
    } catch (error) {
      console.error('清空購物車失敗:', error);
      alert('清空購物車失敗，請稍後再試');
    }
  };

  const handleCheckout = async () => {
    const token = localStorage.getItem('token');

    try {
      const response = await fetch('http://localhost:5000/api/cart/checkout', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        alert('結帳成功！訂單編號：' + data.booking.id);
        navigate('/bookings');
      } else {
        const data = await response.json();
        alert(data.message  '結帳失敗');
      }
    } catch (error) {
      console.error('結帳失敗:', error);
      alert('結帳失敗，請稍後再試');
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
      </div>
    );
  }

  return (
    <div className="container mx-auto mt-8">
      <h2 className="text-2xl font-bold mb-4">購物車</h2>

      {!cart  cart.items.length === 0 ? (
        <div className="bg-white rounded shadow p-6 text-center">
          <p className="text-gray-600 mb-4">購物車是空的</p>
          <Link 
            to="/trips"
            className="inline-block px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            去逛逛行程
          </Link>
        </div>
      ) : (
        <>
          <div className="bg-white rounded shadow p-6 mb-6">
            <ul className="divide-y">
              {cart.items.map((item) => (
                <li key={item.id} className="py-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold mb-2">
                        <Link 
                          to={`/trips/${item.tripId}`}
                          className="text-blue-600 hover:underline"
                        >
                          {item.tripName}
                        </Link>
                      </h3>
                      
                      {item.trip && (
                        <div className="text-sm text-gray-600 mb-2">
                          <span>{item.trip.country}</span>
                          {item.trip.city && <span> · {item.trip.city}</span>}
                          {item.trip.duration && <span> · {item.trip.duration}天</span>}
                        </div>
                      )}
                      
                      <p className="text-gray-700">
                        單價: NT$ {item.price.toLocaleString()}
                      </p>
                      
                      <div className="flex items-center mt-2">
                        <label className="mr-2">數量:</label>
                        <select
                          value={item.quantity}
                          onChange={(e) => handleUpdateQuantity(item.id, parseInt(e.target.value))}
                          className="border rounded px-2 py-1"
                        >
                          {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(num => (
                            <option key={num} value={num}>{num}</option>
                          ))}
                        </select>
                      </div>
                    </div>
                    
                    <div className="text-right ml-4">
                      <p className="text-xl font-bold text-blue-600 mb-2">
                        NT$ {item.subtotal.toLocaleString()}
                      </p>
                      <button
                        onClick={() => handleRemoveItem(item.id)}
                        className="text-red-500 hover:text-red-700 text-sm"
                      >
                        移除
                      </button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>

          <div className="bg-white rounded shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <span className="text-lg">總計:</span>
              <span className="text-2xl font-bold text-blue-600">
                NT$ {cart.totalPrice.toLocaleString()}
              </span>
            </div>
            
            <div className="flex space-x-4">
              <button
                onClick={handleCheckout}
                className="flex-1 px-6 py-3 bg-blue-600 text-white rounded hover:bg-blue-700 font-semibold"
              >
                前往結帳
              </button>
              
              <button
                onClick={handleClearCart}
                className="px-6 py-3 bg-gray-500 text-white rounded hover:bg-gray-600"
              >
                清空購物車
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
