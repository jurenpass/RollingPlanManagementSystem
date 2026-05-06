import subprocess
import os

os.chdir('g:\\newplan')

# 清理之前的打包文件
subprocess.run(['rmdir', '/s', '/q', 'build', 'dist'], shell=True, capture_output=True)

# 执行打包命令
result = subprocess.run(
    ['pyinstaller', 'furnace_order_manager_pyqt5.spec'],
    capture_output=True,
    text=True,
    timeout=300  # 5分钟超时
)

print("=" * 50)
print("STDOUT:")
print("=" * 50)
print(result.stdout)
print("\n" + "=" * 50)
print("STDERR:")
print("=" * 50)
print(result.stderr)
print("\n" + "=" * 50)
print(f"Return code: {result.returncode}")