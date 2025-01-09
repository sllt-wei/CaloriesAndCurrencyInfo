# encoding:utf-8
import requests
import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from plugins import *

@plugins.register(
    name="CaloriesAndCurrencyInfo",
    desire_priority=100,
    hidden=False,
    desc="A plugin to fetch calorie information and currency conversion",
    version="0.2",
    author="Your Name",
)
class CaloriesAndCurrencyPlugin(Plugin):
    def __init__(self):
        super().__init__()
        try:
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            logger.info("[CaloriesAndCurrencyPlugin] Initialized.")
        except Exception as e:
            logger.warn("[CaloriesAndCurrencyPlugin] Initialization failed.")
            raise e

    def on_handle_context(self, e_context):
        if e_context["context"].type != ContextType.TEXT:
            return

        content = e_context["context"].content.strip()

        if content.startswith("卡路里"):
            # 处理卡路里查询
            food_item = content.replace("卡路里", "").strip()
            calorie_info = self.get_calorie_info(food_item)

            if calorie_info:
                if len(calorie_info) > 0:
                    reply_text = f"关于 \"{food_item}\" 的卡路里信息：\n" + "\n".join(
                        [f"{item['food']}: {item['calories']}" for item in calorie_info]
                    )
                else:
                    reply_text = f"未找到与 \"{food_item}\" 相关的卡路里信息。"
                reply = Reply(ReplyType.TEXT, reply_text)
            else:
                reply = Reply(ReplyType.TEXT, "未能获取相关卡路里信息，请稍后再试。")

            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS

        elif content.startswith("汇率"):
            try:
                # 解析输入的货币转换请求
                parts = content.replace("汇率", "").strip().split("到")
                if len(parts) != 2:
                    raise ValueError("输入格式错误")
                amount_and_src = parts[0].strip().split()
                target_currency = parts[1].strip()

                if len(amount_and_src) != 2:
                    raise ValueError("输入格式错误")
                amount = float(amount_and_src[0])
                source_currency = amount_and_src[1]

                # 货币转换
                conversion_result = self.get_currency_conversion(amount, source_currency, target_currency)

                if conversion_result:
                    reply_text = f"{amount} {source_currency} 等于 {conversion_result:.2f} {target_currency}"
                else:
                    reply_text = f"未能转换 {source_currency} 到 {target_currency}，请检查输入的货币符号。"

                reply = Reply(ReplyType.TEXT, reply_text)
            except Exception as e:
                reply = Reply(ReplyType.TEXT, f"汇率查询失败：{str(e)}")

            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS

    def get_help_text(self, **kwargs):
        supported_currencies = {
            "USD": "美元 (USD)",
            "AUD": "澳元 (AUD)",
            "BGN": "保加利亚列弗 (BGN)",
            "CAD": "加拿大元 (CAD)",
            "CHF": "瑞士法郎 (CHF)",
            "CNY": "人民币 (CNY)",
            "EGP": "埃及镑 (EGP)",
            "EUR": "欧元 (EUR)",
            "GBP": "英镑 (GBP)",
            "JPY": "日元 (JPY)",
            "INR": "印度卢比 (INR)",
            "RUB": "俄罗斯卢布 (RUB)",
        }

        help_text = (
            "该插件支持以下功能：\n"
            "1. 查询食物的卡路里：输入【卡路里 [食物名称]】\n"
            "2. 进行货币转换：输入【汇率 [金额] [源货币] 到 [目标货币]】\n\n"
            "示例：\n"
            "  - 【卡路里 土豆】将返回土豆的卡路里信息。\n"
            "  - 【汇率 1000 人民币 到 美元】将返回1000人民币等于多少美元。\n\n"
            "支持的货币符号及名称：\n"
        )
        for code, name in supported_currencies.items():
            help_text += f"  - {code}: {name}\n"

        help_text += "\n请根据上述格式输入查询内容。"
        return help_text

    def get_calorie_info(self, food_item):
        api_url = "https://shanhe.kim/api/za/calories.php"
        try:
            response = requests.get(api_url, params={"food": food_item})
            response.raise_for_status()
            data = response.json()

            if data.get("code") == "200":
                return data.get("data", [])
            else:
                logger.error(f"API error: {data.get('msg')}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch calorie information: {e}")
            return None

    def get_currency_conversion(self, amount, source_currency, target_currency):
        # 使用已提供的 API URL
        api_url = f"https://v6.exchangerate-api.com/v6/a38630efad4f507c02fb2825/latest/{source_currency}"
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()

            if data.get("result") == "success":
                rates = data.get("conversion_rates", {})
                if target_currency in rates:
                    return amount * rates[target_currency]
                else:
                    logger.error(f"Unsupported target currency: {target_currency}")
                    return None
            else:
                logger.error(f"API error: {data.get('error-type')}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch exchange rate: {e}")
            return None

# 示例调用
if __name__ == "__main__":
    plugin = CaloriesAndCurrencyPlugin()
    print(plugin.get_help_text())
