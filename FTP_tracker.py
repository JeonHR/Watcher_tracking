import os
import csv
import xml.etree.ElementTree as ET
from ftplib import FTP
from datetime import datetime
import sys

def load_config():
    """
    실행 파일 디렉터리에 있는 config.xml 파일을 로드합니다.
    """
    try:
        # 실행 파일이 있는 경로에서 config.xml 경로 확인
        config_path = os.path.join(os.path.dirname(sys.executable), "config.xml")
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"설정 파일이 존재하지 않습니다: {config_path}")
        
        tree = ET.parse(config_path)
        root = tree.getroot()

        ftp_details = {
            'host': root.find('./ftp/host').text,
            'user': root.find('./ftp/user').text,
            'password': root.find('./ftp/password').text,
            'directory': root.find('./ftp/directory').text
        }

        paths = {
            'log': root.find('./paths/log').text
        }

        filters = {
            'extensions': root.find('./filters/extensions').text.split(','),  # 확장자 목록
            'min_size': int(root.find('./filters/min_size').text)  # 최소 파일 크기
        }

        return ftp_details, paths, filters
    except Exception as e:
        print(f"설정 파일 로드 중 오류 발생: {e}")
        return None, None, None

def upload_files_to_ftp(ftp_details, log_path, filters, folder_path):
    """
    파일을 FTP 서버로 업로드하고 로그를 기록합니다.
    """
    try:
        # FTP 연결
        ftp = FTP(ftp_details['host'])
        ftp.login(ftp_details['user'], ftp_details['password'])
        ftp.cwd(ftp_details['directory'])
        
        # 로그 파일 초기화 (헤더 작성)
        if not os.path.exists(log_path):
            with open(log_path, 'w', newline='') as log_file:
                writer = csv.writer(log_file)
                writer.writerow(["Timestamp", "File Name", "Status", "Message"])  # CSV 헤더
        
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            
            # 파일 조건 확인
            if os.path.isfile(file_path) and \
               file.endswith(tuple(filters['extensions'])) and \
               os.path.getsize(file_path) >= filters['min_size']:
                try:
                    with open(file_path, 'rb') as f:
                        ftp.storbinary(f"STOR {file}", f)
                    
                    log_entry = [datetime.now().strftime('%Y-%m-%d %H:%M:%S'), file, "SUCCESS", 
                                 f"Uploaded successfully to {ftp_details['host']}/{ftp_details['directory']}"]
                    
                    # 업로드된 파일 삭제
                    os.remove(file_path)

                except Exception as upload_error:
                    log_entry = [datetime.now().strftime('%Y-%m-%d %H:%M:%S'), file, "FAILED", str(upload_error)]
                
                # 로그를 CSV 파일에 기록
                with open(log_path, 'a', newline='') as log_file:
                    writer = csv.writer(log_file)
                    writer.writerow(log_entry)

        ftp.quit()
    except Exception as e:
        print(f"FTP 연결 오류: {e}")

if __name__ == "__main__":
    # 실행 파일 디렉터리에서 config.xml 로드
    folder_to_upload = "C:/Users/admin/Desktop/TDE/SSH_COM"  # 업로드할 파일이 있는 로컬 디렉터리
    
    ftp_details, paths, filters = load_config()
    if ftp_details and paths and filters:
        upload_files_to_ftp(ftp_details, paths['log'], filters, folder_to_upload)
