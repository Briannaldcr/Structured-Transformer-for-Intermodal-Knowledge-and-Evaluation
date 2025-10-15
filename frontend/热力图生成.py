import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as patches
from matplotlib.widgets import Button, Slider, RadioButtons
from scipy import ndimage
from PIL import Image
import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading


class AdvancedHeatmapTool:
    """高级热力图绘制工具"""

    def __init__(self, width=1200, height=800):
        self.width = width
        self.height = height
        self.heatmap_data = np.zeros((height, width))
        self.background_image = None
        self.drawing_mode = 'brush'
        self.brush_size = 20
        self.intensity = 0.8
        self.blur_radius = 15
        self.color_scheme = 'rainbow'
        self.polygon_points = []
        self.is_drawing = False

        # 色彩方案定义 - 最内侧使用鲜艳的大红色
        self.color_schemes = {
            'rainbow': ['#000040', '#0000FF', '#0080FF', '#00FFFF', '#00FF80', '#80FF00', '#FFFF00', '#FF8000', '#FF0000', '#FF0000', '#FF0000'],
            'heat': ['#000000', '#330000', '#660000', '#990000', '#CC0000', '#FF0000', '#FF0000', '#FF0000', '#FF0000', '#FF0000', '#FF0000', '#FF0000'],
            'cool': ['#000066', '#0000CC', '#0033FF', '#0066FF', '#0099FF', '#00CCFF', '#00FFFF', '#33FFCC', '#66FF99', '#FFFF00', '#FF8000', '#FF0000'],
            'plasma': ['#0D0887', '#42049E', '#6A00A8', '#8F0DA4', '#B12A90', '#CC4778', '#E16462', '#F68E56', '#FF0000', '#FF0000'],
            'viridis': ['#440154', '#3B528B', '#21908C', '#5DC863', '#B8DE29', '#FF0000'],
            'inferno': ['#000004', '#1B0C41', '#3B0F70', '#5C1A6B', '#7C2E5F', '#9C4651', '#BC5E42', '#DC7633', '#FC8E24', '#FF0000', '#FF0000', '#FF0000']
        }

        self.setup_gui()

    def setup_gui(self):
        """设置GUI界面"""
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("Python高级热力图绘制工具")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')

        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 控制面板
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding=10)
        control_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))

        self.setup_controls(control_frame)

        # 画布区域
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.setup_matplotlib(canvas_frame)

    def setup_controls(self, parent):
        """设置控制控件"""
        # 第一行控件
        row1 = ttk.Frame(parent)
        row1.pack(fill=tk.X, pady=5)

        # 绘制模式
        ttk.Label(row1, text="绘制模式:").pack(side=tk.LEFT, padx=(0, 5))
        self.mode_var = tk.StringVar(value='brush')
        mode_combo = ttk.Combobox(row1, textvariable=self.mode_var, width=12,
                                  values=['brush', 'eraser', 'circle', 'rectangle', 'ellipse', 'polygon', 'gradient'])
        mode_combo.pack(side=tk.LEFT, padx=(0, 20))
        mode_combo.bind('<<ComboboxSelected>>', self.on_mode_change)

        # 笔刷大小
        ttk.Label(row1, text="笔刷大小:").pack(side=tk.LEFT, padx=(0, 5))
        self.brush_scale = tk.Scale(row1, from_=5, to=100, orient=tk.HORIZONTAL,
                                    command=self.on_brush_change)
        self.brush_scale.set(20)
        self.brush_scale.pack(side=tk.LEFT, padx=(0, 20))

        # 强度值
        ttk.Label(row1, text="强度值:").pack(side=tk.LEFT, padx=(0, 5))
        self.intensity_scale = tk.Scale(row1, from_=0, to=100, orient=tk.HORIZONTAL,
                                        command=self.on_intensity_change)
        self.intensity_scale.set(80)
        self.intensity_scale.pack(side=tk.LEFT, padx=(0, 20))

        # 第二行控件
        row2 = ttk.Frame(parent)
        row2.pack(fill=tk.X, pady=5)

        # 模糊半径
        ttk.Label(row2, text="模糊半径:").pack(side=tk.LEFT, padx=(0, 5))
        self.blur_scale = tk.Scale(row2, from_=0, to=50, orient=tk.HORIZONTAL,
                                   command=self.on_blur_change)
        self.blur_scale.set(15)
        self.blur_scale.pack(side=tk.LEFT, padx=(0, 20))

        # 色彩方案
        ttk.Label(row2, text="色彩方案:").pack(side=tk.LEFT, padx=(0, 5))
        self.color_var = tk.StringVar(value='rainbow')
        color_combo = ttk.Combobox(row2, textvariable=self.color_var, width=10,
                                   values=list(self.color_schemes.keys()))
        color_combo.pack(side=tk.LEFT, padx=(0, 20))
        color_combo.bind('<<ComboboxSelected>>', self.on_color_change)

        # 第三行 - 按钮组
        row3 = ttk.Frame(parent)
        row3.pack(fill=tk.X, pady=10)

        # 导入导出按钮
        ttk.Button(row3, text="导入图片", command=self.import_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(row3, text="导出PNG", command=lambda: self.export_image('png')).pack(side=tk.LEFT, padx=5)
        ttk.Button(row3, text="导出SVG", command=lambda: self.export_image('svg')).pack(side=tk.LEFT, padx=5)
        ttk.Button(row3, text="导出数据", command=self.export_data).pack(side=tk.LEFT, padx=5)

        # 预设按钮
        ttk.Separator(row3, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=10)
        ttk.Button(row3, text="高斯分布", command=self.generate_gaussian).pack(side=tk.LEFT, padx=5)
        ttk.Button(row3, text="正弦波", command=self.generate_sine).pack(side=tk.LEFT, padx=5)
        ttk.Button(row3, text="随机热点", command=self.generate_random).pack(side=tk.LEFT, padx=5)
        ttk.Button(row3, text="环形结构", command=self.generate_ring).pack(side=tk.LEFT, padx=5)

        # 清空按钮
        ttk.Separator(row3, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=10)
        ttk.Button(row3, text="清空画布", command=self.clear_canvas).pack(side=tk.LEFT, padx=5)

    def setup_matplotlib(self, parent):
        """设置matplotlib画布"""
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.fig.patch.set_facecolor('#f0f0f0')

        # 创建画布
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # 工具栏
        toolbar = NavigationToolbar2Tk(self.canvas, parent)
        toolbar.update()

        # 连接鼠标事件
        self.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.canvas.mpl_connect('button_release_event', self.on_mouse_release)

        self.render_heatmap()

    def on_mode_change(self, event=None):
        """模式改变事件"""
        self.drawing_mode = self.mode_var.get()
        self.polygon_points = []

    def on_brush_change(self, value):
        """笔刷大小改变事件"""
        self.brush_size = int(value)

    def on_intensity_change(self, value):
        """强度改变事件"""
        self.intensity = int(value) / 100.0

    def on_blur_change(self, value):
        """模糊半径改变事件"""
        self.blur_radius = int(value)
        self.render_heatmap()

    def on_color_change(self, event=None):
        """色彩方案改变事件"""
        self.color_scheme = self.color_var.get()
        self.render_heatmap()

    def on_mouse_press(self, event):
        """鼠标按下事件"""
        if event.inaxes != self.ax or event.xdata is None or event.ydata is None:
            return

        x, y = int(event.xdata), int(event.ydata)

        if self.drawing_mode == 'brush':
            self.is_drawing = True
            self.add_heat_point(x, y, self.intensity, self.brush_size)
            self.render_heatmap()
        elif self.drawing_mode == 'eraser':
            self.is_drawing = True
            self.erase_heat_point(x, y, self.brush_size)
            self.render_heatmap()
        elif self.drawing_mode == 'polygon':
            self.polygon_points.append((x, y))
        else:
            self.start_point = (x, y)
            self.is_drawing = True

    def on_mouse_move(self, event):
        """鼠标移动事件"""
        if not self.is_drawing or event.inaxes != self.ax or event.xdata is None or event.ydata is None:
            return

        if self.drawing_mode == 'brush':
            x, y = int(event.xdata), int(event.ydata)
            self.add_heat_point(x, y, self.intensity, self.brush_size)
            self.render_heatmap()
        elif self.drawing_mode == 'eraser':
            x, y = int(event.xdata), int(event.ydata)
            self.erase_heat_point(x, y, self.brush_size)
            self.render_heatmap()

    def on_mouse_release(self, event):
        """鼠标释放事件"""
        if not self.is_drawing or event.inaxes != self.ax or event.xdata is None or event.ydata is None:
            return

        x, y = int(event.xdata), int(event.ydata)

        if self.drawing_mode == 'brush':
            self.is_drawing = False
        elif self.drawing_mode != 'polygon' and hasattr(self, 'start_point'):
            self.draw_shape(self.start_point[0], self.start_point[1], x, y)
            self.render_heatmap()
            self.is_drawing = False

    def add_heat_point(self, x, y, intensity, size):
        """添加热力点"""
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return

        radius = size // 2
        y_indices, x_indices = np.ogrid[-radius:radius + 1, -radius:radius + 1]
        distance = np.sqrt(x_indices ** 2 + y_indices ** 2)

        # 创建圆形遮罩
        mask = distance <= radius
        falloff = np.cos(distance / radius * np.pi / 2)
        falloff[~mask] = 0

        # 计算影响区域
        y_min = max(0, y - radius)
        y_max = min(self.height, y + radius + 1)
        x_min = max(0, x - radius)
        x_max = min(self.width, x + radius + 1)

        # 调整falloff数组大小
        falloff_y_start = max(0, radius - y)
        falloff_y_end = falloff_y_start + (y_max - y_min)
        falloff_x_start = max(0, radius - x)
        falloff_x_end = falloff_x_start + (x_max - x_min)

        # 应用热力值
        contribution = intensity * falloff[falloff_y_start:falloff_y_end,
                                   falloff_x_start:falloff_x_end]
        self.heatmap_data[y_min:y_max, x_min:x_max] = np.minimum(1.0,
                                                                 self.heatmap_data[y_min:y_max,
                                                                 x_min:x_max] + contribution)

    def erase_heat_point(self, x, y, size):
        """橡皮擦功能 - 擦除热力点"""
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return

        radius = size // 2
        y_indices, x_indices = np.ogrid[-radius:radius + 1, -radius:radius + 1]
        distance = np.sqrt(x_indices ** 2 + y_indices ** 2)

        # 创建圆形遮罩
        mask = distance <= radius
        falloff = np.cos(distance / radius * np.pi / 2)
        falloff[~mask] = 0

        # 计算影响区域
        y_min = max(0, y - radius)
        y_max = min(self.height, y + radius + 1)
        x_min = max(0, x - radius)
        x_max = min(self.width, x + radius + 1)

        # 调整falloff数组大小
        falloff_y_start = max(0, radius - y)
        falloff_y_end = falloff_y_start + (y_max - y_min)
        falloff_x_start = max(0, radius - x)
        falloff_x_end = falloff_x_start + (x_max - x_min)

        # 擦除热力值（减去而不是增加）
        eraser_strength = 0.8 * falloff[falloff_y_start:falloff_y_end,
                                        falloff_x_start:falloff_x_end]
        self.heatmap_data[y_min:y_max, x_min:x_max] = np.maximum(0.0,
                                                                 self.heatmap_data[y_min:y_max,
                                                                 x_min:x_max] - eraser_strength)

    def draw_shape(self, x1, y1, x2, y2):
        """绘制形状"""
        mode = self.drawing_mode

        if mode == 'circle':
            radius = int(np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))
            self.fill_circle(x1, y1, radius)
        elif mode == 'rectangle':
            self.fill_rectangle(x1, y1, x2, y2)
        elif mode == 'ellipse':
            self.fill_ellipse(x1, y1, abs(x2 - x1), abs(y2 - y1))
        elif mode == 'gradient':
            self.fill_gradient(x1, y1, x2, y2)

    def fill_circle(self, cx, cy, radius):
        """填充圆形"""
        y, x = np.ogrid[:self.height, :self.width]
        distance = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
        mask = distance <= radius
        falloff = 1 - (distance / radius)
        falloff = np.maximum(0, falloff)
        self.heatmap_data = np.minimum(1.0, self.heatmap_data + self.intensity * falloff * mask)

    def fill_rectangle(self, x1, y1, x2, y2):
        """填充矩形"""
        x_min, x_max = min(x1, x2), max(x1, x2)
        y_min, y_max = min(y1, y2), max(y1, y2)

        x_min = max(0, x_min)
        x_max = min(self.width, x_max)
        y_min = max(0, y_min)
        y_max = min(self.height, y_max)

        self.heatmap_data[y_min:y_max, x_min:x_max] = np.minimum(1.0,
                                                                 self.heatmap_data[y_min:y_max,
                                                                 x_min:x_max] + self.intensity)

    def fill_ellipse(self, cx, cy, rx, ry):
        """填充椭圆"""
        if rx == 0 or ry == 0:
            return

        y, x = np.ogrid[:self.height, :self.width]
        distance = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
        mask = distance <= 1
        falloff = 1 - np.sqrt(distance)
        falloff = np.maximum(0, falloff)
        self.heatmap_data = np.minimum(1.0, self.heatmap_data + self.intensity * falloff * mask)

    def fill_gradient(self, x1, y1, x2, y2):
        """填充渐变"""
        y, x = np.ogrid[:self.height, :self.width]

        # 计算到起点和终点的距离
        d1 = np.sqrt((x - x1) ** 2 + (y - y1) ** 2)
        d2 = np.sqrt((x - x2) ** 2 + (y - y2) ** 2)

        total_distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        if total_distance == 0:
            return

        intensity_map = self.intensity * (1 - np.minimum(d2 / total_distance, 1))
        intensity_map = np.maximum(0, intensity_map)

        self.heatmap_data = np.minimum(1.0, self.heatmap_data + intensity_map)

    def render_heatmap(self):
        """渲染热力图"""
        self.ax.clear()

        # 应用高斯模糊
        if self.blur_radius > 0:
            blurred_data = ndimage.gaussian_filter(self.heatmap_data, sigma=self.blur_radius / 3)
        else:
            blurred_data = self.heatmap_data

        # 绘制背景图片
        if self.background_image is not None:
            self.ax.imshow(self.background_image, extent=[0, self.width, self.height, 0],
                           aspect='auto', alpha=1.0, interpolation='nearest')  # 保持背景清晰不虚化

        # 创建色彩映射
        colors = self.color_schemes[self.color_scheme]
        cmap = LinearSegmentedColormap.from_list('custom', colors, N=256)

        # 绘制热力图
        masked_data = np.ma.masked_where(blurred_data <= 0.01, blurred_data)
        im = self.ax.imshow(masked_data, cmap=cmap, alpha=0.5,
                            extent=[0, self.width, self.height, 0], aspect='auto')

        # 添加色彩条
        if not hasattr(self, 'colorbar') or self.colorbar is None:
            self.colorbar = self.fig.colorbar(im, ax=self.ax, fraction=0.046, pad=0.04)
        else:
            self.colorbar.update_normal(im)

        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(self.height, 0)
        self.ax.set_title(f"热力图 - {self.drawing_mode}模式", fontsize=14, fontweight='bold')

        self.canvas.draw()

    def import_image(self):
        """导入图片"""
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp *.tiff"), ("所有文件", "*.*")]
        )

        if file_path:
            try:
                # 加载图片
                img = Image.open(file_path)
                img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)

                # 询问导入方式
                choice = messagebox.askyesnocancel(
                    "导入方式",
                    "是：作为背景图片\n否：转换为热力数据\n取消：不导入"
                )

                if choice is True:  # 作为背景
                    self.background_image = np.array(img)
                elif choice is False:  # 转换为热力数据
                    # 转换为灰度
                    gray_img = img.convert('L')
                    gray_array = np.array(gray_img) / 255.0
                    # 反转亮度（暗的区域变成热点）
                    heat_data = 1 - gray_array
                    self.heatmap_data = np.maximum(self.heatmap_data, heat_data)

                self.render_heatmap()
                messagebox.showinfo("成功", "图片导入成功！")

            except Exception as e:
                messagebox.showerror("错误", f"导入图片失败：{str(e)}")

    def export_image(self, format_type='png'):
        """导出图片"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format_type == 'svg':
            filename = filedialog.asksaveasfilename(
                defaultextension=".svg",
                filetypes=[("SVG文件", "*.svg")],
                initialfile=f"heatmap_{timestamp}.svg"
            )
        else:
            filename = filedialog.asksaveasfilename(
                defaultextension=f".{format_type}",
                filetypes=[(f"{format_type.upper()}文件", f"*.{format_type}")],
                initialfile=f"heatmap_{timestamp}.{format_type}"
            )

        if filename:
            try:
                # 创建高分辨率图像
                fig, ax = plt.subplots(figsize=(12, 8), dpi=300)

                # 应用高斯模糊
                if self.blur_radius > 0:
                    blurred_data = ndimage.gaussian_filter(self.heatmap_data, sigma=self.blur_radius / 3)
                else:
                    blurred_data = self.heatmap_data

                # 绘制背景图片
                if self.background_image is not None:
                    ax.imshow(self.background_image, extent=[0, self.width, self.height, 0],
                              aspect='auto', alpha=0.3)

                # 创建色彩映射
                colors = self.color_schemes[self.color_scheme]
                cmap = LinearSegmentedColormap.from_list('custom', colors, N=256)

                # 绘制热力图
                masked_data = np.ma.masked_where(blurred_data <= 0.01, blurred_data)
                im = ax.imshow(masked_data, cmap=cmap, alpha=0.8,
                               extent=[0, self.width, self.height, 0], aspect='auto')

                # 添加色彩条
                cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
                cbar.set_label('强度', fontsize=12)

                ax.set_xlim(0, self.width)
                ax.set_ylim(self.height, 0)
                ax.set_title("高级热力图", fontsize=16, fontweight='bold')

                plt.tight_layout()

                if format_type == 'svg':
                    plt.savefig(filename, format='svg', dpi=300, bbox_inches='tight')
                else:
                    plt.savefig(filename, format=format_type, dpi=300, bbox_inches='tight',
                                transparent=(format_type == 'png'))

                plt.close(fig)
                messagebox.showinfo("成功", f"图片已导出为 {filename}")

            except Exception as e:
                messagebox.showerror("错误", f"导出失败：{str(e)}")

    def export_data(self):
        """导出数据"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json")],
            initialfile=f"heatmap_data_{timestamp}.json"
        )

        if filename:
            try:
                data = {
                    'width': self.width,
                    'height': self.height,
                    'data': self.heatmap_data.tolist(),
                    'color_scheme': self.color_scheme,
                    'blur_radius': self.blur_radius,
                    'timestamp': datetime.now().isoformat()
                }

                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                messagebox.showinfo("成功", f"数据已导出为 {filename}")

            except Exception as e:
                messagebox.showerror("错误", f"导出数据失败：{str(e)}")

    def generate_gaussian(self):
        """生成高斯分布"""
        self.clear_canvas()

        center_x, center_y = self.width // 2, self.height // 2
        sigma = 100

        y, x = np.ogrid[:self.height, :self.width]
        distance = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
        self.heatmap_data = np.exp(-(distance ** 2) / (2 * sigma ** 2))

        self.render_heatmap()

    def generate_sine(self):
        """生成正弦波"""
        self.clear_canvas()

        y, x = np.ogrid[:self.height, :self.width]
        self.heatmap_data = (np.sin(x / 50) * np.sin(y / 50) + 1) / 2

        self.render_heatmap()

    def generate_random(self):
        """生成随机热点"""
        self.clear_canvas()

        for _ in range(20):
            x = np.random.randint(0, self.width)
            y = np.random.randint(0, self.height)
            intensity = np.random.uniform(0.2, 0.8)
            size = np.random.randint(20, 100)
            self.add_heat_point(x, y, intensity, size)

        self.render_heatmap()

    def generate_ring(self):
        """生成环形结构"""
        self.clear_canvas()

        center_x, center_y = self.width // 2, self.height // 2
        inner_radius, outer_radius = 100, 200

        y, x = np.ogrid[:self.height, :self.width]
        distance = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)

        # 创建环形
        ring_mask = (distance >= inner_radius) & (distance <= outer_radius)
        ring_intensity = 1 - np.abs(distance - (inner_radius + outer_radius) / 2) / ((outer_radius - inner_radius) / 2)
        ring_intensity = np.maximum(0, ring_intensity)

        self.heatmap_data = ring_intensity * ring_mask

        self.render_heatmap()

    def clear_canvas(self):
        """清空画布"""
        self.heatmap_data = np.zeros((self.height, self.width))
        self.background_image = None
        self.polygon_points = []
        self.render_heatmap()

    def run(self):
        """运行应用"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        """关闭应用"""
        plt.close('all')
        self.root.destroy()


def main():
    """主函数"""
    print("启动Python高级热力图绘制工具...")
    print("功能说明：")
    print("1. 支持多种绘制模式：画笔、圆形、矩形、椭圆、多边形、渐变")
    print("2. 可导入图片作为背景或转换为热力数据")
    print("3. 支持导出PNG、SVG格式和JSON数据")
    print("4. 内置多种学术级色彩方案")
    print("5. 支持高斯模糊和实时渲染")
    print("\n正在初始化...")

    try:
        app = AdvancedHeatmapTool()
        app.run()
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()