import sys
import os
import shutil
import tempfile
from PyQt5.QtWidgets import QApplication

sys.path.insert(0, 'g:\\newplan')

# 创建一个简单的测试，直接调用run_excel_macro_with_pandas方法
app = QApplication(sys.argv)

from furnace_order_manager_pyqt5 import MainWindow

window = MainWindow()
window.plan_dir = 'g:\\newplan'

try:
    # 创建测试副本
    src_path = r'g:\newplan\计划号\H1552.xls'
    
    # 使用临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        dst_path = os.path.join(temp_dir, 'H1552_test.xls')
        
        # 复制文件
        shutil.copy(src_path, dst_path)
        print(f"创建测试文件: {dst_path}")
        
        # 处理文件
        has_low_roll_width, has_no_aps = window.run_excel_macro_with_pandas(dst_path)
        print(f"处理成功！")
        print(f"  has_low_roll_width: {has_low_roll_width}")
        print(f"  has_no_aps: {has_no_aps}")
        
    print("临时文件已自动清理")
    print("\n✓ H1552.xls 现在可以正常处理！")
        
except Exception as e:
    print(f"处理失败: {str(e)}")
    import traceback
    traceback.print_exc()
