# Todo
- Profile Logged user & Password Change // Done
- Link to print QR Code on Siswa Dashboard // Done
- Groups Decorators Permission // Done
- Login Middleware for Logged // Done
- Saparate Pages for Absensi Masuk & Pulang // Done
- Jadwal Page // Done
- Database Seeder for Jadwals // Done
- Group siswa button on Angkatan & Absensi // Done
- Import Absensi Data as Excel // Done

## Install Dependency
```
pip install -r requirements.txt
```

## Seed Jadwal Data
```
python manage.py dumpdata app.Jadwal --output Jadwal.json
```

```
python manage.py loaddata Jadwal.json 
```