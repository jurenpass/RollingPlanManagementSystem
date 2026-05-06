import subprocess
import sys

# 运行打包后的程序
app_path = r"g:\newplan\dist\轧制计划管理系统_20260426_233017.exe"

print(f"运行打包后的程序: {app_path}")
print("请点击自动导出按钮，观察控制台输出...")
print("=" * 80)

try:
    # 运行程序并捕获输出
    process = subprocess.Popen(
        [app_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=True
    )
    
    # 实时读取输出
    while True:
        # 读取标准输出
        stdout_line = process.stdout.readline()
        if stdout_line:
            print(f"[STDOUT] {stdout_line.strip()}")
        
        # 读取标准错误
        stderr_line = process.stderr.readline()
        if stderr_line:
            print(f"[STDERR] {stderr_line.strip()}")
        
        # 检查进程是否结束
        if process.poll() is not None:
            # 读取剩余输出
            for stdout_line in process.stdout:
                print(f"[STDOUT] {stdout_line.strip()}")
            for stderr_line in process.stderr:
                print(f"[STDERR] {stderr_line.strip()}")
            break
            
except Exception as e:
    print(f"运行程序时出错: {e}")
