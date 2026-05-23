#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钢卷生产流程动画演示
展示钢卷从计划到生产的整个流程
"""

import pygame
import sys
import time
import math

# 初始化Pygame
pygame.init()

# 设置屏幕尺寸
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("钢卷生产流程动画 - 轧制计划管理系统")

# 定义颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (192, 192, 192)
DARK_GRAY = (64, 64, 64)
BLUE = (0, 112, 192)
LIGHT_BLUE = (173, 216, 230)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 128, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
BROWN = (139, 69, 19)

# 设置字体
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

class Coil:
    """钢卷类"""
    def __init__(self, coil_no, width, thickness, status="待生产"):
        self.coil_no = coil_no
        self.width = width
        self.thickness = thickness
        self.status = status
        self.x = 0
        self.y = 0
        self.color = BLUE

    def draw(self, surface):
        """绘制钢卷"""
        # 绘制钢卷主体（矩形）
        rect = pygame.Rect(self.x - 30, self.y - 20, 60, 40)
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, BLACK, rect, 2)

        # 绘制钢卷内部螺旋效果
        for i in range(3):
            offset = 5 + i * 8
            inner_rect = pygame.Rect(self.x - 25 + offset, self.y - 15 + offset/2,
                                    50 - offset*2, 30 - offset)
            if inner_rect.width > 0 and inner_rect.height > 0:
                pygame.draw.rect(surface, LIGHT_BLUE, inner_rect, 1)

        # 绘制钢卷号
        coil_text = font_small.render(self.coil_no[-4:], True, WHITE)
        text_rect = coil_text.get_rect(center=(self.x, self.y))
        surface.blit(coil_text, text_rect)

class ProductionLine:
    """生产线"""
    def __init__(self):
        self.elements = []
        self.coils = []
        self.time = 0

    def add_element(self, element):
        self.elements.append(element)

    def add_coil(self, coil):
        self.coils.append(coil)

class Element:
    """生产线元素基类"""
    def __init__(self, x, y, width, height, color, label):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.label = label

    def draw(self, surface):
        """绘制元素"""
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, BLACK, rect, 2)

        # 绘制标签
        label_text = font_small.render(self.label, True, WHITE)
        text_rect = label_text.get_rect(center=(self.x + self.width/2, self.y + self.height/2))
        surface.blit(label_text, text_rect)

class Arrow:
    """箭头"""
    def __init__(self, x, y, direction="right"):
        self.x = x
        self.y = y
        self.direction = direction

    def draw(self, surface):
        """绘制箭头"""
        if self.direction == "right":
            points = [(self.x, self.y), (self.x + 20, self.y - 10),
                    (self.x + 20, self.y + 10)]
        elif self.direction == "down":
            points = [(self.x - 10, self.y), (self.x + 10, self.y),
                    (self.x, self.y + 20)]
        elif self.direction == "left":
            points = [(self.x, self.y), (self.x - 20, self.y - 10),
                    (self.x - 20, self.y + 10)]
        else:  # up
            points = [(self.x - 10, self.y + 20), (self.x + 10, self.y + 20),
                    (self.x, self.y)]

        pygame.draw.polygon(surface, DARK_GREEN, points)

def draw_text(surface, text, x, y, color=BLACK, size="medium"):
    """绘制文本"""
    if size == "large":
        text_surface = font_large.render(text, True, color)
    elif size == "small":
        text_surface = font_small.render(text, True, color)
    else:
        text_surface = font_medium.render(text, True, color)

    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)
    return text_rect

def draw_slab(surface, x, y, width=80, height=40, color=BROWN):
    """绘制板坯"""
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(surface, BLACK, rect, 2)

    # 添加纹理效果
    for i in range(3):
        line_y = y + 10 + i * 10
        pygame.draw.line(surface, DARK_GRAY, (x+5, line_y), (x+width-5, line_y), 1)

def draw_roller(surface, x, y, length=100):
    """绘制辊道"""
    pygame.draw.rect(surface, GRAY, (x, y, length, 20))
    pygame.draw.rect(surface, BLACK, (x, y, length, 20), 2)

    # 绘制辊子纹理
    for i in range(int(length / 15)):
        roller_x = x + 7 + i * 15
        pygame.draw.circle(surface, DARK_GRAY, (roller_x, y + 10), 5)
        pygame.draw.circle(surface, BLACK, (roller_x, y + 10), 5, 1)

def draw_furnace(surface, x, y, width=150, height=120):
    """绘制加热炉"""
    # 炉体
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, RED, rect, 3)

    # 炉膛
    inner_rect = pygame.Rect(x + 10, y + 10, width - 20, height - 20)
    pygame.draw.rect(surface, ORANGE, inner_rect)

    # 火焰效果
    for i in range(5):
        flame_x = x + 20 + i * 25
        flame_height = 30 + (i % 3) * 10
        pygame.draw.polygon(surface, YELLOW, [
            (flame_x, y + height - 10),
            (flame_x + 10, y + height - 10 - flame_height),
            (flame_x + 20, y + height - 10)
        ])

    # 标签
    label = font_small.render("加热炉", True, WHITE)
    text_rect = label.get_rect(center=(x + width/2, y + height/2))
    surface.blit(label, text_rect)

def draw_mill_stand(surface, x, y, stand_no):
    """绘制轧机机架"""
    # 机架主体
    rect = pygame.Rect(x, y, 60, 100)
    pygame.draw.rect(surface, BLUE, rect)
    pygame.draw.rect(surface, BLACK, rect, 2)

    # 轧辊
    pygame.draw.rect(surface, GRAY, (x + 5, y + 20, 50, 15))
    pygame.draw.rect(surface, GRAY, (x + 5, y + 65, 50, 15))

    # 标签
    label = font_small.render(f"RT{stand_no}", True, WHITE)
    text_rect = label.get_rect(center=(x + 30, y + 50))
    surface.blit(label, text_rect)

def draw_rolling_mill(surface, x, y):
    """绘制轧机"""
    # 底座
    pygame.draw.rect(surface, DARK_GRAY, (x, y + 80, 300, 40))

    # 机架组
    for i in range(4):
        stand_x = x + 30 + i * 70
        draw_mill_stand(surface, stand_x, y, i + 1)

    # 标签
    label = font_medium.render("粗轧机组", True, WHITE)
    text_rect = label.get_rect(center=(x + 150, y + 110))
    surface.blit(label, text_rect)

def draw_progress_bar(x, y, width, height, progress, label=""):
    """绘制进度条"""
    # 背景
    bg_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, GRAY, bg_rect)
    pygame.draw.rect(screen, BLACK, bg_rect, 2)

    # 进度
    fill_width = int(width * progress)
    fill_rect = pygame.Rect(x, y, fill_width, height)
    pygame.draw.rect(screen, GREEN, fill_rect)

    # 标签
    if label:
        label_surface = font_small.render(label, True, WHITE)
        label_rect = label_surface.get_rect(center=(x + width//2, y + height//2))
        screen.blit(label_surface, label_rect)

def draw_stage_indicators(current_step):
    """绘制阶段指示器"""
    stages = ["计划", "上料", "加热", "粗轧", "精轧", "成品"]
    box_width = 100
    start_x = WIDTH - (len(stages) * (box_width + 10) + 50)

    for i, stage_name in enumerate(stages):
        x = start_x + i * (box_width + 10)
        y = HEIGHT - 70

        color = GREEN if i <= current_step else GRAY
        rect = pygame.Rect(x, y, box_width, 30)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, BLACK, rect, 2)

        text = font_small.render(stage_name, True, WHITE)
        text_rect = text.get_rect(center=(x + box_width//2, y + 15))
        screen.blit(text, text_rect)

def draw_plan_import():
    """绘制计划导入阶段"""
    # 绘制电脑/计划图标
    pygame.draw.rect(screen, GRAY, (WIDTH//2 - 150, 200, 300, 200))
    pygame.draw.rect(screen, BLACK, (WIDTH//2 - 150, 200, 300, 200), 3)

    # 屏幕
    pygame.draw.rect(screen, BLUE, (WIDTH//2 - 130, 220, 260, 140))

    # 计划列表文字
    draw_text(screen, "生产计划列表", WIDTH//2, 260, WHITE, "medium")
    draw_text(screen, "计划号: H5175", WIDTH//2, 290, WHITE, "small")
    draw_text(screen, "钢卷数: 20", WIDTH//2, 320, WHITE, "small")
    draw_text(screen, "总重量: 500t", WIDTH//2, 350, WHITE, "small")

    # 底座
    pygame.draw.rect(screen, DARK_GRAY, (WIDTH//2 - 50, 400, 100, 30))

    # 箭头
    Arrow(WIDTH//2 - 250, 300, "right").draw(screen)
    Arrow(WIDTH//2 + 250, 300, "left").draw(screen)

    draw_text(screen, "计划数据", WIDTH//2 - 200, 300, BLUE, "medium")
    draw_text(screen, "系统", WIDTH//2 + 200, 300, BLUE, "medium")

def draw_slab_loading(progress):
    """绘制板坯上料阶段"""
    y_pos = 350 - progress * 100

    # 上料台
    pygame.draw.rect(screen, GRAY, (100, 450, 100, 50))
    draw_text(screen, "上料台", 150, 475, WHITE, "small")

    # 板坯
    draw_slab(screen, 110, y_pos)

    if progress > 0.5:
        # 箭头移动
        arrow_x = 100 + progress * 100
        Arrow(arrow_x, 300, "right").draw(screen)

def draw_furnace_heating(progress):
    """绘制加热炉阶段"""
    # 加热炉
    draw_furnace(screen, 450, 250)

    # 板坯移动到加热炉
    slab_x = 200 + progress * 250
    draw_slab(screen, slab_x, 300)

    # 温度显示
    if progress > 0.3:
        temp = 20 + progress * 1100  # 20°C 到 1120°C
        temp_text = font_medium.render(f"温度: {int(temp)}°C", True, RED)
        screen.blit(temp_text, (500, 220))

        # 加热进度
        draw_progress_bar(500, 390, 100, 15, progress, "加热进度")

    # 输出箭头
    if progress > 0.8:
        Arrow(620, 300, "right").draw(screen)

def draw_roughing_mill(progress):
    """绘制粗轧阶段"""
    # 轧机
    draw_rolling_mill(screen, 400, 200)

    # 钢坯移动和轧制
    if progress < 0.3:
        # 钢坯进入
        slab_x = 200 + progress * 200
        draw_slab(screen, slab_x, 280, 80 - progress * 20, 40 - progress * 10, ORANGE)
    elif progress < 0.7:
        # 轧制中
        slab_x = 400 + (progress - 0.3) * 300
        thickness = 60 - (progress - 0.3) * 40
        draw_slab(screen, slab_x, 290, 100, thickness, ORANGE)

        # 轧制火花效果
        if int(progress * 10) % 2 == 0:
            pygame.draw.circle(screen, YELLOW, (int(slab_x + 50), 280), 5)
    else:
        # 离开
        slab_x = 520 + (progress - 0.7) * 200
        thickness = 20
        draw_slab(screen, slab_x, 290, 100, thickness, ORANGE)

    # 轧制信息
    if progress > 0.3 and progress < 0.7:
        reduction = int(progress * 100)
        reduction_text = font_small.render(f"压下量: {reduction}%", True, BLUE)
        screen.blit(reduction_text, (550, 180))

        speed_text = font_small.render(f"轧制速度: {3.5 + progress * 1.5:.1f} m/s", True, BLUE)
        screen.blit(speed_text, (550, 200))

def draw_finishing_mill(progress):
    """绘制精轧阶段"""
    # 精轧机组（更紧凑）
    pygame.draw.rect(screen, DARK_GRAY, (400, 280, 350, 40))

    for i in range(6):
        stand_x = 420 + i * 55
        # 轧辊
        pygame.draw.rect(screen, GRAY, (stand_x, 290, 40, 15))
        pygame.draw.rect(screen, GRAY, (stand_x, 305, 40, 15))
        # 机架标签
        label = font_small.render(f"F{i+1}", True, WHITE)
        screen.blit(label, (stand_x + 10, 295))

    draw_text(screen, "精轧机组", 575, 340, BLUE, "small")

    # 钢带
    if progress < 0.2:
        strip_x = 200 + progress * 200
        draw_slab(screen, strip_x, 297, 100, 16, ORANGE)
    elif progress < 0.8:
        strip_x = 400 + (progress - 0.2) * 350
        thickness = max(3, 16 - (progress - 0.2) * 15)
        pygame.draw.rect(screen, ORANGE, (strip_x, 300 - thickness/2, 100, thickness))
        pygame.draw.rect(screen, BLACK, (strip_x, 300 - thickness/2, 100, thickness), 2)
    else:
        strip_x = 550 + (progress - 0.8) * 200
        thickness = 3
        pygame.draw.rect(screen, ORANGE, (strip_x, 298, 100, thickness))
        pygame.draw.rect(screen, BLACK, (strip_x, 298, 100, thickness), 2)

    # 厚度显示
    if progress > 0.3 and progress < 0.8:
        thickness = max(3, 16 - (progress - 0.2) * 15)
        thick_text = font_small.render(f"成品厚度: {thickness:.1f} mm", True, GREEN)
        screen.blit(thick_text, (500, 250))

def draw_finished_coils(progress):
    """绘制成品钢卷"""
    # 输出辊道
    draw_roller(screen, 200, 350, 800)

    # 生成钢卷
    num_coils = int(progress * 5)
    for i in range(num_coils):
        coil_x = 250 + i * 150
        coil_y = 300

        # 创建钢卷对象并绘制
        coil = Coil(f"62019{500+i}", 1250, 3.0, "合格")
        coil.x = coil_x
        coil.y = coil_y
        coil.draw(screen)

        # 质量标签
        if i < num_coils - 1:
            quality = "A" if i % 2 == 0 else "B"
            quality_text = font_small.render(f"质量: {quality}", True, GREEN)
            screen.blit(quality_text, (coil_x - 25, coil_y + 30))

    # 统计信息
    if progress > 0.5:
        draw_text(screen, f"已生产: {num_coils} 卷", 100, 200, BLUE, "medium")
        draw_text(screen, f"合格率: {85 + num_coils * 2}%", 100, 240, GREEN, "medium")
        draw_text(screen, f"生产速度: {2.5 + progress * 0.5:.1f} m/s", 100, 280, ORANGE, "medium")

    # 成品库标签
    draw_text(screen, "成品钢卷库", 600, 200, DARK_GREEN, "large")

def run_animation():
    """运行动画"""
    clock = pygame.time.Clock()
    running = True

    # 创建生产线
    line = ProductionLine()

    # 动画阶段
    stage = 0  # 0: 计划导入, 1: 板坯上料, 2: 加热, 3: 粗轧, 4: 精轧, 5: 成品
    stage_duration = 5  # 每个阶段持续时间（秒）
    stage_timer = 0
    animation_progress = 0

    # 钢卷列表
    coils = []
    coil_positions = []

    # 当前处理的钢卷
    current_coil = None

    # 流程步骤
    steps = [
        "步骤1: 导入生产计划",
        "步骤2: 板坯上料",
        "步骤3: 加热炉加热",
        "步骤4: 粗轧机组轧制",
        "步骤5: 精轧机组轧制",
        "步骤6: 成品钢卷输出"
    ]
    current_step = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # 空格键切换阶段
                    stage = (stage + 1) % 6
                    stage_timer = 0
                    animation_progress = 0
                    current_step = stage
                elif event.key == pygame.K_RIGHT:
                    # 右箭头加速
                    stage_timer += 0.5
                elif event.key == pygame.K_LEFT:
                    # 左箭头减速
                    stage_timer = max(0, stage_timer - 0.5)

        # 更新动画
        dt = clock.tick(30) / 1000.0
        stage_timer += dt
        animation_progress = min(1.0, stage_timer / stage_duration)

        # 阶段切换
        if stage_timer >= stage_duration:
            stage_timer = 0
            animation_progress = 0
            if stage < 5:
                stage += 1
                current_step = stage

        # 清屏
        screen.fill(LIGHT_GRAY)

        # 绘制标题
        title = font_large.render("钢卷生产流程动画演示", True, BLUE)
        title_rect = title.get_rect(center=(WIDTH // 2, 50))
        screen.blit(title, title_rect)

        # 绘制当前步骤
        if current_step < len(steps):
            step_text = font_medium.render(steps[current_step], True, DARK_GREEN)
            step_rect = step_text.get_rect(center=(WIDTH // 2, 100))
            screen.blit(step_text, step_rect)

        # 根据阶段绘制不同的内容
        if stage == 0:
            # 阶段0: 计划导入
            draw_plan_import()
        elif stage == 1:
            # 阶段1: 板坯上料
            draw_slab_loading(animation_progress)
        elif stage == 2:
            # 阶段2: 加热炉加热
            draw_furnace_heating(animation_progress)
        elif stage == 3:
            # 阶段3: 粗轧
            draw_roughing_mill(animation_progress)
        elif stage == 4:
            # 阶段4: 精轧
            draw_finishing_mill(animation_progress)
        elif stage == 5:
            # 阶段5: 成品
            draw_finished_coils(animation_progress)

        # 绘制底部说明
        instructions = font_small.render("空格键: 切换阶段 | 左/右箭头: 减速/加速 | ESC: 退出", True, GRAY)
        screen.blit(instructions, (20, HEIGHT - 40))

        # 绘制阶段进度条
        draw_progress_bar(20, HEIGHT - 70, 200, 20, animation_progress, f"阶段进度: {int(animation_progress * 100)}%")

        # 绘制阶段指示器
        draw_stage_indicators(current_step)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run_animation()
