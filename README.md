# Bank Statement Manager
Banka Ekstre Yükleme, Yönetimi ve KPI Tabanlı Finansal Raporlama Platformu
Bank Statement Manager; kurumsal firmaların banka ekstrelerini güvenli bir şekilde yükleyebildiği, sınıflandırabildiği ve finansal performans göstergelerini (KPI) gerçek zamanlı olarak takip edebildiği modern bir ekstre yönetim ve analitik çözümüdür.

Sistem; Django REST Framework tabanlı ölçeklenebilir bir backend mimarisi ile Next.js üzerinde inşa edilen dinamik ve yüksek performanslı bir frontend arayüzünü bir araya getirir.
Bu yapı sayesinde kullanıcılar, çoklu banka hesaplarını tek noktadan yönetebilir, ekstre verilerini otomatik olarak yorumlayabilir ve gelir-gider akışlarını KPI dashboard’ları üzerinden analiz ederek karar alma süreçlerini hızlandırabilir.

## Özellikler

- **CSV İçe Aktarma**: Banka ekstrelerini CSV formatında yükleyin
- **Otomatik Kategorileme**: İşlemler otomatik olarak kategorilere ayrılır
- **Para Birimi Dönüştürme**: Çoklu para birimi desteği ve dönüştürme
- **Finansal Raporlar**: Detaylı finansal analiz ve raporlar
- **Haftalık Raporlar**: Celery ile otomatik haftalık e-posta raporları
- **JWT Kimlik Doğrulama**: Güvenli kullanıcı kimlik doğrulama
- **Modern UI**: Tailwind CSS ile modern ve responsive arayüz
- **Türkçe Arayüz**: Tam Türkçe kullanıcı arayüzü

## Teknolojiler

### Backend
- Django 4.2.7
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- JWT Authentication

### Frontend
- Next.js 14
- TypeScript
- Tailwind CSS
- Axios

## Kurulum

### Gereksinimler
- Python 3.13+
- Node.js 18+
- Docker & Docker Compose (PostgreSQL ve Redis için)
- PostgreSQL 15 (veya Docker ile)

### Backend Kurulumu

1. Repository'yi klonlayın:
```bash
git clone https://github.com/Sarizeybekk/bank-statement-manager.git
cd bank-statement-manager
```

2. Virtual environment oluşturun:
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Bağımlılıkları yükleyin:
```bash
pip install -r requirements.txt
```

4. Environment dosyasını oluşturun:
```bash
.env
```

5. `.env` dosyasını düzenleyin ve veritabanı bilgilerinizi girin.

6. Docker Compose ile PostgreSQL ve Redis'i başlatın:
```bash
docker-compose up -d db redis
```

7. Veritabanı migration'larını çalıştırın:
```bash
python manage.py migrate
```

8. Django sunucusunu başlatın:
```bash
python manage.py runserver
```

### Frontend Kurulumu

1. Frontend klasörüne gidin:
```bash
cd frontend
```

2. Bağımlılıkları yükleyin:
```bash
npm install
```

3. Development sunucusunu başlatın:
```bash
npm run dev
```

Frontend `http://localhost:3000` adresinde çalışacaktır.

## Celery Worker ve Beat

Haftalık raporlar için Celery worker ve beat servislerini başlatın:

```bash
celery -A config worker -l info
celery -A config beat -l info
```

Veya Docker Compose ile:
```bash
docker-compose up -d celery celery-beat
```

## API Dokümantasyonu

API dokümantasyonuna erişmek için:
- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`

## CSV Formatı

CSV dosyası şu sütunları içermelidir:
- `date`: Tarih (YYYY-MM-DD formatında)
- `amount`: Tutar (sayısal değer)
- `currency`: Para birimi (TRY, USD, EUR, vb.)
- `description`: Açıklama
- `type`: İşlem türü (`credit` veya `debit`)

Örnek:
```csv
date,amount,currency,description,type
2025-07-01,4500.00,TRY,"Satış: Fatura #1023",credit
2025-07-02,-1200.00,TRY,"Kira Ödemesi",debit
```

## Test

Testleri çalıştırmak için:
```bash
pytest
```
<img width="1832" height="2644" alt="image" src="https://github.com/user-attachments/assets/5561f1c5-a11d-4e8e-ba20-37820b259a69" />



