import datetime
import logging
import concurrent.futures
import sys
import time
from pymodbus import FramerType
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ConnectionException, ModbusIOException

# 设置日志级别为INFO，获取日志记录器实例
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(stream_handler)


class AgingTest:
    
    # ROH 灵巧手错误代码
    EC01_ILLEGAL_FUNCTION = 0X1  # 无效的功能码
    EC02_ILLEGAL_DATA_ADDRESS = 0X2  # 无效的数据地址
    EC03_ILLEGAL_DATA_VALUE = 0X3  # 无效的数据（协议层，非应用层）
    EC04_SERVER_DEVICE_FAILURE = 0X4  # 设备故障
    UNKNOWN_FAILURE = 0X5  # 未知错误

    roh_exception_list = {
        EC01_ILLEGAL_FUNCTION: '无效的功能码',
        EC02_ILLEGAL_DATA_ADDRESS: '无效的数据地址',
        EC03_ILLEGAL_DATA_VALUE: '无效的数据（协议层，非应用层）',
        EC04_SERVER_DEVICE_FAILURE: '设备故障',
        UNKNOWN_FAILURE: '未知错误'
    }
    # 寄存器 ROH_SUB_EXCEPTION 保存了具体的错误代码
    ERR_STATUS_INIT = 0X1  # 等待初始化或者正在初始化，不接受此读写操作
    ERR_STATUS_CALI = 0X2  # 等待校正，不接受此读写操作
    ERR_INVALID_DATA = 0X3  # 无效的寄存器值
    ERR_STATUS_STUCK = 0X4  # 电机堵转
    ERR_OP_FAILED = 0X5  # 操作失败
    ERR_SAVE_FAILED = 0X6  # 保存失败
    ROH_SUB_EXCEPTION         = (1006) # R

    roh_sub_exception_list = {
        ERR_STATUS_INIT: '等待初始化或者正在初始化，不接受此读写操作',
        ERR_STATUS_CALI: '等待校正，不接受此读写操作',
        ERR_INVALID_DATA: '无效的寄存器值',
        ERR_STATUS_STUCK: '电机堵转',
        ERR_OP_FAILED: '操作失败',
        ERR_SAVE_FAILED: '保存失败'
    }
    

    def get_exception(self, response):
        """
        根据传入的响应确定错误类型。

        参数：
        response：包含错误信息的响应对象。

        返回：
        错误类型的描述字符串。
        """
        strException = ''
        if response.exception_code > self.EC04_SERVER_DEVICE_FAILURE:
            strException = self.roh_exception_list.get(self.UNKNOWN_FAILURE)
        elif response.exception_code == self.EC04_SERVER_DEVICE_FAILURE:
            response2 = self.client.read_holding_registers(address=self.ROH_SUB_EXCEPTION,slave=2)
            strException = '设备故障，具体原因为'+self.roh_sub_exception_list.get(response2.registers[0])
        else:
            strException = self.roh_exception_list.get(response.exception_code)
        return strException
    
    def __init__(self):
        """
        初始化AgeTest类的实例。

        在这里设置与Modbus设备通信相关的参数，包括端口号、节点ID、帧类型、波特率等，
        同时定义了与手指位置和电机电流相关的寄存器地址、初始手势、握手势、最大循环次数等属性。
        """
        self.node_id = 2
        self.port = 'COM4'
        self.FRAMER_TYPE = FramerType.RTU
        self.BAUDRATE = 115200
        self.client = None
        self.ROH_FINGER_POS_TARGET0 = 1135
        self.ROH_FINGER_POS_TARGET1 = 1136
        self.ROH_FINGER_POS_TARGET2 = 1137
        self.ROH_FINGER_POS_TARGET3 = 1138
        self.ROH_FINGER_POS_TARGET4 = 1139
        self.ROH_FINGER_POS_TARGET5 = 1140
        self.ROH_FINGER_CURRENT0 = 1105
        self.ROH_FINGER_CURRENT1 = 1106
        self.ROH_FINGER_CURRENT2 = 1107
        self.ROH_FINGER_CURRENT3 = 1108
        self.ROH_FINGER_CURRENT4 = 1109
        self.ROH_FINGER_CURRENT5 = 1110
        self.ROH_BEEP_PERIOD  = 1010
        self.motor_currents = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.initial_gesture = [0, 0, 0, 0, 0, 65535]  # 自然展开手势
        # self.grasp_gesture = [16294, 28966, 33673, 29328, 23897, 65535]  # 握手势
        self.grasp_gesture = [16294, 65535, 65535, 65535, 65535, 65535]  # 握手势
        self.MAX_CYCLE_NUM = 1
        self.FINGER_POS_TARGET_MAX_LOSS = 32
        self.max_average_times = 3
        self.current_standard = 100
        
    def set_port(self,port):
        self.port = port
        
    def set_cycle_times(self,max_cycle_num):
        self.MAX_CYCLE_NUM = max_cycle_num
        
    def get_cycle_times(self):
        return self.MAX_CYCLE_NUM

    def read_from_register(self, address, count):
        """
        从指定的寄存器地址读取数据。

        最多尝试读取max_retries次，如果读取成功则返回读取结果。如果遇到连接超时或读取超时等错误，
        会进行相应处理（如重新连接或增加重试次数），其他异常也会被记录。

        :param address: 要读取的寄存器地址。
        :param count: 要读取的寄存器数量。
        :return: 如果成功读取则返回pymodbus的read_holding_registers响应对象，否则返回None。
        """
        max_retries = 2
        retry_count = 0
        response = None
        while retry_count < max_retries:
            try:
                response = self.client.read_holding_registers(address=address, count=count, slave=self.node_id)
                time.sleep(0.1)
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
                time.sleep(1.5)
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
    
    # def do_alarm(self):
    #     """
    #     蜂鸣器报警，当设备异常时，每隔3s报警一次
    #     """
    #     while True:
    #         self.write_to_regesister(address=self.ROH_BEEP_PERIOD ,value=1000)
    #         time.sleep(3)

    def do_gesture(self, gesture):
        """
        执行特定的手势动作。

        实际是向特定寄存器（ROH_FINGER_POS_TARGET0）写入手势数据。

        :param gesture: 要执行的手势数据。
        :return: 调用write_to_regesister方法的结果，即写入是否成功的布尔值。
        """
        return self.write_to_regesister(address=self.ROH_FINGER_POS_TARGET0, value=gesture)

    def count_motor_curtent(self, address):
        """
        计算电机电流的平均值。

        多次（最多MAX_NUM次）读取指定地址（ROH_FINGER_CURRENT0）的电流数据，然后计算这些数据的平均值并返回。

        :param address: 要读取电流数据的寄存器地址。
        :return: 一个包含6个电机电流平均值的列表。
        """
        sum_currents = [0] * 6
        ave_currents = [0] * 6
        for i in range(self.max_average_times):
            currents = self.read_from_register(address=address, count=6)
            if currents is None or currents.isError():
                logger.error(f"[port = {self.port}]currents: read_holding_registers has an error\n")
            else:
                time.sleep(0.1)
            currents_list = currents.registers if currents else []
            sum_currents = [sum_currents[j] + currents_list[j] for j in range(len(currents_list))]
        currents = [sum_currents[k] / self.max_average_times for k in range(len(currents_list))]
        ave_currents = [round(num, 1) for num in currents]
        return ave_currents

    def checkCurrent(self, curs):
        """
        检查电机电流是否超过100mA。

        遍历输入的电流列表，如果有任何一个电流值大于100则返回False，否则返回True。

        :param curs: 一个包含电机电流值的列表。
        :return: 一个布尔值，表示电流是否都在正常范围内。
        """
        return all(c <= self.current_standard for c in curs)

    def get_motor_currents(self):
        """
        获取电机电流。

        首先执行初始手势和握手势动作（如果成功且设备未损坏），然后分别读取对应的电机电流并更新self.motor_currents属性，
        最后返回操作是否成功的状态。

        :return: 一个布尔值，表示获取电机电流的操作是否成功。
        """
        status = False
        if self.do_gesture(self.initial_gesture) and not self.judge_if_hand_broken(address=self.ROH_FINGER_POS_TARGET0,
                                                                                   gesture=self.initial_gesture):
            # self.motor_currents = self.count_motor_curtent(address=self.ROH_FINGER_CURRENT0)
            status = True
            # logger.info(f'[port = {self.port}]执行自然展开手势, 电机电流为 -->{self.motor_currents}\n')
        if self.do_gesture(self.grasp_gesture) and not self.judge_if_hand_broken(address=self.ROH_FINGER_POS_TARGET0,
                                                                                gesture=self.grasp_gesture):
            self.motor_currents = self.count_motor_curtent(address=self.ROH_FINGER_CURRENT0)
            status = True
            logger.info(f'[port = {self.port}]执行抓握手势，电机电流为 -->{self.motor_currents}\n')
        return status

    def get_current(self):
        """
        返回当前存储的电机电流值（self.motor_currents）。

        :return: 一个包含电机电流值的列表。
        """
        return self.motor_currents

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
            logger.info(f"[port = {self.port}]Successfully connected to Modbus device.\n")
        except ConnectionException as e:
            logger.error(f"Error during setup[port = {self.port}]: {e}\n")
        except Exception as e:
            logger.error(f"Error during setup[port = {self.port}]: {e}\n")
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
                logger.info(f"[port = {self.port}]Connection to Modbus device closed.\n")
            except Exception as e:
                logger.error(f"[port = {self.port}]Error during teardown: {e}\n")

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

    创建 AgeTest 类的实例，设置端口号并连接设备，然后进行多次（最多 MAX_CYCLE_NUM 次）测试循环，
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
    logger.info('标准：各个手头无异常，手指不脱线，并记录各个电机的电流值 < 单位 mA >\n')
    try:
        start_time1 = time.time()
        end_time1 = start_time1 + max_cycle_num * 3600
        # end_time1 = start_time1 + 15
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
    # print(f'最终测试结果：{result}')
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
    agingTest = AgingTest()
    agingTest.set_port(port)
    if not connected_status:
        connected_status = agingTest.connect_device()
    port_result = {
        "port": port,
        "gestures": []
    }
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if connected_status:
        try:
            if agingTest.get_motor_currents():
                current = agingTest.get_current()
                gesture_result = {
                        "timestamp":timestamp,
                        "content": current,
                        "result": "通过"
                    }
                # if agingTest.checkCurrent(current):
                #     gesture_result = {
                #         "timestamp":timestamp,
                #         "content": current,
                #         "result": "通过"
                #     }
                # else:
                #     gesture_result = {
                #         "timestamp":timestamp,
                #         "content": current,
                #         "result": "不通过"
                #     }
                    # agingTest.do_alarm()
                port_result["gestures"].append(gesture_result)
            else:
                gesture_result = {
                    "timestamp":timestamp,
                    "content": '手指出现异常',
                    "result": "不通过"
                }
                port_result["gestures"].append(gesture_result)
        except Exception as current_error:
            logger.error(f"获取电机电流或检查电流时出现错误：{current_error}")
            gesture_result = {
                "timestamp":timestamp,
                "content": f'获取电机电流或检查电流时出现错误：{current_error}',
                "result": "不通过"
            }
            port_result["gestures"].append(gesture_result)
            
        finally:
            agingTest.disConnect_device()
    else:
        gesture_result = {
                "timestamp":timestamp,
                "content": '当前端口无法获取到设备或无法连接到设备',
                "result": "不通过"
            }
        port_result["gestures"].append(gesture_result)
        
    return port_result, connected_status

if __name__ == "__main__":
    port = ['COM6']
    main(ports = port,max_cycle_num=1)