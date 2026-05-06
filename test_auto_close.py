
import tkinter as tk
from tkinter import ttk

def custom_messagebox_test(root, title, message, msg_type='info', auto_close=None):
    """自定义消息框 - 更大的窗口和字体"""
    import tkinter as tk
    from tkinter import ttk
    
    # 创建自定义窗口
    msg_window = tk.Toplevel(root)
    msg_window.title(title)
    msg_window.geometry("600x500")
    msg_window.resizable(True, True)
    
    # 计算居中位置
    screen_width = msg_window.winfo_screenwidth()
    screen_height = msg_window.winfo_screenheight()
    x = (screen_width // 2) - (600 // 2)
    y = (screen_height // 2) - (500 // 2)
    msg_window.geometry(f"600x500+{x}+{y}")
    
    # 设置窗口样式
    msg_window.configure(bg='#f0f0f0')
    
    # 创建主框架
    main_frame = tk.Frame(msg_window, bg='#f0f0f0', padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 消息内容
    message_label = tk.Label(
        main_frame,
        text=message,
        font=('宋体', 14),
        bg='#f0f0f0',
        justify=tk.LEFT,
        wraplength=550
    )
    message_label.pack(expand=True, fill=tk.BOTH)
    
    # 按钮框架
    btn_frame = tk.Frame(main_frame, bg='#f0f0f0')
    btn_frame.pack(side=tk.BOTTOM, pady=20)
    
    # 自动关闭定时器
    auto_close_timer = None
    
    if msg_type == 'yesno':
        # 是/否按钮
        user_choice = [False]  # 使用列表存储，以便在内部函数中修改
        
        def on_yes():
            if auto_close_timer:
                msg_window.after_cancel(auto_close_timer)
            user_choice[0] = True
            msg_window.destroy()
        
        def on_no():
            if auto_close_timer:
                msg_window.after_cancel(auto_close_timer)
            user_choice[0] = False
            msg_window.destroy()
        
        yes_btn = ttk.Button(
            btn_frame,
            text="是",
            command=on_yes,
            width=10
        )
        yes_btn.pack(side=tk.LEFT, padx=10)
        
        no_btn = ttk.Button(
            btn_frame,
            text="否",
            command=on_no,
            width=10
        )
        no_btn.pack(side=tk.LEFT, padx=10)
        
        # 确保弹窗在最前面
        msg_window.transient(root)
        msg_window.lift()
        msg_window.focus_force()
        # 设置"是"按钮为默认焦点
        yes_btn.focus_set()
        # 绑定回车键到"是"按钮
        msg_window.bind('<Return>', lambda event: on_yes())
        msg_window.wait_window()
        
        return user_choice[0]
    else:
        # 确定按钮
        def on_ok():
            if auto_close_timer:
                msg_window.after_cancel(auto_close_timer)
            msg_window.destroy()
        
        ok_btn = ttk.Button(
            btn_frame,
            text="确定",
            command=on_ok,
            width=10
        )
        ok_btn.pack()
        
        # 设置自动关闭
        if auto_close is not None and auto_close > 0:
            # 添加倒计时标签
            countdown_label = tk.Label(
                btn_frame,
                text=f"({auto_close}秒后自动关闭)",
                font=('宋体', 10),
                bg='#f0f0f0',
                fg='gray'
            )
            countdown_label.pack(pady=(5, 0))
            
            remaining_time = [auto_close]
            
            def update_countdown():
                print(f"倒计时: {remaining_time[0]}秒")
                remaining_time[0] -= 1
                if remaining_time[0] > 0:
                    countdown_label.config(text=f"({remaining_time[0]}秒后自动关闭)")
                    nonlocal auto_close_timer
                    auto_close_timer = msg_window.after(1000, update_countdown)
                else:
                    print("倒计时结束，关闭窗口")
                    on_ok()
            
            auto_close_timer = msg_window.after(1000, update_countdown)
        
        # 确保弹窗在最前面
        msg_window.transient(root)
        msg_window.lift()
        msg_window.focus_force()
        # 设置"确定"按钮为默认焦点
        ok_btn.focus_set()
        # 绑定回车键到"确定"按钮
        msg_window.bind('<Return>', lambda event: on_ok())
        
        # 只有当没有设置自动关闭时才使用wait_window()
        if auto_close is None:
            msg_window.wait_window()

def test():
    root = tk.Tk()
    root.title("测试")
    root.geometry("400x300")
    
    def on_click():
        print("点击按钮，准备显示窗口")
        custom_messagebox_test(root, "完成", "没有需要导出的计划号", auto_close=3)
        print("函数调用返回")
    
    btn = tk.Button(root, text="测试自动关闭", command=on_click, font=("宋体", 14))
    btn.pack(pady=50)
    
    root.mainloop()

if __name__ == "__main__":
    test()
