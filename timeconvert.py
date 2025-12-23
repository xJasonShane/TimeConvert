import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import re

class TimeConvertApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TimeConvert")
        self.root.geometry("500x400")
        self.root.resizable(True, True)
        
        # 设置主题样式
        self.style = ttk.Style()
        self.style.configure("TLabel", font=(".", 10))
        self.style.configure("TButton", font=(".", 10))
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 输入区域
        self.input_label = ttk.Label(self.main_frame, text="输入时间/日期:")
        self.input_label.pack(anchor="w", pady=(0, 5))
        
        self.input_text = tk.Text(self.main_frame, height=5, wrap=tk.WORD)
        self.input_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 格式区域
        self.format_frame = ttk.LabelFrame(self.main_frame, text="目标格式")
        self.format_frame.pack(fill=tk.X, pady=(0, 10), padx=(0, 0))
        
        # 预设格式列表
        self.preset_formats = {
            "YYYY-MM-DD HH:MM:SS": "%Y-%m-%d %H:%M:%S",
            "YYYY-MM-DD": "%Y-%m-%d",
            "HH:MM:SS": "%H:%M:%S",
            "YYYY/MM/DD HH:MM:SS": "%Y/%m/%d %H:%M:%S",
            "YYYY/MM/DD": "%Y/%m/%d",
            "MM/DD/YYYY": "%m/%d/%Y",
            "DD/MM/YYYY": "%d/%m/%Y",
            "YYYY年MM月DD日 HH时MM分SS秒": "%Y年%m月%d日 %H时%M分%S秒",
            "YYYY年MM月DD日": "%Y年%m月%d日",
            "ISO格式": "%Y-%m-%dT%H:%M:%SZ",
            "星期，DD月YYYY": "%A, %d %B %Y",
        }
        
        # 预设格式选择
        self.preset_var = tk.StringVar(value="YYYY-MM-DD HH:MM:SS")
        self.preset_combo = ttk.Combobox(self.format_frame, textvariable=self.preset_var, 
                                         values=list(self.preset_formats.keys()), state="readonly")
        self.preset_combo.pack(fill=tk.X, pady=(5, 5))
        self.preset_combo.bind("<<ComboboxSelected>>", self.on_preset_selected)
        
        # 自定义格式输入
        self.custom_format_label = ttk.Label(self.format_frame, text="或自定义格式:")
        self.custom_format_label.pack(anchor="w", pady=(5, 0))
        
        self.format_var = tk.StringVar(value=self.preset_formats["YYYY-MM-DD HH:MM:SS"])
        self.format_entry = ttk.Entry(self.format_frame, textvariable=self.format_var)
        self.format_entry.pack(fill=tk.X, pady=(0, 5))
        
        # 格式说明
        self.format_help = ttk.Label(self.format_frame, 
                                    text="格式说明: %Y(年), %m(月), %d(日), %H(时), %M(分), %S(秒)",
                                    font=(".", 8), foreground="gray")
        self.format_help.pack(anchor="w")
        
        # 实时转换 - 绑定输入和格式变化事件
        self.input_text.bind("<KeyRelease>", self.convert_time)
        self.format_entry.bind("<KeyRelease>", self.convert_time)
        self.preset_combo.bind("<<ComboboxSelected>>", lambda event: self.convert_time())
        
        # 输出区域
        self.output_label = ttk.Label(self.main_frame, text="转换结果:")
        self.output_label.pack(anchor="w", pady=(0, 5))
        
        self.output_frame = ttk.Frame(self.main_frame)
        self.output_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.output_text = tk.Text(self.output_frame, height=5, wrap=tk.WORD)
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        self.output_copy_button = ttk.Button(self.output_frame, text="复制", command=self.copy_to_clipboard, width=8)
        self.output_copy_button.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 按钮区域
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill=tk.X)
        
        self.paste_button = ttk.Button(self.button_frame, text="粘贴", command=self.paste_from_clipboard)
        self.paste_button.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        self.copy_button = ttk.Button(self.button_frame, text="复制", command=self.copy_to_clipboard)
        self.copy_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def paste_from_clipboard(self):
        """从剪贴板粘贴内容到输入框"""
        try:
            clipboard_content = self.root.clipboard_get()
            self.input_text.delete(1.0, tk.END)
            self.input_text.insert(tk.END, clipboard_content)
        except Exception as e:
            messagebox.showerror("错误", f"粘贴失败: {str(e)}")
    
    def on_preset_selected(self, event):
        """处理预设格式选择事件"""
        selected = self.preset_var.get()
        if selected in self.preset_formats:
            self.format_var.set(self.preset_formats[selected])
    
    def copy_to_clipboard(self):
        """将转换结果复制到剪贴板"""
        try:
            output_content = self.output_text.get(1.0, tk.END).strip()
            if output_content:
                self.root.clipboard_clear()
                self.root.clipboard_append(output_content)
            # 无声复制，不显示弹窗
        except Exception as e:
            pass
    
    def convert_time(self, event=None):
        """转换时间格式"""
        try:
            # 获取输入内容和目标格式
            input_content = self.input_text.get(1.0, tk.END).strip()
            target_format = self.format_var.get()
            
            # 清除之前的结果
            self.output_text.delete(1.0, tk.END)
            
            if not input_content or not target_format:
                return
            
            # 解析时间
            dt = self.parse_time(input_content)
            if dt:
                # 转换为目标格式
                converted_time = dt.strftime(target_format)
                # 显示结果
                self.output_text.insert(tk.END, converted_time)
        except Exception as e:
            pass
    
    def parse_time(self, time_str):
        """解析各种时间格式"""
        # 预处理函数：将中文日期中的一位数转换为两位数
        def preprocess_chinese_date(s):
            # 按从长到短的顺序处理中文数字组合
            # 先处理最长的组合，避免部分匹配导致错误
            chinese_num_map = {
                # 时、分、秒的完整组合（59以内）
                '五十九': '59',
                '五十八': '58',
                '五十七': '57',
                '五十六': '56',
                '五十五': '55',
                '五十四': '54',
                '五十三': '53',
                '五十二': '52',
                '五十一': '51',
                '五十': '50',
                '四十九': '49',
                '四十八': '48',
                '四十七': '47',
                '四十六': '46',
                '四十五': '45',
                '四十四': '44',
                '四十三': '43',
                '四十二': '42',
                '四十一': '41',
                '四十': '40',
                '三十九': '39',
                '三十八': '38',
                '三十七': '37',
                '三十六': '36',
                '三十五': '35',
                '三十四': '34',
                '三十三': '33',
                '三十二': '32',
                # 月和日的完整组合
                '三十一': '31',
                '三十': '30',
                '二十九': '29',
                '二十八': '28',
                '二十七': '27',
                '二十六': '26',
                '二十五': '25',
                '二十四': '24',
                '二十三': '23',
                '二十二': '22',
                '二十一': '21',
                '二十': '20',
                '十九': '19',
                '十八': '18',
                '十七': '17',
                '十六': '16',
                '十五': '15',
                '十四': '14',
                '十三': '13',
                '十二': '12',
                '十一': '11',
                '十': '10',
                # 单个数字
                '九': '9',
                '八': '8',
                '七': '7',
                '六': '6',
                '五': '5',
                '四': '4',
                '三': '3',
                '二': '2',
                '一': '1',
                '〇': '0',
            }
            
            # 按顺序替换中文数字
            for cn, an in chinese_num_map.items():
                s = s.replace(cn, an)
            
            # 将一位数的月份转换为两位数：年X月 -> 年0X月
            s = re.sub(r'(年)([0-9])(月)', r'\g<1>0\g<2>\g<3>', s)
            # 将一位数的日期转换为两位数：月X日 -> 月0X日
            s = re.sub(r'(月)([0-9])(日)', r'\g<1>0\g<2>\g<3>', s)
            # 将一位数的小时转换为两位数：日X时 -> 日0X时
            s = re.sub(r'(日)([0-9])(时)', r'\g<1>0\g<2>\g<3>', s)
            # 将一位数的分钟转换为两位数：时X分 -> 时0X分
            s = re.sub(r'(时)([0-9])(分)', r'\g<1>0\g<2>\g<3>', s)
            # 将一位数的秒转换为两位数：分X秒 -> 分0X秒
            s = re.sub(r'(分)([0-9])(秒)', r'\g<1>0\g<2>\g<3>', s)
            
            return s
        
        # 常见时间格式列表
        common_formats = [
            # 英文格式
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
            "%Y/%m/%d %H:%M:%S",
            "%Y/%m/%d %H:%M",
            "%Y/%m/%d",
            "%d-%m-%Y %H:%M:%S",
            "%d-%m-%Y %H:%M",
            "%d-%m-%Y",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M",
            "%d/%m/%Y",
            "%H:%M:%S",
            "%H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            # 中文格式
            "%Y年%m月%d日 %H:%M:%S",
            "%Y年%m月%d日 %H:%M",
            "%Y年%m月%d日",
            "%Y年%m月%d日%H时%M分%S秒",
            "%Y年%m月%d日%H时%M分",
            "%Y年%m月%d日%H时",
            "%m月%d日 %H:%M:%S",
            "%m月%d日 %H:%M",
            "%m月%d日",
        ]
        
        # 尝试直接解析
        for fmt in common_formats:
            try:
                return datetime.datetime.strptime(time_str, fmt)
            except ValueError:
                continue
        
        # 尝试解析带有时区的ISO格式
        try:
            return datetime.datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        except ValueError:
            pass
        
        # 尝试预处理中文日期格式
        try:
            processed_str = preprocess_chinese_date(time_str)
            for fmt in common_formats:
                try:
                    return datetime.datetime.strptime(processed_str, fmt)
                except ValueError:
                    continue
        except Exception:
            pass
        
        # 最后尝试解析时间戳，且只对纯数字字符串进行解析
        # 时间戳格式：纯数字，长度10位（秒）或13位（毫秒）或含小数点
        if re.match(r'^[0-9]+(\.[0-9]+)?$', time_str):
            # 检查长度是否合理（避免单个数字被解析）
            # 秒级时间戳：10位左右，毫秒级：13位左右
            str_len = len(time_str.replace('.', ''))
            if 9 <= str_len <= 14:
                try:
                    # 整数时间戳（秒）
                    timestamp = int(time_str)
                    return datetime.datetime.fromtimestamp(timestamp)
                except ValueError:
                    try:
                        # 浮点数时间戳（秒）
                        timestamp = float(time_str)
                        return datetime.datetime.fromtimestamp(timestamp)
                    except ValueError:
                        pass
        
        return None

if __name__ == "__main__":
    root = tk.Tk()
    app = TimeConvertApp(root)
    root.mainloop()
