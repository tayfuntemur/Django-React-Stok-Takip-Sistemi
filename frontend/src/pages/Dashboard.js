import React, { useState, useEffect } from 'react';
import StatCard from '../components/StatCard';
import apiService from '../services/api';

function Dashboard() {
  const [stats, setStats] = useState({
    bugun: 0,
    bu_ay: 0,
    fis_sayisi: 0
  });
  const [kasaBakiye, setKasaBakiye] = useState(0);
  const [toplamUrun, setToplamUrun] = useState(0);
  const [dusukStok, setDusukStok] = useState(0);
  const [sonSatislar, setSonSatislar] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [satisOzeti, kasa, urunler, dusuk, bugunSatis] = await Promise.all([
        apiService.getSatisOzeti(),
        apiService.getKasa(),
        apiService.getUrunler(),
        apiService.dusukStok(10),
        apiService.getBugunSatislar()
      ]);

      setStats(satisOzeti.data);
      setKasaBakiye(kasa.data.length > 0 ? parseFloat(kasa.data[0].bakiye) : 0);
      setToplamUrun(urunler.data.length);
      setDusukStok(dusuk.data.length);
      setSonSatislar(bugunSatis.data.slice(0, 5));
      setLoading(false);
    } catch (error) {
      console.error('Dashboard yüklenirken hata:', error);
      setLoading(false);
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <button className="btn btn-primary" onClick={loadDashboardData}>
          🔄 Yenile
        </button>
      </div>

      <div className="stat-grid">
        <StatCard
          title="Bugünkü Satış"
          value={`${stats.bugun.toLocaleString('tr-TR')} TL`}
          icon="💰"
          color="#00A65A"
          loading={loading}
        />
        <StatCard
          title="Toplam Ürün"
          value={toplamUrun}
          icon="📦"
          color="#3C8DBC"
          loading={loading}
        />
        <StatCard
          title="Kasa Bakiye"
          value={`${kasaBakiye.toLocaleString('tr-TR')} TL`}
          icon="🏦"
          color="#FF6000"
          loading={loading}
        />
        <StatCard
          title="Düşük Stok"
          value={`${dusukStok} Ürün`}
          icon="⚠️"
          color="#DD4B39"
          loading={loading}
        />
      </div>

      <div className="dashboard-section">
        <div className="section-header">
          <h2>Bugünkü Satışlar</h2>
          <span className="badge-count">{sonSatislar.length} Fiş</span>
        </div>

        {loading ? (
          <div className="loading-message">Yükleniyor...</div>
        ) : sonSatislar.length === 0 ? (
          <div className="empty-message">Bugün henüz satış yapılmamış.</div>
        ) : (
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Fiş No</th>
                  <th>Toplam Tutar</th>
                  <th>Saat</th>
                </tr>
              </thead>
              <tbody>
                {sonSatislar.map(fis => (
                  <tr key={fis.id}>
                    <td>#{fis.fis_no}</td>
                    <td className="amount">{parseFloat(fis.toplam_tutar).toLocaleString('tr-TR')} TL</td>
                    <td>{new Date(fis.olusturma_tarihi).toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;