import datetime
import logging
import sys
import time
import concurrent.futures
from pymodbus.exceptions import ConnectionException, ModbusIOException
from pymodbus import FramerType
from pymodbus.client import ModbusSerialClient

# 设置日志级别为INFO，获取日志记录器实例
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(stream_handler)

fail_port_list = set()
class AgingTest:
    def __init__(self):
        self.node_id = 2
        self.port = 'COM4'
        self.FRAMER_TYPE = FramerType.RTU
        self.client = None
        self.BAUDRATE = 115200
        self.FINGER_POS_TARGET_MAX_LOSS = 32
        self.ROH_FINGER_POS_TARGET0 = 1135
        self.ROH_FINGER_CURRENT_LIMIT0 = 1095
        self.MAX_CYCLE_NUM = 1# 测试循环的最大次数，初始为1
        # 定义28个手势动作，每个动作分两步完成
        self.initial_gesture = [0, 0, 0, 0, 0, 728]
        self.fist_gesture = [[0, 0, 0, 0, 0, 728], [0, 65535, 65535, 65535, 65535, 728]]
        self.second_gesture = [[0, 0, 0, 0, 0, 728], [65535, 0, 0, 0, 0, 728]]
        self.third_gesture = [[0, 0, 0, 0, 0, 728], [0, 0, 0, 0, 0, 65535]]
        self.aging_speed = 1# 动作间隔，最少0.4，否则手指会碰撞，值越小越快

        self.gestures = self.create_gesture_dict()
        
    def set_port(self,port):
        self.port = port
        
    def set_cycle_times(self,max_cycle_num):
        self.MAX_CYCLE_NUM = max_cycle_num
        
    def get_cycle_times(self):
        return self.MAX_CYCLE_NUM
    
    def create_gesture_dict(self):
        gesture_dict = {
            'fist': self.fist_gesture,
            'second': self.second_gesture,
            'third': self.third_gesture
        }
        return gesture_dict
    
    def get_initial_gesture(self):
        return self.initial_gesture
    
    def get_op_address(self):
        return self.ROH_FINGER_POS_TARGET0
    
    def read_from_register(self, address, count):
        """
        从指定的寄存器地址读取数据。
        :param address: 要读取的寄存器地址。
        :param count: 要读取的寄存器数量。
        :return: 如果成功读取则返回pymodbus的read_holding_registers响应对象，否则返回None。
        """
        try:
            response = self.client.read_holding_registers(address=address, count=count, slave=self.node_id)
            if response.isError():
                logger.error(f'[port = {self.port}]读寄存器失败\n')
                fail_port_list.update([self.port])
        except Exception as e:
            logger.error(f'[port = {self.port}]异常: {e}')
        return response
        
    def write_to_regesister(self, address, value):
        """
        向指定的寄存器地址写入数据。
        :param address: 要写入的寄存器地址。
        :param value: 要写入的值。
        :return: 如果写入成功则返回True，否则返回False。
        """
        try:
            response = self.client.write_registers(address, value, self.node_id)
            if not response.isError():
                    return True
            else:
                logger.error(f'[port = {self.port}]写寄存器失败\n')
                fail_port_list.update([self.port])
                return False
        except Exception as e:
                logger.error(f'[port = {self.port}]异常: {e}')
                return False 
        
        
    def connect_device(self):
        """
        连接到Modbus设备。

        创建ModbusSerialClient实例并尝试连接到指定端口的设备，根据连接结果记录日志并返回连接是否成功的布尔值。

        :return: 一个布尔值，表示是否成功连接到设备。
        """
        connect_status = False
        try:
            self.client = ModbusSerialClient(port=self.port, framer=self.FRAMER_TYPE, baudrate=self.BAUDRATE)
            connect_status = self.client.connect()
            logger.info(f"[port = {self.port}]Successfully connected to Modbus device.")
        except ConnectionException as e:
            logger.error(f"[port = {self.port}]Error during setup: {e}")
        except Exception as e:
            logger.error(f"[port = {self.port}]Error during setup: {e}")
        return connect_status

    def disConnect_device(self):
        """
        断开与Modbus设备的连接。

        如果存在client实例则关闭连接并将client设置为None，同时记录日志，如果出现异常也会记录。
        """
        if self.client:
            try:
                self.client.close()
                self.client = None
                logger.info(f"[port = {self.port}]Connection to Modbus device closed.")
            except Exception as e:
                logger.error(f"[port = {self.port}]Error during teardown: {e}")

    def do_gesture(self,key,gesture):
        """
        执行特定的手势动作。

        实际是向特定寄存器（ROH_FINGER_POS_TARGET0）写入手势数据。

        :param gesture: 要执行的手势数据。
        :return: 调用write_to_regesister方法的结果，即写入是否成功的布尔值。
        """
        # print(f"[port = {self.port}]执行    ---->  {key}")
        time.sleep(self.aging_speed)
        return self.write_to_regesister(address=self.ROH_FINGER_POS_TARGET0, value=gesture)
    
    def set_max_current(self):
        value = [200,200,200,200,200,200]
        return self.write_to_regesister(address=self.ROH_FINGER_CURRENT_LIMIT0,value=value)

    def judge_if_hand_broken(self, address, gesture):
        """
        判断设备是否损坏。

        通过读取指定地址的寄存器数据，并与给定的手势数据对比，如果有任何一个寄存器值与手势值的差值超过FINGER_POS_TARGET_MAX_LOSS则认为设备损坏。

        :param address: 要读取数据的寄存器地址。
        :param gesture: 用于对比的手势数据。
        :return: 一个布尔值，表示设备是否损坏。
        """
        is_broken = False
        response = self.read_from_register(address=address, count=6)
        if response is not None and not response.isError():
            for i in range(len(response.registers)):
                if abs(response.registers[i] - gesture[i]) > self.FINGER_POS_TARGET_MAX_LOSS:
                    print(f'{response.registers[i] } ----{gesture[i]}')
                    is_broken = True
        return is_broken
    
def check_port(valid_port: set = {}, total_port: list = {}):
    """
    从total_port列表中去除valid_port集合中的元素，并同步去除对应的node_ids列表中的元素，
    基于total_port中的端口和node_ids中的元素按位置一一对应关系。

    参数:
    valid_port (set): 要去除的端口集合，默认为空集合。
    total_port (list): 总的端口列表，默认为空列表。

    返回:
    list: 去除指定端口后的端口列表。
    """
    # 检查参数类型是否符合要求
    if not isinstance(valid_port, set):
        raise TypeError("valid_port参数应该是set类型")
    if not isinstance(total_port, list):
        raise TypeError("total_port参数应该是list类型")

    # 使用列表推导式从total_port中筛选出不在valid_port中的元素，同时记录符合条件的索引位置
    valid_indices = [index for index, port in enumerate(total_port) if port not in valid_port]
    # 使用筛选出的有效索引位置，从total_port列表中构建新的端口列表
    result_ports = [total_port[i] for i in valid_indices]
    return result_ports

def main(ports=None, max_cycle_num=1):
    """
    测试的主函数。

    创建 GestureStressTest 类的实例，设置端口号并连接设备，然后进行多次（最多 MAX_CYCLE_NUM 次）测试循环，
    在每次循环中获取电机电流并检查电流是否正常，根据结果设置 result 变量，最后断开设备连接并返回测试结果。

    :param port: 可选参数，默认为 COM4，要连接的设备端口号。
    :return: 一个字符串，表示测试结果（"通过"或其他未在代码中明确设置的结果）。
    """
    final_result = '通过'
    overall_result = []
    connected_status = False
    
    start_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f'---------------------------------------------开始老化测试<开始时间：{start_time}>----------------------------------------------\n')
    logger.info('测试目的：循环做抓握手势，进行压测')
    logger.info('标准：各个手头无异常，手指不脱线\n')
    try:
        start_time = time.time()
        end_time = start_time + max_cycle_num * 3600
        # end_time = start_time + 60
        i = 0
        while time.time() < end_time:
            logger.info(f"##########################第 {i + 1} 轮测试开始######################\n")
            ports = check_port(valid_port=fail_port_list,total_port=ports)
            if len(ports)==0:
                logger.info('无可测试设备')
                break
            result = '通过'
            with concurrent.futures.ThreadPoolExecutor(max_workers=64) as executor:
                futures = [executor.submit(run_tests_for_port, port, connected_status) for port in ports]
                for future in concurrent.futures.as_completed(futures):
                    port_result, _ = future.result()
                    overall_result.append(port_result)
                    for gesture_result in port_result["gestures"]:
                        if gesture_result["result"]!= "通过":
                            result = '不通过'
                            final_result = '不通过'
                            break
            logger.info(f"#################第 {i + 1} 轮测试结束，测试结果：{result}#############\n")
            i += 1

    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        pass
    end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f'---------------------------------------------老化测试结束<结束时间：{end_time}>----------------------------------------------\n')
    # print(f'最终测试结果：{overall_result}')
    # print_overall_result(overall_result)
    return overall_result, final_result

def print_overall_result(overall_result):
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


def run_tests_for_port(port, connected_status):
    aging_test = AgingTest()
    aging_test.set_port(port)
    if not connected_status:
        aging_test.connect_device()
        connected_status = True
    port_result = {
        "port": port,
        "gestures": []
    }

    try:
        if aging_test.set_max_current():# 设置最大的电量限制为200ma
            for key, gesture in aging_test.gestures.items():
                    logger.info(f"[port = {port}]执行    ---->  {key}\n")
                    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
                    # 做新的手势
                    for step in gesture:
                        if aging_test.do_gesture(key=key, gesture=step) and not aging_test.judge_if_hand_broken(address=aging_test.get_op_address(), gesture=step):
                            gesture_result = {
                                "timestamp":timestamp,
                                "content": key,
                                "result": "通过"
                            }
                        else:
                            gesture_result = {
                                "timestamp":timestamp,
                                "content": key,
                                "result": "不通过"
                            }
                            # 先恢复默认手势
                    if aging_test.do_gesture(key=key, gesture=aging_test.get_initial_gesture()) and not aging_test.judge_if_hand_broken(address=aging_test.get_op_address(), gesture=aging_test.get_initial_gesture()):
                        gesture_result = {
                            "timestamp":timestamp,
                            "content": key,
                            "result": "通过"
                        }
                    else:
                        gesture_result = {
                            "timestamp":timestamp,
                            "content": key,
                            "result": "不通过"
                        }

                    port_result["gestures"].append(gesture_result)
                    # logger.info(f'[port = {port}]测试结果 {gesture_result["result"]}')
        else:
            gesture_result = {
                            "timestamp":timestamp,
                            "content": key,
                            "result": "不通过"
                        }

            port_result["gestures"].append(gesture_result)
           
    except Exception as e:
            logger.error(f"操作手势过程中发生错误：{e}\n")
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            gesture_result = {
                "timestamp":timestamp,
                "content": f'操作手势过程中发生错误：{e}',
                "result": "不通过"
            }
            port_result["gestures"].append(gesture_result)
            # logger.info(f'[port = {port}]测试结果 {gesture_result["result"]}')

    aging_test.disConnect_device()
    return port_result, connected_status


if __name__ == "__main__":
    ports = ['COM4']
    max_cycle_num = 1
    main(ports, max_cycle_num)