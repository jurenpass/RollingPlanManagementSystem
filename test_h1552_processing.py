import sys
import os
import tempfile
from PyQt5.QtWidgets import QApplication

sys.path.insert(0, 'g:\\newplan')

from furnace_order_manager_pyqt5 import MainWindow

app = QApplication(sys.argv)
window = MainWindow()
window.plan_dir = 'g:\\newplan'

try:
    # 直接处理原始文件
    file_path = r'g:\newplan\计划号\H1552.xls'
    print(f"开始处理文件: {file_path}")
    
    # 处理文件
    has_low_roll_width, has_no_aps = window.run_excel_macro_with_pandas(file_path)
    print(f"处理成功！has_low_roll_width={has_low_roll_width}, has_no_aps={has_no_aps}")
        
except Exception as e:
    print(f"处理失败: {str(e)}")
    import traceback
    traceback.print_exc()
