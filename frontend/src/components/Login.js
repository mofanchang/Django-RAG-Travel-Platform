import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/accounts/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        // 儲存 token
        localStorage.setItem('token', data.token);
        alert('登入成功！');
        navigate('/');
        window.location.reload(); // 重新載入以更新導覽列
      } else {
        setError(data.message  '登入失敗');
      }
    } catch (err) {
      setError('登入失敗，請稍後再試');
      console.error('登入錯誤:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto mt-8">
      <div className="max-w-md mx-auto bg-white rounded shadow p-8">
        <h2 className="text-2xl font-bold mb-6 text-center">登入</h2>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 mb-2">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-600"
              required
            />
          </div>
          
          <div className="mb-6">
            <label className="block text-gray-700 mb-2">密碼</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-600"
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
          >
            {loading ? '登入中...' : '登入'}
          </button>
        </form>
        
        <p className="mt-4 text-center text-gray-600">
          還沒有帳號？
          <Link to="/register" className="text-blue-600 hover:underline ml-1">
            註冊
          </Link>
        </p>
      </div>
    </div>
  );
}
