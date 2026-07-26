import time
import logging
import requests
from typing import List, Dict, Generator

# Lấy logger theo tên module
logger = logging.getLogger(__name__)

class TradeDataCrawler:
    def __init__(self, config, auth):
        self.config = config
        self.auth = auth
        self.base_url = config['crawler'].get('base_url', "https://system-tradedata.pro/api")
        self.token = None
        self.session = requests.Session()
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def login(self) -> bool:
        """Thực hiện đăng nhập lấy Bearer Token"""
        login_url = f"{self.base_url}/Auth/Login"
        payload = {
            "account": self.auth['username'],
            "pwd": self.auth['password']
        }

        logger.info(f"Đang đăng nhập: {self.auth['username']}")

        try:
            response = self.session.post(
                login_url, json=payload, headers=self.headers, timeout=10
            )
            response.raise_for_status()

            # Khi tradedata.pro bị sập/bảo trì, server vẫn trả HTTP 200 nhưng
            # là trang HTML (shell của web app) thay vì JSON thật. Bắt riêng
            # trường hợp này để log thông báo rõ ràng thay vì traceback khó hiểu.
            content_type = response.headers.get("Content-Type", "")
            if "application/json" not in content_type:
                logger.error(
                    "Đăng nhập thất bại: Server trả về '%s' thay vì JSON — "
                    "khả năng cao tradedata.pro đang bảo trì/sập, không phải lỗi tài khoản. "
                    "Vui lòng thử đăng nhập lại bằng trình duyệt để xác nhận.",
                    content_type or "(không rõ)",
                )
                return False

            res_json = response.json()

            if res_json.get("successful"):
                self.token = res_json.get("result", "")
                if not self.token:
                    logger.error("Login thành công nhưng không có Token trả về.")
                    return False

                # Cập nhật Token vào session headers
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                logger.info("Đăng nhập thành công!")
                return True
            else:
                msg = res_json.get("message", "Lỗi server")
                logger.warning(f"Đăng nhập thất bại: {msg}")
                return False

        except Exception as e:
            logger.exception(f"Lỗi khi đăng nhập: {e}")
            return False

    def fetch_data_generator(self, start_date: str, end_date: str, company_name: str = "", hs_code: str = "") -> Generator[List[Dict], None, None]:
        """
        Hàm Generator dùng để stream dữ liệu (Streaming).
        
        INPUT: 
        - start_date, end_date (str): Định dạng 'YYYY-MM-DD'
        - company_name (str): Tên các công ty. Phân cách bởi dấu ';'
        - hs_code (str): Phân cách bởi dấu ';'
        
        OUTPUT (Yield):
        - Trả về từng gói dữ liệu (List[Dict]) mỗi khi crawl xong 1 trang.
        
        LƯU Ý: 
        - Cần dùng vòng lặp `for` để lấy dữ liệu.
        - Hàm này KHÔNG tự chia file. Việc chia file do logic bên app.py.
        """
        if not self.token:
            logger.error("Chưa có Token. Vui lòng chạy login() trước.")
            return

        search_url = f"{self.base_url}/Search/TradeDataV2"
        current_page = 1
        
        # --- LẤY CẤU HÌNH TỪ YAML ---
        crawler_cfg = self.config.get('crawler', {})
        sleep_time = crawler_cfg.get('sleep_time', 1)       # sleep bình thường giữa các trang OK
        sleep_success = crawler_cfg.get('sleep_success', 0.5)  # fast-path: 200-OK → 0.5s
        sleep_rate_limit = crawler_cfg.get('sleep_rate_limit', 5.0)  # 429 → back-off 5s
        
        # LOGIC ĐIỀU KHIỂN:
        # Nếu trong settings.yaml KHÔNG có dòng này -> Giá trị là None -> Chạy vô tận.
        # Nếu trong settings.yaml để là 0 hoặc null  -> Giá trị là 0/None -> Chạy vô tận.
        # Nếu có số cụ thể (ví dụ 5) -> Sẽ dừng khi đạt 5.
        max_pages = crawler_cfg.get('max_pages') 
        max_items = crawler_cfg.get('max_items') 
        
        total_items_fetched = 0 

        # Payload cấu hình
        payload = {
            "keydoc": company_name,
            "countryCode": "",
            "ie": "i",
            "startDate": start_date,
            "endDate": end_date,
            "hsCode": hs_code,
            "product": "",
            "importer": "",
            "exporter": "",
            "loadingPort": "",
            "unLoadingPort": "",
            "country": "",
            "billNo": "",
            "isShip": True,
            "isNotNullImporter": False,
            "isNotNullExporter": False,
            "isNotImporterForwarder": False,
            "isNotExporterForwarder": False,
            "languages": "en",
            "searchType": 2,
            "sortType": 0,
            "minValueWeight": 0,
            "maxValueWeight": 0,
            "minValueNumber": 0,
            "maxValueNumber": 0,
            "minValuePrice": 0,
            "maxValuePrice": 0,
            "downloadNum": 5000,
            "smtpIndex": 0,
            "pageIndex": current_page, # Sử dụng biến current_page
            "pageSize": 500,
            # "threeEnCountryCode": "ETH,UGA,KEN,DZA,DJI,EGY,GHA,RWA,SYC,GMB,CMR,COD,ZMB,MRT,CPV,MDG,STP,ZWE,LBR,MAR,SOM,NAM,BDI,ERI,SLE,GNQ,CAF,MOZ,NGA,COM,BWA,CIV,NER,ZAF,GIN,SDN,AGO,TZA,LBY,MUS,MYT,SWZ,MLI,TUN,LSO,MWI,GNB,TCD,SSD,IND,VNM,PAK,IDN,PHL,UZB,KGZ,KAZ,LKA,AFG,ARE,BHR,BGD,CHN,IRN,IRQ,JPN,KOR,KWT,MYS,OMN,QAT,SAU,SGP,TWN,THA,TUR,AZE,PSE,MAC,ISR,BRN,KHM,MDV,GEO,CUW,JOR,MNG,SYR,TJK,NPL,LBN,YEM,HKG,MMR,CYP,TLS,TKM,YDY,CIS,CAT,LAO,RUS,UKR,GBR,AEU,BEL,DNK,FIN,FRA,DEU,GRC,ITA,NLD,NOR,ESP,MDA,SHN,FRO,SXM,BIH,REU,GIB,LVA,AUT,SRB,BGR,CZE,MLT,SWE,MKD,HUN,LTU,MNE,CHE,POL,ALB,EST,ROU,BLR,LUX,IRL,SVN,HRV,ISL,PRT,SVK,LIE,RKS,MEX,CRI,USA,HND,GTM,NIC,SLV,CAN,TCA,ASM,CYM,DOM,JAM,CUB,BMU,LCA,DMA,BHS,BLZ,KNA,BRB,GRD,MSR,TTO,AIA,ABW,GRL,ATG,VCT,HTI,MTQ,GLP,PRI,AUS,WLF,FSM,PNG,FJI,NCL,TON,PYF,SLB,MNP,COK,KIR,GUM,VUT,WSM,VGB,VIR,NZL,ARG,CHL,COL,ECU,PAN,PER,PRY,BOL,URY,VEN,BRA,PEU,SUR,GUY,GUF",
            "threeEnCountryCode": "VNM",
            "code": "",
            "cKey": ""
        }
        logger.info(f"Bắt đầu Crawl: {start_date} -> {end_date}")
        if max_pages or max_items:
            logger.info(f"Cấu hình giới hạn: Max Pages={max_pages}, Max Items={max_items}")
        else:
            logger.info("Cấu hình: KHÔNG GIỚI HẠN (Chạy đến khi hết dữ liệu)")

        while True:
            # --- KIỂM TRA GIỚI HẠN (SAFETY BREAKERS) ---
            
            # 1. Check số trang (chỉ kích hoạt nếu max_pages > 0)
            if max_pages and current_page > max_pages:
                logger.info(f"⏹ Đã đạt giới hạn {max_pages} trang (theo Config). Dừng.")
                break

            # 2. Check số dòng (chỉ kích hoạt nếu max_items > 0)
            if max_items and total_items_fetched >= max_items:
                logger.info(f"⏹ Đã đạt giới hạn {max_items} dòng (theo Config). Dừng.")
                break

            payload["pageIndex"] = current_page
            
            try:
                response = self.session.post(
                    search_url, json=payload, headers=self.headers, timeout=30
                )

                # ── Xử lý Rate-Limit trước khi raise_for_status ──────────────
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", sleep_rate_limit))
                    logger.warning(
                        "⚠️ 429 Too Many Requests trang %d. Back-off %ds...",
                        current_page, retry_after
                    )
                    time.sleep(retry_after)
                    continue  # retry cùng trang

                response.raise_for_status()
                res_json = response.json()

                if res_json.get("successful"):
                    result_data = res_json.get("result", {})
                    data_list = result_data.get("data", []) if result_data else []

                    if not data_list:
                        logger.info("✅ Trang %d rỗng. Đã lấy hết dữ liệu.", current_page)
                        break

                    yield data_list

                    count = len(data_list)
                    total_items_fetched += count
                    logger.info("--> Trang %d: +%d dòng (Tổng: %d)", current_page, count, total_items_fetched)

                    current_page += 1

                    # ── Fast-path: 200-OK → sleep ngắn để đẩy tốc độ ─────────
                    time.sleep(sleep_success)

                else:
                    logger.warning("Lỗi API trang %d: %s", current_page, res_json.get('message'))
                    break

            except requests.exceptions.Timeout:
                logger.error("Timeout trang %d. Retry sau %.1fs...", current_page, sleep_time)
                time.sleep(sleep_time)
                continue
            except requests.exceptions.HTTPError as http_err:
                logger.error("HTTPError trang %d: %s", current_page, http_err)
                break
            except Exception as e:
                logger.exception("Lỗi crawl trang %d: %s", current_page, e)
                break