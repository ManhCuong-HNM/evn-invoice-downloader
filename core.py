# FILE: D:\TEST_1\core.py
import time, os, base64, requests, json, glob, zipfile, shutil, re, sys
import pandas as pd
import pdfplumber
from PIL import Image, ImageOps
import numpy as np
import onnxruntime as ort
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

os.environ['WDM_SSL_VERIFY'] = '0'        # Bỏ qua lỗi chứng chỉ SSL
os.environ['WDM_LOG_LEVEL'] = '0'         # Tắt log rác của driver manager

# --- CẤU HÌNH CAPTCHA OFFLINE ---
CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
IDX_TO_CHAR = {i: c for i, c in enumerate(CHARS)}
_GLOBAL_ORT_SESSION = None

def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()

def get_model_path():
    app_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Mặc định sử dụng model Premium xịn nhất
    model_type = "Premium"
    try:
        config_path = os.path.join(app_dir, "config.json")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                model_type = cfg.get("model_type", "Premium").strip()
    except:
        pass
        
    # 1. Ưu tiên lấy từ thư mục con tương ứng (Lite / Standard / Premium)
    sub_path = os.path.join(app_dir, "models", model_type, "captcha_model.onnx")
    if os.path.exists(sub_path):
        return sub_path
        
    # 2. Dự phòng 1: Thư mục models chính ngoài
    local_path = os.path.join(app_dir, "models", "captcha_model.onnx")
    if os.path.exists(local_path):
        return local_path
        
    # 3. Dự phòng 2: File cùng cấp thư mục chạy
    return os.path.join(app_dir, "captcha_model.onnx")

def predict_captcha_onnx(image_path):
    """
    Giải captcha sử dụng mô hình ONNX offline.
    """
    global _GLOBAL_ORT_SESSION
    try:
        if not os.path.exists(image_path):
            return "", 0.0
            
        # 1. Đọc ảnh và tiền xử lý
        img = Image.open(image_path).convert('RGB')
        if img.size != (206, 74):
            img = img.resize((206, 74), Image.Resampling.LANCZOS)
        
        arr_rgb = np.array(img, dtype=np.float32)
        r = arr_rgb[:, :, 0]
        g = arr_rgb[:, :, 1]
        b = arr_rgb[:, :, 2]
        
        intensity = b - np.maximum(r, g)
        intensity = np.clip(intensity, 0.0, 255.0)
        
        gray_arr = 255.0 - intensity
        gray_arr = np.clip(gray_arr, 0.0, 255.0).astype(np.uint8)
        gray_img = Image.fromarray(gray_arr, mode='L')
        gray_img = ImageOps.autocontrast(gray_img, cutoff=2)
        
        img_arr = np.array(gray_img, dtype=np.float32) / 255.0
        img_arr = np.clip(img_arr, 0.0, 1.0)
        img_tensor = np.expand_dims(np.expand_dims(img_arr, axis=0), axis=0)
        
        # 2. Khởi tạo session toàn cục duy nhất
        if _GLOBAL_ORT_SESSION is None:
            onnx_model_path = get_model_path()
            if not os.path.exists(onnx_model_path):
                print(f"❌ Không tìm thấy file model tại: {onnx_model_path}")
                return "", 0.0
                
            sess_options = ort.SessionOptions()
            sess_options.intra_op_num_threads = 1
            sess_options.inter_op_num_threads = 1
            sess_options.enable_cpu_mem_arena = False
            sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_BASIC
            _GLOBAL_ORT_SESSION = ort.InferenceSession(onnx_model_path, sess_options, providers=['CPUExecutionProvider'])
        
        # 3. Dự đoán
        input_name = _GLOBAL_ORT_SESSION.get_inputs()[0].name
        preds = _GLOBAL_ORT_SESSION.run(None, {input_name: img_tensor})
        
        # 4. Giải mã
        predicted_chars = []
        confidences = []
        for pred in preds:
            probs = softmax(pred[0])
            char_idx = np.argmax(probs)
            predicted_chars.append(IDX_TO_CHAR[char_idx])
            confidences.append(probs[char_idx])
            
        code = "".join(predicted_chars)
        avg_conf = float(np.mean(confidences) * 100)
        return code, avg_conf
    except Exception as e:
        print(f"⚠️ Lỗi giải captcha AI offline: {e}")
        return "", 0.0

def rename_latest_file_strict(folder, exact_name):
    time.sleep(2)
    files = [f for f in glob.glob(os.path.join(folder, "*")) if os.path.isfile(f)]
    if not files: return None
    latest = max(files, key=os.path.getctime)
    while any(latest.endswith(ext) for ext in [".crdownload", ".tmp", ".download"]):
        time.sleep(1)
        files = [f for f in glob.glob(os.path.join(folder, "*")) if os.path.isfile(f)]
        latest = max(files, key=os.path.getctime)
    dst = os.path.join(folder, exact_name)
    if os.path.exists(dst): os.remove(dst)
    try: os.rename(latest, dst); return dst
    except: return None

# --- CHỨC NĂNG 1: TẢI HÓA ĐƠN (OFFLINE-FIRST MODE) ---
def run_process_gui(excel_path, folder, month, year, browser_type, headless=False):
    print(f"🚀 KHỞI ĐỘNG HỆ THỐNG (Browser: {browser_type}, Headless: {headless})")
    dr = None
    try:
        df = pd.read_excel(excel_path)
        print(f"📊 Danh sách: {len(df)} tài khoản.")
        
        # --- CẤU HÌNH CHO PHÉP TẢI NHIỀU FILE LIÊN TỤC ---
        prefs = {
            "download.default_directory": folder.replace("/", "\\"),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True,
            # CHÌA KHÓA: Cho phép tự động tải nhiều file (1 = Allow, 2 = Block)
            "profile.default_content_setting_values.automatic_downloads": 1 
        }

        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

        if browser_type == "Chrome":
            opt = webdriver.ChromeOptions()
            opt.add_experimental_option("prefs", prefs)
            
            # --- CÁC TRICK LÁCH LUẬT CHỐNG BOT CHO CHROME ---
            opt.add_argument("--disable-blink-features=AutomationControlled")
            opt.add_experimental_option("excludeSwitches", ["enable-automation"])
            opt.add_experimental_option('useAutomationExtension', False)
            opt.add_argument(f"user-agent={user_agent}")
            
            if headless: 
                opt.add_argument("--headless=new")
                opt.add_argument("--window-size=1920,1080")
                
            try:
                service = ChromeService(ChromeDriverManager().install())
            except:
                service = ChromeService()
            dr = webdriver.Chrome(service=service, options=opt)
            dr.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            })
            
        else:
            opt = webdriver.EdgeOptions()
            opt.add_experimental_option("prefs", prefs)
            
            # --- CÁC TRICK LÁCH LUẬT CHỐNG BOT CHO EDGE ---
            opt.add_argument("--disable-blink-features=AutomationControlled")
            opt.add_experimental_option("excludeSwitches", ["enable-automation"])
            opt.add_experimental_option('useAutomationExtension', False)
            opt.add_argument(f"user-agent={user_agent}")
            
            if headless: 
                opt.add_argument("--headless=new") # Edge hỗ trợ headless=new tốt hơn bản cũ
                opt.add_argument("--window-size=1920,1080")
                
            try:
                service = EdgeService(EdgeChromiumDriverManager().install())
            except:
                service = EdgeService()
            dr = webdriver.Edge(service=service, options=opt)
            dr.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            })

        dr.maximize_window()
        wait = WebDriverWait(dr, 15)
        
        for idx, row in df.iterrows():
            u, p = str(row.iloc[0]).strip(), str(row.iloc[1]).strip()
            print(f"\n👤 [{idx+1}/{len(df)}] Xử lý: {u}")
            
            try:
                # Tải cấu hình confidence_threshold động từ config.json
                conf_threshold = 80.0
                try:
                    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
                    if os.path.exists(config_path):
                        with open(config_path, "r", encoding="utf-8") as f:
                            cfg = json.load(f)
                            conf_threshold = float(cfg.get("confidence_threshold", 80.0))
                except:
                    pass
                    
                login_success = False
                max_attempts = 15
                
                for attempt in range(1, max_attempts + 1):
                    # Mỗi lần thử lại, mở lại trang để lấy captcha mới
                    dr.get("https://cskh.npc.com.vn/DichVuTTCSKH/IndexNPC?index=2")
                    try:
                        wait.until(EC.element_to_be_clickable((By.ID, "btnTaiKhoan"))).click()
                        user_input = wait.until(EC.visibility_of_element_located((By.ID, "frmDangKy_TenDangNhap_DN")))
                        user_input.clear()
                        user_input.send_keys(u)
                        
                        pass_input = dr.find_element(By.ID, "frmDangKy_MatKhau_DN")
                        pass_input.clear()
                        pass_input.send_keys(p)
                    except Exception:
                        time.sleep(1.5)
                        continue
                    
                    # Chụp ảnh captcha
                    timestamp = time.strftime("%H%M%S")
                    cp = os.path.join(folder, f"captcha_{u}_{timestamp}.png")
                    try:
                        captcha_el = dr.find_element(By.ID, "CaptchaImage")
                        for _ in range(10):
                            size = captcha_el.size
                            if size.get('width', 0) > 0 and size.get('height', 0) > 0:
                                break
                            time.sleep(0.2)
                        captcha_el.screenshot(cp)
                    except Exception:
                        continue
                    
                    # Báo log tối giản lên giao diện
                    print("🤖 Đang giải mã...")
                    ct, conf = predict_captcha_onnx(cp)
                    
                    # Nếu giải lỗi hoặc độ tự tin dưới ngưỡng, âm thầm thử lại lượt khác (không in log rác)
                    if not ct or conf < conf_threshold:
                        try: os.remove(cp)
                        except: pass
                        continue
                    
                    # Điền captcha và bấm Đăng nhập
                    try:
                        inp = dr.find_element(By.ID, "CaptchaInputText")
                        inp.clear()
                        inp.send_keys(ct)
                        dr.find_element(By.CSS_SELECTOR, ".btn.btn-primary.btn-send-contact").click()
                        time.sleep(2.5) # Đợi web chuyển hướng đăng nhập
                    except Exception:
                        try: os.remove(cp)
                        except: pass
                        continue
                    
                    # Xử lý Alert thông báo lỗi của EVN
                    has_alert = False
                    is_wrong_credentials = False
                    try:
                        alert = dr.switch_to.alert
                        alert_text = alert.text
                        alert.accept()
                        has_alert = True
                        
                        # Phát hiện nếu SAI MẬT KHẨU/TÀI KHOẢN thật để dừng thử lại sớm
                        if "mật khẩu" in alert_text.lower() or "tên đăng nhập" in alert_text.lower() or "không đúng" in alert_text.lower():
                            is_wrong_credentials = True
                    except:
                        pass
                    
                    if has_alert:
                        try: os.remove(cp)
                        except: pass
                        
                        if is_wrong_credentials:
                            break # Dừng thử lại lập tức do sai mật khẩu thật
                        continue # Thử lại captcha mới dưới nền
                    
                    # Kiểm tra trạng thái đăng nhập thành công
                    dr.get("https://cskh.npc.com.vn/DichVuTTCSKH/IndexNPC?index=2")
                    try:
                        wait.until(EC.presence_of_element_located((By.ID, "frmHoaDon_ThangHoaDon")))
                        print("✨ Đã giải mã được...")
                        print(f"✅ Đăng nhập thành công: {u}")
                        login_success = True
                        try: os.remove(cp)
                        except: pass
                        break
                    except Exception:
                        try: os.remove(cp)
                        except: pass
                        continue
                
                # Kết thúc lượt thử tài khoản hiện tại
                if not login_success:
                    print(f"🚫 Đăng nhập thất bại (Sai pass/captcha): {u}")
                    dr.delete_all_cookies()
                    continue

                val_m = str(int(month))
                Select(dr.find_element(By.ID, "frmHoaDon_ThangHoaDon")).select_by_value(val_m)
                Select(dr.find_element(By.ID, "frmHoaDon_NamHoaDon")).select_by_value(str(year))
                dr.find_element(By.ID, "frmHoaDon_frmIdButtonTimKiem").click()
                
                # Xóa phần html debug (vì không cần nữa)
                # Đợi tối đa 20 giây để bảng hóa đơn load (EVN đôi khi load rất chậm)
                btns = []
                for _ in range(20):
                    time.sleep(1)
                    btns = dr.find_elements(By.XPATH, "//button[contains(@onclick, 'TraCuuHD_onClickTaiHoaDonNPC')]")
                    if btns:
                        break
                    
                    # Nếu thấy rõ thông báo không có hóa đơn thì dừng chờ luôn
                    try:
                        empty_msgs = dr.find_elements(By.XPATH, "//*[contains(text(), 'Không có dữ liệu') or contains(text(), 'Không tìm thấy hóa đơn') or contains(text(), 'Chưa có thông tin')]")
                        # Tuy nhiên do chữ 'Không có dữ liệu' có thể nằm sẵn trong DOM ẩn, 
                        # nên cách an toàn nhất vẫn là chờ đủ hoặc khi nào btns xuất hiện.
                    except: pass
                
                if not btns:
                    print(f"💡 Không có dữ liệu tháng {month} (hoặc máy chủ EVN phản hồi quá chậm).")
                else:
                    print(f"🔍 Tìm thấy {len(btns)} hóa đơn. Bắt đầu tải hóa đơn...")
                    
                    # Bước 1: Quét toàn bộ bảng để đếm xem có Mã KH nào bị trùng lặp không
                    mkh_counts = {}
                    mkh_list = []
                    for i in range(len(btns)):
                        row_xp = f"(//tr[.//button[contains(@onclick, 'TraCuuHD')]])[{i+1}]"
                        mkh_w = dr.find_element(By.XPATH, row_xp + "//td[contains(@class, 'uk-text-truncate')]").text.strip()
                        mkh_list.append(mkh_w)
                        mkh_counts[mkh_w] = mkh_counts.get(mkh_w, 0) + 1
                        
                    # Bước 2: Bắt đầu bấm tải và xử lý đổi tên
                    for i in range(len(btns)):
                        try:
                            # Tìm lại phần tử để tránh lỗi Stale Element
                            row_xp = f"(//tr[.//button[contains(@onclick, 'TraCuuHD')]])[{i+1}]"
                            mkh_w = mkh_list[i]
                            
                            btn = dr.find_element(By.XPATH, row_xp + "//button[contains(@onclick, 'TraCuuHD')]")
                            stt_val = dr.find_element(By.XPATH, f"{row_xp}/td[1]").text.strip()
                            
                            dr.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                            time.sleep(0.5)
                            dr.execute_script("arguments[0].click();", btn)
                            
                            # Logic đổi tên: NẾU TRÙNG thì thêm STT vào trước (Ví dụ: 1-PA01HH0088900.zip)
                            if mkh_counts[mkh_w] > 1:
                                final_name = f"{stt_val}-{mkh_w}.zip"
                            else:
                                final_name = f"{mkh_w}.zip"
                                
                            print(f"   📥 Đang tải hóa đơn {i+1}: {final_name}")
                            # Đợi 1 chút giữa các lần click để trình duyệt kịp xử lý luồng tải
                            time.sleep(1) 
                            rename_latest_file_strict(folder, final_name)
                            
                        except Exception as loop_e:
                            if "NoSuchElement" in str(type(loop_e)):
                                print(f"   ⚠️ Mất kết nối giao diện dẫu tìm hóa đơn thứ {i+1} (Máy chủ EVN lag/reset khung nhìn). Dừng tải cho tài khoản {u} tại mốc này!")
                                break
                            else:
                                print(f"   ❌ Trục trặc hóa đơn {i+1}: {loop_e}")
                                continue
                                
                        
                    print(f"✅ Đã tải xong {len(btns)} hóa đơn cho {u}.")
            except Exception as inner_e:
                import traceback
                print(f"⚠️ Lỗi xử lý tại tài khoản {u}: {inner_e}")
                print(f"🛠️ Dấu vết lỗi chi tiết (Traceback):\n{traceback.format_exc()}")
            dr.delete_all_cookies()

        dr.quit(); print("\n🏁 HOÀN TẤT.")
    except Exception as e:
        if dr: dr.quit()
        import traceback
        print(f"🚫 Lỗi hệ thống nghiêm trọng: {e}")
        print(f"🛠️ Dấu vết lỗi (Traceback):\n{traceback.format_exc()}")

# --- GIỮ NGUYÊN CÁC HÀM organize, rename, print, extract TỪ BẢN V5.3 ---
def organize_downloaded_files(folder):
    print(f"🚀 GIẢI NÉN TẠI: {folder}")
    d_tong, d_ct = os.path.join(folder, "HoaDon_Tong"), os.path.join(folder, "HoaDon_ChiTiet")
    os.makedirs(d_tong, exist_ok=True); os.makedirs(d_ct, exist_ok=True)
    import re
    zips = glob.glob(os.path.join(folder, "*.zip"))
    if not zips: print("💡 Không thấy file zip"); return
    
    # Sắp xếp số thứ tự tự nhiên (1, 2, ..., 10, 11)
    zips = sorted(zips, key=lambda f: [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', os.path.basename(f))])
    
    c1, c2, err_count = 0, 0, 0
    total_zips = len(zips)
    
    for z in zips:
        m = os.path.splitext(os.path.basename(z))[0]
        t = os.path.join(folder, "temp_" + m)
        try:
            with zipfile.ZipFile(z, 'r') as zf: zf.extractall(t)
            if os.path.exists(os.path.join(t, "HoaDon.pdf")): shutil.copy2(os.path.join(t, "HoaDon.pdf"), os.path.join(d_tong, f"{m}.pdf")); c1 += 1
            if os.path.exists(os.path.join(t, "ChiTiet.pdf")): shutil.copy2(os.path.join(t, "ChiTiet.pdf"), os.path.join(d_ct, f"{m}.pdf")); c2 += 1
            shutil.rmtree(t); print(f"✅ Đã tách: {m}")
        except zipfile.BadZipFile:
            print(f"⚠️ Bỏ qua: {m} (Lỗi giải nén - File rỗng do lag mạng)")
            err_count += 1
        except Exception as e:
            print(f"⚠️ Lỗi giải nén {m}: {e}")
            err_count += 1
            
    print(f"📊 Tổng kết: {c1} file Tổng, {c2} file Chi tiết.")
    print(f"✅ KQ Giải Nén: Trích xuất thành công {total_zips - err_count}/{total_zips} file ZIP.")
    if err_count > 0:
        print(f"⚠️ Có {err_count} file bị lỗi trong quá trình tải nên không thể giải nén!")

def rename_with_excel_mapping(f, e, m, y, mode):
    s = "KH -> CSHT" if mode == 1 else "CSHT -> KH"
    print(f"🚀 ÁNH XẠ: {s}")
    try:
        df = pd.read_excel(e); mp = dict(zip(df.iloc[:,0].astype(str).str.strip(), df.iloc[:,1].astype(str).str.strip())) if mode==1 else dict(zip(df.iloc[:,1].astype(str).str.strip(), df.iloc[:,0].astype(str).str.strip()))
        sfx = f"_{str(m).zfill(2)}-{y}"; count = 0
        for p in glob.glob(os.path.join(f, "*.pdf")):
            old = os.path.splitext(os.path.basename(p))[0]
            nw = f"{mp[old]}{sfx}.pdf" if (mode==1 and old in mp) else ""
            if mode==2:
                for k,v in mp.items():
                    if old.startswith(k): nw = f"{v}.pdf"; break
            if nw:
                dst = os.path.join(f, nw)
                if os.path.exists(dst): os.remove(dst)
                os.rename(p, dst); print(f"   🔄 {old} -> {nw}"); count += 1
        print(f"✅ Thành công {count} file.")
    except Exception as err: print(f"🚫 Lỗi: {err}")

def print_all_pdfs(folder):
    print(f"🖨️ ĐANG GỬI LỆNH IN (Chế độ tương thích máy in cũ): {folder}")
    pdfs = glob.glob(os.path.join(folder, "*.pdf"))
    if not pdfs: print("💡 Không thấy file PDF"); return
    for index, p in enumerate(pdfs, 1):
        try: 
            print(f"   📄 [{index}/{len(pdfs)}] Gửi lệnh in: {os.path.basename(p)} - Đang chờ xử lý (5s)...")
            os.startfile(p, "print")
            time.sleep(5) # Tăng thời gian trễ lên 5s để spooler của máy in cũ kịp xử lý
        except Exception as e: 
            print(f"   ❌ Lỗi in {os.path.basename(p)}: {e}")
            pass
    print("✅ Đã gửi xong tất cả lệnh in. Vui lòng kiểm tra khay giấy máy in.")

def extract_total_invoices(folder, save):
    print(f"🚀 TRÍCH XUẤT HÓA ĐƠN TỔNG: {folder}")
    print("=" * 60)
    
    pdfs = glob.glob(os.path.join(folder, "*.pdf"))
    
    # Kiểm tra thư mục rỗng
    if not pdfs:
        print("❌ LỖI: Không tìm thấy file PDF nào trong thư mục!")
        print(f"   📁 Thư mục: {folder}")
        raise Exception("Không tìm thấy file PDF nào trong thư mục được chọn!")
    
    print(f"📊 Tìm thấy {len(pdfs)} file PDF. Bắt đầu quét...")
    print("-" * 60)
    
    res = []
    success_count = 0
    error_count = 0
    error_files = []
    
    for p in pdfs:
        fname = os.path.basename(p)
        print(f"📄 Đang quét: {fname}")
        
        try:
            with pdfplumber.open(p) as pdf:
                txt = "\n".join(pg.extract_text() or "" for pg in pdf.pages)
                
                if not txt.strip():
                    print(f"   ⚠️ LỖI: File PDF rỗng hoặc không đọc được nội dung!")
                    error_count += 1
                    error_files.append((fname, "File PDF rỗng hoặc không đọc được"))
                    continue
                
                # Regex patterns
                s = re.search(r"Serial\):\s*(\S+)", txt)
                n = re.search(r"Số\s*\(No\):\s*(\d+)", txt)
                d = re.search(r"Ngày.*?(\d+)\s*tháng.*?(\d+)\s*năm.*?(\d+)", txt)
                pm = re.search(r"từ ngày\s*(\d{2}/\d{2}/\d{4})\s*đến ngày[\s\S]*?(\d{2}/\d{2}/\d{4})", txt)
                m = re.search(r"Mã khách hàng.*?: (\S+)", txt)
                q = re.search(r"1\s*kWh\s*([\d\.,]+)\s*-", txt)
                c = re.search(r"Cộng tiền hàng.*?: ([\d\.,]+)", txt)
                v = re.search(r"Tiền thuế GTGT.*?: ([\d\.,]+)", txt)
                t = re.search(r"Tỷ giá.*?:\s*([\d\.,]+)", txt)
                
                # Kiểm tra các trường bắt buộc
                missing_fields = []
                if not s: missing_fields.append("Ký hiệu (Serial)")
                if not n: missing_fields.append("Số hóa đơn")
                if not m: missing_fields.append("Mã khách hàng")
                
                if missing_fields:
                    print(f"   ⚠️ CẢNH BÁO: Thiếu trường: {', '.join(missing_fields)}")
                
                # Nếu thiếu cả 3 trường quan trọng => file không phải hóa đơn EVN
                if not s and not n and not m:
                    print(f"   ❌ LỖI: File không đúng định dạng hóa đơn EVN!")
                    error_count += 1
                    error_files.append((fname, "Không đúng định dạng hóa đơn EVN"))
                    continue
                
                res.append({
                    "Tên file": fname,
                    "Ký hiệu": s.group(1) if s else "",
                    "Số hóa đơn": n.group(1) if n else "",
                    "Ngày hóa đơn": f"{d.group(1).zfill(2)}/{d.group(2).zfill(2)}/{d.group(3)}" if d else "",
                    "Ngày đầu kỳ": pm.group(1) if pm else "",
                    "Ngày cuối kỳ": pm.group(2) if pm else "",
                    "Mã khách hàng": m.group(1) if m else "",
                    "Số lượng (Kwh)": q.group(1) if q else "",
                    "Cộng tiền hàng": c.group(1) if c else "",
                    "Tiền thuế GTGT": v.group(1) if v else "",
                    "Tổng tiền thanh toán": t.group(1) if t else ""
                })
                success_count += 1
                print(f"   ✅ Thành công!")
                
        except Exception as e:
            print(f"   ❌ LỖI: {str(e)}")
            error_count += 1
            error_files.append((fname, str(e)))
    
    # Tổng kết
    print("=" * 60)
    print(f"📊 TỔNG KẾT:")
    print(f"   ✅ Thành công: {success_count} file")
    print(f"   ❌ Lỗi: {error_count} file")
    
    if error_files:
        print("\n📋 DANH SÁCH FILE LỖI:")
        for fname, reason in error_files:
            print(f"   • {fname}: {reason}")
    
    if res:
        pd.DataFrame(res).to_excel(save, index=False)
        print(f"\n💾 Đã lưu kết quả: {save}")
        print(f"✅ HOÀN TẤT: Xuất {len(res)} dòng dữ liệu.")
    else:
        print("\n❌ Không có dữ liệu nào được trích xuất!")
        raise Exception("Không trích xuất được dữ liệu nào. Kiểm tra lại file PDF!")


def extract_detailed_invoices(folder, save):
    print(f"🚀 TRÍCH XUẤT HÓA ĐƠN CHI TIẾT: {folder}")
    print("=" * 60)
    
    pdfs = glob.glob(os.path.join(folder, "*.pdf"))
    
    # Kiểm tra thư mục rỗng
    if not pdfs:
        print("❌ LỖI: Không tìm thấy file PDF nào trong thư mục!")
        print(f"   📁 Thư mục: {folder}")
        raise Exception("Không tìm thấy file PDF nào trong thư mục được chọn!")
    
    print(f"📊 Tìm thấy {len(pdfs)} file PDF. Bắt đầu quét...")
    print("-" * 60)
    
    def cl(v): 
        return float(v.replace('.', '').replace(',', '.')) if v else 0.0
    
    res = []
    success_count = 0
    error_count = 0
    error_files = []
    
    for p_path in pdfs:
        fname = os.path.basename(p_path)
        print(f"📄 Đang xử lý: {fname}")
        
        try:
            with pdfplumber.open(p_path) as pdf:
                txt = "\n".join(pg.extract_text() or "" for pg in pdf.pages)
                
                if not txt.strip():
                    print(f"   ⚠️ LỖI: File PDF rỗng hoặc không đọc được nội dung!")
                    error_count += 1
                    error_files.append((fname, "File PDF rỗng hoặc không đọc được"))
                    continue
                
                h = re.search(r"kèm theo hóa đơn số\s*(\d+)\s*ngày\s*(\d+)\s*tháng\s*(\d+)\s*năm\s*(\d+)", txt)
                no, dt = (h.group(1), f"{h.group(2).zfill(2)}/{h.group(3).zfill(2)}/{h.group(4)}") if h else ("", "")
                
                pm = re.search(r"từ\s*(\d{2}/\d{2}/\d{4})\s*đến\s*(\d{2}/\d{2}/\d{4})", txt)
                p1, p2 = (pm.group(1), pm.group(2)) if pm else ("", "")
                
                segs = re.split(r"ĐIỂM ĐO ĐẾM THỨ \d+ :", txt)
                
                if len(segs) <= 1:
                    # Không tìm thấy điểm đo => không phải file chi tiết
                    print(f"   ❌ LỖI: Không tìm thấy 'ĐIỂM ĐO ĐẾM' - File không đúng định dạng hóa đơn chi tiết!")
                    error_count += 1
                    error_files.append((fname, "Không đúng định dạng hóa đơn chi tiết"))
                    continue
                
                it = 0
                for s in segs[1:]:
                    mkh = re.match(r"\s*(\S+)", s).group(1) if re.match(r"\s*(\S+)", s) else ""
                    if not mkh: 
                        continue
                    ps = s.split("KHUNG GIỜ MUA ĐIỆN")[-1]
                    lns = re.findall(r"(?:bình thường|cao điểm|thấp điểm|Toàn thời gian)\s+[\d\.,]+\s+([\d\.,]+)\s+([\d\.,]+)", ps, re.I)
                    t_q = sum(cl(item[0]) for item in lns)
                    t_net = sum(cl(item[1]) for item in lns)
                    t_vat = round(t_net * 0.08)
                    t_pay = t_net + t_vat
                    res.append({
                        "Tên file": fname, "Số hóa đơn": no, "Ngày hóa đơn": dt,
                        "Ngày đầu kỳ": p1, "Ngày cuối kỳ": p2,
                        "Mã khách hàng": mkh, "Số lượng (Kwh)": t_q,
                        "Cộng tiền hàng": t_net, "Tiền thuế GTGT": t_vat, "Tổng tiền thanh toán": t_pay
                    })
                    it += 1
                
                if it > 0:
                    success_count += 1
                    print(f"   ✅ Thành công! Có {it} điểm đo.")
                else:
                    print(f"   ⚠️ CẢNH BÁO: Không trích xuất được điểm đo nào!")
                    
        except Exception as e:
            print(f"   ❌ LỖI: {str(e)}")
            error_count += 1
            error_files.append((fname, str(e)))
    
    # Tổng kết
    print("=" * 60)
    print(f"📊 TỔNG KẾT:")
    print(f"   ✅ Thành công: {success_count} file")
    print(f"   ❌ Lỗi: {error_count} file")
    
    if error_files:
        print("\n📋 DANH SÁCH FILE LỖI:")
        for fname, reason in error_files:
            print(f"   • {fname}: {reason}")
    
    if res:
        pd.DataFrame(res).to_excel(save, index=False)
        print(f"\n💾 Đã lưu kết quả: {save}")
        print(f"✅ HOÀN TẤT: Xuất {len(res)} dòng dữ liệu.")
    else:
        print("\n❌ Không có dữ liệu nào được trích xuất!")
        raise Exception("Không trích xuất được dữ liệu nào. Kiểm tra lại file PDF!")