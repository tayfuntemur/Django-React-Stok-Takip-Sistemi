import React, { useState } from 'react';


function Header() {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    console.log('Arama:', searchQuery);
    // TODO: Arama fonksiyonu eklenecek
  };

  const handleLogout = () => {
    // TODO: Logout işlemi
    console.log('Çıkış yapılıyor...');
  };

  return (
    <header className="header">
      <div className="header-left">
        <h1 className="page-title">Dashboard</h1>
      </div>

      <div className="header-center">
        <form className="search-form" onSubmit={handleSearch}>
          <input
            type="text"
            className="search-input"
            placeholder="Ürün, barkod veya kategori ara..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <button type="submit" className="search-btn">
            🔍
          </button>
        </form>
      </div>

      <div className="header-right">
        <div className="header-actions">
          {/* Bildirimler */}
          <button className="icon-btn" title="Bildirimler">
            <span className="icon">🔔</span>
            <span className="badge">3</span>
          </button>

          {/* Kullanıcı Menüsü */}
          <div className="user-menu">
            <div className="user-avatar">A</div>
            <div className="user-info">
              <div className="user-name">Admin</div>
              <div className="user-role">Yönetici</div>
            </div>
            <button className="dropdown-btn">▼</button>
          </div>

          {/* Çıkış */}
          <button className="logout-btn" onClick={handleLogout} title="Çıkış Yap">
            🚪
          </button>
        </div>
      </div>
    </header>
  );
}

export default Header;