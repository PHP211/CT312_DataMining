import time
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def crawl_genk_mobile():
    url = "https://genk.vn/do-choi-so.chn"
    max_articles = 2000  # Số lượng bài viết muốn cào
    
    # Khởi tạo trình duyệt Chrome với Selenium
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Chạy Chrome ở chế độ ẩn (không hiện cửa sổ trình duyệt)
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Mở trang web
    driver.get(url)
    
    # Cuộn xuống trang web để tải thêm dữ liệu
    last_height = driver.execute_script("return document.body.scrollHeight")
    news_list = []  # Danh sách để lưu dữ liệu bài viết

    while len(news_list) < max_articles:
        # Nhấp vào nút "Xem thêm" nếu tìm thấy
        try:
            # Tìm nút "Xem thêm"
            xem_them_button = driver.find_element(By.XPATH, "//a[contains(text(), 'Xem thêm')]")
            driver.execute_script("arguments[0].click();", xem_them_button)
            time.sleep(4)  # Chờ nội dung tải thêm
        except Exception as e:
            # Nếu không tìm thấy nút "Xem thêm", tiếp tục cuộn
            pass

        # Cuộn xuống dưới cùng của trang
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Chờ trang tải thêm nội dung (thời gian có thể điều chỉnh)
        time.sleep(2)
        
        # Lấy nội dung trang hiện tại sau khi đã cuộn hoặc nhấp "Xem thêm"
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        articles = soup.find_all('li', class_='knswli')

        # Duyệt qua các bài viết để lấy thông tin mới
        for article in articles[len(news_list):]:  # Chỉ duyệt qua các bài viết chưa cào
            title_tag = article.find('h4', class_='knswli-title')
            subtitle_tag = article.find('span', class_='knswli-sapo')
            category_tag = article.find('a', class_='knswli-category')
            time_tag = article.find('span', class_='knswli-time')

            # Lấy title, subtitle và chủ đề nếu có
            title = title_tag.get_text(strip=True) if title_tag else 'No title'
            subtitle = subtitle_tag.get_text(strip=True) if subtitle_tag else 'No subtitle'
            category = category_tag.get_text(strip=True) if category_tag else 'No category'
            datetime = time_tag.get_text(strip=True) if time_tag else 'No time'

            # Tạo dictionary cho bài viết
            news_item = {
                'title': title,
                'subtitle': subtitle,
                'category': category,
                'time': datetime
            }
            
            # Thêm vào danh sách các bài viết
            news_list.append(news_item)
            
            # Kiểm tra số lượng bài viết đã thu thập được
            if len(news_list) >= max_articles:
                break
        
        # Tính chiều cao mới của trang và kiểm tra nếu không có thay đổi
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # Dừng cuộn nếu không có thêm nội dung mới
        last_height = new_height
    
    # Đóng trình duyệt
    driver.quit()
    
    # Lưu dữ liệu vào file JSON
    with open('genk_do_choi_so.json', 'w', encoding='utf-8') as json_file:
        json.dump(news_list[:max_articles], json_file, ensure_ascii=False, indent=4)

    print(f"Lưu dữ liệu thành công! Đã lưu {len(news_list[:max_articles])} bản tin vào genk_do_choi_so.json")

# Gọi hàm để cào dữ liệu
crawl_genk_mobile()
