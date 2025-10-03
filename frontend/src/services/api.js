import axios from 'axios';

// API base URL
const API_BASE_URL = 'http://localhost:8000/api';

// Axios instance oluştur
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Cookie'leri gönder (Django session için)
});

// API fonksiyonları
const apiService = {
  // Kategoriler
  getKategoriler: () => api.get('/kategoriler/'),
  getKategori: (id) => api.get(`/kategoriler/${id}/`),
  createKategori: (data) => api.post('/kategoriler/', data),
  updateKategori: (id, data) => api.put(`/kategoriler/${id}/`, data),
  deleteKategori: (id) => api.delete(`/kategoriler/${id}/`),

  // Ürünler
  getUrunler: () => api.get('/urunler/'),
  getUrun: (stokNo) => api.get(`/urunler/${stokNo}/`),
  createUrun: (data) => api.post('/urunler/', data),
  updateUrun: (stokNo, data) => api.put(`/urunler/${stokNo}/`, data),
  deleteUrun: (stokNo) => api.delete(`/urunler/${stokNo}/`),
  barkodAra: (barkod) => api.get(`/urunler/barkod_ara/?barkod=${barkod}`),
  dusukStok: (limit = 10) => api.get(`/urunler/dusuk_stok/?limit=${limit}`),

  // Satış Fişleri
  getSatisFisleri: () => api.get('/satis-fisleri/'),
  getSatisFisi: (id) => api.get(`/satis-fisleri/${id}/`),
  createSatisFisi: (data) => api.post('/satis-fisleri/', data),
  getBugunSatislar: () => api.get('/satis-fisleri/bugun/'),
  getSatisOzeti: () => api.get('/satis-fisleri/ozet/'),

  // Satışlar
  getSatislar: () => api.get('/satislar/'),
  createSatis: (data) => api.post('/satislar/', data),

  // Kasa 
  getKasa: () => api.get('/kasa/'),

  // Tedarikçiler
  getTedarikciler: () => api.get('/tedarikciler/'),
  
  // Ödeme
  getOdemeler: () => api.get('/odemeler/'),
  createOdeme: (data) => api.post('/odemeler/', data),
};

export default apiService;