import os
import pandas as pd
from ftplib import FTP
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor


# FTP 설정
FTP_HOST = "10.86.254.61"
FTP_USER = "eagle"
FTP_PASS = "eagle123"
FTP_LOG_DIR = "Eagle/ENG_DATA/PTE DATA/HR/log/"
LOCAL_LOG_DIR = "C:/Users/hyeongryeol.jeon/Desktop/loh/log/"

if not os.path.exists(LOCAL_LOG_DIR):
    os.makedirs(LOCAL_LOG_DIR)

# FTP에서 로그 파일 다운로드
def download_logs_from_ftp():
    try:
        print("Connecting to FTP server...")
        ftp = FTP(FTP_HOST)
        print("Logging in...")
        ftp.login(FTP_USER, FTP_PASS)
        print("Changing directory...")
       
        ftp.cwd(FTP_LOG_DIR)
        print("Listing files...")
        files = ftp.nlst()
        print("Files:", files)

        for file in files:
            local_file_path = os.path.join(LOCAL_LOG_DIR, os.path.basename(file))
            print(f"Downloading {file} to {local_file_path}...")


            with open(local_file_path, 'wb') as f:
                ftp.retrbinary(f"RETR {file}", f.write)
            print(f"Downloaded {file}")

        ftp.quit()
    except Exception as e:
        print(f"FTP 연결 또는 파일 다운로드 중 오류 발생: {e}")

# 로그 파일 파싱 및 최신 상태 반환
def parse_logs():
    logs = []

    try:
        log_files = [f for f in os.listdir(LOCAL_LOG_DIR) if f.endswith("_upload_log.csv")]

        for log_file in log_files:
            log_path = os.path.join(LOCAL_LOG_DIR, log_file)
            try:
                data = pd.read_csv(log_path)
                latest_log = data.iloc[-1]
                logs.append({
                    "File": log_file,
                    "Timestamp": latest_log["Timestamp"],
                    "Status": latest_log["Status"],
                    "Message": latest_log["Message"]
                })
            except Exception as e:
                print(f"로그 파일 {log_file} 읽기 중 오류 발생: {e}")

    except Exception as e:
        print(f"로그 파일 파싱 중 오류 발생: {e}")

    return logs


# PyQt5 앱 정의
class LogViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FTP Log Viewer")
        self.setGeometry(200, 200, 600, 350)

        # 테이블 위젯 생성
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["File", "Timestamp", "Status", "Message"])

        # 레이아웃 설정
        layout = QVBoxLayout()
        layout.addWidget(self.table_widget)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        
        # 초기 로그 업데이트
        self.update_logs()

        # 열의 크기를 글자에 맞게 자동 조정
        self.table_widget.resizeColumnsToContents()

                
        
    def update_logs(self):
        download_logs_from_ftp()  # FTP에서 로그 파일 다운로드
        logs = parse_logs()  # 로그 파싱

        self.table_widget.setRowCount(len(logs))

        for row, log in enumerate(logs):
            self.table_widget.setItem(row, 0, QTableWidgetItem(log["File"]))
            self.table_widget.setItem(row, 1, QTableWidgetItem(log["Timestamp"]))
            self.table_widget.setItem(row, 2, QTableWidgetItem(log["Status"]))
            self.table_widget.setItem(row, 3, QTableWidgetItem(log["Message"]))

            # 상태에 따른 색상 표시
            if log["Status"] == "SUCCESS":
                self.table_widget.item(row, 2).setBackground(QColor("green"))
            else:
                self.table_widget.item(row, 2).setBackground(QColor("red"))


if __name__ == "__main__":
    # PyQt5 앱 실행
    app = QApplication([])
    viewer = LogViewerApp()
    viewer.show()
    app.exec()
