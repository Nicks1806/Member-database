# TWS Member Database
> Trade With Suli — Internal Sales & CRM Tool  
> **Live:** https://tws-database.vercel.app  
> **Stack:** Vanilla JS · Supabase · Vercel

---

## Fitur

| Tab | Fitur |
|-----|-------|
| **Database Member** | Search by email/nama/HP · Filter membership type · Monitor expiry (7/30/90 hari) · Edit inline · Export CSV & Excel |
| **Follow Up** | 23K+ leads · Filter PIC/Source/Status · Reminder H+1/H+3/H+7 · Bulk update · Import CSV/paste · Export per filter |

---

## Cara Deploy

### Pertama kali
1. Fork / clone repo ini
2. Buka [vercel.com](https://vercel.com) → **Add New Project**
3. Import dari GitHub → pilih repo `tws-database`
4. Setting:
   - Framework: **Other**
   - Build Command: *(kosongkan)*
   - Output Directory: `.`
5. **Deploy** — selesai!

### Update data (rutin mingguan)
```
Kirim data baru ke Claude AI (CSV / xlsx / list nomor)
→ Claude update Supabase via API
→ Buka app → data langsung ter-refresh
(tidak perlu redeploy)
```

### Update kode / tampilan
```bash
# Edit index.html sesuai kebutuhan
git add index.html
git commit -m "update: deskripsi perubahan"
git push
# Vercel auto-deploy dalam ~15 detik
```

---

## Supabase Config

| Item | Value |
|------|-------|
| Project URL | `https://nfyqbkmvcaamwcpeiptp.supabase.co` |
| Tables | `members` · `followup` · `audit_log` |
| RLS | Enabled (anon read/write) |
| Sync | Polling 5 detik |

### Schema: `members`
```sql
id          uuid primary key
email       text
nama        text
phone       text
memberships jsonb   -- array of {name, start, exp, is_lifetime}
total       numeric
updated_at  timestamptz
```

### Schema: `followup`
```sql
id          uuid primary key
nama        text
email       text
phone       text
amount      text
pic         text        -- Calvin / Nick / Alif
status      text        -- Cold / Warm / Hot / Closing
progress    text        -- H+1 / H+3 / H+7 / H+14 / H+30
source      text        -- User Regis / Discord / User Pending
tanggal     date
updated_at  timestamptz
```

---

## Struktur File

```
tws-database/
├── index.html      ← Single file app (~800KB)
├── vercel.json     ← Vercel routing config
└── README.md       ← Ini
```

> ⚠️ Jangan split jadi multiple file. Tetap 1 `index.html`.

---

## Tim

| Nama | Role |
|------|------|
| Calvin | Sales Execution |
| Nick | Sales Execution |
| Alif | Sales Execution |
| Marcel | Head of Sales |

---

## Update Log

| Tanggal | Versi | Perubahan |
|---------|-------|-----------|
| Apr 2026 | v13 | Migrasi ke Supabase fetch (dari embedded data) · File 87% lebih kecil · Loading screen |
| Mar 2026 | v12 | Versi terakhir dengan data embedded |
