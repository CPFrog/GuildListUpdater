import time
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from selenium import webdriver
from bs4 import BeautifulSoup
import chromedriver_autoinstaller
import edgedriver_autoinstaller
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

guild_url = 'https://loawa.com/guild/'
url = 'https://loawa.com/char/'


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('로스트아크 길드원 목록 갱신 v1.2.1 by CP개구링')
        grid = QGridLayout()
        self.setLayout(grid)

        grid.addWidget(QLabel('길드명:'), 0, 0)

        self.gname_text = QLineEdit()
        self.gname_text.returnPressed.connect(self.button_event)
        grid.addWidget(self.gname_text, 0, 1)

        search_btn = QPushButton('검색', self)
        search_btn.clicked.connect(self.button_event)
        grid.addWidget(search_btn, 1, 1)

        self.setGeometry(200, 200, 300, 100)
        self.show()

    def button_event(self):
        global guild
        guild = self.gname_text.text()
        startTime = time.time()

        self.list_update(guild)
        QMessageBox.information(self, '완료 알림', f'길드원 목록 갱신이 완료되었습니다.\n소요시간: {time.time() - startTime:.2f}초')

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Enter:
            self.button_event()

        elif e.key() == Qt.Key_Escape:
            self.close()

    def closeEvent(self, e):
        QMessageBox.information(self, '프로그램 종료 알림', '프로그램이 종료됩니다.')

    def list_update(self, guild_name):
        global driver_ver
        try:
            driver_ver = edgedriver_autoinstaller.get_edge_version().split('.')[0]  # Edge 브라우저 드라이버 버전 확인
            browser = 0  # edge의 브라우저 코드 = 0
        except:  # Edge 브라우저가 없는 환경인 경우 --> 크롬으로 대체
            driver_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
            browser = 1  # chrome의 브라우저 코드 = 1
        # 나중에 할진 모르겠지만.. safari = 2, firefox = 3, opera = 4

        if browser == 0:
            options = webdriver.EdgeOptions()  # 옵션 생성
            options.add_argument('--headless')  # 창 숨기는 옵션 추가
            try:
                driver = webdriver.Edge(f'./{driver_ver}/msedgedriver', options=options)
            except:
                edgedriver_autoinstaller.install(True)
                driver = webdriver.Edge(f'./{driver_ver}/msedgedriver', options=options)

        elif browser == 1:
            options = webdriver.ChromeOptions()  # 옵션 생성
            options.add_argument('--headless')  # 창 숨기는 옵션 추가
            try:
                driver = webdriver.Chrome(f'./{driver_ver}/chromedriver', options=options)
            except:
                chromedriver_autoinstaller.install(True)
                driver = webdriver.Chrome(f'./{driver_ver}/chromedriver', options=options)
        driver.implicitly_wait(3)

        driver.get(guild_url + guild_name)
        guild_soup = BeautifulSoup(driver.page_source, 'html.parser')
        member_list = guild_soup.find_all('table', {'class': 'tfs13'})

        # 나중에 브라우저 종류 추가될 경우 if-elif문 형태로 변경할것
        if browser == 0:
            caps = DesiredCapabilities().EDGE
        else:
            caps = DesiredCapabilities().CHROME
        caps['pageLoadStrategy'] = 'none'

        for itr in member_list:
            cname = itr.find('span', {'class': 'text-theme-0 tfs13'}).text.strip()
            print(cname)
            driver.get(url + cname)

        driver.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
