import logging
import os
import signal
import threading
import time
import tkinter as tk
import sys
from tkinter import filedialog
import tkinter.messagebox
import importlib
import datetime
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from pymodbus import FramerType
from pymodbus.client import ModbusSerialClient, serial
from pymodbus.exceptions import ModbusIOException
import serial.tools.list_ports

# 设置日志级别为INFO，获取日志记录器实例
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(stream_handler)

class TestClient:
    class StdoutRedirector:
        _instance = None
        _lock = threading.Lock()
        
        def __new__(cls, *args, **kwargs):
           if not cls._instance:
               with cls._lock:
                   if not cls._instance:
                       cls._instance = super().__new__(cls)
           return cls._instance
       
        def __init__(self, text_widget):
            self.text_widget = text_widget
            self.text_widget.config(state=tk.NORMAL)
            self.buffer = ''
            self.keyword_color_fail = "red"
            self.keyword_color_pass = "green"
            self.lock = threading.Lock()
        def write(self, string):
            try:
                with self.lock:
                    self.buffer += string
                    lines = self.buffer.split('\n')
                    for line in lines[: -1]:
                        if "不通过" in line:
                            self.text_widget.insert(tk.END, line + '\n', "fail_tag")
                        elif "通过" in line:
                            self.text_widget.insert(tk.END, line + '\n', "pass_tag")
                        else:
                            self.text_widget.insert(tk.END, line + '\n')
                    self.buffer = lines[-1]
                    self.text_widget.see(tk.END)
            except Exception as e:
                logger.error(f"Error in write method: {e}")

        def reset(self):
            with self.lock:
                self.processed_lines.clear()

        def flush(self):
            pass
        
    def __init__(self):
        """
        初始化TestClient类的实例。

        这个函数创建了测试工具的主窗口，设置了一些基本的变量，
        并创建了界面的初始组件。
        """
        self.version = 'V0.8'
        self.root = tk.Tk()
        self.root.title("测试工具")
        self.root.geometry('1200x800')
        self.style = ttk.Style()
        self.script_options = []
        self.script_name = None
        self.keyword_color_fail = "red"
        self.keyword_color_pass = "green"

        # 与脚本执行相关的线程和运行状态变量初始化
        self.thread = None
        self.running = False
        
        self.stdout_redirector = None
        
        # 端口相关变量初始化，初始化为无可用端口
        self.port_names = []
        #已加载端口新信息，方便查看当前进展
        self.notify_ports=[]
        self.update_port_complete = False
        # 用于存储不同端口对应的版本号
        self.port_versions = {}
        self.device_version = ''
        #当前选中的端口
        self.selected_port = '无可用端口'
        # 是否选中所有端口
        self.is_all_ports_selected = False
        
        #老化时间选项
        self.aging_duration_options = [0.5, 1, 1.5, 3, 8, 12, 24, 48, 96, 168]
        #默认老化时长
        self.selected_aging_duration = 0.5
        #刷新功能间隔时长
        self.last_refresh_time = 0
        
        self.updating_port_info = False
        
        self.create_widgets()
        self.update_selected_option()
        
        # 注册信号处理函数
        signal.signal(signal.SIGINT, self.on_signal)
        signal.signal(signal.SIGTERM, self.on_signal)


    def create_style(self):
        """
        创建自定义的Tkinter样式。

        这个函数为Tkinter的ttk部件配置各种样式，包括按钮、标签、框架等。
        """
        # 配置TButton的样式，设置字体、前景色、背景色、样式、边框宽度和内边距等
        self.style.configure('TButton',
                             font=('Helvetica', 12),
                             foreground='black',
                             background='#d9d9d9',
                             relief='raised',
                             borderwidth=2,
                             padding=(5, 2))

        # 自定义带3D效果的Label样式，设置边框宽度、样式和内边距
        self.style.configure('3DLabel.TLabel',
                             borderwidth=2,
                             relief='raised',
                             padding=(5, 2))

        # 自定义关于标签的样式，设置前景色和换行宽度
        self.style.configure('AboutLabel.TLabel',
                             foreground='black',
                             wraplength=300)

        # 为ttk.Frame设置样式，设置背景颜色为lightgray
        self.style.configure('GrayFrame.TFrame', background='lightgray')
        
        # 创建样式对象
        style = ttk.Style()
        style.configure('TCheckbutton', font=('Arial', 12))

    def create_widgets(self):
        """
        创建测试工具的各种界面组件。

        这个函数创建了菜单栏、端口号相关部件、测试结果显示部件、
        开始测试按钮、任务状态标签等界面组件，并进行布局。
        """
        self.create_style()

        # 创建菜单栏
        menu_bar = tk.Menu(self.root)
        file_menu_items = [
            ("加载脚本", self.load_scripts_from_menu),
            ("保存记录", self.save_record),
            ("退出", menu_bar.pack_forget),
        ]
        file_menu = self.create_menu("文件", file_menu_items)
        about_menu_items = [("版本", self.about_version)]
        about_menu = self.create_menu("关于", about_menu_items)
        menu_bar.add_cascade(label="文件", menu=file_menu)
        menu_bar.add_separator()
        menu_bar.add_cascade(label="关于", menu=about_menu)
        self.root.config(menu=menu_bar)

        label_font = ('Helvetica', 12, 'bold')

        # 端口号相关框架及部件布局
        port_frame = ttk.Frame(self.root)
        port_frame.grid(row=1, column=0, padx=5, pady=2,sticky=tk.W)

        port_label = ttk.Label(port_frame, text='端口号:', font=label_font)
        port_label.grid(row=0, column=0, padx=5, pady=5)

        option_menu_frame = ttk.Frame(port_frame)
        option_menu_frame.grid(row=0, column=1, padx=5, pady=5)

        self.combobox_ports = ttk.Combobox(option_menu_frame, values=self.port_names, state='readonly')
        self.combobox_ports.grid(row=0, column=0, padx=5, pady=5)
        # 绑定响应函数
        self.combobox_ports.bind("<<ComboboxSelected>>", self.on_combobox_ports_select)
        
        self.select_all_ports_ckbutton = ttk.Checkbutton(option_menu_frame, text='选中所有端口设备')
        self.select_all_ports_ckbutton['style'] = 'TCheckbutton'
        self.select_all_ports_ckbutton.state(['!selected'])
        self.select_all_ports_ckbutton['command'] = self.on_checkbutton_click
        self.select_all_ports_ckbutton.grid(row=0, column=1, padx=5, pady=5)

        version_label = ttk.Label(option_menu_frame, text='软件版本:', font=label_font)
        version_label.grid(row=0, column=2, padx=5, pady=5)

        self.version_text = tk.Label(option_menu_frame, font=label_font)
        self.version_text.grid(row=0, column=3, padx=5, pady=5)

        refresh_button = ttk.Button(option_menu_frame, text='刷新', command=self.update_selected_option)
        refresh_button.grid(row=0, column=4, padx=5, pady=5)
        
        # 添加一个标签用于显示刷新状态
        self.refresh_status_label = tk.Label(option_menu_frame, text='', foreground='blue')
        self.refresh_status_label.grid(row=0, column=5, padx=5, pady=5)
        
        # 老化时间
        aging_frame = ttk.Frame(self.root)
        aging_frame.grid(row=2, column=0, padx=5, pady=2,sticky=tk.W)

        cycle_label = ttk.Label(aging_frame, text='老化时间(单位H):', font=label_font)
        cycle_label.grid(row=0, column=0, padx=5, pady=5)
        
        option_menu_frame2 = ttk.Frame(aging_frame)
        option_menu_frame2.grid(row=0, column=1, padx=5, pady=5)

        self.combobox_aging = ttk.Combobox(option_menu_frame2,
                                     values=self.aging_duration_options, state='readonly')
        self.combobox_aging.set(self.selected_aging_duration)
       
        self.combobox_aging.grid(row=0, column=0, padx=5, pady=5)
        # 绑定响应函数
        self.combobox_aging.bind("<<ComboboxSelected>>", self.on_combobox_aging_select)
        
        # 测试结果标签布局
        test_result_label = ttk.Label(self.root, text='测试详情', font=label_font)
        test_result_label.grid(row=3, column=0, columnspan=4, padx=20, pady=5)
        self.root.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # 文本框相关框架及部件布局
        text_frame = ttk.Frame(self.root, style='GrayFrame.TFrame')
        text_frame.grid(row=4, column=0, columnspan=4, padx=10, pady=5)
        text_frame.grid_columnconfigure(0, weight=1)

        text_subframe = ttk.Frame(text_frame)
        text_subframe.pack(fill=tk.BOTH, expand=True)

        self.text_test_result = ScrolledText(text_subframe, height=30, width=120, font=('Helvetica', 10), bg='white',
                                             relief='sunken')
        self.text_test_result.pack(side=tk.LEFT)
        self.text_test_result.tag_config("fail_tag", foreground=self.keyword_color_fail)
        self.text_test_result.tag_config("pass_tag", foreground=self.keyword_color_pass)

        scrollbar = ttk.Scrollbar(text_frame, command=self.text_test_result.yview, style='GrayFrame.TFrame')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_test_result['yscrollcommand'] = scrollbar.set
        
        # 首次加载脚本，提供打印信息到客户端
        self.stdout_redirector = self.StdoutRedirector(self.text_test_result)
        stream_handler = logging.StreamHandler(stream=self.stdout_redirector)
        logger.addHandler(stream_handler)
        sys.stdout = self.stdout_redirector

        # 开始测试按钮布局
        self.start_test_button = ttk.Button(self.root, text='开始测试', command=self.load_scripts)
        self.start_test_button.grid(row=5, column=1, padx=10, pady=5)
        self.root.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # 任务状态标签布局
        self.thread_status_label = ttk.Label(self.root, text='任务状态: 未运行', font=('Helvetica', 12, 'italic'))
        self.thread_status_label.grid(row=6, column=1, padx=10, pady=5)
        self.root.grid_columnconfigure((0, 1, 2, 3), weight=1)
       
        self.root.protocol('WM_DELETE_WINDOW', lambda: self.on_close())

    def on_combobox_ports_select(self,event):
        selected_index = self.combobox_ports.current()
        self.selected_port = self.port_names[selected_index]
        self.version_text.config(text=self.port_versions.get(self.selected_port))
        logger.info(f'已选中{self.selected_port}设备')
        
    def on_combobox_aging_select(self,event):
        selected_index = self.combobox_aging.current()
        self.selected_aging_duration = self.aging_duration_options[selected_index]
        logger.info(f'已选中老化时长为{self.selected_aging_duration}小时')
    
    def create_menu(self,title, items):
        menu = tk.Menu(self.root, tearoff=0)
        for item in items:
            if isinstance(item, tuple):
                menu.add_command(label=item[0], command=item[1])
            else:
                menu.add_separator()
        return menu

    def about_version(self):
        """
        显示关于版本信息的弹出窗口。

        这个函数创建一个弹出窗口，显示软件版本、发布时间和版权信息。
        """
        now = datetime.datetime.now()
        text = f"软件版本: {self.version}\n运行时间: {now.strftime('%Y-%m-%d %H:%M:%S')}\n版权所有© 2015·2025 上海傲意信息科技有限公司"
        tkinter.messagebox.showinfo("版本信息", text)

    def show(self):
        """
        启动Tkinter主事件循环。

        这个函数启动Tkinter主窗口的事件循环，使界面能够响应用户操作。
        """
        self.root.mainloop()

    def on_close(self):
        """
        处理窗口关闭事件。

        如果有正在运行的线程，这个函数会等待线程结束，
        恢复标准输出，然后关闭主窗口。
        """
        if self.thread and self.thread.is_alive():
            # self.thread.join()
             self.stop_running_thread()
        self.text_test_result.config(state=tk.DISABLED)
        sys.stdout = sys.__stdout__
        self.root.destroy()
        
    def on_signal(self, signum, frame):
        if self.thread and self.thread.is_alive():
            self.stop_running_thread()
        self.text_test_result.config(state=tk.DISABLED)
        sys.stdout = sys.__stdout__
        self.root.destroy()
        
    def stop_running_thread(self):
        if self.thread:
            try:
                # 尝试获取线程的 ID
                thread_id = self.thread.ident
                # 使用 _thread 模块尝试强制中断线程
                import _thread
                _thread.interrupt_main()

                # 等待一段时间让线程退出
                for _ in range(10):
                    if not self.thread.is_alive():
                        break
                    time.sleep(0.1)

                if self.thread.is_alive():
                    raise RuntimeError(f"Thread with ID {thread_id} did not exit.")
            except KeyboardInterrupt:
                # 如果在主线程捕获到 KeyboardInterrupt，可以进行一些额外的清理操作
                logger.error("Main thread interrupted. Performing cleanup.")
                self.on_close()
        
    def on_checkbutton_click(self):
        """
        是否将所有端口选中
        """
        if self.select_all_ports_ckbutton.instate(['selected']):
            self.is_all_ports_selected = True
            logger.info(f'已勾选所有端口设备')
        else:
            self.is_all_ports_selected = False
            logger.info(f'已勾选单个端口设备')
            
    def getDevicePortNames(self):
        """获取端口信息
        Returns:
            返回端口信息列表 
        """
        portInfos = serial.tools.list_ports.comports()
        portNames = [portInfo.device for portInfo in portInfos if portInfo]
        if  portNames:
            # self.update_port_complete = True
            return self.checkPortDevices(portNames)
        else:
            self.update_port_complete = True
            return ['无可用端口']
        # return ['无可用端口'] if not portNames else self.checkPortDevices(portNames)
    
    def checkPortDevices(self,ports):
        portNames = []
        self.update_port_complete = False
        self.notify_ports.clear()
        for port in ports:
            try:
                client = ModbusSerialClient(port=port, framer=FramerType.RTU, baudrate=115200,timeout=0.1)
                status = client.connect()
                if status:
                     response = client.read_holding_registers(address=1001, count=1, slave=2)
                     if(not response.isError()):
                        portNames.append(port)
                        self.notify_ports.append(port)
            except Exception as e:
                logger.error(f"Error during setup: {e}\n")
            except ModbusIOException as e:
                logger.error(f"Error during setup: {e}\n")
            finally:
                client.close()
        self.update_port_complete = True
        return ['无可用端口'] if not portNames else portNames

    def update_selected_option(self):
        self.current_time = time.time()
        if (self.current_time - self.last_refresh_time >= 5) and not self.running and not self.updating_port_info:
            self.updating_port_info = True
            threading.Thread(target=self.update_port_info_in_thread).start()
            
    def update_port_info_in_thread(self):
        try:
            # 显示刷新状态
            self.refresh_status_label.config(text='正在获取端口信息，请稍等...')
            # 在更新完成后检查是否隐藏标签
            self.check_and_hide_refresh_status()
            self.port_names = self.getDevicePortNames()
            self.combobox_ports['values'] = self.port_names
            self.combobox_ports.set(self.port_names[0])
            self.selected_port = self.port_names[0]
            for port in self.port_names:
                version = self.get_software_version(port)
                self.port_versions[port] = version
            self.version_text.config(text=self.port_versions.get(self.selected_port))
            self.root.update()
            self.last_refresh_time = self.current_time
        except Exception as e:
            logger.info(f"更新过程中出现错误：{e}")
        finally:
            self.updating_port_info = False
            
            
    def check_and_hide_refresh_status(self):
        if self.update_port_complete and len(self.port_names)>0:
            if self.port_names and self.port_names [0] == '无可用端口':
                logger.info('检测端口完成，未检测到可用设备')
            else:
                logger.info(f'检测端口完成，共检测出 {len (self.port_names)} 个设备')
            self.refresh_status_label.config(text='')
            self.update_port_complete = False
        else:
            # logger.info(f'已检测到{len(self.notify_ports)}个端口')
            # 如果还在更新，延迟一段时间后再次检查
            self.root.after(1000, self.check_and_hide_refresh_status)

    def set_task_status_label(self, text, color):
        self.thread_status_label.config(text=text, foreground=color)
        self.root.update_idletasks()
        
    def update_status_on_completion(self, result):
        if result == "通过":
            self.set_task_status_label('任务状态: 已结束，测试结论：' + result, 'green')
        else:
            self.set_task_status_label('任务状态: 已结束，测试结论：' + result, 'red')

    def run_script_with_status_update(self, module):
        def run_script():
            try:
                selected_ports=[]
                if not self.is_all_ports_selected:
                    selected_ports.append(self.selected_port)
                    logger.info(f'开始执行的脚本为:{self.script_name}，执行设备为{selected_ports}，老化时长为{self.selected_aging_duration}小时\n')
                    overall_result, result = module.main(ports=selected_ports, max_cycle_num=self.selected_aging_duration)
                else:
                    selected_ports = self.port_names
                    logger.info(f'开始执行的脚本为:{self.script_name}，执行设备为{selected_ports}，老化时长为{self.selected_aging_duration}小时\n')
                    overall_result, result = module.main(ports=selected_ports, max_cycle_num=self.selected_aging_duration)
                logger.info(f'本次测试结论为：{result} \n详细测试数据为：\n')
                self.print_overall_result(overall_result)
                if self.running:
                    self.running = False
                    self.root.after(0, lambda r=result: self.update_status_on_completion(r))
            except Exception as e:
                logger.error(f'Error in script execution: {e}')
            # finally:
            #     # self.stdout_redirector = None
            #     sys.stdout = sys.__stdout__

        #异步更新界面
        thread = threading.Thread(target=run_script)
        thread.daemon = True# 主界面退出，子任务也能退出
        thread.start()
        
    def print_overall_result(self,overall_result):
        port_data_dict = {}

        # 整理数据
        for item in overall_result:
            if item['port'] not in port_data_dict:
                port_data_dict[item['port']] = []
            for gesture in item['gestures']:
                port_data_dict[item['port']].append((gesture['timestamp'],gesture['content'], gesture['result']))

        # 打印数据
        for port, data_list in port_data_dict.items():
            logger.info(f"Port: {port}")
            for timestamp, content, result in data_list:
                logger.info(f" timestamp:{timestamp} content: {content}, Result: {result}")

    def load_scripts(self):
        if self.port_names[0]=='无可用端口':
            logger.error('无可用端口')
            return
        
        if self.script_name is not None:
            if not self.running:
                result = tk.messagebox.askquestion('确认', '测试即将开始，请耐心等待。是否继续执行？')
                if result == 'yes':
                    # 继续执行的代码
                    sys.path.append(os.getcwd())
                    try:
                        # 尝试导入脚本模块
                        module = importlib.import_module(self.script_name.rsplit('.', 1)[0])
                    except ImportError as e:
                        tk.messagebox.showerror('错误', f"导入模块失败：{self.script_name}，错误信息：{e}")
                        return
                    self.text_test_result.delete(1.0, tk.END)
                    # 避免界面卡顿
                    self.running = True
                    self.set_task_status_label('任务状态: 运行中', 'blue')
                    self.thread = threading.Thread(target=self.run_script_with_status_update, args=(module,))
                    self.thread.start()
                else:
                    # 用户选择了“否”，不执行
                    return
            else:
                tk.messagebox.showinfo('提示', '有任务在运行...不要重复加载任务')
        else:
            tk.messagebox.showinfo('提示', '请先加载脚本')

    def load_scripts_from_menu(self):
        # 弹出文件选择对话框，让用户选择要执行的脚本
        file_path = filedialog.askopenfilename(initialdir='scripts', title='选择要执行的脚本',
                                                filetypes=(('Python files', '*.py'),))
        if file_path:
            #使用with语句打开脚本文件，确保在读取完成后自动关闭文件,释放资源
            with open(file_path, 'r') as f: 
                self.script_name = os.path.splitext(os.path.basename(file_path))[0]
                logger.info(f'加载脚本{self.script_name}，请点击开始测试按钮，执行脚本\n')

    def save_record(self):
        """
        保存测试记录的函数。

        这个函数的目的是将测试结果保存到一个文本文件中。如果当前没有指定脚本名称，
        则使用默认的脚本名称"default_script"。否则，使用当前的脚本名称加上时间戳来命名文件，
        然后将测试结果写入到该文件中。

        无输入参数。

        无返回值，但会创建一个文本文件并写入测试结果内容。
        """
        content = self.text_test_result.get('1.0', tk.END)
        if not self.script_name:
            script_name = "default_script"
        else:
            script_name = self.script_name
            timestamp = time.strftime("%Y%m%d%H%M%S")
            file_name = f"{script_name}_test_result_{timestamp}.txt"
            current_dir = os.getcwd()
            file_path = os.path.join(current_dir, file_name)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            tk.messagebox.showinfo('保存成功', f'文件已保存为：{file_path}')

    def get_software_version(self,port):
        """
        获取软件版本号的函数。

        函数尝试从指定端口的Modbus设备中读取固件版本信息。如果端口为'无可用端口'，则直接返回默认的版本号'无法获取版本号'。
        它创建一个ModbusSerialClient实例，连接到指定端口的设备，然后尝试读取特定寄存器（ROH_FW_VERSION）中的版本信息。
        如果读取成功且无错误，将调用`getVersion`函数处理读取到的响应并获取格式化后的版本号。

        输入：
            无（通过`self`获取相关的端口等信息）。

        返回值：
            一个字符串，表示软件版本号。如果获取失败则返回'无法获取版本号'。
        """
        sw_version = '无法获取版本号'
        ROH_FW_VERSION = 1001  # 固件版本寄存器地址
        # ROH_FW_REVISION = 1002
        NODE_ID = 2
        
        if port == '无可用端口':
           return sw_version
        try:
            client = ModbusSerialClient(port=port, framer=FramerType.RTU, baudrate=115200,timeout=0.1)
            client.connect()
            logging.info("Successfully connected to Modbus device.")
            response = client.read_holding_registers(ROH_FW_VERSION, 2, NODE_ID)
            if not response.isError() and port!= '无可用端口':
                sw_version = self.extract_version(response)
        except Exception as e:
            logger.error(f"Error during setup: {e}\n")
        except ModbusIOException as e:
            logger.error(f"Error during setup: {e}\n")
        finally:
            client.close()

        return sw_version

    def refresh_software_version(self,port):
        """
        刷新软件版本号。
        """
        self.device_version = self.get_software_version(port)
        self.version_text.config(text=self.device_version)

    def extract_version(self, response):
        """
        从给定的响应中提取版本号并转换为特定格式。

        参数：
        response：包含从寄存器读取的值的对象。

        返回：
        以“V主版本号.次版本号.补丁版本号”格式的字符串版本号
        """
        if hasattr(response, 'registers'):
            if len(response.registers) > 0:
                value1 = response.registers[0]
                value2 = response.registers[1]
                major_version = (value1 >> 8) & 0xFF
                minor_version = value1 & 0xFF
                patch_version = value2 & 0xFF
                return f"V{major_version}.{minor_version}.{patch_version}"
        else:
            return "无法获取版本号"

def main():
    client = TestClient()
    client.show()

if __name__ == "__main__":
    main()
