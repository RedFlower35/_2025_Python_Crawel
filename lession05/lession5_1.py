from pathlib import Path

def get_html_path() -> str:
    """回傳檔案的絕對路徑（ waiting_demo.html 與此檔同目錄）"""
    return str((Path(__file__).parent / "waiting_demo.html").resolve())

def main():
    html_path = get_html_path()
    print(html_path)
    
if __name__ == "__main__":
    main()