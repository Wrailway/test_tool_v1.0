import datetime
import logging
import struct
import sys
import concurrent.futures
import time
import unittest
import threading

from pymodbus.exceptions import ConnectionException, ModbusIOException
from pymodbus import FramerType, ModbusException
from pymodbus.client import ModbusSerialClient, serial

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(stream_handler)

# ModBus-RTU registers for ROH
MODBUS_PROTOCOL_VERSION_MAJOR = 1

ROH_PROTOCOL_VERSION      = (1000) # R
ROH_FW_VERSION            = (1001) # R
ROH_FW_REVISION           = (1002) # R
ROH_HW_VERSION            = (1003) # R
ROH_BOOT_VERSION          = (1004) # R
ROH_NODE_ID               = (1005) # R/W
ROH_SUB_EXCEPTION         = (1006) # R
ROH_BATTERY_VOLTAGE       = (1007) # R
ROH_SELF_TEST_LEVEL       = (1008) # R/W
ROH_BEEP_SWITCH           = (1009) # R/W
ROH_BEEP_PERIOD           = (1010) # W
ROH_BUTTON_PRESS_CNT      = (1011) # R/W
ROH_RECALIBRATE           = (1012) # W
ROH_START_INIT            = (1013) # W
ROH_RESET                 = (1014) # W
ROH_POWER_OFF             = (1015) # W
ROH_RESERVED0             = (1016) # R/W
ROH_RESERVED1             = (1017) # R/W
ROH_RESERVED2             = (1018) # R/W
ROH_RESERVED3             = (1019) # R/W
ROH_CALI_END0             = (1020) # R/W
ROH_CALI_END1             = (1021) # R/W
ROH_CALI_END2             = (1022) # R/W
ROH_CALI_END3             = (1023) # R/W
ROH_CALI_END4             = (1024) # R/W
ROH_CALI_END5             = (1025) # R/W
ROH_CALI_END6             = (1026) # R/W
ROH_CALI_END7             = (1027) # R/W
ROH_CALI_END8             = (1028) # R/W
ROH_CALI_END9             = (1029) # R/W
ROH_CALI_START0           = (1030) # R/W
ROH_CALI_START1           = (1031) # R/W
ROH_CALI_START2           = (1032) # R/W
ROH_CALI_START3           = (1033) # R/W
ROH_CALI_START4           = (1034) # R/W
ROH_CALI_START5           = (1035) # R/W
ROH_CALI_START6           = (1036) # R/W
ROH_CALI_START7           = (1037) # R/W
ROH_CALI_START8           = (1038) # R/W
ROH_CALI_START9           = (1039) # R/W
ROH_CALI_THUMB_POS0       = (1040) # R/W
ROH_CALI_THUMB_POS1       = (1041) # R/W
ROH_CALI_THUMB_POS2       = (1042) # R/W
ROH_CALI_THUMB_POS3       = (1043) # R/W
ROH_CALI_THUMB_POS4       = (1044) # R/W
ROH_FINGER_P0             = (1045) # R/W
ROH_FINGER_P1             = (1046) # R/W
ROH_FINGER_P2             = (1047) # R/W
ROH_FINGER_P3             = (1048) # R/W
ROH_FINGER_P4             = (1049) # R/W
ROH_FINGER_P5             = (1050) # R/W
ROH_FINGER_P6             = (1051) # R/W
ROH_FINGER_P7             = (1052) # R/W
ROH_FINGER_P8             = (1053) # R/W
ROH_FINGER_P9             = (1054) # R/W
ROH_FINGER_I0             = (1055) # R/W
ROH_FINGER_I1             = (1056) # R/W
ROH_FINGER_I2             = (1057) # R/W
ROH_FINGER_I3             = (1058) # R/W
ROH_FINGER_I4             = (1059) # R/W
ROH_FINGER_I5             = (1060) # R/W
ROH_FINGER_I6             = (1061) # R/W
ROH_FINGER_I7             = (1062) # R/W
ROH_FINGER_I8             = (1063) # R/W
ROH_FINGER_I9             = (1064) # R/W
ROH_FINGER_D0             = (1065) # R/W
ROH_FINGER_D1             = (1066) # R/W
ROH_FINGER_D2             = (1067) # R/W
ROH_FINGER_D3             = (1068) # R/W
ROH_FINGER_D4             = (1069) # R/W
ROH_FINGER_D5             = (1070) # R/W
ROH_FINGER_D6             = (1071) # R/W
ROH_FINGER_D7             = (1072) # R/W
ROH_FINGER_D8             = (1073) # R/W
ROH_FINGER_D9             = (1074) # R/W
ROH_FINGER_G0             = (1075) # R/W
ROH_FINGER_G1             = (1076) # R/W
ROH_FINGER_G2             = (1077) # R/W
ROH_FINGER_G3             = (1078) # R/W
ROH_FINGER_G4             = (1079) # R/W
ROH_FINGER_G5             = (1080) # R/W
ROH_FINGER_G6             = (1081) # R/W
ROH_FINGER_G7             = (1082) # R/W
ROH_FINGER_G8             = (1083) # R/W
ROH_FINGER_G9             = (1084) # R/W
ROH_FINGER_STATUS0        = (1085) # R
ROH_FINGER_STATUS1        = (1086) # R
ROH_FINGER_STATUS2        = (1087) # R
ROH_FINGER_STATUS3        = (1088) # R
ROH_FINGER_STATUS4        = (1089) # R
ROH_FINGER_STATUS5        = (1090) # R
ROH_FINGER_STATUS6        = (1091) # R
ROH_FINGER_STATUS7        = (1092) # R
ROH_FINGER_STATUS8        = (1093) # R
ROH_FINGER_STATUS9        = (1094) # R
ROH_FINGER_CURRENT_LIMIT0 = (1095) # R/W
ROH_FINGER_CURRENT_LIMIT1 = (1096) # R/W
ROH_FINGER_CURRENT_LIMIT2 = (1097) # R/W
ROH_FINGER_CURRENT_LIMIT3 = (1098) # R/W
ROH_FINGER_CURRENT_LIMIT4 = (1099) # R/W
ROH_FINGER_CURRENT_LIMIT5 = (1100) # R/W
ROH_FINGER_CURRENT_LIMIT6 = (1101) # R/W
ROH_FINGER_CURRENT_LIMIT7 = (1102) # R/W
ROH_FINGER_CURRENT_LIMIT8 = (1103) # R/W
ROH_FINGER_CURRENT_LIMIT9 = (1104) # R/W
ROH_FINGER_CURRENT0       = (1105) # R
ROH_FINGER_CURRENT1       = (1106) # R
ROH_FINGER_CURRENT2       = (1107) # R
ROH_FINGER_CURRENT3       = (1108) # R
ROH_FINGER_CURRENT4       = (1109) # R
ROH_FINGER_CURRENT5       = (1110) # R
ROH_FINGER_CURRENT6       = (1111) # R
ROH_FINGER_CURRENT7       = (1112) # R
ROH_FINGER_CURRENT8       = (1113) # R
ROH_FINGER_CURRENT9       = (1114) # R
ROH_FINGER_FORCE_LIMIT0   = (1115) # R/W
ROH_FINGER_FORCE_LIMIT1   = (1116) # R/W
ROH_FINGER_FORCE_LIMIT2   = (1117) # R/W
ROH_FINGER_FORCE_LIMIT3   = (1118) # R/W
ROH_FINGER_FORCE_LIMIT4   = (1119) # R/W
ROH_FINGER_FORCE0         = (1120) # R
ROH_FINGER_FORCE1         = (1121) # R
ROH_FINGER_FORCE2         = (1122) # R
ROH_FINGER_FORCE3         = (1123) # R
ROH_FINGER_FORCE4         = (1124) # R
ROH_FINGER_SPEED0         = (1125) # R/W
ROH_FINGER_SPEED1         = (1126) # R/W
ROH_FINGER_SPEED2         = (1127) # R/W
ROH_FINGER_SPEED3         = (1128) # R/W
ROH_FINGER_SPEED4         = (1129) # R/W
ROH_FINGER_SPEED5         = (1130) # R/W
ROH_FINGER_SPEED6         = (1131) # R/W
ROH_FINGER_SPEED7         = (1132) # R/W
ROH_FINGER_SPEED8         = (1133) # R/W
ROH_FINGER_SPEED9         = (1134) # R/W
ROH_FINGER_POS_TARGET0    = (1135) # R/W
ROH_FINGER_POS_TARGET1    = (1136) # R/W
ROH_FINGER_POS_TARGET2    = (1137) # R/W
ROH_FINGER_POS_TARGET3    = (1138) # R/W
ROH_FINGER_POS_TARGET4    = (1139) # R/W
ROH_FINGER_POS_TARGET5    = (1140) # R/W
ROH_FINGER_POS_TARGET6    = (1141) # R/W
ROH_FINGER_POS_TARGET7    = (1142) # R/W
ROH_FINGER_POS_TARGET8    = (1143) # R/W
ROH_FINGER_POS_TARGET9    = (1144) # R/W
ROH_FINGER_POS0           = (1145) # R
ROH_FINGER_POS1           = (1146) # R
ROH_FINGER_POS2           = (1147) # R
ROH_FINGER_POS3           = (1148) # R
ROH_FINGER_POS4           = (1149) # R
ROH_FINGER_POS5           = (1150) # R
ROH_FINGER_POS6           = (1151) # R
ROH_FINGER_POS7           = (1152) # R
ROH_FINGER_POS8           = (1153) # R
ROH_FINGER_POS9           = (1154) # R
ROH_FINGER_ANGLE_TARGET0  = (1155) # R/W
ROH_FINGER_ANGLE_TARGET1  = (1156) # R/W
ROH_FINGER_ANGLE_TARGET2  = (1157) # R/W
ROH_FINGER_ANGLE_TARGET3  = (1158) # R/W
ROH_FINGER_ANGLE_TARGET4  = (1159) # R/W
ROH_FINGER_ANGLE_TARGET5  = (1160) # R/W
ROH_FINGER_ANGLE_TARGET6  = (1161) # R/W
ROH_FINGER_ANGLE_TARGET7  = (1162) # R/W
ROH_FINGER_ANGLE_TARGET8  = (1163) # R/W
ROH_FINGER_ANGLE_TARGET9  = (1164) # R/W
ROH_FINGER_ANGLE0         = (1165) # R
ROH_FINGER_ANGLE1         = (1166) # R
ROH_FINGER_ANGLE2         = (1167) # R
ROH_FINGER_ANGLE3         = (1168) # R
ROH_FINGER_ANGLE4         = (1169) # R
ROH_FINGER_ANGLE5         = (1170) # R
ROH_FINGER_ANGLE6         = (1171) # R
ROH_FINGER_ANGLE7         = (1172) # R
ROH_FINGER_ANGLE8         = (1173) # R
ROH_FINGER_ANGLE9         = (1174) # R

# 当前版本号信息
PROTOCOL_VERSION = 'V1.0.0'
FW_VERSION = 'V3.0.0'
FW_REVISION = 'V0.130'
HW_VERSION = '1B01'
BOOT_VERSION = 'V1.7.0'

#设备寄存器的默认值，测试后用于恢复，否则设备可能无法使用

SELF_TEST_LEVEL       = 1 # 开机自检开关， 0 时等待 ROH_START_INIT 写 1 自检，设成 1 时允许开机归零，设成 2 时允许开机完整
BEEP_SWITCH           = 1 # 蜂鸣器开关，1 时允许发声，0 时蜂鸣器静音
BEEP_PERIOD           = 500 # 蜂鸣器发声时常（单位毫)

FINGER_P0             = 25000 # 大拇指弯曲 P 值
FINGER_P1             = 25000 # 食指弯曲 P 值
FINGER_P2             = 25000 # 中指弯曲 P 值
FINGER_P3             = 25000 # 无名指弯曲 P 值
FINGER_P4             = 25000 # 小指弯曲 P 值
FINGER_P5             = 25000 # 大拇指旋转 P 值

FINGER_I0             = 100 # 大拇指弯曲 I 值
FINGER_I1             = 100 # 食指弯曲 I 值
FINGER_I2             = 100 # 中指弯曲 I 值
FINGER_I3             = 100 # 无名指弯曲 I 值
FINGER_I4             = 100 # 小指弯曲 I 值
FINGER_I5             = 100 # 大拇指旋转 I 值


FINGER_D0             = 25000 # 大拇指弯曲 D 值
FINGER_D1             = 25000 # 食指弯曲 D 值
FINGER_D2             = 25000 # 中指弯曲 D 值
FINGER_D3             = 25000 # 无名指弯曲 D 值
FINGER_D4             = 25000 # 小指弯曲 D 值
FINGER_D5             = 25000 # 大拇指旋转 D 值


FINGER_G0             = 100 # 大拇指弯曲 G 值
FINGER_G1             = 25 # 食指弯曲 G 值
FINGER_G2             = 25 # 中指弯曲 G 值
FINGER_G3             = 25 # 无名指弯曲 G 值
FINGER_G4             = 25 # 小指弯曲 G 值
FINGER_G5             = 25 # 大拇指旋转 G 值


FINGER_CURRENT_LIMIT0  = 1200 # 大拇指弯曲电机电流限制值（mA）
FINGER_CURRENT_LIMIT1  = 1200 # 食指弯曲电机电流限制值（mA）
FINGER_CURRENT_LIMIT2  = 1200 # 中指弯曲电机电流限制值（mA）
FINGER_CURRENT_LIMIT3  = 1200 # 无名指弯曲电机电流限制值（mA）
FINGER_CURRENT_LIMIT4  = 1200 # 小指弯曲电机电流限制值（mA）
FINGER_CURRENT_LIMIT5  = 1200 # 大拇指旋转电机电流限制值（mA）


FINGER_FORCE_LIMIT0  = 15000 # 大拇指力量限制值（单位 mN）
FINGER_FORCE_LIMIT1  = 15000 # 食指指力量限制值（单位 mN）
FINGER_FORCE_LIMIT2  = 15000 # 中指力量限制值（单位 mN）
FINGER_FORCE_LIMIT3  = 15000 # 无名指力量限制值（单位 mN）
FINGER_FORCE_LIMIT4  = 15000 # 小指力量限制值（单位 mN）

FINGER_SPEED0 = 65535 # 大拇指弯曲逻辑速度（逻辑位置/秒）
FINGER_SPEED1 = 65535 # 食指弯曲逻辑速度（逻辑位置/秒）
FINGER_SPEED2 = 65535 # 中指弯曲逻辑速度（逻辑位置/秒）
FINGER_SPEED3 = 65535 # 无名指弯曲逻辑速度（逻辑位置/秒）
FINGER_SPEED4 = 65535 # 小指弯曲逻辑速度（逻辑位置/秒）
FINGER_SPEED5 = 65535 # 大拇旋转逻辑速度（逻辑位置/秒）

FINGER_POS_TARGET0 = 0 #大拇指弯曲逻辑目标位置
FINGER_POS_TARGET1 = 0 #食指弯曲逻辑目标位置
FINGER_POS_TARGET2 = 0 #中指弯曲逻辑目标位置
FINGER_POS_TARGET3 = 0 #无名指弯曲逻辑目标位置
FINGER_POS_TARGET4 = 0 #小指弯曲逻辑目标位置
FINGER_POS_TARGET5 = 0 #大拇旋转指逻辑目标位置
FINGER_POS_TARGET_MAX_LOSS = 32 # 位置最大精度损失


FINGER_ANGLE_TARGET0 = 32367 # 大拇指电机轴与旋转轴夹角的目标值
FINGER_ANGLE_TARGET1 = 32367 # 食指第一节与掌平面夹角的目标值
FINGER_ANGLE_TARGET2 = 32367 # 中指第一节与掌平面夹角的目标值
FINGER_ANGLE_TARGET3 = 32367 # 无名指第一节与掌平面夹角的目标值
FINGER_ANGLE_TARGET4 = 32367 # 小指第一节与掌平面夹角的目标值
FINGER_ANGLE_TARGET5 = 0 # 大拇旋转目标角度
FINGER_ANGLE_TARGET_MAX_LOSS = 5 # 角度最大精度损失


WAIT_TIME = 0.2 # 延迟打印，方便查看
    
class FingerStatusGetter:
    STATUS_OPENING = 0x0
    STATUS_CLOSING = 0X1
    STATUS_POS_REACHED = 0X2
    STATUS_OVER_CURRENT = 0X3
    STATUS_FORCE_REACHED = 0X4
    STATUS_STUCK = 0X5

    roh_finger_status_list = {
        STATUS_OPENING: '正在展开',
        STATUS_CLOSING: '正在抓取',
        STATUS_POS_REACHED: '位置到位停止',
        STATUS_OVER_CURRENT: '电流保护停止',
        STATUS_FORCE_REACHED: '力控到位停止',
        STATUS_STUCK: '电机堵转停止'
    }

    def get_finger_status(self, response):
        """
        根据传入的响应获取手指状态描述。

        参数：
        response：包含手指状态寄存器值的响应对象。

        返回：
        手指状态的描述字符串。
        """
        if not hasattr(response, 'registers'):
            return '无效的响应对象，无法获取手指状态'
        register_value = response.registers[0] if len(response.registers) > 0 else None
        if register_value is None:
            return '响应中没有有效的手指状态寄存器值'
        return self.roh_finger_status_list.get(register_value, '未知的手指状态')


class ModbusClient:
    # node_id = 2
    baudrate=115200
    framer=FramerType.RTU
    port = None
    _instance = None
    _lock = threading.Lock()
    
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

    roh_sub_exception_list = {
        ERR_STATUS_INIT: '等待初始化或者正在初始化，不接受此读写操作',
        ERR_STATUS_CALI: '等待校正，不接受此读写操作',
        ERR_INVALID_DATA: '无效的寄存器值',
        ERR_STATUS_STUCK: '电机堵转',
        ERR_OP_FAILED: '操作失败',
        ERR_SAVE_FAILED: '保存失败'
    }
    

    def get_exception(self, response,node_id=2):
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
            # response2 = self.client.read_holding_registers(ROH_SUB_EXCEPTION, 1, self.NODE_ID)
            response2 = self.client.read_holding_registers(address=ROH_SUB_EXCEPTION,slave=node_id)
            strException = '设备故障，具体原因为'+self.roh_sub_exception_list.get(response2.registers[0])
        else:
            strException = self.roh_exception_list.get(response.exception_code)
        return strException

    def __new__(cls, port):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance.port = port
                    cls._instance.connect()
        return cls._instance

    def connect(self):
        try:
            self.client = ModbusSerialClient(self.port, self.framer, self.baudrate)
            if not self.client.connect():
                raise ConnectionException(f"[port = {self.port}]Could not connect to Modbus device.")
            logger.info(f"[port = {self.port}]Successfully connected to Modbus device.")
        except ConnectionException as e:
            logger.error(f"[port = {self.port}]Error during connection: {e}")
            raise

    def read_from_register(self, address, count=1, node_id=2):
        max_retries = 1
        retry_count = 0
        while retry_count < max_retries:
            try:
                if not self.client:
                    raise ValueError(f"[port = {self.port}]Modbus client not initialized.")
                response = self.client.read_holding_registers(address, count,node_id)
                time.sleep(0.5)
                if not response.isError():
                    logger.info(f'[port = {self.port}]Read value successfully: {response.registers[0]}\n')
                    return response
                else:
                    error_type = self.get_exception(response,node_id)
                    if "connection timeout" in error_type.lower():
                        self.connect()
                    elif "read timeout" in error_type.lower():
                        retry_count += 1
                        time.sleep(0.5)
                    else:
                        logger.error(f'[port = {self.port}]Read register failed: {error_type}\n')
                        return None
            except ModbusIOException as e:
                logger.error(f'[port = {self.port}]Modbus I/O exception: {e}')
                if "connection error" in str(e).lower():
                    self.connect()
                else:
                    return None
            except ValueError as e:
                logger.error(f'[port = {self.port}]Value error: {e}')
                return None
            except Exception as e:
                logger.error(f'[port = {self.port}]Other exception: {e}')
                return None
        return None

    def write_to_register(self, address, values, node_id=2):
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            try:
                if not self.client:
                    raise ValueError(f"[port = {self.port}]Modbus client not initialized.")
                response = self.client.write_registers(address, values,node_id)
                time.sleep(0.5)
                if not response.isError():
                    logger.info(f'[port = {self.port}]Write value successfully: {values}\n')
                    return True
                else:
                    error_type = self.get_exception(response)
                    if "connection timeout" in error_type.lower():
                        self.connect()
                    elif "write timeout" in error_type.lower():
                        retry_count += 1
                        time.sleep(0.5)
                    else:
                        logger.error(f'[port = {self.port}]Write register failed: {error_type}\n')
                        return False
            except ModbusIOException as e:
                logger.error(f'[port = {self.port}]Modbus I/O exception: {e}')
                if "connection error" in str(e).lower():
                    self.connect()
                else:
                    return False
            except ValueError as e:
                logger.error(f'[port = {self.port}]Value error: {e}')
                return False
            except Exception as e:
                logger.error(f'[port = {self.port}]Other exception: {e}')
                return False
        return False


class TestModbus(unittest.TestCase):
    TEST_STRAT = 0X0
    TEST_PASS = 0X1
    TEST_FAIL = 0X2
    TEST_END = 0X3
    TEST_UNKOWN = 0X4

    roh_test_status_list = {
        TEST_STRAT: '开始测试',
        TEST_PASS: '测试通过',
        TEST_FAIL: '测试不通过',
        TEST_END: '测试结束',
        TEST_UNKOWN: '发生未知错误'
    }

    def print_test_info(self, status, info=''):
        # 检查 status 是否为合法值
        if status not in [self.TEST_STRAT, self.TEST_PASS, self.TEST_FAIL, self.TEST_END] and status not in self.roh_test_status_list:
            raise ValueError(f"[port = {self.port}]Invalid status value: {status}")

        if status == self.TEST_STRAT:
            """打印测试开始信息"""
            start_message = f'###########################  {self.roh_test_status_list.get(status)} <{info}> ############################'
            border = '-' * len(start_message)
            print(border)
            print(start_message)
            print(border + '\n')
        elif status == self.TEST_PASS or status == self.TEST_FAIL:
            """打印测试通过或失败信息"""
            pass_fail_message = f'--------------------------------  {self.roh_test_status_list.get(status)}  ----------------------------------'
            border = '-' * len(pass_fail_message)
            print(border)
            print(pass_fail_message)
            print(border + '\n')
        elif status == self.TEST_END:
            """打印测试结束信息"""
            end_message = f'################################  {self.roh_test_status_list.get(status)} #################################'
            border = '-' * len(end_message)
            logger.info(border)
            logger.info(end_message)
            logger.info(border + '\n')
        else:
            """打印其他状态信息"""
            logger.info(f'{self.roh_test_status_list.get(status)}\n')
            
    def __init__(self, port, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # logger.info(f'[port = {port}]TestModbus__init__')
        self.port = port
        self.node_id = 2
        self.client = None
        self.fingerStatusGetter = None

    def setUp(self):
        logger.info(f'[port = {self.port}]setUp\n')
        self.client = ModbusClient(port=self.port)
        self.fingerStatusGetter = FingerStatusGetter()

    def tearDown(self):
        logger.info(f'[port = {self.port}]tearDown\n')
        self.client = None
        self.modbusClient = None
        self.fingerStatusGetter = None
    
    def isNotNoneOrError(self, response):
        if(response is None or response.isError()):
            return False
        else:
            return True
        
    def check_and_print_test_info(self, response):
        if self.isNotNoneOrError(response):
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)

    def test_read_protocol_version(self):
        self.print_test_info(status=self.TEST_STRAT,info='read protocol version')
        response = self.client.read_from_register(address=ROH_PROTOCOL_VERSION)
        self.check_and_print_test_info(response=response)
            
    def test_read_fw_version(self):
        self.print_test_info(status=self.TEST_STRAT,info='read fireware version')
        response = self.client.read_from_register(address=ROH_FW_VERSION)
        self.check_and_print_test_info(response=response)
            
    def test_read_fw_revision(self):
        self.print_test_info(status=self.TEST_STRAT,info='read fireware revision')
        response = self.client.read_from_register(address=ROH_FW_REVISION)
        self.check_and_print_test_info(response=response)
            
            
    def test_read_hw_version(self): 
        self.print_test_info(status=self.TEST_STRAT,info='read hardware version')
        response = self.client.read_from_register(address=ROH_HW_VERSION)
        self.check_and_print_test_info(response=response)
 
    
    def test_read_boot_version(self):
        self.print_test_info(status=self.TEST_STRAT,info='read boot loader version')
        response = self.client.read_from_register(address=ROH_BOOT_VERSION)
        self.check_and_print_test_info(response=response)
            
            
    def test_read_nodeID_version(self):
        self.print_test_info(status=self.TEST_STRAT,info='read node id')
        response = self.client.read_from_register(address=ROH_NODE_ID)
        self.check_and_print_test_info(response=response)
            
            
    def wait_device_reboot(self, max_attempts=60, delay_time=1,target_node_id = 2):
        attempt_count = 0
        while attempt_count < max_attempts:
            logger.info(f'[port = {self.port}]等待设备重启中...{attempt_count}')
            time.sleep(delay_time)
            if(attempt_count % 5 == 0 ):
                response = self.client.read_from_register(address=ROH_NODE_ID,node_id=target_node_id)
                if(self.isNotNoneOrError(response=response)):
                    logger.info(f'[port = {self.port}]设备已启动')
                    break
            attempt_count += 1
                       
    def test_write_nodeID_version(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write node id：3')
        default_node_id = 2
        target_node_id = 3
        
        logger.info(f'[port = {self.port}]尝试更改设备ID 为 {target_node_id}\n')
        response1 = self.client.write_to_register(address=ROH_NODE_ID,values=target_node_id,node_id=default_node_id)
        if(not response1):
            logger.info(f'[port = {self.port}]更改设备id失败 node id ={target_node_id}')
            self.print_test_info(status=self.TEST_FAIL)
            return
        
        self.wait_device_reboot(60,1,target_node_id)
        response2 = self.client.read_from_register(address=ROH_NODE_ID,node_id=target_node_id)
        
        if(self.isNotNoneOrError(response=response2)):
            self.assertEqual(response2.registers[0],target_node_id)
            logger.info(f'[port = {self.port}]更改设备id = {response2.registers[0]}成功\n')
        else:
            logger.info(f'[port = {self.port}]读取设备id = {response2.registers[0]}失败\n')
            self.print_test_info(status=self.TEST_FAIL)
            return
            
        logger.info(f'[port = {self.port}]恢复设备ID 为 {default_node_id}\n')
        response3 = self.client.write_to_register(address=ROH_NODE_ID,values=default_node_id,node_id=target_node_id)
        
        if(not response3):
            logger.info(f'[port = {self.port}]更改设备id失败 node id ={default_node_id}')
            self.print_test_info(status=self.TEST_FAIL)
            return
        
        self.wait_device_reboot(max_attempts=60,delay_time=1,target_node_id=default_node_id)
        
        response4 = self.client.read_from_register(address=ROH_NODE_ID,node_id=default_node_id)
        if(self.isNotNoneOrError(response=response4)):
            self.assertEqual(response4.registers[0],default_node_id)
            logger.info(f'[port = {self.port}]恢复设备id = {response4.registers[0]}成功\n')
            self.print_test_info(status=self.TEST_PASS)
        else:
            logger.info(f'恢复设备id = {response4.registers[0]}失败\n')
            self.print_test_info(status=self.TEST_FAIL)
        
    def test_read_battery_voltage(self):
        self.print_test_info(status=self.TEST_STRAT,info='read battery_voltage')
        response = self.client.read_from_register(address=ROH_BATTERY_VOLTAGE)
        self.check_and_print_test_info(response=response)
    
    def test_read_self_test_level(self):
        self.print_test_info(status=self.TEST_STRAT,info='read self test level')
        response = self.client.read_from_register(address=ROH_SELF_TEST_LEVEL)
        self.check_and_print_test_info(response=response)
            
    def test_write_self_test_level_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write self test level：0')
        if(self.client.write_to_register(address = ROH_SELF_TEST_LEVEL,values = 0)):
            response = self.client.read_from_register(ROH_SELF_TEST_LEVEL)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_SELF_TEST_LEVEL,values = SELF_TEST_LEVEL)
            
    def test_write_self_test_level_1(self):
        self.print_test_info(status=self.TEST_STRAT,info='write self test level：1')
        if(self.client.write_to_register(address = ROH_SELF_TEST_LEVEL,values = 1)):
            response = self.client.read_from_register(ROH_SELF_TEST_LEVEL)
            self.assertEqual(response.registers[0],1)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_SELF_TEST_LEVEL,values = SELF_TEST_LEVEL)
            
    def test_write_self_test_level_2(self):
        self.print_test_info(status=self.TEST_STRAT,info='write self test level：2')
        if(self.client.write_to_register(address = ROH_SELF_TEST_LEVEL,values = 2)):
            response = self.client.read_from_register(address=ROH_SELF_TEST_LEVEL)
            self.assertEqual(response.registers[0],2)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_SELF_TEST_LEVEL,values = SELF_TEST_LEVEL)
    
    def test_write_self_test_level_4(self):
        self.print_test_info(status=self.TEST_STRAT,info='write self test level：4')
        if(not self.client.write_to_register(address = ROH_SELF_TEST_LEVEL,values = 4)):
            response = self.client.read_from_register(address=ROH_SELF_TEST_LEVEL)
            self.assertNotEqual(response.registers[0],4)
            logger.info(f'写入4失败，值有效范围0,1,2')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # # 恢复默认值，超过范围的值写不进去，不需要恢复默认值
        # self.client.write_to_register(address = ROH_SELF_TEST_LEVEL,values = SELF_TEST_LEVEL)

    def test_read_beep_switch(self):
        self.print_test_info(status=self.TEST_STRAT,info='read beep switch')
        response = self.client.read_from_register(address=ROH_BEEP_SWITCH)
        self.check_and_print_test_info(response)
            
    #写的范围为0或者非0      
    def test_write_beep_switch_0(self):  
        self.print_test_info(status=self.TEST_STRAT,info='write beep switch:0')
        if(self.client.write_to_register(address = ROH_BEEP_SWITCH,values = 0)):
            response = self.client.read_from_register(address=ROH_BEEP_SWITCH)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_BEEP_SWITCH,values = BEEP_SWITCH)
            
    def test_write_beep_switch_1(self):
        self.print_test_info(status=self.TEST_STRAT,info='write beep switch:1')
        if(self.client.write_to_register(address = ROH_BEEP_SWITCH,values = 1)):
            response = self.client.read_from_register(address=ROH_BEEP_SWITCH)
            self.assertEqual(response.registers[0],1)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_BEEP_SWITCH,values = BEEP_SWITCH)
            
    # 值范围1-65535，增加0异常值  
    def test_write_beep_period_1(self):
        self.print_test_info(status=self.TEST_STRAT,info='write beep period :1')
        if(self.client.write_to_register(address = ROH_BEEP_PERIOD,values = 1)):
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_BEEP_PERIOD,values = BEEP_PERIOD)
            
    def test_write_beep_period_65535(self):     
        self.print_test_info(status=self.TEST_STRAT,info='write beep period: 65535')
        if(self.client.write_to_register(address = ROH_BEEP_PERIOD,values = 65535)):
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_BEEP_PERIOD,values = BEEP_PERIOD)
            
    def test_write_beep_period_0(self):       
        self.print_test_info(status=self.TEST_STRAT,info='write beep period: 0')
        if(not self.client.write_to_register(address = ROH_BEEP_PERIOD,values = 0)):
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值, 无效的值，不需要 恢复
        # self.client.write_to_register(address = ROH_BEEP_PERIOD,values = BEEP_PERIOD)

    @unittest.skip("ROH_BUTTON_PRESS_CNT暂时没有，直接跳过这个测试用例")  
    def test_read_button_press_cnt(self):
        self.print_test_info(status=self.TEST_STRAT,info='read button_press_cnt')
        # if(self.client.read_from_register(ROH_BUTTON_PRESS_CNT)):
        #     self.print_test_info(status=self.TEST_PASS)
        # else:
        #     self.print_test_info(status=self.TEST_FAIL)
        logger.info('skip it,暂时不生效')
        
    @unittest.skip("ROH_BUTTON_PRESS_CNT暂时没有，直接跳过这个测试用例")  
    def test_write_button_press_cnt(self):
        self.print_test_info(status=self.TEST_STRAT,info='write button_press_cnt')
        logger.info('skip it，暂时不生效')
        
# # | ROH_RECALIBRATE           |       1012 | W         |                    | 重新校正，写入特定值（非公开）会让 ROH 灵巧手进入校正状态    
 
# # | ROH_START_INIT            |       1013 | W         |                    | 开始自检，仅等待自检状态下有效 
    @unittest.skip("ROH_START_INIT暂时没有，直接跳过这个测试用例")  
    def test_write_start_init(self):
        self.print_test_info(status=self.TEST_STRAT,info='write start init')
        logger.info('skip it')
        
# # | ROH_RESET                 |       1014 | W         |                    | 复位，写入非 0 值时进入 DFU 模式，写入 0 时重启到工作模式   
    @unittest.skip("ROH_RESET暂时没有，直接跳过这个测试用例") 
    def test_write_reset(self):
        self.print_test_info(status=self.TEST_STRAT,info='write reset')
        logger.info('skip it')
        
# # | ROH_POWER_OFF             |       1015 | W         |                    | 关机，暂时不可用  
    @unittest.skip("ROH_POWER_OFF暂时没有，直接跳过这个测试用例") 
    def test_write_power_off(self):
        self.print_test_info(status=self.TEST_STRAT,info='write power off')
        logger.info('skip it，暂时不生效')
        
# # | ROH_CALI_END0             |       1020 | R/W       | 出厂校正值         | 大拇指运行区间（绝对位置）上限（uint16），设置时保存到非易失存储器，用户无需设置                                                 |
# # | ROH_CALI_END1             |       1021 | R/W       | 出厂校正值         | 食指运行区间（绝对位置）上限（uint16），设置时保存到非易失存储器，用户无需设置                                                   |
# # | ROH_CALI_END2             |       1022 | R/W       | 出厂校正值         | 中指运行区间（绝对位置）上限（uint16），设置时保存到非易失存储器，用户无需设置                                                   |
# # | ROH_CALI_END3             |       1023 | R/W       | 出厂校正值         | 无名指运行区间（绝对位置）上限（uint16），设置时保存到非易失存储器，用户无需设置                                                 |
# # | ROH_CALI_END4             |       1024 | R/W       | 出厂校正值         | 小指运行区间（绝对位置）上限（uint16），设置时保存到非易失存储器，用户无需设置                                                   |
# # | ROH_CALI_END5             |       1025 | R/W       | 出厂校正值         | 大拇指旋转运行区间（绝对位置）上限（uint16），设置时保存到非易失存储器，用户无需设置                                             |                                                                                                                            |
# # | ROH_CALI_START0           |       1030 | R/W       | 出厂校正值         | 大拇指运行区间（绝对位置）下限（uint16），设置时保存到非易失存储器，用户无需设置                                                 |
# # | ROH_CALI_START1           |       1031 | R/W       | 出厂校正值         | 食指运行区间（绝对位置）下限（uint16），设置时保存到非易失存储器，用户无需设置                                                   |
# # | ROH_CALI_START2           |       1032 | R/W       | 出厂校正值         | 中指运行区间（绝对位置）下限（uint16），设置时保存到非易失存储器，用户无需设置                                                   |
# # | ROH_CALI_START3           |       1033 | R/W       | 出厂校正值         | 无名指运行区间（绝对位置）下限（uint16），设置时保存到非易失存储器，用户无需设置                                                 |
# # | ROH_CALI_START4           |       1034 | R/W       | 出厂校正值         | 小指运行区间（绝对位置）下限（uint16），设置时保存到非易失存储器，用户无需设置                                                   |
# # | ROH_CALI_START5           |       1035 | R/W       | 出厂校正值         | 大拇指旋转运行区间（绝对位置）下限（uint16），设置时保存到非易失存储器，用户无需设置                                             |                                                                                                                           |
# # | ROH_CALI_THUMB_POS0       |       1040 | R/W       | 出厂校正值         | 大拇指侧掌位预设位置（绝对位置，uint16），设置时保存到非易失存储器，用户无需设置                                                 |
# # | ROH_CALI_THUMB_POS1       |       1041 | R/W       | 出厂校正值         | 大拇指对掌位 1 预设位置（绝对位置，uint16），设置时保存到非易失存储器，用户无需设置                                              |
# # | ROH_CALI_THUMB_POS2       |       1042 | R/W       | 出厂校正值         | 大拇指对掌位 2 预设位置（绝对位置，uint16），设置时保存到非易失存储器，用户无需设置                                              |                                                                                                                         |


    def test_read_finger_p0(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger p0')
        response = self.client.read_from_register(address=ROH_FINGER_P0)
        self.check_and_print_test_info(response)
            
    #  写值范围100~25000  
    def test_write_finger_p0_100(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p0 ：100')
        if(self.client.write_to_register(address = ROH_FINGER_P0,values = 100)):
            response = self.client.read_from_register(address=ROH_FINGER_P0)
            self.assertEqual(response.registers[0],100)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_P0,values = FINGER_P0 )
        
    def test_write_finger_p0_10000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p0 ：10000')
        if(self.client.write_to_register(address = ROH_FINGER_P0,values = 10000)):
            response = self.client.read_from_register(address=ROH_FINGER_P0)
            self.assertEqual(response.registers[0],10000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_P0,values = FINGER_P0)
            
    def test_write_finger_p0_25000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p0 ：25000')
        if(self.client.write_to_register(address = ROH_FINGER_P0,values = 25000)):
            response = self.client.read_from_register(address=ROH_FINGER_P0)
            self.assertEqual(response.registers[0],25000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_P0,values = FINGER_P0)
            
    def test_write_finger_p0_99(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p0 ：99')
        if(self.client.write_to_register(address = ROH_FINGER_P0,values = 99)):
            response = self.client.read_from_register(address=ROH_FINGER_P0)
            self.assertNotEqual(response.registers[0],99)
            logger.info(f'写入99失败，有效值范围100~25000')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
    def test_write_finger_p0_25001(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p0 ：25001')
        if(self.client.write_to_register(address = ROH_FINGER_P0,values = 25001)):
            response = self.client.read_from_register(address=ROH_FINGER_P0)
            self.assertNotEqual(response.registers[0],25001)
            logger.info(f'写入25001失败，有效值范围100~25000')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
        
    def test_read_finger_p1(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger p1')
        response = self.client.read_from_register(ROH_FINGER_P1)
        self.check_and_print_test_info(response)
            
    #  写值范围100~25000  
    def test_write_finger_p1_100(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p1： 100')
        if(self.client.write_to_register(address = ROH_FINGER_P1,values = 100)):
            response = self.client.read_from_register(address=ROH_FINGER_P1)
            self.assertEqual(response.registers[0],100)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_P1,values = FINGER_P1)
        
    def test_write_finger_p1_10000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p1： 10000')
        if(self.client.write_to_register(address = ROH_FINGER_P1,values = 10000)):
            response = self.client.read_from_register(ROH_FINGER_P1)
            self.assertEqual(response.registers[0],10000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_P1,values = FINGER_P1)
            
    def test_write_finger_p1_25000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p1： 25000')
        if(self.client.write_to_register(address = ROH_FINGER_P0,values = 25000)):
            response = self.client.read_from_register(ROH_FINGER_P0)
            self.assertEqual(response.registers[0],25000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_P1,values = FINGER_P1)
            
    def test_write_finger_p1_99(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p1： 99')
        if(self.client.write_to_register(address = ROH_FINGER_P1,values = 99)):
            response = self.client.read_from_register(address=ROH_FINGER_P1)
            self.assertNotEqual(response.registers[0],99)
            logger.info(f'写入99失败，有效值范围100~25000')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
    def test_write_finger_p1_25001(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p1： 25001')
        if(self.client.write_to_register(address = ROH_FINGER_P1,values = 25001)):
            response = self.client.read_from_register(address=ROH_FINGER_P1)
            self.assertNotEqual(response.registers[0],25001)
            logger.info(f'写入25001失败，有效值范围100~25000')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
    def test_read_finger_p2(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger p2')
        response = self.client.read_from_register(ROH_FINGER_P2)
        self.check_and_print_test_info(response)
            
    #  写值范围100~25000  
    def test_write_finger_p2_100(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p2： 100')
        if(self.client.write_to_register(address = ROH_FINGER_P2,values = 100)):
            response = self.client.read_from_register(ROH_FINGER_P2)
            self.assertEqual(response.registers[0],100)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_P2,values = FINGER_P2)
        
    def test_write_finger_p2_10000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p2： 10000')
        if(self.client.write_to_register(address = ROH_FINGER_P2,values = 10000)):
            response = self.client.read_from_register(address=ROH_FINGER_P2)
            self.assertEqual(response.registers[0],10000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_P2,values = FINGER_P2)
            
    def test_write_finger_p2_25000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p2： 25000')
        if(self.client.write_to_register(address = ROH_FINGER_P2,values = 25000)):
            response = self.client.read_from_register(ROH_FINGER_P2)
            self.assertEqual(response.registers[0],25000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_P2,values = FINGER_P2 )
            
    def test_write_finger_p2_99(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p2： 99')
        if(self.client.write_to_register(address = ROH_FINGER_P2,values = 99)):
            response = self.client.read_from_register(address=ROH_FINGER_P2)
            self.assertNotEqual(response.registers[0],99)
            logger.info(f'写入99失败，有效值范围100~25000')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
    def test_write_finger_p2_25001(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p2： 25001')
        if(self.client.write_to_register(address = ROH_FINGER_P2,values = 25001)):
            response = self.client.read_from_register(ROH_FINGER_P2)
            self.assertNotEqual(response.registers[0],25001)
            logger.info(f'写入25001失败，有效值范围100~25000')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
    def test_read_finger_p3_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger p3')
        response = self.client.read_from_register(address=ROH_FINGER_P3)
        self.check_and_print_test_info(response)
        
            
    #  写值范围100~25000  
    def test_write_finger_p3_100(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p3： 100')
        if(self.client.write_to_register(address = ROH_FINGER_P3,values = 100)):
            response = self.client.read_from_register(address=ROH_FINGER_P3)
            self.assertEqual(response.registers[0],100)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_P3,values = FINGER_P3)
        
    def test_write_finger_p3_10000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p3： 10000')
        if(self.client.write_to_register(address = ROH_FINGER_P3,values = 10000)):
            response = self.client.read_from_register(address=ROH_FINGER_P3)
            self.assertEqual(response.registers[0],10000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_P3,values = FINGER_P3)
            
    def test_write_finger_p3_25000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p3： 25000')
        if(self.client.write_to_register(address = ROH_FINGER_P3,values = 25000)):
            response = self.client.read_from_register(address=ROH_FINGER_P3)
            self.assertEqual(response.registers[0],25000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_P3,values = FINGER_P3)
            
    def test_write_finger_p3_99(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p3： 99')
        if(self.client.write_to_register(address = ROH_FINGER_P3,values = 99)):
            response = self.client.read_from_register(address=ROH_FINGER_P3)
            self.assertNotEqual(response.registers[0],99)
            logger.info(f'写入99失败，有效值范围100~25000')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
    def test_write_finger_p3_25001(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p3： 25001')
        if(self.client.write_to_register(address = ROH_FINGER_P3,values = 25001)):
            response = self.client.read_from_register(address=ROH_FINGER_P3)
            self.assertNotEqual(response.registers[0],25001)
            logger.info(f'写入25001失败，有效值范围100~25000')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
    def test_read_finger_p4(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger p4')
        response = self.client.read_from_register(address=ROH_FINGER_P4)
        self.check_and_print_test_info(response)
            
    #  写值范围100~25000    
    def test_write_finger_p4_100(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p4： 100')
        if(self.client.write_to_register(address = ROH_FINGER_P4,values = 100)):
            response = self.client.read_from_register(address=ROH_FINGER_P4)
            self.assertEqual(response.registers[0],100)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_P4,values = FINGER_P4)
        
    def test_write_finger_p4_10000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p4： 10000')
        if(self.client.write_to_register(address = ROH_FINGER_P4,values = 10000)):
            response = self.client.read_from_register(address=ROH_FINGER_P4)
            self.assertEqual(response.registers[0],10000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_P4,values = FINGER_P4)
            
    def test_write_finger_p4_25000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p4： 25000')
        if(self.client.write_to_register(address = ROH_FINGER_P4,values = 25000)):
            response = self.client.read_from_register(address=ROH_FINGER_P4)
            self.assertEqual(response.registers[0],25000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_P4,values = FINGER_P4)
            
    def test_write_finger_p4_99(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p4： 99')
        if(self.client.write_to_register(address = ROH_FINGER_P4,values = 99)):
            response = self.client.read_from_register(address=ROH_FINGER_P4)
            self.assertNotEqual(response.registers[0],99)
            logger.info(f'写入99失败，有效值范围100~25000')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
    def test_write_finger_p4_25001(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p4： 25001')
        if(self.client.write_to_register(address = ROH_FINGER_P4,values = 25001)):
            response = self.client.read_from_register(address=ROH_FINGER_P4)
            self.assertNotEqual(response.registers[0],25001)
            logger.info(f'写入25001失败，有效值范围100~25000')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
    def test_read_finger_p5(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger p5')
        response = self.client.read_from_register(address=ROH_FINGER_P5)
        self.check_and_print_test_info(response)
            
    #  写值范围100~25000    
    def test_write_finger_p5_100(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p5： 100')
        if(self.client.write_to_register(address = ROH_FINGER_P5,values = 100)):
            response = self.client.read_from_register(address=ROH_FINGER_P5)
            self.assertEqual(response.registers[0],100)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_P5,values = FINGER_P5)
        
    def test_write_finger_p5_10000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p5： 10000')
        if(self.client.write_to_register(address = ROH_FINGER_P5,values = 10000)):
            response = self.client.read_from_register(address=ROH_FINGER_P5)
            self.assertEqual(response.registers[0],10000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_P5,values = FINGER_P5)
            
    def test_write_finger_p5_25000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p5： 25000')
        if(self.client.write_to_register(address = ROH_FINGER_P5,values = 25000)):
            response = self.client.read_from_register(address=ROH_FINGER_P5)
            self.assertEqual(response.registers[0],25000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_P5,values = FINGER_P5)
            
    def test_write_finger_p5_99(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p5： 99')
        if(self.client.write_to_register(address = ROH_FINGER_P5,values = 99)):
            response = self.client.read_from_register(address=ROH_FINGER_P5)
            self.assertNotEqual(response.registers[0],99)
            logger.info(f'写入99失败，有效值范围100~25000')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
    def test_write_finger_p5_25001(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger p5： 25001')
        if(self.client.write_to_register(address = ROH_FINGER_P5,values = 25001)):
            response = self.client.read_from_register(address=ROH_FINGER_P5)
            self.assertNotEqual(response.registers[0],25001)
            logger.info(f'写入25001失败，有效值范围100~25000')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
    def test_read_finger_I0(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger I0')
        response = self.client.read_from_register(address=ROH_FINGER_I0)
        self.check_and_print_test_info(response)
        
            
    # 有效值范围0-5000    
    def test_write_finger_I0_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger I0： 0')
        if(self.client.write_to_register(address = ROH_FINGER_I0,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_I0)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
          # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_I0,values = FINGER_I0)
        
    def test_write_finger_I0_2000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger I0： 2000')
        if(self.client.write_to_register(address = ROH_FINGER_I0,values = 2000)):
            response = self.client.read_from_register(address=ROH_FINGER_I0)
            self.assertEqual(response.registers[0],2000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
          # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_I0,values = FINGER_I0)
            
    # 取值范围 5000   
    def test_write_finger_I0_5000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger I0： 5000')
        if(self.client.write_to_register(address = ROH_FINGER_I0,values = 5000)):
            response = self.client.read_from_register(address=ROH_FINGER_I0)
            self.assertEqual(response.registers[0],5000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_I0,values = FINGER_I0)
            
    def test_write_finger_I0_5001(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger I0： 5001')
        if(self.client.write_to_register(address = ROH_FINGER_I0,values = 5001)):
            response = self.client.read_from_register(address=ROH_FINGER_I0)
            self.assertNotEqual(response.registers[0],5001)
            logger.info(f'写入5001失败，有效值范围0~5000')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
    def test_read_finger_I1(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger I1')
        response = self.client.read_from_register(address=ROH_FINGER_I1)
        self.check_and_print_test_info(response)
        
            
    # 有效值范围0-5000    
    def test_write_finger_I1_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger I1： 0')
        if(self.client.write_to_register(address = ROH_FINGER_I1,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_I1)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_I1,values = FINGER_I1)
        
    def test_write_finger_I1_2000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger I1： 2000')
        if(self.client.write_to_register(address = ROH_FINGER_I1,values = 2000)):
            response = self.client.read_from_register(address=ROH_FINGER_I1)
            self.assertEqual(response.registers[0],2000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_I1,values = FINGER_I1)
            
    # 取值范围 5000   
    def test_write_finger_I1_5000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger I1： 5000')
        if(self.client.write_to_register(address = ROH_FINGER_I1,values = 5000)):
            response = self.client.read_from_register(address=ROH_FINGER_I1)
            self.assertEqual(response.registers[0],5000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_I1,values = FINGER_I1)
            
    def test_write_finger_I1_5001(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger I1： 5001')
        if(self.client.write_to_register(address = ROH_FINGER_I1,values = 5001)):
            response = self.client.read_from_register(address=ROH_FINGER_I1)
            self.assertNotEqual(response.registers[0],5001)
            logger.info(f'写入5001失败，有效值范围0~5000')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
    def test_read_finger_I2(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger I2')
        response = self.client.read_from_register(address=ROH_FINGER_I2)
        self.check_and_print_test_info(response)
        
            
    # 有效值范围0-5000    
    def test_write_finger_I2_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger I2： 0')
        if(self.client.write_to_register(address = ROH_FINGER_I2,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_I2)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_I2,values = FINGER_I2)
        
    def test_write_finger_I2_2000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger I2： 2000')
        if(self.client.write_to_register(address = ROH_FINGER_I2,values = 2000)):
            response = self.client.read_from_register(address=ROH_FINGER_I2)
            self.assertEqual(response.registers[0],2000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_I2,values = FINGER_I2)
            
    # 取值范围 5000   
    def test_write_finger_I2_5000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger I2： 5000')
        if(self.client.write_to_register(address = ROH_FINGER_I2,values = 5000)):
            response = self.client.read_from_register(address=ROH_FINGER_I2)
            self.assertEqual(response.registers[0],5000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_I2,values = FINGER_I2)
            
    def test_write_finger_I2_5001(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger I2： 5001')
        if(self.client.write_to_register(address = ROH_FINGER_I2,values = 5001)):
            response = self.client.read_from_register(address=ROH_FINGER_I2)
            self.assertNotEqual(response.registers[0],5001)
            logger.info(f'写入5001失败，有效值范围0~5000')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)

    def test_read_finger_I3(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger I3')
        response = self.client.read_from_register(address=ROH_FINGER_I3)
        self.check_and_print_test_info(response)
            
    # 有效值范围0-5000    
    def test_write_finger_I3_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  I3： 0')
        if(self.client.write_to_register(address = ROH_FINGER_I3,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_I3)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_I3,values = FINGER_I3)
        
    def test_write_finger_I3_2000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  I3： 2000')
        if(self.client.write_to_register(address = ROH_FINGER_I3,values = 2000)):
            response = self.client.read_from_register(address=ROH_FINGER_I3)
            self.assertEqual(response.registers[0],2000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_I3,values = FINGER_I3)
            
    # 取值范围 5000   
    def test_write_finger_I3_5000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  I3： 5000')
        if(self.client.write_to_register(address = ROH_FINGER_I3,values = 5000)):
            response = self.client.read_from_register(address=ROH_FINGER_I3)
            self.assertEqual(response.registers[0],5000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
          # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_I3,values = FINGER_I3)
            
    def test_write_finger_I3_5001(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  I3： 5001')
        if(self.client.write_to_register(address = ROH_FINGER_I3,values = 5001)):
            response = self.client.read_from_register(address=ROH_FINGER_I3)
            self.assertNotEqual(response.registers[0],5001)
            logger.info(f'写入5001失败，有效值范围0~5000')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)

    def test_read_finger_I4(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger I4')
        response = self.client.read_from_register(address=ROH_FINGER_I4)
        self.check_and_print_test_info(response)
      
            
    # 有效值范围0-5000    
    def test_write_finger_I4_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  I4： 0')
        if(self.client.write_to_register(address = ROH_FINGER_I4,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_I4)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_I4,values = FINGER_I4)
        
    def test_write_finger_I4_2000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  I4： 2000')
        if(self.client.write_to_register(address = ROH_FINGER_I4,values = 2000)):
            response = self.client.read_from_register(address=ROH_FINGER_I4)
            self.assertEqual(response.registers[0],2000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_I4,values = FINGER_I4)
            
    # 取值范围 5000   
    def test_write_finger_I4_5000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  I4： 5000')
        if(self.client.write_to_register(address = ROH_FINGER_I4,values = 5000)):
            response = self.client.read_from_register(address=ROH_FINGER_I4)
            self.assertEqual(response.registers[0],5000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
          # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_I4,values = FINGER_I4)
            
    def test_write_finger_I4_5001(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  I4： 5001')
        if(self.client.write_to_register(address = ROH_FINGER_I4,values = 5001)):
            response = self.client.read_from_register(address=ROH_FINGER_I4)
            self.assertNotEqual(response.registers[0],5001)
            logger.info(f'写入5001失败，有效值范围0~5000')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
    def test_read_finger_I5(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger I5')
        response = self.client.read_from_register(address=ROH_FINGER_I5)
        self.check_and_print_test_info(response)
            
    # 有效值范围0-5000    
    def test_write_finger_I5_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  I5： 0')
        if(self.client.write_to_register(address = ROH_FINGER_I5,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_I5)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_I5,values = FINGER_I5)
        
    def test_write_finger_I5_2000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  I5： 2000')
        if(self.client.write_to_register(address = ROH_FINGER_I5,values = 2000)):
            response = self.client.read_from_register(address=ROH_FINGER_I5)
            self.assertEqual(response.registers[0],2000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_I5,values = FINGER_I5)
            
    # 取值范围 5000   
    def test_write_finger_I5_5000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  I5： 5000')
        if(self.client.write_to_register(address = ROH_FINGER_I5,values = 5000)):
            response = self.client.read_from_register(address=ROH_FINGER_I5)
            self.assertEqual(response.registers[0],5000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_I5,values = FINGER_I5)
            
    def test_write_finger_I5_5001(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  I5： 5001')
        if(self.client.write_to_register(address = ROH_FINGER_I5,values = 5001)):
            response = self.client.read_from_register(address=ROH_FINGER_I5)
            self.assertNotEqual(response.registers[0],5001)
            logger.info(f'写入5001失败，有效值范围0~5000')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
    def test_read_finger_D0(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger D0')
        response = self.client.read_from_register(address=ROH_FINGER_D0)
        self.check_and_print_test_info(response)
            
    # # 有效值范围0-25000    
    def test_write_finger_D0_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  D0： 0')
        if(self.client.write_to_register(address = ROH_FINGER_D0,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_D0)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_D0,values = FINGER_D0)
        
    def test_write_finger_D0_12000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  D0： 12000')
        if(self.client.write_to_register(address = ROH_FINGER_D0,values = 12000)):
            response = self.client.read_from_register(address=ROH_FINGER_D0)
            self.assertEqual(response.registers[0],12000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_D0,values = FINGER_D0)
            
    def test_write_finger_D0_25000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  D0： 25000')
        if(self.client.write_to_register(address = ROH_FINGER_D0,values = 25000)):
            response = self.client.read_from_register(address=ROH_FINGER_D0)
            self.assertEqual(response.registers[0],25000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_D0,values = FINGER_D0)
            
    def test_write_finger_D0_25001(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  D0： 25001')
        if(self.client.write_to_register(address = ROH_FINGER_D0,values = 25001)):
            response = self.client.read_from_register(address=ROH_FINGER_D0)
            self.assertNotEqual(response.registers[0],25001)
            logger.info(f'写入25001失败，有效值范围0~25000')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
    def test_read_finger_D1(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger D1')
        response = self.client.read_from_register(address=ROH_FINGER_D1)
        self.check_and_print_test_info(response)
            
    # # 有效值范围0-25000    
    def test_write_finger_D1_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  D1： 0')
        if(self.client.write_to_register(address = ROH_FINGER_D1,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_D1)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_D1,values = FINGER_D1)
        
    def test_write_finger_D1_12000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  D1： 12000')
        if(self.client.write_to_register(address = ROH_FINGER_D1,values = 12000)):
            response = self.client.read_from_register(address=ROH_FINGER_D1)
            self.assertEqual(response.registers[0],12000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_D1,values = FINGER_D1)
            
    def test_write_finger_D1_25000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  D1： 25000')
        if(self.client.write_to_register(address = ROH_FINGER_D1,values = 25000)):
            response = self.client.read_from_register(address=ROH_FINGER_D1)
            self.assertEqual(response.registers[0],25000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_D1,values = FINGER_D1)
            
    def test_write_finger_D1_25001(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  D1： 25001')
        if(self.client.write_to_register(address = ROH_FINGER_D1,values = 25001)):
            response = self.client.read_from_register(address=ROH_FINGER_D1)
            self.assertNotEqual(response.registers[0],25001)
            logger.info(f'写入25001失败，有效值范围0~25000')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
    def test_read_finger_D2(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger D2')
        response = self.client.read_from_register(address=ROH_FINGER_D2)
        self.check_and_print_test_info(response)
            
    def test_write_finger_D2_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  D2： 0')
        if(self.client.write_to_register(address = ROH_FINGER_D2,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_D2)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_D2,values = FINGER_D2)
        
    def test_write_finger_D2_12000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  D2： 12000')
        if(self.client.write_to_register(address = ROH_FINGER_D2,values = 12000)):
            response = self.client.read_from_register(address=ROH_FINGER_D2)
            self.assertEqual(response.registers[0],12000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_D2,values = FINGER_D2)
            
    def test_write_finger_D2_25000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  D2： 25000')
        if(self.client.write_to_register(address = ROH_FINGER_D2,values = 25000)):
            response = self.client.read_from_register(address=ROH_FINGER_D2)
            self.assertEqual(response.registers[0],25000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_D2,values = FINGER_D2)
            
    def test_write_finger_D2_25001(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  D2： 25001')
        if(self.client.write_to_register(address = ROH_FINGER_D2,values = 25001)):
            response = self.client.read_from_register(address=ROH_FINGER_D2)
            self.assertNotEqual(response.registers[0],25001)
            logger.info(f'写入25001失败，有效值范围0~25000')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)

    def test_read_finger_D3(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger D3')
        response = self.client.read_from_register(address=ROH_FINGER_D3)
        self.check_and_print_test_info(response)
             
    def test_write_finger_D3_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  D3： 0')
        if(self.client.write_to_register(address = ROH_FINGER_D3,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_D3)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_D3,values = FINGER_D3)
        
    def test_write_finger_D3_12000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  D3： 12000')
        if(self.client.write_to_register(address = ROH_FINGER_D3,values = 12000)):
            response = self.client.read_from_register(address=ROH_FINGER_D3)
            self.assertEqual(response.registers[0],12000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_D3,values = FINGER_D3)
            
    def test_write_finger_D3_25000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  D3： 25000')
        if(self.client.write_to_register(address = ROH_FINGER_D3,values = 25000)):
            response = self.client.read_from_register(address=ROH_FINGER_D3)
            self.assertEqual(response.registers[0],25000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_D3,values = FINGER_D3)
            
    def test_write_finger_D3_25001(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  D3： 25001')
        if(self.client.write_to_register(address = ROH_FINGER_D3,values = 25001)):
            response = self.client.read_from_register(address=ROH_FINGER_D3)
            self.assertNotEqual(response.registers[0],25001)
            logger.info(f'写入25001失败，有效值范围0~25000')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
    def test_read_finger_D4(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger D4')
        response = self.client.read_from_register(address=ROH_FINGER_D4)
        self.check_and_print_test_info(response)
            
    def test_write_finger_D4_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  D4： 0')
        if(self.client.write_to_register(address = ROH_FINGER_D4,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_D4)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_D4,values = FINGER_D4)
        
    def test_write_finger_D4_12000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  D4： 12000')
        if(self.client.write_to_register(address = ROH_FINGER_D4,values = 12000)):
            response = self.client.read_from_register(address=ROH_FINGER_D4)
            self.assertEqual(response.registers[0],12000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_D4,values = FINGER_D4)
            
    def test_write_finger_D4_25000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  D4： 25000')
        if(self.client.write_to_register(address = ROH_FINGER_D4,values = 25000)):
            response = self.client.read_from_register(address=ROH_FINGER_D4)
            self.assertEqual(response.registers[0],25000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_D4,values = FINGER_D4)
            
    def test_write_finger_D4_25001(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  D4： 25001')
        if(self.client.write_to_register(address = ROH_FINGER_D4,values = 25001)):
            response = self.client.read_from_register(address=ROH_FINGER_D4)
            self.assertNotEqual(response.registers[0],25001)
            logger.info(f'写入25001失败，有效值范围0~25000')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
    def test_read_finger_D5(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger D5')
        response = self.client.read_from_register(ROH_FINGER_D5)
        self.check_and_print_test_info(response)
            
    def test_write_finger_D5_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  D5: 0')
        if(self.client.write_to_register(address = ROH_FINGER_D5,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_D5)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_D5,values = FINGER_D5)
        
    def test_write_finger_D5_12000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  D5: 12000')
        if(self.client.write_to_register(address = ROH_FINGER_D5,values = 12000)):
            response = self.client.read_from_register(address=ROH_FINGER_D5)
            self.assertEqual(response.registers[0],12000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_D5,values = FINGER_D5)
            
    def test_write_finger_D5_25000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  D5: 25000')
        if(self.client.write_to_register(address = ROH_FINGER_D5,values = 25000)):
            response = self.client.read_from_register(address=ROH_FINGER_D5)
            self.assertEqual(response.registers[0],25000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_D5,values = FINGER_D5)
            
    def test_write_finger_D5_25001(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  D5: 25001')
        if(self.client.write_to_register(address = ROH_FINGER_D5,values = 25001)):
            response = self.client.read_from_register(address=ROH_FINGER_D5)
            self.assertNotEqual(response.registers[0],25001)
            logger.info(f'写入25001失败，有效值范围0~25000')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)

    def test_read_finger_G0(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger G0')
        response = self.client.read_from_register(address=ROH_FINGER_G0)
        self.check_and_print_test_info(response)
    
    # 有效值范围20~100
    def test_write_finger_G0_20(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G0: 20')
        if(self.client.write_to_register(address = ROH_FINGER_G0,values = 20)):
            response = self.client.read_from_register(address=ROH_FINGER_G0)
            self.assertEqual(response.registers[0],20)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_G0,values = FINGER_G0)
        
    def test_write_finger_G0_60(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G0: 60')
        if(self.client.write_to_register(address = ROH_FINGER_G0,values = 60)):
            response = self.client.read_from_register(address=ROH_FINGER_G0)
            self.assertEqual(response.registers[0],60)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_G0,values = FINGER_G0)
            
    def test_write_finger_G0_100(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G0: 100')
        if(self.client.write_to_register(address = ROH_FINGER_G0,values = 100)):
            response = self.client.read_from_register(address=ROH_FINGER_G0)
            self.assertEqual(response.registers[0],100)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_G0,values = FINGER_G0)
            
    def test_write_finger_G0_19(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G0: 19')
        if(self.client.write_to_register(address = ROH_FINGER_G0,values = 19)):
            response = self.client.read_from_register(address=ROH_FINGER_G0)
            self.assertNotEqual(response.registers[0],19)
            logger.info(f'写入19失败，有效值范围20~100')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
    def test_write_finger_G0_101(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G0: 101')
        if(self.client.write_to_register(address = ROH_FINGER_G0,values = 101)):
            response = self.client.read_from_register(address=ROH_FINGER_G0)
            self.assertNotEqual(response.registers[0],101)
            logger.info(f'写入101失败，有效值范围20~100')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)

    def test_read_finger_G1(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger G1')
        response = self.client.read_from_register(address=ROH_FINGER_G1)
        self.check_and_print_test_info(response)
    
    # 有效值范围20~100
    def test_write_finger_G1_20(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G1: 20')
        if(self.client.write_to_register(address = ROH_FINGER_G1,values = 20)):
            response = self.client.read_from_register(address=ROH_FINGER_G1)
            self.assertEqual(response.registers[0],20)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_G1,values = FINGER_G1)
        
    def test_write_finger_G1_60(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G1: 60')
        if(self.client.write_to_register(address = ROH_FINGER_G1,values = 60)):
            response = self.client.read_from_register(address=ROH_FINGER_G1)
            self.assertEqual(response.registers[0],60)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_G1,values = FINGER_G1)
            
    def test_write_finger_G1_100(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G1: 100')
        if(self.client.write_to_register(address = ROH_FINGER_G1,values = 100)):
            response = self.client.read_from_register(address=ROH_FINGER_G1)
            self.assertEqual(response.registers[0],100)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_G1,values = FINGER_G1)
            
    def test_write_finger_G1_19(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G1: 19')
        if(self.client.write_to_register(address = ROH_FINGER_G1,values = 19)):
            response = self.client.read_from_register(address=ROH_FINGER_G1)
            self.assertNotEqual(response.registers[0],19)
            logger.info(f'写入19失败，有效值范围20~100')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
    def test_write_finger_G1_101(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G1: 101')
        if(self.client.write_to_register(address = ROH_FINGER_G1,values = 101)):
            response = self.client.read_from_register(address=ROH_FINGER_G1)
            self.assertNotEqual(response.registers[0],101)
            logger.info(f'写入101失败，有效值范围20~100')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)

    def test_read_finger_G2(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger G2')
        response = self.client.read_from_register(address=ROH_FINGER_G2)
        self.check_and_print_test_info(response)
    
    # 有效值范围20~100
    def test_write_finger_G2_20(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G2: 20')
        if(self.client.write_to_register(address = ROH_FINGER_G2,values = 20)):
            response = self.client.read_from_register(address=ROH_FINGER_G2)
            self.assertEqual(response.registers[0],20)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
          # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_G2,values = FINGER_G2)
        
        
    def test_write_finger_G2_60(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G2: 60')
        if(self.client.write_to_register(address = ROH_FINGER_G2,values = 60)):
            response = self.client.read_from_register(address=ROH_FINGER_G2)
            self.assertEqual(response.registers[0],60)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
          # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_G2,values = FINGER_G2)
            
    def test_write_finger_G2_100(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G2: 100')
        if(self.client.write_to_register(address = ROH_FINGER_G2,values = 100)):
            response = self.client.read_from_register(address=ROH_FINGER_G2)
            self.assertEqual(response.registers[0],100)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_G2,values = FINGER_G2)
            
    def test_write_finger_G2_19(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G2: 19')
        if(self.client.write_to_register(address = ROH_FINGER_G2,values = 19)):
            response = self.client.read_from_register(address=ROH_FINGER_G2)
            self.assertNotEqual(response.registers[0],19)
            logger.info(f'写入19失败，有效值范围20~100')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
    def test_write_finger_G2_101(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G2: 101')
        if(self.client.write_to_register(address = ROH_FINGER_G2,values = 101)):
            response = self.client.read_from_register(address=ROH_FINGER_G2)
            self.assertNotEqual(response.registers[0],101)
            logger.info(f'写入101失败，有效值范围20~100')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)

    def test_read_finger_G3(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger G3')
        response = self.client.read_from_register(address=ROH_FINGER_G3)
        self.check_and_print_test_info(response)
    
    # 有效值范围20~100
    def test_write_finger_G3_20(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G3: 20')
        if(self.client.write_to_register(address = ROH_FINGER_G3,values = 20)):
            response = self.client.read_from_register(address=ROH_FINGER_G3)
            self.assertEqual(response.registers[0],20)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_G3,values = FINGER_G3)
        
    def test_write_finger_G3_60(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G3: 60')
        if(self.client.write_to_register(address = ROH_FINGER_G3,values = 60)):
            response = self.client.read_from_register(address=ROH_FINGER_G3)
            self.assertEqual(response.registers[0],60)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_G3,values = FINGER_G3)
            
    def test_write_finger_G3_100(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G3: 100')
        if(self.client.write_to_register(address = ROH_FINGER_G3,values = 100)):
            response = self.client.read_from_register(address=ROH_FINGER_G3)
            self.assertEqual(response.registers[0],100)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_G3,values = FINGER_G3)
            
    def test_write_finger_G3_19(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G3: 19')
        if(self.client.write_to_register(address = ROH_FINGER_G3,values = 19)):
            response = self.client.read_from_register(address=ROH_FINGER_G3)
            self.assertNotEqual(response.registers[0],19)
            logger.info(f'写入19失败，有效值范围20~100')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
    def test_write_finger_G3_101(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G3: 101')
        if(self.client.write_to_register(address = ROH_FINGER_G3,values = 101)):
            response = self.client.read_from_register(address=ROH_FINGER_G3)
            self.assertNotEqual(response.registers[0],101)
            logger.info(f'写入101失败，有效值范围20~100')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)

    def test_read_finger_G4(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger G4')
        response = self.client.read_from_register(address=ROH_FINGER_G4)
        self.check_and_print_test_info(response)
    
    # 有效值范围20~100
    def test_write_finger_G4_20(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G4: 20')
        if(self.client.write_to_register(address = ROH_FINGER_G4,values = 20)):
            response = self.client.read_from_register(address=ROH_FINGER_G4)
            self.assertEqual(response.registers[0],20)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_G4,values = FINGER_G4)
        
    def test_write_finger_G4_60(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G4: 60')
        if(self.client.write_to_register(address = ROH_FINGER_G4,values = 60)):
            response = self.client.read_from_register(address=ROH_FINGER_G4)
            self.assertEqual(response.registers[0],60)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_G4,values = FINGER_G4)
            
    def test_write_finger_G4_100(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G4: 100')
        if(self.client.write_to_register(address = ROH_FINGER_G4,values = 100)):
            response = self.client.read_from_register(address=ROH_FINGER_G4)
            self.assertEqual(response.registers[0],100)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_G4,values = FINGER_G4)
            
    def test_write_finger_G4_19(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G4: 19')
        if(self.client.write_to_register(address = ROH_FINGER_G4,values = 19)):
            response = self.client.read_from_register(address=ROH_FINGER_G4)
            self.assertNotEqual(response.registers[0],19)
            logger.info(f'写入19失败，有效值范围20~100')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
    def test_write_finger_G4_101(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G4: 101')
        if(self.client.write_to_register(address = ROH_FINGER_G4,values = 101)):
            response = self.client.read_from_register(address=ROH_FINGER_G4)
            self.assertNotEqual(response.registers[0],101)
            logger.info(f'写入101失败，有效值范围20~100')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            

    def test_read_finger_G5(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger G5')
        response = self.client.read_from_register(ROH_FINGER_G5)
        self.check_and_print_test_info(response)
    
    # 有效值范围20~100
    def test_write_finger_G5_20(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G5: 20')
        if(self.client.write_to_register(address = ROH_FINGER_G5,values = 20)):
            response = self.client.read_from_register(address=ROH_FINGER_G5)
            self.assertEqual(response.registers[0],20)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_G5,values = FINGER_G5)
        
    def test_write_finger_G5_60(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G5: 60')
        if(self.client.write_to_register(address = ROH_FINGER_G5,values = 60)):
            response = self.client.read_from_register(address=ROH_FINGER_G5)
            self.assertEqual(response.registers[0],60)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_G5,values = FINGER_G5)
            
    def test_write_finger_G5_100(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G5: 100')
        if(self.client.write_to_register(address = ROH_FINGER_G5,values = 100)):
            response = self.client.read_from_register(address=ROH_FINGER_G5)
            self.assertEqual(response.registers[0],100)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_G5,values = FINGER_G5)
            
    def test_write_finger_G5_19(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G5: 19')
        if(self.client.write_to_register(address = ROH_FINGER_G5,values = 19)):
            response = self.client.read_from_register(address=ROH_FINGER_G5)
            self.assertNotEqual(response.registers[0],19)
            logger.info(f'写入19失败，有效值范围20~100')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
    def test_write_finger_G5_101(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger  G5: 101')
        if(self.client.write_to_register(address = ROH_FINGER_G5,values = 101)):
            response = self.client.read_from_register(address=ROH_FINGER_G5)
            self.assertNotEqual(response.registers[0],101)
            logger.info(f'写入101失败，有效值范围20~100')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
            

    def test_read_finger_status0(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger status0')
        response = self.client.read_from_register(address=ROH_FINGER_STATUS0)
        self.check_and_print_test_info(response)
        
    def test_read_finger_status1(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger status1')
        response = self.client.read_from_register(address=ROH_FINGER_STATUS1)
        self.check_and_print_test_info(response)

    def test_read_finger_status2(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger status2')
        response = self.client.read_from_register(address=ROH_FINGER_STATUS2)
        self.check_and_print_test_info(response)
            
    def test_read_finger_status3(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger status3')
        response = self.client.read_from_register(address=ROH_FINGER_STATUS3)
        self.check_and_print_test_info(response)

    def test_read_finger_status4(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger status4')
        response = self.client.read_from_register(address=ROH_FINGER_STATUS4)
        self.check_and_print_test_info(response)
            
    def test_read_finger_status5(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger status5')
        response = self.client.read_from_register(address=ROH_FINGER_STATUS5)
        self.check_and_print_test_info(response)

    def test_read_finger_current_limit0(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger current limit0')
        response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT0)
        self.check_and_print_test_info(response)
            
    #电流值范围0-1178，1178这个值暂时写不进去  
    def test_write_finger_current_limit0_0(self):
        
        self.print_test_info(status=self.TEST_STRAT,info='write finger current limit0: 0')
        if(self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT0,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT0)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT0,values = FINGER_CURRENT_LIMIT0)
        
    def test_write_finger_current_limit0_600(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger current limit0: 600')
        if(self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT0,values = 600)):
            response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT0)
            self.assertEqual(response.registers[0],600)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT0,values = FINGER_CURRENT_LIMIT0)
            
    @unittest.skip("ROH_FINGER_CURRENT_LIMIT0 1178值无法写入需要 研发修改") 
    def test_write_finger_current_limit0_1178(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger current limit0: 1178')
        if(self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT0,values = 1178)):
            response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT0)
            self.assertEqual(response.registers[0],1178)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT0,values = FINGER_CURRENT_LIMIT0)
        
            
    def test_write_finger_current_limit0_1179(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger current limit0: 1179')
        if(self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT0,values = 1179)):
            response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT0)
            self.assertNotEqual(response.registers[0],1179)
            logger.info(f'写入1179失败，有效值范围0~1178')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
    
    def test_read_finger_current_limit1(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger current limit1')
        response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT1)
        self.check_and_print_test_info(response)
            
    #电流值范围0-1178
    def test_write_finger_current_limit1_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger current limit1: 0')
        if(self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT1,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT1)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT1,values = FINGER_CURRENT_LIMIT1)
        
    def test_write_finger_current_limit1_600(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger current limit1: 600')
        if(self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT1,values = 600)):
            response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT1)
            self.assertEqual(response.registers[0],600)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT1,values = FINGER_CURRENT_LIMIT1)
        
    @unittest.skip('ROH_FINGER_CURRENT_LIMIT1 1178值无法写入需要 研发修改')      
    def test_write_finger_current_limit1_1178(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger current limit1: 1178')
        if(self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT1,values = 1178)):
            response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT1)
            self.assertEqual(response.registers[0],1178)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT1,values = FINGER_CURRENT_LIMIT1)
        
            
    def test_write_finger_current_limit1_1179(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger current limit1: 1179')
        if(self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT1,values = 1179)):
            response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT1)
            self.assertNotEqual(response.registers[0],1179)
            logger.info(f'写入1179失败，有效值范围0~1178')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
    def test_read_finger_current_limit2(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger current limit2')
        response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT2)
        self.check_and_print_test_info(response)
            
    #电流值范围0-1178
    def test_write_finger_current_limit2_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger current limit2: 0')
        if(self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT2,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT2)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT2,values = FINGER_CURRENT_LIMIT2)
        
    def test_write_finger_current_limit2_600(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger current limit2: 600')
        if(self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT2,values = 600)):
            response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT2)
            self.assertEqual(response.registers[0],600)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT2,values = FINGER_CURRENT_LIMIT2)
        
    @unittest.skip('ROH_FINGER_CURRENT_LIMIT2 1178值无法写入需要 研发修改')        
    def test_write_finger_current_limit2_1178(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger current limit2: 1178')
        if(self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT2,values = 1178)):
            response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT2)
            self.assertEqual(response.registers[0],1178)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT2,values = FINGER_CURRENT_LIMIT2)
        
            
    def test_write_finger_current_limit2_1179(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger current limit2: 1179')
        if(self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT2,values = 1179)):
            response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT2)
            self.assertNotEqual(response.registers[0],1179)
            logger.info(f'写入1179失败，有效值范围0~1178')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)

    def test_read_finger_current_limit3(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger current limit3')
        response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT3)
        self.check_and_print_test_info(response)
            
    #电流值范围0-1178
    def test_write_finger_current_limit3_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger current limit3: 0')
        if(self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT3,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT3)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT3,values = FINGER_CURRENT_LIMIT3)
        
    def test_write_finger_current_limit3_600(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger current limit3: 600')
        if(self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT3,values = 600)):
            response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT3)
            self.assertEqual(response.registers[0],600)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT3,values = FINGER_CURRENT_LIMIT3)
        
    @unittest.skip('ROH_FINGER_CURRENT_LIMIT3 1178值无法写入需要 研发修改')            
    def test_write_finger_current_limit3_1178(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger current limit3: 1178')
        if(self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT3,values = 1178)):
            response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT3)
            self.assertEqual(response.registers[0],1178)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT3,values = FINGER_CURRENT_LIMIT3)
        
            
    def test_write_finger_current_limit3_1179(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger current limit3: 1179')
        if(self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT3,values = 1179)):
            response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT3)
            self.assertNotEqual(response.registers[0],1179)
            logger.info(f'写入1179失败，有效值范围0~1178')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
    def test_read_finger_current_limit4(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger current limit4')
        response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT4)
        self.check_and_print_test_info(response)
            
    #电流值范围0-1178
    def test_write_finger_current_limit4_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger current limit4: 0')
        if(self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT4,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT4)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT4,values = FINGER_CURRENT_LIMIT4)
        
    def test_write_finger_current_limit4_600(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger current limit4: 600')
        if(self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT4,values = 600)):
            response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT4)
            self.assertEqual(response.registers[0],600)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT4,values = FINGER_CURRENT_LIMIT4)
        
    @unittest.skip('ROH_FINGER_CURRENT_LIMIT4 1178值无法写入需要 研发修改')    
    def test_write_finger_current_limit4_1178(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger current limit4: 1178')
        if(self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT4,values = 1178)):
            response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT4)
            self.assertEqual(response.registers[0],1178)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT4,values = FINGER_CURRENT_LIMIT4)
            
    def test_write_finger_current_limit4_1179(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger current limit4: 1179')
        if(self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT4,values = 1179)):
            response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT4)
            self.assertNotEqual(response.registers[0],1179)
            logger.info(f'写入1179失败，有效值范围0~1178')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)

    def test_read_finger_current_limit5(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger current limit5')
        response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT5)
        self.check_and_print_test_info(response)
            
    #电流值范围0-1178
    def test_write_finger_current_limit5_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger current limit5: 0')
        if(self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT5,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT5)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
          # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT5,values = FINGER_CURRENT_LIMIT5)
        
    def test_write_finger_current_limit5_600(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger current limit5: 600')
        if(self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT5,values = 600)):
            response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT5)
            self.assertEqual(response.registers[0],600)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
          # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT5,values = FINGER_CURRENT_LIMIT5)
    
    @unittest.skip('ROH_FINGER_CURRENT_LIMIT5 1178值无法写入需要 研发修改')
    def test_write_finger_current_limit5_1178(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger current limit5: 1178')
        if(self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT5,valuew = 1178)):
            response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT5)
            self.assertEqual(response.registers[0],1178)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT5,values = FINGER_CURRENT_LIMIT5)
        
            
    def test_write_finger_current_limit5_1179(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger current limit5: 1179')
        if(self.client.write_to_register(address = ROH_FINGER_CURRENT_LIMIT5,values = 1179)):
            response = self.client.read_from_register(address=ROH_FINGER_CURRENT_LIMIT5)
            self.assertNotEqual(response.registers[0],1179)
            logger.info(f'写入1179失败，有效值范围0~1178')
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)

    def test_read_finger_current0(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger current0')
        response = self.client.read_from_register(address=ROH_FINGER_CURRENT0)
        self.check_and_print_test_info(response)
            
    def test_read_finger_current1(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger current1')
        response = self.client.read_from_register(address=ROH_FINGER_CURRENT1)
        self.check_and_print_test_info(response)
            
    def test_read_finger_current2(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger current2')
        response = self.client.read_from_register(address=ROH_FINGER_CURRENT2)
        self.check_and_print_test_info(response)
            
    def test_read_finger_current3(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger current3')
        response = self.client.read_from_register(address=ROH_FINGER_CURRENT3)
        self.check_and_print_test_info(response)
        
            
    def test_read_finger_current4(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger current4')
        response = self.client.read_from_register(address=ROH_FINGER_CURRENT4)
        self.check_and_print_test_info(response)
            
    def test_read_finger_current5(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger current5')
        response = self.client.read_from_register(address=ROH_FINGER_CURRENT5)
        self.check_and_print_test_info(response)  
            

    def test_read_finger_force_limit0(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger force limit0')
        response = self.client.read_from_register(address=ROH_FINGER_FORCE_LIMIT0)
        self.check_and_print_test_info(response)
            
    #力范围 0-15000  
    def test_write_finger_force_limit0_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger force limit0: 0')
        if(self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT0,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_FORCE_LIMIT0)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT0,values = FINGER_FORCE_LIMIT0)
        
    def test_write_finger_force_limit0_7000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger force limit0: 7000')
        if(self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT0,values = 7000)):
            response = self.client.read_from_register(address=ROH_FINGER_FORCE_LIMIT0)
            self.assertEqual(response.registers[0],7000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT0,values = FINGER_FORCE_LIMIT0)
            
    def test_write_finger_force_limit0_15000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger force limit0: 15000')
        if(self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT0,values = 15000)):
            response = self.client.read_from_register(address=ROH_FINGER_FORCE_LIMIT0)
            self.assertEqual(response.registers[0],15000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT0,values = FINGER_FORCE_LIMIT0)
        
    @unittest.skip('ROH_FINGER_FORCE_LIMIT0 力传感器功能暂时没添加，对值范围没做限制')
    def test_write_finger_force_limit0_15001(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger force limit0: 15001')
        if(self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT0,values = 15001)):
            response = self.client.read_from_register(address=ROH_FINGER_FORCE_LIMIT0)
            self.assertNotEqual(response.registers[0],15001)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # # 恢复默认值,后续要注释掉，只给调试使用
        # self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT0,values = FINGER_FORCE_LIMIT0)

    def test_read_finger_force_limit1(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger force limit1')
        response = self.client.read_from_register(address=ROH_FINGER_FORCE_LIMIT1)
        self.check_and_print_test_info(response)
            
    #力范围 0-15000  
    def test_write_finger_force_limit1_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger force limit1: 0')
        if(self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT1,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_FORCE_LIMIT1)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT1,values = FINGER_FORCE_LIMIT1)
        
    def test_write_finger_force_limit1_7000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger force limit1: 7000')
        if(self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT1,values = 7000)):
            response = self.client.read_from_register(address=ROH_FINGER_FORCE_LIMIT1)
            self.assertEqual(response.registers[0],7000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT1,values = FINGER_FORCE_LIMIT1)
            
    def test_write_finger_force_limit1_15000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger force limit1: 15000')
        if(self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT1,values = 15000)):
            response = self.client.read_from_register(address=ROH_FINGER_FORCE_LIMIT1)
            self.assertEqual(response.registers[0],15000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT1,values = FINGER_FORCE_LIMIT1)
        
    @unittest.skip('ROH_FINGER_FORCE_LIMIT1 力传感器功能暂时没添加，对值范围没做限制')
    def test_write_finger_force_limit1_15001(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger force limit1: 15001')
        if(self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT1,value = 15001)):
            response = self.client.read_from_register(ROH_FINGER_FORCE_LIMIT1,1)
            self.assertNotEqual(response.registers[0],15001)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # # 恢复默认值，后续要注释掉，当前调试使用
        # self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT1,value = FINGER_FORCE_LIMIT1)

    def test_read_finger_force_limit2(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger force limit2')
        response = self.client.read_from_register(address=ROH_FINGER_FORCE_LIMIT2)
        self.check_and_print_test_info(response)
            
    #力范围 0-15000  
    def test_write_finger_force_limit2_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger force limit2: 0')
        if(self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT2,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_FORCE_LIMIT2)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT2,values = FINGER_FORCE_LIMIT2)
        
    def test_write_finger_force_limit2_7000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger force limit2: 7000')
        if(self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT2,values = 7000)):
            response = self.client.read_from_register(address=ROH_FINGER_FORCE_LIMIT2)
            self.assertEqual(response.registers[0],7000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT2,values = FINGER_FORCE_LIMIT2)
            
    def test_write_finger_force_limit2_15000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger force limit2: 15000')
        if(self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT2,values = 15000)):
            response = self.client.read_from_register(address=ROH_FINGER_FORCE_LIMIT2)
            self.assertEqual(response.registers[0],15000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT2,values = FINGER_FORCE_LIMIT2)
        
    @unittest.skip('ROH_FINGER_FORCE_LIMIT2 力传感器功能暂时没添加，对值范围没做限制')
    def test_write_finger_force_limit2_15001(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger force limit2: 15001')
        if(self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT2,values = 15001)):
            response = self.client.read_from_register(address=ROH_FINGER_FORCE_LIMIT2)
            self.assertNotEqual(response.registers[0],15001)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值，后续要注释掉，当前为调试使用
        self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT2,values = FINGER_FORCE_LIMIT2)
            
    def test_read_finger_force_limit3(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger force limit3')
        response = self.client.read_from_register(address=ROH_FINGER_FORCE_LIMIT3)
        self.check_and_print_test_info(response)
            
    #力范围 0-15000  
    def test_write_finger_force_limit3_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger force limit3: 0')
        if(self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT3,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_FORCE_LIMIT3)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT3,values = FINGER_FORCE_LIMIT3)
        
    def test_write_finger_force_limit3_7000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger force limit3: 7000')
        if(self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT3,values = 7000)):
            response = self.client.read_from_register(address=ROH_FINGER_FORCE_LIMIT3)
            self.assertEqual(response.registers[0],7000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT3,values = FINGER_FORCE_LIMIT3)
            
    def test_write_finger_force_limit3_15000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger force limit3: 15000')
        if(self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT3,values = 15000)):
            response = self.client.read_from_register(address=ROH_FINGER_FORCE_LIMIT3)
            self.assertEqual(response.registers[0],15000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT3,values = FINGER_FORCE_LIMIT3)
        
    @unittest.skip('ROH_FINGER_FORCE_LIMIT3 力传感器功能暂时没添加，对值范围没做限制')     
    def test_write_finger_force_limit3_15001(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger force limit3: 15001')
        if(self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT3,values = 15001)):
            response = self.client.read_from_register(address=ROH_FINGER_FORCE_LIMIT3)
            self.assertNotEqual(response.registers[0],15001)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值，后续要注释掉，当前为调试使用
        self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT3,values = FINGER_FORCE_LIMIT3)

    def test_read_finger_force_limit4(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger force limit4')
        response = self.client.read_from_register(address=ROH_FINGER_FORCE_LIMIT4)
        self.check_and_print_test_info(response)
     
    #力范围 0-15000  
    def test_write_finger_force_limit4_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger force limit4: 0')
        if(self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT4,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_FORCE_LIMIT4)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT4,values = FINGER_FORCE_LIMIT4)
        
    def test_write_finger_force_limit4_7000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger force limit4: 7000')
        if(self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT4,values = 7000)):
            response = self.client.read_from_register(address=ROH_FINGER_FORCE_LIMIT4)
            self.assertEqual(response.registers[0],7000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT4,values = FINGER_FORCE_LIMIT4)
            
    def test_write_finger_force_limit4_15000(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger force limit4: 15000')
        if(self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT4,values = 15000)):
            response = self.client.read_from_register(address=ROH_FINGER_FORCE_LIMIT4)
            self.assertEqual(response.registers[0],15000)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT4,values = FINGER_FORCE_LIMIT4)
            
        
    @unittest.skip('ROH_FINGER_FORCE_LIMIT4 力传感器功能暂时没添加，对值范围没做限制')   
    def test_write_finger_force_limit4_15001(self):
    
        self.print_test_info(status=self.TEST_STRAT,info='write finger force limit4: 15001')
        
        if(self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT4,values = 15001)):
            response = self.client.read_from_register(address=ROH_FINGER_FORCE_LIMIT4)
            self.assertNotEqual(response.registers[0],15001)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值，后续需要注释掉，当前为调试使用
        self.client.write_to_register(address = ROH_FINGER_FORCE_LIMIT4,values = FINGER_FORCE_LIMIT4)

    def test_read_finger_force0(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger force0')
        response = self.client.read_from_register(address=ROH_FINGER_FORCE0)
        self.check_and_print_test_info(response)
        
    def test_read_finger_force1(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger force1')
        response = self.client.read_from_register(address=ROH_FINGER_FORCE1)
        self.check_and_print_test_info(response)
            
    def test_read_finger_force2(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger force2')
        response = self.client.read_from_register(address=ROH_FINGER_FORCE2)
        self.check_and_print_test_info(response)

    def test_read_finger_force3(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger force3')
        response = self.client.read_from_register(address=ROH_FINGER_FORCE3)
        self.check_and_print_test_info(response)
            
    def test_read_finger_force4(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger force4')
        response = self.client.read_from_register(address=ROH_FINGER_FORCE4)
        self.check_and_print_test_info(response)
            
    def test_read_finger_speed0(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger speed0')
        response = self.client.read_from_register(address=ROH_FINGER_SPEED0)
        self.check_and_print_test_info(response)
            
    #速度范围 0-65535  
    def test_write_finger_speed0_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger speed0: 0')
        if(self.client.write_to_register(address = ROH_FINGER_SPEED0,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_SPEED0)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
        
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_SPEED0,values = FINGER_SPEED0)
        
    def test_write_finger_speed0_32767(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger speed0: 32767')
        if(self.client.write_to_register(address = ROH_FINGER_SPEED0,values = 32767)):
            response = self.client.read_from_register(address=ROH_FINGER_SPEED0)
            self.assertEqual(response.registers[0],32767)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
        
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_SPEED0,values = FINGER_SPEED0)
            
        
    def test_write_finger_speed0_65535(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger speed0: 65535')
        if(self.client.write_to_register(address = ROH_FINGER_SPEED0,values = 65535)):
            response = self.client.read_from_register(address=ROH_FINGER_SPEED0)
            self.assertEqual(response.registers[0],65535)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_SPEED0,values = FINGER_SPEED0)
            
    def test_read_finger_speed1(self):

        self.print_test_info(status=self.TEST_STRAT,info='read finger speed1')
        response = self.client.read_from_register(address=ROH_FINGER_SPEED1)
        self.check_and_print_test_info(response)
            
    #速度范围 0-65535  
    def test_write_finger_speed1_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger speed1: 0')
        if(self.client.write_to_register(address = ROH_FINGER_SPEED1,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_SPEED1)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_SPEED1,values = FINGER_SPEED1)
        
    def test_write_finger_speed1_32767(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger speed1: 32767')
        if(self.client.write_to_register(address = ROH_FINGER_SPEED1,values = 32767)):
            response = self.client.read_from_register(address=ROH_FINGER_SPEED1)
            self.assertEqual(response.registers[0],32767)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_SPEED1,values = FINGER_SPEED1)
            
    
    def test_write_finger_speed1_65535(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger speed1: 65535')
        if(self.client.write_to_register(address = ROH_FINGER_SPEED1,values = 65535)):
            response = self.client.read_from_register(address=ROH_FINGER_SPEED1)
            self.assertEqual(response.registers[0],65535)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_SPEED1,values = FINGER_SPEED1)

    def test_read_finger_speed2(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger speed2')
        response = self.client.read_from_register(address=ROH_FINGER_SPEED2)
        self.check_and_print_test_info(response)
            
    #速度范围 0-65535  
    def test_write_finger_speed2_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger speed2: 0')
        if(self.client.write_to_register(address = ROH_FINGER_SPEED2,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_SPEED2)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_SPEED2,values = FINGER_SPEED2)
        
    def test_write_finger_speed2_32767(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger speed2: 32767')
        if(self.client.write_to_register(address = ROH_FINGER_SPEED2,values = 32767)):
            response = self.client.read_from_register(address=ROH_FINGER_SPEED2)
            self.assertEqual(response.registers[0],32767)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_SPEED2,values = FINGER_SPEED2)
            
    def test_write_finger_speed2_65535(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger speed2: 65535')
        if(self.client.write_to_register(address = ROH_FINGER_SPEED2,values = 65535)):
            response = self.client.read_from_register(address=ROH_FINGER_SPEED2)
            self.assertEqual(response.registers[0],65535)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_SPEED2,values = FINGER_SPEED2)

    def test_read_finger_speed3(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger speed3')
        response = self.client.read_from_register(address=ROH_FINGER_SPEED3)
        self.check_and_print_test_info(response)
            
    #速度范围 0-65535  
    def test_write_finger_speed3_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger speed3: 0')
        if(self.client.write_to_register(address = ROH_FINGER_SPEED3,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_SPEED3)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_SPEED3,values = FINGER_SPEED3)
            
    def test_write_finger_speed3_32767(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger speed3: 32767')
        if(self.client.write_to_register(address = ROH_FINGER_SPEED3,values = 32767)):
            response = self.client.read_from_register(address=ROH_FINGER_SPEED3)
            self.assertEqual(response.registers[0],32767)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_SPEED3,values = FINGER_SPEED3)
        
    def test_write_finger_speed3_65535(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger speed3: 65535')
        if(self.client.write_to_register(address = ROH_FINGER_SPEED3,values = 65535)):
            response = self.client.read_from_register(address=ROH_FINGER_SPEED3)
            self.assertEqual(response.registers[0],65535)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_SPEED3,values = FINGER_SPEED3)
            
    def test_read_finger_speed4(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger speed4')
        response = self.client.read_from_register(address=ROH_FINGER_SPEED4)
        self.check_and_print_test_info(response)
            
    #速度范围 0-65535  
    def test_write_finger_speed4_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger speed4: 0')
        if(self.client.write_to_register(address = ROH_FINGER_SPEED4,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_SPEED4)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_SPEED4,values = FINGER_SPEED4)
            
    def test_write_finger_speed4_32767(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger speed4: 32767')
        if(self.client.write_to_register(address = ROH_FINGER_SPEED4,values = 32767)):
            response = self.client.read_from_register(address=ROH_FINGER_SPEED4)
            self.assertEqual(response.registers[0],32767)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_SPEED4,values = FINGER_SPEED4)
        
    def test_write_finger_speed4_65535(self):
    
        self.print_test_info(status=self.TEST_STRAT,info='write finger speed4: 65535')
        if(self.client.write_to_register(address = ROH_FINGER_SPEED4,values = 65535)):
            response = self.client.read_from_register(address=ROH_FINGER_SPEED4)
            self.assertEqual(response.registers[0],65535)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_SPEED4,values = FINGER_SPEED4)
            
    def test_read_finger_speed5(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger speed5')
        response = self.client.read_from_register(address=ROH_FINGER_SPEED5)
        self.check_and_print_test_info(response)
            
    #速度范围 0-65535  
    def test_write_finger_speed5_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger speed5: 0')
        if(self.client.write_to_register(address = ROH_FINGER_SPEED5,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_SPEED5)
            self.assertEqual(response.registers[0],0)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_SPEED5,values = FINGER_SPEED5)
            
    def test_write_finger_speed5_32767(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger speed5: 32767')
        if(self.client.write_to_register(address = ROH_FINGER_SPEED5,values = 32767)):
            response = self.client.read_from_register(address=ROH_FINGER_SPEED5)
            self.assertEqual(response.registers[0],32767)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_SPEED5,values = FINGER_SPEED5)
          
    def test_write_finger_speed5_65535(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger speed5: 65535')
        if(self.client.write_to_register(address = ROH_FINGER_SPEED5,values = 65535)):
            response = self.client.read_from_register(address=ROH_FINGER_SPEED5)
            self.assertEqual(response.registers[0],65535)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
        
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_SPEED5,values = FINGER_SPEED5)

    def test_read_finger_pos_target0(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger pos target0')
        response = self.client.read_from_register(address=ROH_FINGER_POS_TARGET0)
        self.check_and_print_test_info(response)
            
    #弯曲逻辑范围 0-65535  
    def test_write_finger_pos_target0_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger pos target0: 0')
        if(self.client.write_to_register(address = ROH_FINGER_POS_TARGET0,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_POS_TARGET0)
            self.assertLessEqual(abs(response.registers[0]-0),FINGER_POS_TARGET_MAX_LOSS)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_POS_TARGET0,values = FINGER_POS_TARGET0)
        
    def test_write_finger_pos_target0_32767(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger pos target0: 32767')
        if(self.client.write_to_register(address = ROH_FINGER_POS_TARGET0,values = 32767)):
            response = self.client.read_from_register(address=ROH_FINGER_POS_TARGET0)
            self.assertLessEqual(abs(response.registers[0]-32767),FINGER_POS_TARGET_MAX_LOSS)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_POS_TARGET0,values = FINGER_POS_TARGET0)
            
    def test_write_finger_pos_target0_65535(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger pos target0: 65535')
        if(self.client.write_to_register(address = ROH_FINGER_POS_TARGET0,values = 65535)):
            response = self.client.read_from_register(address=ROH_FINGER_POS_TARGET0)
            self.assertLessEqual(abs(response.registers[0]-65535),FINGER_POS_TARGET_MAX_LOSS)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_POS_TARGET0,values = FINGER_POS_TARGET0)
    
    def test_read_finger_pos_target1(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger pos target1')
        response = self.client.read_from_register(address=ROH_FINGER_POS_TARGET1)
        self.check_and_print_test_info(response)
            
    #弯曲逻辑范围 0-65535  
    def test_write_finger_pos_target1_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger pos target1: 0')
        if(self.client.write_to_register(address = ROH_FINGER_POS_TARGET1,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_POS_TARGET1)
            self.assertLessEqual(abs(response.registers[0]-0),FINGER_POS_TARGET_MAX_LOSS)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_POS_TARGET1,values = FINGER_POS_TARGET1)
        
    def test_write_finger_pos_target1_32767(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger pos target1: 32767')
        if(self.client.write_to_register(address = ROH_FINGER_POS_TARGET1,values = 32767)):
            response = self.client.read_from_register(address=ROH_FINGER_POS_TARGET1)
            self.assertLessEqual(abs(response.registers[0]-32767),FINGER_POS_TARGET_MAX_LOSS)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_POS_TARGET1,values = FINGER_POS_TARGET1)
            
    def test_write_finger_pos_target1_65535(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger pos target1: 65535')
        if(self.client.write_to_register(address = ROH_FINGER_POS_TARGET1,values = 65535)):
            response = self.client.read_from_register(address=ROH_FINGER_POS_TARGET1)
            self.assertLessEqual(abs(response.registers[0]-65535),FINGER_POS_TARGET_MAX_LOSS)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_POS_TARGET1,values = FINGER_POS_TARGET1)

    def test_read_finger_pos_target2(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger pos target2')
        response = self.client.read_from_register(ROH_FINGER_POS_TARGET2)
        self.check_and_print_test_info(response)
            
   #弯曲逻辑范围 0-65535  
    def test_write_finger_pos_target2_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger pos target2: 0')
        if(self.client.write_to_register(address = ROH_FINGER_POS_TARGET2,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_POS_TARGET2)
            self.assertLessEqual(abs(response.registers[0]-0),FINGER_POS_TARGET_MAX_LOSS)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_POS_TARGET2,values = FINGER_POS_TARGET2)
        
    def test_write_finger_pos_target2_32767(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger pos target2: 32767')
        if(self.client.write_to_register(address = ROH_FINGER_POS_TARGET2,values = 32767)):
            response = self.client.read_from_register(address=ROH_FINGER_POS_TARGET2)
            self.assertLessEqual(abs(response.registers[0]-32767),FINGER_POS_TARGET_MAX_LOSS)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_POS_TARGET2,values = FINGER_POS_TARGET2)
            
    def test_write_finger_pos_target2_65535(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger pos target2: 65535')
        if(self.client.write_to_register(address = ROH_FINGER_POS_TARGET2,values = 65535)):
            response = self.client.read_from_register(address=ROH_FINGER_POS_TARGET2)
            self.assertLessEqual(abs(response.registers[0]-65535),FINGER_POS_TARGET_MAX_LOSS)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_POS_TARGET2,values = FINGER_POS_TARGET2)

    def test_read_finger_pos_target3(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger pos target3')
        response = self.client.read_from_register(address=ROH_FINGER_POS_TARGET3)
        self.check_and_print_test_info(response)
        
    #弯曲逻辑范围 0-65535  
    def test_write_finger_pos_target3_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger pos target3: 0')
        if(self.client.write_to_register(address = ROH_FINGER_POS_TARGET3,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_POS_TARGET3)
            self.assertLessEqual(abs(response.registers[0]-0),FINGER_POS_TARGET_MAX_LOSS)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_POS_TARGET3,values = FINGER_POS_TARGET3)
        
    def test_write_finger_pos_target3_32767(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger pos target3: 32767')
        if(self.client.write_to_register(address = ROH_FINGER_POS_TARGET3,values = 32767)):
            response = self.client.read_from_register(address=ROH_FINGER_POS_TARGET3)
            self.assertLessEqual(abs(response.registers[0]-32767),FINGER_POS_TARGET_MAX_LOSS)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_POS_TARGET3,values = FINGER_POS_TARGET3)
            
    def test_write_finger_pos_target3_65535(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger pos target3: 65535')
        if(self.client.write_to_register(address = ROH_FINGER_POS_TARGET3,values = 65535)):
            response = self.client.read_from_register(address=ROH_FINGER_POS_TARGET3)
            self.assertLessEqual(abs(response.registers[0]-65535),FINGER_POS_TARGET_MAX_LOSS)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_POS_TARGET3,values = FINGER_POS_TARGET3)

    def test_read_finger_pos_target4(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger pos target4')
        response = self.client.read_from_register(address=ROH_FINGER_POS_TARGET4)
        self.check_and_print_test_info(response)
            
    #弯曲逻辑范围 0-65535  
    def test_write_finger_pos_target4_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger pos target4: 0')
        if(self.client.write_to_register(address = ROH_FINGER_POS_TARGET4,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_POS_TARGET4)
            self.assertLessEqual(abs(response.registers[0]-0),FINGER_POS_TARGET_MAX_LOSS)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_POS_TARGET4,values = FINGER_POS_TARGET4)
        
    def test_write_finger_pos_target4_32767(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger pos target4: 32767')
        if(self.client.write_to_register(address = ROH_FINGER_POS_TARGET4,values = 32767)):
            response = self.client.read_from_register(address=ROH_FINGER_POS_TARGET4)
            self.assertLessEqual(abs(response.registers[0]-32767),FINGER_POS_TARGET_MAX_LOSS)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_POS_TARGET4,values = FINGER_POS_TARGET4)
            
    def test_write_finger_pos_target4_65535(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger pos target4: 65535')
        if(self.client.write_to_register(address = ROH_FINGER_POS_TARGET4,values = 65535)):
            response = self.client.read_from_register(address=ROH_FINGER_POS_TARGET4)
            self.assertLessEqual(abs(response.registers[0]-65535),FINGER_POS_TARGET_MAX_LOSS)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_POS_TARGET4,values = FINGER_POS_TARGET4)

    def test_read_finger_pos_target5(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger pos target5')
        response = self.client.read_from_register(address=ROH_FINGER_POS_TARGET5)
        self.check_and_print_test_info(response)
            
    #弯曲逻辑范围 0-65535  
    def test_write_finger_pos_target5_0(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger pos target4: 0')
        if(self.client.write_to_register(address = ROH_FINGER_POS_TARGET5,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_POS_TARGET5)
            self.assertLessEqual(abs(response.registers[0]-0),FINGER_POS_TARGET_MAX_LOSS)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_POS_TARGET5,values = FINGER_POS_TARGET5)
        
    def test_write_finger_pos_target5_32767(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger pos target5: 32767')
        if(self.client.write_to_register(address = ROH_FINGER_POS_TARGET5,values = 32767)):
            response = self.client.read_from_register(address=ROH_FINGER_POS_TARGET5)
            self.assertLessEqual(abs(response.registers[0]-32767),FINGER_POS_TARGET_MAX_LOSS)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_POS_TARGET5,values = FINGER_POS_TARGET5)
            
    def test_write_finger_pos_target5_65535(self):
        self.print_test_info(status=self.TEST_STRAT,info='write finger pos target5: 65535')
        if(self.client.write_to_register(address = ROH_FINGER_POS_TARGET5,values = 65535)):
            response = self.client.read_from_register(address=ROH_FINGER_POS_TARGET5)
            self.assertLessEqual(abs(response.registers[0]-65535),FINGER_POS_TARGET_MAX_LOSS)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_POS_TARGET5,values = FINGER_POS_TARGET5)

    def test_read_finger_pos0(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger pos0')
        response = self.client.read_from_register(address=ROH_FINGER_POS0)
        self.check_and_print_test_info(response)
       
    def test_read_finger_pos1(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger pos1')
        response = self.client.read_from_register(address=ROH_FINGER_POS1)
        self.check_and_print_test_info(response)
        
    def test_read_finger_pos2(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger pos2')
        response = self.client.read_from_register(address=ROH_FINGER_POS2)
        self.check_and_print_test_info(response)
            
    def test_read_finger_pos3(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger pos3')
        response = self.client.read_from_register(address=ROH_FINGER_POS3)
        self.check_and_print_test_info(response)
            
    def test_read_finger_pos4(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger pos4')
        response = self.client.read_from_register(address=ROH_FINGER_POS4)
        self.check_and_print_test_info(response)
            
    def test_read_finger_pos5(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger pos5')
        response = self.client.read_from_register(address=ROH_FINGER_POS5)
        self.check_and_print_test_info(response)

    def get_min_angle(self,addr):
        if(self.client.write_to_register(address = addr,values = 0)):
            response = self.client.read_from_register(address=addr)
            logger.info(f'get min angle : {addr} ->{response.registers[0]}')
            return response.registers[0]
        else:
            logger.info(f'get min angle : {addr} 尝试获取最小值失败')
            return 0
        
    def get_max_angle(self,addr):
        if(self.client.write_to_register(address = addr,values = 32767)):
            response = self.client.read_from_register(address=addr)
            logger.info(f'get max angle : {addr} ->{response.registers[0]}')
            return response.registers[0]
        else:
            logger.info(f'get max angle : {addr} 尝试获取最大值失败')
            return 32767
        
    def test_read_finger_angle_target0(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger angle target0')
        response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET0)
        self.check_and_print_test_info(response)
        
    #角度范围 ，假设angle极大值为min，极小值为max，测试几个点min、max、小于min、大于max并且不大于32767、大于max并且大于32767
    def test_write_finger_angle_target0_min(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target0: min angle')
        MIN_ANGLE = self.get_min_angle(ROH_FINGER_ANGLE_TARGET0)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET0,values = MIN_ANGLE)):
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET0)
            self.assertLessEqual(abs(response.registers[0]-MIN_ANGLE),FINGER_ANGLE_TARGET_MAX_LOSS)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET0,values = FINGER_ANGLE_TARGET0)
            
    def test_write_finger_angle_target0_smin(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target0: smaller than min angle')
        MIN_ANGLE = self.get_min_angle(ROH_FINGER_ANGLE_TARGET0)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET0,values = 0)):
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET0)
            self.assertEqual(response.registers[0],MIN_ANGLE) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET0,values = FINGER_ANGLE_TARGET0)
        
    def test_write_finger_angle_target0_normal(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target0: normal angle')
        
        MIN_ANGLE = self.get_min_angle(ROH_FINGER_ANGLE_TARGET0)
        MAX_ANGLE = self.get_max_angle(ROH_FINGER_ANGLE_TARGET0)
        NORMAL_ANGLE= int(MIN_ANGLE + (MAX_ANGLE - MIN_ANGLE)/2)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET0,values = NORMAL_ANGLE)):
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET0)
            self.assertLessEqual(abs(response.registers[0]-NORMAL_ANGLE),FINGER_ANGLE_TARGET_MAX_LOSS) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET0,values = FINGER_ANGLE_TARGET0)
            
    def test_write_finger_angle_target0_max(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target0: max angle')
        MAX_ANGLE = self.get_max_angle(ROH_FINGER_ANGLE_TARGET0)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET0,values = MAX_ANGLE)):
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET0)
            self.assertLessEqual(abs(response.registers[0]-MAX_ANGLE),FINGER_ANGLE_TARGET_MAX_LOSS) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET0,values = FINGER_ANGLE_TARGET0)
            
    def test_write_finger_angle_target0_bmax1(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target0: bigger than max angle（不大于32767）')
        MAX_ANGLE = self.get_max_angle(ROH_FINGER_ANGLE_TARGET0)

        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET0,values = 32767)):# 超过极大值，并且不超过32767，都返回最大值
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET0)
            self.assertEqual(response.registers[0],MAX_ANGLE) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET0,values = FINGER_ANGLE_TARGET0)
    
    def test_write_finger_angle_target0_bmax2(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target0: bigger than max angle（大于32767）')
        MIN_ANGLE = self.get_min_angle(ROH_FINGER_ANGLE_TARGET0)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET0,values = 36768)):# 超过极大值，并且超过32767，相当于取最小值
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET0)
            self.assertEqual(response.registers[0],MIN_ANGLE) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)    
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET0,values = FINGER_ANGLE_TARGET0)
    

    def test_read_finger_angle_target1(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger angle target1')
        response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET1)
        self.check_and_print_test_info(response)
        
    #角度范围 ，假设angle极大值为min，极小值为max，测试几个点min、max、小于min、大于max并且不大于32767、大于max并且大于32767
    def test_write_finger_angle_target1_min(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target1: min angle')
        MIN_ANGLE = self.get_min_angle(ROH_FINGER_ANGLE_TARGET1)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET1,values = MIN_ANGLE)):
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET1)
            self.assertLessEqual(abs(response.registers[0]-MIN_ANGLE),FINGER_ANGLE_TARGET_MAX_LOSS) # 精度误差，暂定两次的值误差不超过1算是同一个数
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET1,values = FINGER_ANGLE_TARGET1)
            
    def test_write_finger_angle_target1_smin(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target1: smaller than min angle')
        MIN_ANGLE = self.get_min_angle(ROH_FINGER_ANGLE_TARGET1)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET1,values = 0)): # 边界值有波动，直接取最小值
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET1)
            self.assertEqual(response.registers[0],MIN_ANGLE) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET1,values = FINGER_ANGLE_TARGET1)
        
    def test_write_finger_angle_target1_normal(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target1: normal angle')
        
        MIN_ANGLE = self.get_min_angle(ROH_FINGER_ANGLE_TARGET1)
        MAX_ANGLE = self.get_max_angle(ROH_FINGER_ANGLE_TARGET1)
        NORMAL_ANGLE= int(MIN_ANGLE + (MAX_ANGLE - MIN_ANGLE)/2)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET1,values = NORMAL_ANGLE)): # 从极小值和极大值之间取个值
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET1)
            self.assertLessEqual(abs(response.registers[0]-NORMAL_ANGLE),FINGER_ANGLE_TARGET_MAX_LOSS) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET1,values = FINGER_ANGLE_TARGET1)
            
    def test_write_finger_angle_target1_max(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target1: max angle')
        MAX_ANGLE = self.get_max_angle(ROH_FINGER_ANGLE_TARGET1)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET1,values = MAX_ANGLE)):
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET1)
            self.assertLessEqual(abs(response.registers[0]-MAX_ANGLE),FINGER_ANGLE_TARGET_MAX_LOSS) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET1,values = FINGER_ANGLE_TARGET1)
            
    def test_write_finger_angle_target1_bmax1(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target1: bigger than max angle（不大于32767）')
        MAX_ANGLE = self.get_max_angle(ROH_FINGER_ANGLE_TARGET1)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET1,values = 32767)):# 超过极大值，并且不超过32767，都返回最大值
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET1)
            self.assertEqual(response.registers[0],MAX_ANGLE) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET1,values = FINGER_ANGLE_TARGET1)
    
    def test_write_finger_angle_target1_bmax2(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target1: bigger than max angle（大于32767）')
        MIN_ANGLE = self.get_min_angle(ROH_FINGER_ANGLE_TARGET1)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET1,values = 36768)):# 超过极大值，并且超过32767，相当于取最小值
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET1)
            self.assertEqual(response.registers[0],MIN_ANGLE) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)    
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET1,values = FINGER_ANGLE_TARGET1)

    def test_read_finger_angle_target2(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger angle target2')
        response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET2)
        self.check_and_print_test_info(response)
    
        
    #角度范围 ，假设angle极大值为min，极小值为max，测试几个点min、max、小于min、大于max并且不大于32767、大于max并且大于32767
    def test_write_finger_angle_target2_min(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target2: min angle')
        MIN_ANGLE = self.get_min_angle(ROH_FINGER_ANGLE_TARGET2)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET2,values = MIN_ANGLE)):
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET2)
            self.assertLessEqual(abs(response.registers[0]-MIN_ANGLE),FINGER_ANGLE_TARGET_MAX_LOSS) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET2,values = FINGER_ANGLE_TARGET2)
            
    def test_write_finger_angle_target2_smin(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target2: smaller than min angle')
        MIN_ANGLE = self.get_min_angle(ROH_FINGER_ANGLE_TARGET2)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET2,values = 0)): # 边界值有波动，直接取最小值
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET2)
            self.assertEqual(response.registers[0],MIN_ANGLE) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET2,values = FINGER_ANGLE_TARGET2)
        
    def test_write_finger_angle_target2_normal(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target2: normal angle')
        
        MIN_ANGLE = self.get_min_angle(ROH_FINGER_ANGLE_TARGET2)
        MAX_ANGLE = self.get_max_angle(ROH_FINGER_ANGLE_TARGET2)
        NORMAL_ANGLE= int(MIN_ANGLE + (MAX_ANGLE - MIN_ANGLE)/2)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET2,values = NORMAL_ANGLE)): # 从极小值和极大值之间取个值
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET2)
            self.assertLessEqual(abs(response.registers[0]-NORMAL_ANGLE),FINGER_ANGLE_TARGET_MAX_LOSS) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET2,values = FINGER_ANGLE_TARGET2)
            
    def test_write_finger_angle_target2_max(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target2: max angle')
        MAX_ANGLE = self.get_max_angle(ROH_FINGER_ANGLE_TARGET2)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET2,values = MAX_ANGLE)):
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET2)
            self.assertLessEqual(abs(response.registers[0]-MAX_ANGLE),FINGER_ANGLE_TARGET_MAX_LOSS) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET2,values = FINGER_ANGLE_TARGET2)
            
    def test_write_finger_angle_target2_bmax1(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target2: bigger than max angle（不大于32767）')
        MAX_ANGLE = self.get_max_angle(ROH_FINGER_ANGLE_TARGET2)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET2,values = 32767)):# 超过极大值，并且不超过32767，都返回最大值
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET2)
            self.assertEqual(response.registers[0],MAX_ANGLE) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET2,values = FINGER_ANGLE_TARGET2)
    
    def test_write_finger_angle_target2_bmax2(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target2: bigger than max angle（大于32767）')
        MIN_ANGLE = self.get_min_angle(ROH_FINGER_ANGLE_TARGET2)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET2,values = 36768)):# 超过极大值，并且超过32767，相当于取最小值
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET2)
            self.assertEqual(response.registers[0],MIN_ANGLE) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)    
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET2,values = FINGER_ANGLE_TARGET2)

    def test_read_finger_angle_target3(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger angle target3')
        response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET3)
        self.check_and_print_test_info(response)
        
    #角度范围 ，假设angle极大值为min，极小值为max，测试几个点min、max、小于min、大于max并且不大于32767、大于max并且大于32767
    def test_write_finger_angle_target3_min(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target3: min angle')
        MIN_ANGLE = self.get_min_angle(ROH_FINGER_ANGLE_TARGET3)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET3,values = MIN_ANGLE)):
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET3)
            self.assertLessEqual(abs(response.registers[0]-MIN_ANGLE),FINGER_ANGLE_TARGET_MAX_LOSS) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET3,values = FINGER_ANGLE_TARGET3)
            
    def test_write_finger_angle_target3_smin(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target3: smaller than min angle')
        MIN_ANGLE = self.get_min_angle(ROH_FINGER_ANGLE_TARGET3)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET3,values = 0)): # 边界值有波动，直接取最小值
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET3)
            self.assertEqual(response.registers[0],MIN_ANGLE) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET3,values = FINGER_ANGLE_TARGET3)
        
    def test_write_finger_angle_target3_normal(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target3: normal angle')
        
        MIN_ANGLE = self.get_min_angle(ROH_FINGER_ANGLE_TARGET3)
        MAX_ANGLE = self.get_max_angle(ROH_FINGER_ANGLE_TARGET3)
        NORMAL_ANGLE= int(MIN_ANGLE + (MAX_ANGLE - MIN_ANGLE)/2)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET3,values = NORMAL_ANGLE)): # 从极小值和极大值之间取个值
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET3)
            self.assertLessEqual(abs(response.registers[0]-NORMAL_ANGLE),FINGER_ANGLE_TARGET_MAX_LOSS) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET3,values = FINGER_ANGLE_TARGET3)
            
    def test_write_finger_angle_target3_max(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target3: max angle')
        MAX_ANGLE = self.get_max_angle(ROH_FINGER_ANGLE_TARGET3)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET3,values = MAX_ANGLE)):
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET3)
            self.assertLessEqual(abs(response.registers[0]-MAX_ANGLE),FINGER_ANGLE_TARGET_MAX_LOSS) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET3,values = FINGER_ANGLE_TARGET3)
            
    def test_write_finger_angle_target3_bmax1(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target3: bigger than max angle（不大于32767）')
        MAX_ANGLE = self.get_max_angle(ROH_FINGER_ANGLE_TARGET3)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET3,values = 32767)):# 超过极大值，并且不超过32767，都返回最大值
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET3)
            self.assertEqual(response.registers[0],MAX_ANGLE) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET3,values = FINGER_ANGLE_TARGET3)
    
    def test_write_finger_angle_target3_bmax2(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target3: bigger than max angle（大于32767）')
        MIN_ANGLE = self.get_min_angle(ROH_FINGER_ANGLE_TARGET3)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET3,values = 36768)):# 超过极大值，并且超过32767，相当于取最小值
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET3)
            self.assertEqual(response.registers[0],MIN_ANGLE) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)    
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET3,values = FINGER_ANGLE_TARGET3)

    def test_read_finger_angle_target4(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger angle target4')
        response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET4)
        self.check_and_print_test_info(response)
    
        
    #角度范围 ，假设angle极大值为min，极小值为max，测试几个点min、max、小于min、大于max并且不大于32767、大于max并且大于32767
    def test_write_finger_angle_target4_min(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target4: min angle')
        MIN_ANGLE = self.get_min_angle(ROH_FINGER_ANGLE_TARGET4)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET4,values = MIN_ANGLE)):
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET4)
            self.assertLessEqual(abs(response.registers[0]-MIN_ANGLE),FINGER_ANGLE_TARGET_MAX_LOSS) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET4,values = FINGER_ANGLE_TARGET4)
            
    def test_write_finger_angle_target4_smin(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target4: smaller than min angle')
        MIN_ANGLE = self.get_min_angle(ROH_FINGER_ANGLE_TARGET4)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET4,values = 0)): # 边界值有波动，直接取最小值
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET4)
            self.assertEqual(response.registers[0],MIN_ANGLE) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET4,values = FINGER_ANGLE_TARGET4)
        
    def test_write_finger_angle_target4_normal(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target4: normal angle')
        
        MIN_ANGLE = self.get_min_angle(ROH_FINGER_ANGLE_TARGET4)
        MAX_ANGLE = self.get_max_angle(ROH_FINGER_ANGLE_TARGET4)
        NORMAL_ANGLE= int(MIN_ANGLE + (MAX_ANGLE - MIN_ANGLE)/2)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET4,values = NORMAL_ANGLE)): # 从极小值和极大值之间取个值
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET4)
            self.assertLessEqual(abs(response.registers[0]-NORMAL_ANGLE),FINGER_ANGLE_TARGET_MAX_LOSS) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET4,values = FINGER_ANGLE_TARGET4)
            
    def test_write_finger_angle_target4_max(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target4: max angle')
        MAX_ANGLE = self.get_max_angle(ROH_FINGER_ANGLE_TARGET4)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET4,values = MAX_ANGLE)):
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET4)
            self.assertLessEqual(abs(response.registers[0]-MAX_ANGLE),FINGER_ANGLE_TARGET_MAX_LOSS) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET4,values = FINGER_ANGLE_TARGET4)
            
    def test_write_finger_angle_target4_bmax1(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target4: bigger than max angle（不大于32767）')
        MAX_ANGLE = self.get_max_angle(ROH_FINGER_ANGLE_TARGET4)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET4,values = 32767)):# 超过极大值，并且不超过32767，都返回最大值
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET4)
            self.assertEqual(response.registers[0],MAX_ANGLE) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET4,values = FINGER_ANGLE_TARGET4)
    
    def test_write_finger_angle_target4_bmax2(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target4: bigger than max angle（大于32767）')
        MIN_ANGLE = self.get_min_angle(ROH_FINGER_ANGLE_TARGET4)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET4,values = 36768)):# 超过极大值，并且超过32767，相当于取最小值
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET4)
            self.assertEqual(response.registers[0],MIN_ANGLE) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)    
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET4,values = FINGER_ANGLE_TARGET4)

    def test_read_finger_angle_target5(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger angle target5')
        response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET5)
        self.check_and_print_test_info(response)
    
        
    #角度范围 ，假设angle极大值为min，极小值为max，测试几个点min、max、小于min、大于max并且不大于32767、大于max并且大于32767
    def test_write_finger_angle_target5_min(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target5: min angle')
        MIN_ANGLE = self.get_min_angle(ROH_FINGER_ANGLE_TARGET5)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET5,values = MIN_ANGLE)):
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET5)
            self.assertLessEqual(abs(response.registers[0]-MIN_ANGLE),FINGER_ANGLE_TARGET_MAX_LOSS) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET5,values = FINGER_ANGLE_TARGET5)#
            
    def test_write_finger_angle_target5_smin(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target5: smaller than min angle')
        MIN_ANGLE = self.get_min_angle(ROH_FINGER_ANGLE_TARGET5)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET5,values = 0)): # 边界值有波动，直接取最小值
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET5)
            self.assertEqual(response.registers[0],MIN_ANGLE) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET5,values = FINGER_ANGLE_TARGET5)
        
    def test_write_finger_angle_target5_normal(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target5: normal angle')
        
        MIN_ANGLE = self.get_min_angle(ROH_FINGER_ANGLE_TARGET5)
        MAX_ANGLE = self.get_max_angle(ROH_FINGER_ANGLE_TARGET5)
        NORMAL_ANGLE= int(MIN_ANGLE + (MAX_ANGLE - MIN_ANGLE)/2)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET5,values = NORMAL_ANGLE)): # 从极小值和极大值之间取个值
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET5)
            self.assertLessEqual(abs(response.registers[0]-NORMAL_ANGLE),FINGER_ANGLE_TARGET_MAX_LOSS) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET5,values = FINGER_ANGLE_TARGET5)
            
    def test_write_finger_angle_target5_max(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target5: max angle')
        MAX_ANGLE = self.get_max_angle(ROH_FINGER_ANGLE_TARGET5)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET5,values = MAX_ANGLE)):
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET5)
            self.assertLessEqual(abs(response.registers[0]-MAX_ANGLE),FINGER_ANGLE_TARGET_MAX_LOSS) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET5,values = FINGER_ANGLE_TARGET5)
            
    def test_write_finger_angle_target5_bmax1(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target5: bigger than max angle（不大于32767）')
        MAX_ANGLE = self.get_max_angle(ROH_FINGER_ANGLE_TARGET5)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET5,values = 32767)):# 超过极大值，并且不超过32767，都返回最大值
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET5)
            self.assertEqual(response.registers[0],MAX_ANGLE) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)
            
         # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET5,values = FINGER_ANGLE_TARGET5)
    
    def test_write_finger_angle_target5_bmax2(self): 
        self.print_test_info(status=self.TEST_STRAT,info='write finger angle target5: bigger than max angle（大于32767）')
        MIN_ANGLE = self.get_min_angle(ROH_FINGER_ANGLE_TARGET5)
        
        if(self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET5,values = 36768)):# 超过极大值，并且超过32767，相当于取最小值
            response = self.client.read_from_register(address=ROH_FINGER_ANGLE_TARGET5)
            self.assertEqual(response.registers[0],MIN_ANGLE) 
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL)    
            
        # 恢复默认值
        self.client.write_to_register(address = ROH_FINGER_ANGLE_TARGET5,values = FINGER_ANGLE_TARGET5)


    def test_read_finger_angle0(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger angle0')
        response = self.client.read_from_register(address=ROH_FINGER_ANGLE0)
        self.check_and_print_test_info(response) 

    def test_read_finger_angle1(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger angle1')
        response = self.client.read_from_register(address=ROH_FINGER_ANGLE1)
        self.check_and_print_test_info(response) 
            
    def test_read_finger_angle2(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger angle2')
        response = self.client.read_from_register(address=ROH_FINGER_ANGLE2)
        self.check_and_print_test_info(response) 
       
            
    def test_read_finger_angle3(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger angle3')
        response = self.client.read_from_register(address=ROH_FINGER_ANGLE3)
        self.check_and_print_test_info(response) 
            
    def test_read_finger_angle4(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger angle4')
        response = self.client.read_from_register(address=ROH_FINGER_ANGLE4)
        self.check_and_print_test_info(response) 
            
    def test_read_finger_angle5(self):
        self.print_test_info(status=self.TEST_STRAT,info='read finger angle5')
        response = self.client.read_from_register(address=ROH_FINGER_ANGLE5)
        self.check_and_print_test_info(response) 
    

    # 测试读取多个寄存器
    def test_read_multiple_holding_registers(self):
    
        self.print_test_info(status=self.TEST_STRAT,info='read multiple holding registers')
        response = self.client.read_from_register(address=ROH_FINGER_P0,count=5)
        
        if self.isNotNoneOrError(response):
            self.assertEqual(len(response.registers), 5)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL) 

    # 测试写多个寄存器
    def test_write_multiple_holding_registers(self):
        self.print_test_info(status=self.TEST_STRAT,info='write multiple holding registers')
        start_address = ROH_FINGER_CURRENT_LIMIT0
        values = [1000, 1000, 1000, 1000, 1000, 1000]
        recover_values=[FINGER_CURRENT_LIMIT0,FINGER_CURRENT_LIMIT1,FINGER_CURRENT_LIMIT2,FINGER_CURRENT_LIMIT3,FINGER_CURRENT_LIMIT4,FINGER_CURRENT_LIMIT5]
        
        response_write = self.client.write_to_register(address=start_address, values=values)
        if not response_write:
            logger.error('写多个保持寄存器失败')
            self.print_test_info(status=self.TEST_FAIL) 
            return
        
        read_response = self.client.read_from_register(address=start_address, count=len(values))
        
        if self.isNotNoneOrError(read_response):
            self.assertEqual(read_response.registers, values)
            self.print_test_info(status=self.TEST_PASS)
        else:
            self.print_test_info(status=self.TEST_FAIL) 
            
        # 恢复默认值
        self.client.write_to_register(address=start_address, values=recover_values)
            
    # 测试错误端口号连接失败情况
    def test_connection_failure(self):
        self.print_test_info(status=self.TEST_STRAT,info='test worng connect:worng port COM100')
        try:
            wrong_client = ModbusSerialClient(port='COM100', framer=FramerType.RTU, baudrate=115200)
            wrong_client.connect()
            response = wrong_client.read_holding_registers(0, 5)
            self.assertTrue(response.isError())
            self.print_test_info(status=self.TEST_FAIL)
        
        except ConnectionException as e:
            logger.error(e)
            self.print_test_info(status=self.TEST_PASS)
        except FileNotFoundError as e:
            logger.error(e)
            self.print_test_info(status=self.TEST_PASS)
        
    # # 测试读取超过范围的寄存器数量
    # def test_read_exceeding_registers(self):
    #     self.print_test_info(status=self.TEST_STRAT,info='read exceeding registers:65535+1')
    #     max_address = 65535
    #     try:
    #         self.client.read_from_register(0, max_address + 1)
    #         self.print_test_info(status=self.TEST_FAIL)
    #     except ModbusException as e:
    #         self.assertEqual(e.exception_code, 0x03)
    #         self.print_test_info(status=self.TEST_PASS)
    #     except struct.error as e:
    #         logger.error(f"异常: {e}")
    #         self.print_test_info(status=self.TEST_PASS)
                
            
    # # 测试在网络不稳定情况下的读写操作，暂时保留,意义不大
    # def test_network_unstable_operations(self):
    #     self.print_test_info(status=self.TEST_STRAT,info='test network unstable operations')
    #     import time
    #     import random

    #     for _ in range(10):
    #         try:
    #             # 模拟网络不稳定，随机进行读或写操作
    #             if random.choice([True, False]):
    #                 response = self.client.read_from_register(address=0, count=3)
    #                 if response.isError():
    #                     logger.error(f"网络不稳定时读取保持寄存器失败: {response}")
                        
    #             else:
    #                 value = random.randint(100, 999)
    #                 response = self.client.write_to_register(address=5, values=value)
    #                 if response.isError():
    #                     logger.error(f"网络不稳定时写入保持寄存器失败: {response}")
                        
    #             time.sleep(random.uniform(0.1, 0.5))
                
    #         except Exception as e:
    #             logger.error(f"网络不稳定时操作失败: {e}")
                
    #     self.print_test_info(status=self.TEST_PASS)

    # # # 测试设备响应超时情况
    # def test_device_response_timeout(self):
    #     self.print_test_info(status=self.TEST_STRAT,info='test device response timeout')
    #     slow_client = ModbusSerialClient(port=self.port, framer=FramerType.RTU, baudrate=115200)
    #     slow_client.connect()
        
    #     try:
    #         response = slow_client.read_holding_registers(0, 5, self.node_id)
    #         if response.isError():
    #             logger.error(f"设备响应超时，但未按预期抛出异常: {response}")
                
    #     except ModbusException as e:
    #         logger.error(f"设备响应超时: {e}")
    #         self.print_test_info(status=self.TEST_PASS)
        

def run_tests_for_port(port):
    connected_status = True
    port_result = {
        "port": port,
        "gestures": []
    }
    start_time = time.time()
    # TestModbus.args = {'port': port, 'framer': framer, 'baudrate': baudrate}
    TempTestClass = type('TempTest', (TestModbus,), {'__init__': lambda self, *args, **kwargs: TestModbus.__init__(self, port, *args, **kwargs)})

    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    tests = loader.loadTestsFromTestCase(TempTestClass)
    suite.addTests(tests)

    runner = unittest.TextTestRunner()
    result = runner.run(suite)
     # suite = unittest.TestLoader().loadTestsFromTestCase(TestModbus)
    # # suite = unittest.TestLoader().loadTestsFromTestCase(TestModbus(port, framer, baudrate))
    # runner = unittest.TextTestRunner(verbosity=2)
    # result = runner.run(suite)
    
    #  下面为单个用例调试使用
    # testModbus =TestModbus(port=port)
    # suite = unittest.TestSuite()
    # # 添加单个测试用例，这里添加 test_case1
    # suite.addTest(testModbus)
    # runner = unittest.TextTestRunner(verbosity=2)
    # result = runner.run(suite)
    end_time = time.time()
    elapsed_time = end_time - start_time
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f"\n\n Ran {result.testsRun} tests in {elapsed_time:.3f}s\n")

    if result.failures:
        logger.error(f"Failures: {len(result.failures)}")
        for failure in result.failures:
            test_method_name, failure_message = failure
            logger.info(f"Test method: {test_method_name} failed. Error: {failure_message}\n")
            gesture_result = {
                "timestamp":timestamp,
                "content": f'{test_method_name},{failure_message}',
                "result": "不通过"
            }
            port_result["gestures"].append(gesture_result)

    if result.errors:
        logger.info(f"Errors: {len(result.errors)}")
        for error in result.errors:
            test_method_name, error_message = error
            logger.info(f"Test method: {test_method_name} encountered an error. Error: {error_message}\n")
            gesture_result = {
                "timestamp":timestamp,
                "content": f'{test_method_name},{error_message}',
                "result": "不通过"
            }
            port_result["gestures"].append(gesture_result)

    if result.skipped:
        logger.info(f"Skipped: {len(result.skipped)}")
        for skipped_test in result.skipped:
            test_method_name, reason = skipped_test
            logger.info(f"Test method: {test_method_name} was skipped. Reason: {reason}\n")
            gesture_result = {
                "timestamp":timestamp,
                "content": f'{test_method_name},{reason}',
                "result": "通过"
            }
            port_result["gestures"].append(gesture_result)

    return port_result

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

def main(ports,max_cycle_num=1):
    
    start_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f'---------------------------------------------开始测试MODBUS协议<开始时间：{start_time}>----------------------------------------------\n')
    overall_result = []
    test_result = '通过'
    
    status, valid_ports = check_ports(ports)
    if not (status and len(valid_ports)>=1):
        logger.error('测试结束，无可用端口')
        result = '不通过'
        return overall_result,result

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(run_tests_for_port, port) for port in ports]
        for future in concurrent.futures.as_completed(futures):
            port_result= future.result()
            overall_result.append(port_result)

            for gesture_result in port_result["gestures"]:
                if gesture_result["result"]!= "通过":
                    test_result = '不通过'

    end_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f'---------------------------------------------MODBUS协议测试结束<结束时间：{end_time}>----------------------------------------------\n')
    # print_overall_result(overall_result)
    return overall_result, test_result


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

if __name__ == '__main__':
    ports = ['COM5']
    overall_result,test_result = main(ports=ports,max_cycle_num=1)
    logger.info(f'测试结果：{test_result}\n')
    logger.info(f'详细数据：\n')
    print_overall_result(overall_result)
