import datetime
import logging
import concurrent.futures
import sys
import time
from typing import List, Tuple
from pymodbus import FramerType
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ConnectionException

# 设置日志级别为INFO，获取日志记录器实例
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(stream_handler)

fail_port_list = set()
class AgingTest:
    
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
        self.ROH_FINGER_CURRENT0 = 1105
        self.ROH_FINGER_CURRENT_LIMIT0 = 1095
        self.ROH_BEEP_PERIOD  = 1010
        self.motor_currents = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        # self.initial_gesture = [[0,65535, 65535, 65535, 65535, 62258],[0, 0, 0, 0, 0, 62258]]  # 自然展开手势
        # self.grasp_gesture = [[0, 65535, 65535, 65535, 65535, 62258], [62258, 65535, 65535, 65535, 65535, 62258]]
        self.initial_gesture = [[26069, 31499, 36569, 32949, 28966, 62258],[0, 0, 0, 0, 0, 62258]]  # 自然展开手势
        self.grasp_gesture = [[0,  31499, 36569, 32949, 28966, 62258], [26069, 31499, 36569, 32949, 28966, 62258]]
        # self.grasp_gesture = [16294, 28966, 33673, 29328, 23897, 65535]  # 握手势
        # self.grasp_gesture = [65535, 65535, 65535, 65535, 65535, 65535]  # 握手势16294
        
        self.FINGER_POS_TARGET_MAX_LOSS = 32
        self.max_average_times = 5
        self.current_standard = 100
        self.aging_speed = 1# 动作间隔，最少0.4，否则手指会碰撞，值越小越快
        
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
    
    def do_gesture(self, gesture):
        """
        执行特定的手势动作。
        :param gesture: 要执行的手势数据。
        :return: 调用write_to_regesister方法的结果，即写入是否成功的布尔值。
        """
        time.sleep(self.aging_speed) # 防止大拇指和食指打架，值需要大于0.4
        return self.write_to_regesister(address=self.ROH_FINGER_POS_TARGET0, value=gesture)
    
    def count_motor_curtent(self):
        """
        计算电机电流的平均值。

        多次（最多MAX_NUM次）读取指定地址（ROH_FINGER_CURRENT0）的电流数据，然后计算这些数据的平均值并返回。

        :param address: 要读取电流数据的寄存器地址。
        :return: 一个包含6个电机电流平均值的列表。
        """
        sum_currents = [0] * 6
        ave_currents = [0] * 6
        max_error_times = 3  # 设定最多允许出现错误的次数
        error_count = 0
        for i in range(self.max_average_times):
            currents = self.read_from_register(address=self.ROH_FINGER_CURRENT0, count=6)
            if currents is None or currents.isError():
                error_count += 1
                logger.error("currents: read_holding_registers has an error \n")
                if error_count >= max_error_times:
                    raise ValueError("多次读取电流数据出现错误，无法计算平均值")
            else:
                currents_list = currents.registers if currents else []
                sum_currents = [sum_currents[j] + currents_list[j] for j in range(len(sum_currents))]
                time.sleep(0.2)
        ave_currents = [sum_currents[k] / self.max_average_times for k in range(len(sum_currents))]
        self.motor_currents = ave_currents

    def check_current(self, curs):
        """
        检查电机电流是否超过标准<100mA>
        :param curs: 一个包含电机电流值的列表。
        :return: 一个布尔值，表示电流是否都在正常范围内。
        """
        return all(c <= self.current_standard for c in curs)
    
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
                logger.error(f"[port = {self.port}]Error during dis connect device: {e}\n")


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

def main(ports: list = [],  max_cycle_num: float = 1.5) -> Tuple[List,bool]:
    """
    测试的主函数。
    :param ports: 端口列表
    :param node_ids: 设备id列表,与端口号一一对应
    :return: 测试标题,测试结果数据,测试结论,是否需要显示电机电流(false)
    """
    overall_result = []
    final_result = '通过'
    start_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f'---------------------------------------------开始老化测试<开始时间：{start_time}>----------------------------------------------\n')
    logger.info('测试目的：循环做抓握手势，进行压测')
    logger.info('标准：各个手头无异常，手指不脱线，并记录各个电机的电流值 < 单位 mA >\n')
    try:
        end_time = time.time() + max_cycle_num * 3600
        round_num = 0
        while time.time() < end_time:
            ports = check_port(valid_port=fail_port_list,total_port=ports)
            if len(ports)==0:
                logger.info('无可测试设备')
                break
            round_num += 1
            logger.info(f"##########################第 {round_num} 轮测试开始######################\n")
            result = '通过'

            round_results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=64) as executor:
                futures = [executor.submit(test_single_port, port) for port in ports]
                for future in concurrent.futures.as_completed(futures):
                    port_result, _ = future.result()
                    round_results.append(port_result)
                    for gesture_result in port_result["gestures"]:
                        if gesture_result["result"]!= "通过":
                            result = '不通过'
                            final_result = '不通过'
                            break
            overall_result.extend(round_results)
            # with concurrent.futures.ProcessPoolExecutor() as executor:
            #     futures = [executor.submit(test_single_port, port) for port in ports]
            #     for future in concurrent.futures.as_completed(futures):
            #         try:
            #             port_result, _ = future.result()
            #             round_results.append(port_result)
            #             for gesture_result in port_result["gestures"]:
            #                 if gesture_result["result"] != "通过":
            #                     result = '不通过'
            #                     final_result = '不通过'
            #                     break
            #         except Exception as e:
            #             print(f"Error processing port test: {e}")
            #             result = '不通过'
            # overall_result.extend(round_results)

            logger.info(f"#################第 {round_num} 轮测试结束，测试结果：{result}#############\n")
    except Exception as e:
        final_result = '不通过'
        logger.error(f"Error: {e}")
    # finally:
    #     logger.info("执行测试结束后的清理操作（如有）")
    end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f'---------------------------------------------老化测试结束，测试结果：{final_result}<结束时间：{end_time}>----------------------------------------------\n')
    return overall_result, final_result

def test_single_port(port):
    """
    针对单个端口进行测试，返回该端口测试结果的字典，包含端口号、是否通过及具体手势测试结果等信息。
    """
    aging_test = AgingTest()
    aging_test.port = port
    connected_status = aging_test.connect_device()
    
    port_result = {
        'port': port,
        'gestures': []
    }
    
    if connected_status:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        grasp_gesture = aging_test.grasp_gesture
        initial_gesture = aging_test.initial_gesture
        try:
            if aging_test.set_max_current(): # 设置最大的电量限制为200ma
                if aging_test.do_gesture(grasp_gesture[0]) and aging_test.do_gesture(grasp_gesture[1]):
                    aging_test.count_motor_curtent()
                    logger.info(f'[port = {port}]执行抓握手势，电机电流为 -->{aging_test.motor_currents}\n')
                if aging_test.do_gesture(initial_gesture[0]) and aging_test.do_gesture(initial_gesture[1]):
                    if not aging_test.judge_if_hand_broken(aging_test.ROH_FINGER_POS_TARGET0,initial_gesture[1]):
                        motor_currents = aging_test.motor_currents
                        # if aging_test.check_current(motor_currents):
                        #     gesture_result = build_gesture_result(timestamp =timestamp,content=motor_currents,result='通过')
                        # else:
                        #     gesture_result = build_gesture_result(timestamp =timestamp,content=motor_currents,result='不通过')
                        gesture_result = build_gesture_result(timestamp =timestamp,content=motor_currents,result='通过')
                    else:
                        gesture_result = build_gesture_result(timestamp =timestamp,content='手指出现异常',result='不通过')
                else:
                    gesture_result = build_gesture_result(timestamp =timestamp,content='手指出现异常',result='不通过')
            else:
                gesture_result = build_gesture_result(timestamp =timestamp,content='设置手指最大电流失败',result='不通过')
                    
            port_result['gestures'].append(gesture_result)
        except Exception as e:
            error_gesture_result = build_gesture_result(timestamp =timestamp,content=f'出现错误：{e}',result='不通过')
            port_result['gestures'].append(error_gesture_result)
        finally:
            aging_test.disConnect_device()
    return port_result,connected_status

def build_gesture_result(timestamp,content,result):
    return {
            "timestamp": timestamp,
            "content": content,
            "result": result
        }
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
            for timestamp, description, expected, content, result, comment in data_list:
                logger.info(f" timestamp:{timestamp},content: {content}, Result: {result}")
if __name__ == "__main__":
    ports = ['COM3']
    max_cycle_num = 1
    main(ports = ports, max_cycle_num = max_cycle_num)