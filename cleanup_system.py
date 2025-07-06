#!/usr/bin/env python3
"""
Cleanup Script - Xóa các files và folders thừa trong hệ thống
"""

import os
import shutil
import sys

def cleanup_system():
    """Xóa các files và folders thừa"""
    
    # Files cần xóa
    files_to_delete = [
        "src/data/vnstock_data_source.py",
        "src/data/vnstock_real_data.py", 
        "src/data/1_vietnam_stock_vnstock3.py",
        "app_new.py",
        "src/data/company_api.py",
        "src/data/finance_api.py",
        "src/data/listing_api.py", 
        "src/data/market_api.py",
        "src/data/price_api.py",
        "src/data/screener_api.py",
        "src/data/vnstock.py",
        "test.py",
        "quick_test.py", 
        "test_symbols.py",
        "test_symbol_validation.py",
        "static/index.html",
        "static/script.js",
        "static/styles.css",
        "src/utils/config.py",
        "MODERN_UI_GUIDE.md",
        "SYSTEM_OPTIMIZATION.md", 
        "vnstock_integration_guide.md",
        "VNSTOCK3_INTEGRATION.md",
        "setup.py"
    ]
    
    # Folders cần xóa
    folders_to_delete = [
        "vnstock_local",
        "static"
    ]
    
    deleted_files = 0
    deleted_folders = 0
    
    print("🧹 Bắt đầu dọn dẹp hệ thống...")
    
    # Xóa files
    for file_path in files_to_delete:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✅ Đã xóa file: {file_path}")
                deleted_files += 1
            except Exception as e:
                print(f"❌ Lỗi xóa file {file_path}: {e}")
        else:
            print(f"⚠️ File không tồn tại: {file_path}")
    
    # Xóa folders
    for folder_path in folders_to_delete:
        if os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path)
                print(f"✅ Đã xóa folder: {folder_path}")
                deleted_folders += 1
            except Exception as e:
                print(f"❌ Lỗi xóa folder {folder_path}: {e}")
        else:
            print(f"⚠️ Folder không tồn tại: {folder_path}")
    
    print(f"\n🎉 Hoàn thành dọn dẹp!")
    print(f"📁 Đã xóa {deleted_files} files")
    print(f"📂 Đã xóa {deleted_folders} folders")
    
    # Tính toán dung lượng tiết kiệm (ước tính)
    estimated_saved_mb = deleted_files * 0.1 + deleted_folders * 50  # Ước tính
    print(f"💾 Ước tính tiết kiệm: ~{estimated_saved_mb:.1f} MB")

if __name__ == "__main__":
    print("⚠️ CẢNH BÁO: Script này sẽ xóa vĩnh viễn các files và folders!")
    print("📋 Xem danh sách trong FILES_TO_DELETE.md trước khi chạy")
    
    confirm = input("\n❓ Bạn có chắc chắn muốn tiếp tục? (y/N): ")
    
    if confirm.lower() in ['y', 'yes']:
        cleanup_system()
    else:
        print("❌ Đã hủy cleanup")
        sys.exit(0)