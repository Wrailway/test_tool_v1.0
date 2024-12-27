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

class GestureStressTest:
    def __init__(self):
        self.node_id = 2
        self.port = 'COM4'
        self.FRAMER_TYPE = FramerType.RTU
        self.client = None
        self.BAUDRATE = 115200
        self.FINGER_POS_TARGET_MAX_LOSS = 32
        self.ROH_FINGER_POS_TARGET0 = 1135
        self.MAX_CYCLE_NUM = 1# 测试循环的最大次数，初始为1
        # 定义28个手势动作，每个动作分两步完成
        self.initial_gesture = [0, 0, 0, 0, 0, 0]
        self.fist_gesture = [[0, 62258, 62258, 62258, 62258, 0], [36044, 62258, 62258, 62258, 62258, 0]]
        self.mouse_gesture = [[32768, 0, 0, 0, 45875, 0], [32768, 7864, 0, 7864, 45875, 0]]
        self.key_gesture = [[0, 36044, 62258, 62258, 62258, 0], [42598, 36044, 62258, 62258, 62258, 0]]
        self.point_gesture = [[0, 0, 62258, 62258, 62258, 0], [52428, 0, 62258, 62258, 62258, 0]]
        self.column_gesture = [[52428, 0, 64880, 64880, 64880, 0], [52428, 36044, 64880, 64880, 64880, 0]]
        self.palm_gesture = [[26214, 16384, 16384, 16384, 19661, 0], [26214, 16384, 16384, 16384, 16384, 0]]
        self.salute_gesture = [[29491, 0, 0, 0, 0, 0], [29491, 0, 0, 0, 0, 0]]
        self.chopstick_gesture = [[16384, 19661, 62258, 62258, 62258, 0], [16384, 45875, 62258, 62258, 62258, 0]]
        self.power_gesture = [[0, 62258, 62258, 62258, 62258, 62258], [49151, 62258, 62258, 62258, 62258, 62258]]
        self.grasp_gesture = [[27525, 29491, 32768, 27525, 24903, 62258], [27525, 29491, 32768, 27525, 24903, 62258]]
        self.lift_gesture = [[0, 22937, 22937, 22937, 22937, 62258], [39321, 62258, 62258, 62258, 62258, 62258]]
        self.plate_gesture = [[0, 9830, 11141, 9830, 11141, 62258], [62258, 9830, 11141, 9830, 11141, 62258]]
        self.buckle_gesture = [[36044, 0, 55705, 55705, 55705, 0], [36044, 29491, 55705, 55705, 55705, 62258]]
        self.pinch_ic_gesture = [[29491, 0, 62258, 62258, 62258, 0], [29491, 32768, 62258, 62258, 62258, 62258]]
        self.pinch_io_gesture = [[29491, 0, 0, 0, 0, 62258], [29491, 32768, 0, 0, 0, 62258]]
        self.pinch_tc_gesture = [[0, 29491, 62258, 62258, 62258, 62258], [32768, 29491, 62258, 62258, 62258, 62258]]
        self.pinch_to_gesture = [[0, 29491, 0, 0, 0, 62258], [32768, 29491, 0, 0, 0, 62258]]
        self.pinch_itc_gesture = [[0, 0, 62258, 62258, 62258, 0], [29491, 29491, 62258, 62258, 62258, 62258]]
        self.tripod_ic_gesture = [[30801, 0, 0, 62258, 62258, 62258], [30801, 30146, 32768, 62258, 62258, 62258]]
        self.tripod_io_gesture = [[30801, 0, 0, 0, 0, 62258], [30801, 30146, 32768, 0, 0, 62258]]
        self.tripod_tc_gesture = [[0, 30146, 32768, 62258, 62258, 62258], [30801, 30146, 32768, 62258, 62258, 62258]]
        self.tripod_to_gesture = [[0, 30146, 32768, 0, 0, 62258], [30801, 30146, 32768, 0, 0, 62258]]
        self.tripod_itc_gesture = [[0, 0, 0, 62258, 62258, 62258], [30801, 30146, 32768, 62258, 62258, 62258]]
        self.gun_gesture = [[0, 0, 62258, 62258, 62258, 0], [0, 0, 62258, 62258, 62258, 0]]
        self.love_gesture = [[0, 0, 0, 62258, 62258, 0], [0, 0, 0, 62258, 62258, 0]]
        self.swear_gesture = [[0, 62258, 0, 0, 62258, 0], [0, 62258, 0, 0, 62258, 0]]
        self.victory_gesture = [[62258, 0, 0, 62258, 62258, 0], [62258, 0, 0, 62258, 62258, 0]]
        self.six_gesture = [[0, 62258, 62258, 62258, 0, 0], [0, 62258, 62258, 62258, 0, 0]]

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
            'mouse': self.mouse_gesture,
            'key': self.key_gesture,
            'point': self.point_gesture,
            'column': self.column_gesture,
            'palm': self.palm_gesture,
            'salute': self.salute_gesture,
            'chopstick': self.chopstick_gesture,
            'power': self.power_gesture,
            'grasp': self.grasp_gesture,
            'lift': self.lift_gesture,
            'plate': self.plate_gesture,
            'buckle': self.buckle_gesture,
            'pinch_ic': self.pinch_ic_gesture,
            'pinch_io': self.pinch_io_gesture,
            'pinch_tc': self.pinch_tc_gesture,
            'pinch_to': self.pinch_to_gesture,
            'pinch_itc': self.pinch_itc_gesture,
            'tripod_ic': self.tripod_ic_gesture,
            'tripod_io': self.tripod_io_gesture,
            'tripod_tc': self.tripod_tc_gesture,
            'tripod_to': self.tripod_to_gesture,
            'tripod_itc': self.tripod_itc_gesture,
            'gun': self.gun_gesture,
            'love': self.love_gesture,
            'swear': self.swear_gesture,
            'victory': self.victory_gesture,
            'six': self.six_gesture
        }
        return gesture_dict
    
    def get_initial_gesture(self):
        return self.initial_gesture
    
    def get_op_address(self):
        return self.ROH_FINGER_POS_TARGET0
    
    def read_from_register(self, address, count):
        """
        从指定的寄存器地址读取数据。

        最多尝试读取max_retries次，如果读取成功则返回读取结果。如果遇到连接超时或读取超时等错误，
        会进行相应处理（如重新连接或增加重试次数），其他异常也会被记录。

        :param address: 要读取的寄存器地址。
        :param count: 要读取的寄存器数量。
        :return: 如果成功读取则返回pymodbus的read_holding_registers响应对象，否则返回None。
        """
        max_retries = 3
        retry_count = 0
        response = None
        while retry_count < max_retries:
            try:
                response = self.client.read_holding_registers(address=address, count=count, slave=self.node_id)
                time.sleep(0.2)
                if not response.isError():
                    break
                else:
                    error_type = self.get_exception(response)
                    if "connection timeout" in error_type.lower():
                        self.client.connect()
                    elif "read timeout" in error_type.lower():
                        retry_count += 1
                        time.sleep(0.5)
                    else:
                        logger.error(f'[port = {self.port}]读寄存器失败: {error_type}\n')
            except ModbusIOException as e:
                logger.error(f'[port = {self.port}]Modbus输入输出异常: {e}')
                if "connection error" in str(e).lower():
                    self.client.connect()
            except AssertionError as e:
                logger.error(f'[port = {self.port}]断言错误: {e}')
            except Exception as e:
                logger.error(f'[port = {self.port}]其他异常: {e}')
        return response

    def write_to_regesister(self, address, value):
        """
        向指定的寄存器地址写入数据。

        最多尝试写入max_retries次，根据写入结果和可能出现的错误（如连接超时、写入超时等）进行相应处理，
        并返回写入是否成功的布尔值。

        :param address: 要写入的寄存器地址。
        :param value: 要写入的值。
        :return: 如果写入成功则返回True，否则返回False。
        """
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            try:
                response = self.client.write_registers(address, value, self.node_id)
                time.sleep(2)
                if not response.isError():
                    return True
                else:
                    error_type = self.get_exception(response)
                    if "connection timeout" in error_type.lower():
                        self.client.connect()
                    elif "write timeout" in error_type.lower():
                        retry_count += 1
                    else:
                        logger.error(f'[port = {self.port}]写寄存器失败: {error_type}\n')
                        return False
            except ModbusIOException as e:
                logger.error(f'[port = {self.port}]Modbus输入输出异常: {e}')
                if "connection error" in str(e).lower():
                    self.client.connect()
                else:
                    return False
            except AssertionError as e:
                logger.error(f'[port = {self.port}]断言错误: {e}')
                return False
            except Exception as e:
                logger.error(f'[port = {self.port}]其他异常: {e}')
                return False
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
        return self.write_to_regesister(address=self.ROH_FINGER_POS_TARGET0, value=gesture)

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
                    is_broken = True
        return is_broken
    
def check_ports(ports_list):
    valid_ports = []
    status = True
    if ports_list is not None:
        for port in ports_list:
            if isinstance(port, str) and port.startswith('COM'):
                valid_ports.append(port)
            else:
                status = False
    else:
        status = False
    return status, valid_ports

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
    
    status, valid_ports = check_ports(ports)
    if not (status and len(valid_ports)>=1):
        logger.error('测试结束，无可用端口')
        result = '不通过'
        return overall_result,result
    
    start_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f'---------------------------------------------开始老化测试<开始时间：{start_time}>----------------------------------------------\n')
    logger.info('测试目的：循环做抓握手势，进行压测')
    logger.info('标准：各个手头无异常，手指不脱线\n')
    try:
        start_time1 = time.time()
        end_time1 = start_time1 + max_cycle_num * 3600
        # end_time1 = start_time1 + 60
        i = 0
        while time.time() < end_time1:
            logger.info(f"##########################第 {i + 1} 轮测试开始######################\n")
            result = '通过'
            with concurrent.futures.ThreadPoolExecutor() as executor:
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
    gestureStressTest = GestureStressTest()
    gestureStressTest.set_port(port)
    if not connected_status:
        gestureStressTest.connect_device()
        connected_status = True
    port_result = {
        "port": port,
        "gestures": []
    }

    try:
        for key, gesture in gestureStressTest.gestures.items():
                logger.info(f"[port = {port}]执行    ---->  {key}\n")
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # 先恢复默认手势
                if gestureStressTest.do_gesture(key=key, gesture=gestureStressTest.get_initial_gesture()) and not gestureStressTest.judge_if_hand_broken(address=gestureStressTest.get_op_address(), gesture=gestureStressTest.get_initial_gesture()):
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

                # 做新的手势
                for step in gesture:
                    if gestureStressTest.do_gesture(key=key, gesture=step) and not gestureStressTest.judge_if_hand_broken(address=gestureStressTest.get_op_address(), gesture=step):
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

    gestureStressTest.disConnect_device()
    return port_result, connected_status


if __name__ == "__main__":
    ports = ['COM4']
    max_cycle_num = 1
    main(ports, max_cycle_num)