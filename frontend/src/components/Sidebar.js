import React, { useState } from 'react';


function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const [activeMenu, setActiveMenu] = useState('dashboard');

  const menuItems = [
    {
      id: 'dashboard',
      label: 'Ana Sayfa',
      icon: '🏠',
      path: '/'
    },
    {
      id: 'urunler',
      label: 'Ürünler',
      icon: '📦',
      submenu: [
        { id: 'urun-liste', label: 'Ürün Listesi', path: '/urunler' },
        { id: 'urun-ekle', label: 'Yeni Ürün', path: '/urunler/yeni' }
      ]
    },
    {
      id: 'satislar',
      label: 'Satışlar',
      icon: '💰',
      submenu: [
        { id: 'satis-yap', label: 'Satış Yap', path: '/satis' },
        { id: 'satis-gecmis', label: 'Satış Geçmişi', path: '/satislar' }
      ]
    },
    {
      id: 'kasa',
      label: 'Kasa',
      icon: '🏦',
      submenu: [
        { id: 'kasa-durum', label: 'Kasa Durumu', path: '/kasa' },
        { id: 'odemeler', label: 'Ödemeler', path: '/odemeler' }
      ]
    },
    {
      id: 'raporlar',
      label: 'Raporlar',
      icon: '📊',
      submenu: [
        { id: 'envanter', label: 'Envanter', path: '/raporlar/envanter' },
        { id: 'muhasebe', label: 'Muhasebe', path: '/raporlar/muhasebe' }
      ]
    },
    {
      id: 'ayarlar',
      label: 'Ayarlar',
      icon: '⚙️',
      path: '/ayarlar'
    }
  ];

  const [openSubmenu, setOpenSubmenu] = useState(null);

  const toggleSubmenu = (itemId) => {
    setOpenSubmenu(openSubmenu === itemId ? null : itemId);
  };

  return (
    <div className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      {/* Logo ve Toggle */}
      <div className="sidebar-header">
        <div className="logo">
          {!collapsed && <span className="logo-text">Stok Takip</span>}
          {collapsed && <span className="logo-icon">ST</span>}
        </div>
        <button 
          className="toggle-btn"
          onClick={() => setCollapsed(!collapsed)}
        >
          {collapsed ? '→' : '←'}
        </button>
      </div>

      {/* Menü */}
      <nav className="sidebar-nav">
        {menuItems.map(item => (
          <div key={item.id} className="menu-item-wrapper">
            <div
              className={`menu-item ${activeMenu === item.id ? 'active' : ''}`}
              onClick={() => {
                if (item.submenu) {
                  toggleSubmenu(item.id);
                } else {
                  setActiveMenu(item.id);
                }
              }}
            >
              <span className="menu-icon">{item.icon}</span>
              {!collapsed && (
                <>
                  <span className="menu-label">{item.label}</span>
                  {item.submenu && (
                    <span className="submenu-arrow">
                      {openSubmenu === item.id ? '▼' : '▶'}
                    </span>
                  )}
                </>
              )}
            </div>

            {/* Alt Menü */}
            {item.submenu && openSubmenu === item.id && !collapsed && (
              <div className="submenu">
                {item.submenu.map(subItem => (
                  <div
                    key={subItem.id}
                    className={`submenu-item ${activeMenu === subItem.id ? 'active' : ''}`}
                    onClick={() => setActiveMenu(subItem.id)}
                  >
                    {subItem.label}
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </nav>

      {/* Alt Kısım */}
      {!collapsed && (
        <div className="sidebar-footer">
          <div className="user-info">
            <div className="user-avatar">A</div>
            <div className="user-details">
              <div className="user-name">Admin</div>
              <div className="user-role">Yönetici</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Sidebar;