from typing import Dict, Any, Generator
from autotask.nodes import Node, GeneratorNode, register_node
import pyautogui
import time
import os
import platform
import pyperclip
import traceback

class RPANodeMeta(type):
    """RPA节点的元类，用于处理输入输出的合并"""

    def __new__(mcs, name, bases, attrs):
        # 如果不是基类，则合并输入输出
        if name != "BaseRPANode":
            # 合并INPUTS
            base_inputs = {}
            for base in bases:
                if hasattr(base, "BASE_INPUTS"):
                    base_inputs.update(base.BASE_INPUTS)
            attrs["INPUTS"] = {**base_inputs, **attrs.get("INPUTS", {})}

            # 合并OUTPUTS
            base_outputs = {}
            for base in bases:
                if hasattr(base, "BASE_OUTPUTS"):
                    base_outputs.update(base.BASE_OUTPUTS)
            attrs["OUTPUTS"] = {**base_outputs, **attrs.get("OUTPUTS", {})}

        return super().__new__(mcs, name, bases, attrs)


class BaseRPANode(Node, metaclass=RPANodeMeta):
    """RPA基础节点类，定义通用的输入输出"""

    BASE_INPUTS = {
        "previous_result": {
            "label": "上一步结果",
            "description": "上一个节点的执行结果",
            "type": "",
            "required": False,
        }
    }

    BASE_OUTPUTS = {
        "result": {
            "label": "执行结果",
            "description": "当前节点的相关执行数据",
            "type": "",
        },
    }

    def __init__(self):
        super().__init__()
        # 不再需要在这里合并输入输出

    async def execute(self, node_inputs: Dict[str, Any], workflow_logger) -> Dict[str, Any]:
        # 如果没有传入workflow_logger，使用默认logger
        log = workflow_logger
        pass


@register_node
class MouseClickNode(BaseRPANode):
    NAME = "鼠标点击"
    DESCRIPTION = "模拟鼠标点击指定位置"
    INPUTS = {
        "x": {
            "label": "X坐标",
            "description": "点击位置的X坐标",
            "type": "INT",
            "required": True,
        },
        "y": {
            "label": "Y坐标",
            "description": "点击位置的Y坐标",
            "type": "INT",
            "required": True,
        },
        "clicks": {
            "label": "点击次数",
            "description": "连续点击次数",
            "type": "INT",
            "default": 1,
        },
        "interval": {
            "label": "点击间隔",
            "description": "多次点击时的间隔时间(秒)",
            "type": "FLOAT",
            "default": 0.25,
        },
    }

    async def execute(self, node_inputs: Dict[str, Any], workflow_logger) -> Dict[str, Any]:
        log = workflow_logger
        start_time = time.time()
        try:
            # 检查上一步是否成功

            x = node_inputs["x"]
            y = node_inputs["y"]
            log.debug(f"执行鼠标点击: x={x}, y={y}")
            pyautogui.click(
                x=x,
                y=y,
                clicks=node_inputs.get("clicks", 1),
                interval=node_inputs.get("interval", 0.25),
            )

            return {
                "success": True,
                "error_message": "",
                "execution_time": time.time() - start_time,
                "click_position": {"x": x, "y": y},
            }
        except Exception as e:
            traceback.print_exc()
            error_msg = f"鼠标点击失败: {str(e)}"
            log.error(error_msg)
            return {
                "success": False,
                "error_message": error_msg,
                "execution_time": time.time() - start_time,
                "click_position": None,
            }


@register_node
class ImageClickNode(BaseRPANode):
    NAME = "图像识别点击"
    DESCRIPTION = "查找并点击指定图像。"
    INPUTS = {
        "target_img": {
            "label": "图像路径",
            "description": "要查找的图像文件路径",
            "type": "IMAGEUPLOAD",
            "required": True,
        },
        "confidence": {
            "label": "匹配度",
            "description": "图像匹配的置信度(0-1)",
            "type": "FLOAT",
            "default": 0.8,
            "step": 0.03,
        },
        "wait_time": {
            "label": "等待时间",
            "description": "等待图像出现的最长时间(秒)",
            "type": "FLOAT",
            "default": 1.0,
        },
    }

    async def execute(self, node_inputs: Dict[str, Any], workflow_logger) -> Dict[str, Any]:
        log = workflow_logger
        start_time = time.time()
        try:
            print(node_inputs)

            # 添加图像文件验证
            image_path = node_inputs["target_img"]
            log.debug(f"尝试查找图像文件: {image_path}")

            if not os.path.exists(image_path):
                log.error(f"图像文件不存在: {image_path}")
                return {
                    "success": False,
                    "error_message": f"图像文件不存在: {image_path}",
                    "execution_time": time.time() - start_time,
                    "image_found": False,
                    "click_position": None,
                }

            # 验证图像文件格式
            valid_extensions = (".png", ".jpg", ".jpeg", ".bmp")
            if not image_path.lower().endswith(valid_extensions):
                log.error(f"不支持的图像格式: {image_path}")
                return {
                    "success": False,
                    "error_message": f"不支持的图像格式，请使用以下格式: {valid_extensions}",
                    "execution_time": time.time() - start_time,
                    "image_found": False,
                    "click_position": None,
                }

            wait_time = node_inputs.get("wait_time", 10)
            confidence = node_inputs.get("confidence", 0.9)
            log.debug(f"开始查找图像，等待时间: {wait_time}秒, 匹配度: {confidence}")

            end_time = time.time() + wait_time
            attempts = 0

            # 循环尝试查找图像，直到超时
            while time.time() < end_time:
                attempts += 1
                try:
                    log.debug(f"第 {attempts} 次尝试查找图像...")
                    location = pyautogui.locateCenterOnScreen(
                        image_path, confidence=confidence
                    )

                    if location:
                        log.info(f"找到图像，位置: x={location.x}, y={location.y}")
                        log.debug("执行点击操作...")
                        pyautogui.click(location)
                        return {"result": True}
                        # return {
                        #     "success": True,
                        #     "error_message": "",
                        #     "execution_time": time.time() - start_time,
                        #     "image_found": True,
                        #     "click_position": {"x": location.x, "y": location.y},
                        # }
                except Exception as e:
                    log.debug(f"单次查找失败: {str(e)}")
                    pass

                # 短暂等待后继续尝试
                time.sleep(0.5)

            # 超时未找到图像
            log.warning(f"在 {wait_time} 秒内未找到目标图像，共尝试 {attempts} 次")
            return {"result": False}
            # return {
            #     "success": False,
            #     "error_message": f"未找到目标图像 (尝试次数: {attempts})",
            #     "execution_time": time.time() - start_time,
            #     "image_found": False,
            #     "click_position": None,
            # }

        except Exception as e:
            error_msg = f"图像识别点击失败: {str(e)}"
            log.error(error_msg)
            # 返回False
            return {"result": False}


@register_node
class OpenApplicationNode(BaseRPANode):
    NAME = "打开应用程序"
    DESCRIPTION = "启动指定的应用程序"
    INPUTS = {
        "app_file": {
            "label": "应用程序路径",
            "description": "要启动的应用程序完整路径",
            "type": "STRING",
            "required": True,
        },
        "wait_time": {
            "label": "等待时间",
            "description": "等待应用程序启动的时间(秒)",
            "type": "FLOAT",
            "default": 2.0,
        },
    }

    async def execute(self, node_inputs: Dict[str, Any], workflow_logger) -> Dict[str, Any]:
        log = workflow_logger
        start_time = time.time()
        try:
            workflow_logger.info(f"开始执行打开应用程序: {node_inputs}")
            # 检查上一步是否成功

            app_path = node_inputs["app_file"]
            wait_time = node_inputs.get("wait_time", 3)
            
            workflow_logger.info(f"开始执行打开应用程序: {app_path}")

            # 检查文件是否存在
            if not os.path.exists(app_path):
                raise FileNotFoundError(f"应用程序路径不存在: {app_path}")

            # 启动应用程序
            os.startfile(app_path)
            time.sleep(wait_time)  # 等待应用程序启动

            return {
                "success": True,
                "error_message": "",
                "execution_time": time.time() - start_time,
                "process_info": {
                    "application_path": app_path,
                    "start_time": start_time,
                },
            }

        except Exception as e:
            error_msg = f"启动应用程序失败: {str(e)}"
            log.error(error_msg, exc_info=True)
            log.error(f"开始执行打开应用程序: {traceback.format_exc()}")
            return {
                "success": False,
                "error_message": error_msg,
                "execution_time": time.time() - start_time,
                "process_info": None,
            }


@register_node
class TypeTextNode(BaseRPANode):
    NAME = "输入文本"
    DESCRIPTION = "在当前位置粘贴文本"
    INPUTS = {
        "text": {
            "label": "输入文本",
            "description": "要输入的文本内容",
            "type": "STRING",
            "multiline": True,
            "required": True,
        }
    }

    async def execute(self, node_inputs: Dict[str, Any], workflow_logger) -> Dict[str, Any]:
        log = workflow_logger
        start_time = time.time()
        try:
            # 检查上一步是否成功


            # 保存原有剪贴板内容
            original_clipboard = pyperclip.paste()

            text = node_inputs["text"]
            log.debug(f"执行文本输入: {text}")

            # 设置新文本到剪贴板
            pyperclip.copy(text)

            # 执行粘贴操作
            if platform.system() == "Darwin":  # macOS
                pyautogui.hotkey("command", "v")
            else:  # Windows/Linux
                pyautogui.hotkey("ctrl", "v")

            # 恢复原有剪贴板内容
            pyperclip.copy(original_clipboard)

            return {
                "success": True,
                "error_message": "",
                "execution_time": time.time() - start_time,
                "text_info": {"content": text, "length": len(text)},
            }

        except Exception as e:
            traceback.print_exc()
            error_msg = f"文本输入失败: {str(e)}"
            log.error(error_msg)
            return {
                "success": False,
                "error_message": error_msg,
                "execution_time": time.time() - start_time,
                "text_info": None,
            }


@register_node
class KeyPressNode(BaseRPANode):
    NAME = "按键操作"
    DESCRIPTION = "模拟键盘按键操作"
    INPUTS = {
        "key": {
            "label": "按键",
            "description": "要按下的键(例如: enter, tab, a, b, 1等)",
            "type": "STRING",
            "required": True,
        },
        "modifiers": {
            "label": "组合键",
            "description": "组合键，多个用逗号分隔(例如: ctrl,alt,shift)",
            "type": "STRING",
            "required": False,
            "default": "",
        },
        "presses": {
            "label": "按键次数",
            "description": "连续按键次数",
            "type": "INT",
            "default": 1,
        },
        "interval": {
            "label": "按键间隔",
            "description": "多次按键时的间隔时间(秒)",
            "type": "FLOAT",
            "default": 0.25,
        },
    }

    async def execute(self, node_inputs: Dict[str, Any], workflow_logger) -> Dict[str, Any]:
        log = workflow_logger
        start_time = time.time()
        try:
            # 检查上一步是否成功

            key = node_inputs["key"]
            modifiers_str = node_inputs.get("modifiers", "").strip()
            modifiers = (
                [m.strip().lower() for m in modifiers_str.split(",")]
                if modifiers_str
                else []
            )
            presses = node_inputs.get("presses", 1)
            interval = node_inputs.get("interval", 0.25)

            log.debug(
                f"执行按键操作: key={key}, modifiers={modifiers}, presses={presses}"
            )

            # 如果有组合键
            if modifiers:
                for _ in range(presses):
                    pyautogui.hotkey(*modifiers, key)
                    if presses > 1:
                        time.sleep(interval)
            else:
                # 单个按键
                pyautogui.press(key, presses=presses, interval=interval)

            return {
                "success": True,
                "error_message": "",
                "execution_time": time.time() - start_time,
                "key_info": {"key": key, "modifiers": modifiers, "presses": presses},
            }

        except Exception as e:
            error_msg = f"按键操作失败: {str(e)}"
            log.error(error_msg)
            return {
                "success": False,
                "error_message": error_msg,
                "execution_time": time.time() - start_time,
                "key_info": None,
            }
