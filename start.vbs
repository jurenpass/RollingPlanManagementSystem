Set WshShell = CreateObject("WScript.Shell")

' 使用cmd /c命令运行，隐藏命令行窗口，显示主程序窗口
WshShell.Run "cmd /c python furnace_order_manager.py", 0, False
