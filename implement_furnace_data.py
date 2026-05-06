# -*- coding: utf-8 -*-
"""
实现装炉明细窗口的数据加载功能
从原程序复刻：
1. 读取装炉顺序.xls文件
2. 加载计划号数据
3. 保存表格数据
4. 处理特殊行（换辊行、自定义信息行）
5. 高亮标记
"""

with open('furnace_order_manager_pyqt5.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到 load_furnace_data 方法并替换
old_load_data = '''    def load_furnace_data(self):
        """加载装炉明细数据"""
        try:
            # TODO: 从数据库或文件加载数据
            # 这里先填充测试数据
            print("加载装炉明细数据...")
        except Exception as e:
            print(f"加载数据失败：{e}")'''

new_load_data = '''    def load_furnace_data(self):
        """加载装炉明细数据"""
        try:
            import os
            import tempfile
            import shutil
            import xlrd
            import time
            import json
            from PyQt5.QtWidgets import QTableWidgetItem
            from PyQt5.QtGui import QColor, QBrush
            
            # 读取装炉顺序.xls
            plan_dir = os.path.join(os.getcwd(), "计划号")
            excel_file = os.path.join(plan_dir, "装炉顺序.xls")
            
            print(f"查找装炉顺序文件: {excel_file}")
            
            if not os.path.exists(excel_file):
                print(f"文件不存在: {excel_file}")
                self.block_count_label.setText("0/0")
                return
            
            # 创建临时副本
            temp_file_name = f"temp_装炉顺序_{int(time.time())}.xls"
            temp_file_path = os.path.join(plan_dir, temp_file_name)
            shutil.copy2(excel_file, temp_file_path)
            print(f"创建临时副本: {temp_file_path}")
            
            # 读取数据
            workbook = xlrd.open_workbook(temp_file_path)
            sheet = workbook.sheet_by_index(0)
            
            headers = [str(sheet.cell_value(0, col)).strip() for col in range(sheet.ncols)]
            print(f"列名: {headers}")
            
            # 查找列索引
            order_col = None  # 装炉顺序号
            plan_col = None   # 计划号
            coil_col = None   # 钢卷号
            
            for idx, header in enumerate(headers):
                if '装炉顺序号' in header or '装炉顺序' in header:
                    order_col = idx
                    print(f"找到装炉顺序列: {idx}")
                elif '计划号' in header:
                    plan_col = idx
                    print(f"找到计划号列: {idx}")
                elif '钢卷号' in header:
                    coil_col = idx
                    print(f"找到钢卷号列: {idx}")
            
            if None in [order_col, plan_col, coil_col]:
                print(f"缺少必要列: order_col={order_col}, plan_col={plan_col}, coil_col={coil_col}")
                # 删除临时文件
                if os.path.exists(temp_file_path):
                    try:
                        os.remove(temp_file_path)
                        print(f"删除临时文件: {temp_file_path}")
                    except Exception as e:
                        print(f"删除临时文件失败: {e}")
                self.block_count_label.setText("0/0")
                return
            
            # 读取数据
            furnace_data = []
            for row in range(1, sheet.nrows):
                try:
                    order = sheet.cell_value(row, order_col)
                    # 转换装炉顺序为整数
                    if isinstance(order, float) and order.is_integer():
                        order = int(order)
                    plan_no = str(sheet.cell_value(row, plan_col)).strip()
                    coil_no = str(sheet.cell_value(row, coil_col)).strip()
                    
                    # 清理钢卷号，只保留ASCII数字
                    coil_no = ''.join(c for c in coil_no if c.isdigit())
                    
                    if plan_no and coil_no:
                        furnace_data.append({
                            'order': order,
                            'plan_no': plan_no,
                            'coil_no': coil_no
                        })
                        print(f"加载数据: 装炉顺序={order}, 计划号={plan_no}, 钢卷号={coil_no}")
                    else:
                        print(f"跳过空数据行: 计划号='{plan_no}', 钢卷号='{coil_no}'")
                except Exception as e:
                    print(f"读取行 {row} 失败: {e}")
                    continue
            
            # 删除临时文件
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    print(f"删除临时文件: {temp_file_path}")
                except Exception as e:
                    print(f"删除临时文件失败: {e}")
            
            print(f"加载到 {len(furnace_data)} 条装炉数据")
            if len(furnace_data) == 0:
                print("装炉顺序.xls文件中没有数据")
                self.block_count_label.setText("0/0")
                return
            
            # 清空表格
            self.table_widget.setRowCount(0)
            
            # 加载计划号数据
            for item in furnace_data:
                plan_no = item['plan_no']
                coil_no = item['coil_no']
                
                # 获取计划号文件
                plan_file = self.get_plan_file(plan_no)
                if not plan_file:
                    print(f"未找到计划号文件: {plan_no}")
                    continue
                
                # 读取计划号文件数据
                plan_data = self.read_plan_file(plan_file, coil_no)
                if plan_data:
                    self.add_plan_data_to_table(plan_data)
            
            # 保存表格数据
            self.save_current_table_data()
            
            # 更新块数显示
            self.update_block_count()
            
        except Exception as e:
            print(f"加载装炉明细数据失败: {str(e)}")
            import traceback
            traceback.print_exc()
            self.block_count_label.setText("0/0")
            
    def get_plan_file(self, plan_no):
        """获取计划号文件路径"""
        import os
        # 首先在计划号目录查找
        plan_dir = os.path.join(os.getcwd(), "计划号")
        file_path = os.path.join(plan_dir, f"{plan_no}.xls")
        if os.path.exists(file_path):
            print(f"找到计划号文件: {file_path}")
            return file_path
        # 然后在backup目录查找
        backup_dir = os.path.join(plan_dir, "backup")
        if os.path.exists(backup_dir):
            file_path = os.path.join(backup_dir, f"{plan_no}.xls")
            if os.path.exists(file_path):
                print(f"找到计划号文件(backup): {file_path}")
                return file_path
        # 尝试其他可能的路径
        # 直接在计划号目录的上级目录查找
        parent_dir = os.path.dirname(plan_dir)
        file_path = os.path.join(parent_dir, f"{plan_no}.xls")
        if os.path.exists(file_path):
            print(f"找到计划号文件(上级目录): {file_path}")
            return file_path
        # 尝试在当前工作目录查找
        file_path = os.path.join(os.getcwd(), f"{plan_no}.xls")
        if os.path.exists(file_path):
            print(f"找到计划号文件(当前目录): {file_path}")
            return file_path
        return None
    
    def read_plan_file(self, file_path, target_coil_no):
        """读取计划号文件数据"""
        try:
            import xlrd
            
            workbook = xlrd.open_workbook(file_path)
            sheet = workbook.sheet_by_index(0)
            
            # 获取列名
            headers = [str(sheet.cell_value(0, col)).strip() for col in range(sheet.ncols)]
            
            # 查找钢卷号列
            coil_col = None
            for idx, header in enumerate(headers):
                if '钢卷号' in header:
                    coil_col = idx
                    break
            
            if coil_col is None:
                print(f"计划号文件 {file_path} 中未找到钢卷号列")
                return None
            
            # 查找目标钢卷号
            for row in range(1, sheet.nrows):
                try:
                    coil_no = str(sheet.cell_value(row, coil_col)).strip()
                    # 清理钢卷号，只保留数字
                    cleaned_coil_no = ''.join(c for c in coil_no if c.isdigit())
                    
                    if cleaned_coil_no == target_coil_no:
                        # 读取整行数据
                        row_data = []
                        for col in range(len(headers)):
                            value = sheet.cell_value(row, col)
                            if isinstance(value, float) and value.is_integer():
                                value = int(value)
                            row_data.append(str(value).strip())
                        
                        # 构建数据字典
                        data = {}
                        for i, header in enumerate(headers):
                            data[header] = row_data[i]
                        
                        return data
                except Exception as e:
                    print(f"读取计划号文件行 {row} 失败: {e}")
                    continue
            
            print(f"计划号文件 {file_path} 中未找到钢卷号 {target_coil_no}")
            return None
        except Exception as e:
            print(f"读取计划号文件失败: {str(e)}")
            return None
    
    def add_plan_data_to_table(self, plan_data):
        """将计划数据添加到表格"""
        try:
            from PyQt5.QtWidgets import QTableWidgetItem
            from PyQt5.QtGui import QColor, QBrush
            
            # 列名映射
            column_map = {
                "计划号": "计划号",
                "钢卷号": "钢卷号",
                "牌号（钢级）": "牌号（钢级）",
                "坯宽": "坯宽",
                "减宽": "减宽",
                "调宽": "调宽",
                "轧宽": "轧宽",
                "公差带": "公差带",
                "粗轧报信": "粗轧报信",
                "除鳞": "除鳞",
                "坯厚": "坯厚",
                "坯长": "坯长",
                "轧厚": "轧厚",
                "中厚": "中厚",
                "RT2": "RT2",
                "强度": "强度",
                "切边": "切边",
                "去向": "去向",
                "订宽": "订宽",
                "坯头部宽": "坯头部宽",
                "坯尾部宽": "坯尾部宽",
                "热轧产品分类": "热轧产品分类",
                "炼钢钢种": "炼钢钢种",
                "负公差": "负公差",
                "正公差": "正公差",
                "回炉坯": "回炉坯",
                "原轧宽": "原轧宽"
            }
            
            # 获取列索引
            columns = [
                "计划号", "钢卷号", "牌号（钢级）", "坯宽", "减宽", "调宽", "轧宽", "公差带",
                "粗轧报信", "除鳞", "坯厚", "坯长", "轧厚", "中厚", "RT2", "强度", "切边", "去向", "订宽",
                "坯头部宽", "坯尾部宽", "热轧产品分类", "炼钢钢种", "负公差", "正公差", "回炉坯", "原轧宽"
            ]
            
            # 添加新行
            row_idx = self.table_widget.rowCount()
            self.table_widget.insertRow(row_idx)
            
            # 填充数据
            for col_idx, col_name in enumerate(columns):
                # 查找对应的数据
                data_key = column_map.get(col_name, col_name)
                value = plan_data.get(data_key, "")
                
                item = QTableWidgetItem(value)
                
                # 设置字体
                font = item.font()
                font.setFamily("微软雅黑")
                font.setPointSize(20)
                font.setBold(True)
                item.setFont(font)
                
                # 处理特殊情况和高亮
                self.process_cell_highlight(item, col_name, value)
                
                self.table_widget.setItem(row_idx, col_idx, item)
                
        except Exception as e:
            print(f"添加计划数据到表格失败: {str(e)}")
    
    def process_cell_highlight(self, item, col_name, value):
        """处理单元格高亮"""
        from PyQt5.QtGui import QColor, QBrush
        
        # 检查是否需要高亮
        if col_name == "减宽":
            try:
                # 检查是否为数字
                if value.replace('.', '').replace('-', '').isdigit():
                    width_reduction = float(value)
                    if width_reduction >= 240:
                        # 减宽超标，高亮为红色
                        item.setBackground(QBrush(QColor('#FF0000')))
                        item.setForeground(QBrush(QColor('#FFFFFF')))
                    elif width_reduction < 0:
                        # 逆宽，高亮为红色
                        item.setBackground(QBrush(QColor('#FF0000')))
                        item.setForeground(QBrush(QColor('#FFFFFF')))
            except:
                pass
        
        elif col_name == "轧宽":
            try:
                if value.replace('.', '').isdigit():
                    roll_width = float(value)
                    if roll_width < 860:
                        # 轧宽低于860，高亮为红色
                        item.setBackground(QBrush(QColor('#FF0000')))
                        item.setForeground(QBrush(QColor('#FFFFFF')))
                    elif roll_width < 930:
                        # 轧宽低于930，高亮为黄色
                        item.setBackground(QBrush(QColor('#FFFF00')))
                        item.setForeground(QBrush(QColor('#000000')))
            except:
                pass
        
        elif col_name == "坯厚":
            try:
                if value.replace('.', '').isdigit():
                    blank_thickness = float(value)
                    if blank_thickness > 230:
                        # 坯厚大于230，高亮为红色
                        item.setBackground(QBrush(QColor('#FF0000')))
                        item.setForeground(QBrush(QColor('#FFFFFF')))
            except:
                pass
        
        elif col_name == "除鳞":
            if "回" in value or "无APS" in value:
                # 除鳞字段包含回字或无APS，高亮为红色
                item.setBackground(QBrush(QColor('#FF0000')))
                item.setForeground(QBrush(QColor('#FFFFFF')))
    
    def save_current_table_data(self):
        """保存当前表格数据"""
        try:
            import json
            import os
            # 构建保存文件路径
            plan_dir = os.path.join(os.getcwd(), "计划号")
            os.makedirs(plan_dir, exist_ok=True)
            table_data_file = os.path.join(plan_dir, "furnace_table_data.json")
            
            # 收集当前表格数据
            table_data = []
            seq_num = 1
            for row_idx in range(self.table_widget.rowCount()):
                # 检查是否是换辊行或自定义信息行
                first_item = self.table_widget.item(row_idx, 0)
                is_special_row = False
                if first_item:
                    bg_color = first_item.background().color().name()
                    if bg_color in ['#00ff00', '#00FF00', '#ffff00', '#FFFF00']:
                        is_special_row = True
                
                if not is_special_row:
                    # 正常数据行，获取钢卷号
                    coil_item = self.table_widget.item(row_idx, 1)  # 钢卷号列（索引1）
                    if coil_item:
                        coil_number = coil_item.text().strip()
                        if coil_number:
                            table_data.append({
                                "coil_number": coil_number,
                                "sequence": seq_num
                            })
                            seq_num += 1
            
            # 读取之前的表格数据
            previous_table_data = []
            if os.path.exists(table_data_file):
                try:
                    with open(table_data_file, 'r', encoding='utf-8') as f:
                        previous_table_data = json.load(f)
                except:
                    previous_table_data = []
            
            # 保存最近2次的表格数据
            combined_data = [table_data] + previous_table_data[:1]  # 只保留最近2次的数据
            
            # 保存数据
            with open(table_data_file, 'w', encoding='utf-8') as f:
                json.dump(combined_data, f, ensure_ascii=False, indent=2)
            
            print(f"已保存表格数据: {table_data_file}")
            print(f"当前表格数据: {[item['coil_number'] for item in table_data]}")
            if previous_table_data:
                print(f"上一次表格数据: {[item['coil_number'] for item in previous_table_data[0]]}")
        except Exception as e:
            print(f"保存表格数据失败: {str(e)}")
            import traceback
            traceback.print_exc()'''

content = content.replace(old_load_data, new_load_data)

# 写入文件
with open('furnace_order_manager_pyqt5.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("已实现装炉明细窗口的数据加载功能")
