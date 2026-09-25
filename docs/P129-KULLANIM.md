# P129 Qwen araştırma gösterimi

Tam research release içinde Qwen tabanı, tüm 12 checkpoint ve sentetik veriler vardır. Python 3.11, NVIDIA CUDA ve yeterli RAM/VRAM gerekir; RTX 4070 üzerinde denenmiştir. Native CLI için bunlar gerekmez.

```cmd
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install torch==2.10.0 --index-url https://download.pytorch.org/whl/cu128
.venv\Scripts\python.exe -m pip install -r requirements-p129.txt
set "TURKTOKENIZER_PYTHON=%CD%\.venv\Scripts\python.exe"
DEMO_YONT.cmd
```

Kurulum bağımlılık indirir; gösterim yerel modelle çevrimdışıdır. Serbest sohbet arayüzü değildir; donmuş değerlendirme sorusunun native analizi yeniden yapılıp aynı BPE/özellik/kenarlar kontrol edilir. `--index 10 --arm graph --seed 12937` veya `--arm plain` seçenekleri kullanılabilir. Yeniden eğitim otomatik başlamaz. Tarihsel run.py bütün yerel arşiv bağımlılıklarını bekler; yeni eğitim için ayrı deney klasörü ve kayıtlar hazırlanmalıdır.
