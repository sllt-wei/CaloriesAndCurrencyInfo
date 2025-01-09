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
class CaloriesAndCurrencyInfoPlugin(Plugin):
    def __init__(self):
        super().__init__()
        try:
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            logger.info("[CaloriesAndCurrencyInfoPlugin] Initialized.")
        except Exception as e:
            logger.warn("[CaloriesAndCurrencyInfoPlugin] Initialization failed.")
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

                # 将中文货币名称转换为标准货币代码
                source_currency_code = self.get_currency_code(source_currency)
                target_currency_code = self.get_currency_code(target_currency)

                if not source_currency_code or not target_currency_code:
                    raise ValueError("不支持的货币符号")

                # 货币转换
                conversion_result = self.get_currency_conversion(amount, source_currency_code, target_currency_code)

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
            "AED": "阿联酋迪拉姆 (AED)",
            "AFN": "阿富汗阿富汗尼 (AFN)",
            "ALL": "阿尔巴尼亚列克 (ALL)",
            "AMD": "亚美尼亚德拉姆 (AMD)",
            "ANG": "荷属安的列斯盾 (ANG)",
            "AOA": "安哥拉宽扎 (AOA)",
            "ARS": "阿根廷比索 (ARS)",
            "AUD": "澳元 (AUD)",
            "AWG": "阿鲁巴弗罗林 (AWG)",
            "AZN": "阿塞拜疆马纳特 (AZN)",
            "BAM": "波黑可兑换马克 (BAM)",
            "BBD": "巴巴多斯元 (BBD)",
            "BDT": "孟加拉塔卡 (BDT)",
            "BGN": "保加利亚列弗 (BGN)",
            "BHD": "巴林第纳尔 (BHD)",
            "BIF": "布隆迪法郎 (BIF)",
            "BMD": "百慕大元 (BMD)",
            "BND": "文莱元 (BND)",
            "BOB": "玻利维亚诺 (BOB)",
            "BRL": "巴西雷亚尔 (BRL)",
            "BSD": "巴哈马元 (BSD)",
            "BTN": "不丹努尔特鲁姆 (BTN)",
            "BWP": "博茨瓦纳普拉 (BWP)",
            "BYN": "白俄罗斯卢布 (BYN)",
            "BZD": "伯利兹元 (BZD)",
            "CAD": "加拿大元 (CAD)",
            "CDF": "刚果法郎 (CDF)",
            "CHF": "瑞士法郎 (CHF)",
            "CLP": "智利比索 (CLP)",
            "CNY": "人民币 (CNY)",
            "COP": "哥伦比亚比索 (COP)",
            "CRC": "哥斯达黎加科朗 (CRC)",
            "CUP": "古巴比索 (CUP)",
            "CVE": "佛得角埃斯库多 (CVE)",
            "CZK": "捷克克朗 (CZK)",
            "DJF": "吉布提法郎 (DJF)",
            "DKK": "丹麦克朗 (DKK)",
            "DOP": "多米尼加比索 (DOP)",
            "DZD": "阿尔及利亚第纳尔 (DZD)",
            "EGP": "埃及镑 (EGP)",
            "ERN": "厄立特里亚纳克法 (ERN)",
            "ETB": "埃塞俄比亚比尔 (ETB)",
            "EUR": "欧元 (EUR)",
            "FJD": "斐济元 (FJD)",
            "GBP": "英镑 (GBP)",
            "INR": "印度卢比 (INR)",
            "IRR": "伊朗里亚尔 (IRR)",
            "ISK": "冰岛克朗 (ISK)",
            "JPY": "日元 (JPY)",
            "KES": "肯尼亚先令 (KES)",
            "KRW": "韩元 (KRW)",
            "KWD": "科威特第纳尔 (KWD)",
            "KZT": "哈萨克斯坦腾格 (KZT)",
            "LAK": "老挝基普 (LAK)",
            "LKR": "斯里兰卡卢比 (LKR)",
            "LRD": "利比里亚元 (LRD)",
            "LSL": "莱索托洛提 (LSL)",
            "LYD": "利比亚第纳尔 (LYD)",
            "MAD": "摩洛哥迪拉姆 (MAD)",
            "MYR": "马来西亚林吉特 (MYR)",
            "MXN": "墨西哥比索 (MXN)",
            "NZD": "新西兰元 (NZD)",
            "NOK": "挪威克朗 (NOK)",
            "PKR": "巴基斯坦卢比 (PKR)",
            "PLN": "波兰兹罗提 (PLN)",
            "RUB": "俄罗斯卢布 (RUB)",
            "SAR": "沙特里亚尔 (SAR)",
            "SEK": "瑞典克朗 (SEK)",
            "SGD": "新加坡元 (SGD)",
            "THB": "泰铢 (THB)",
            "TRY": "土耳其里拉 (TRY)",
            "USD": "美元 (USD)",
            "VND": "越南盾 (VND)",
            "ZAR": "南非兰特 (ZAR)"
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

        return help_text

    def get_currency_code(self, currency_name):
        # 根据用户输入的货币名称获取货币代码
        currency_map = {
            "美元": "USD", "人民币": "CNY", "欧元": "EUR", "英镑": "GBP", "日元": "JPY",
            "澳元": "AUD", "加元": "CAD", "新加坡元": "SGD", "瑞士法郎": "CHF", "泰铢": "THB",
            "韩元": "KRW", "印度卢比": "INR", "阿联酋迪拉姆": "AED", "阿根廷比索": "ARS", "巴西雷亚尔": "BRL",
            # 增加更多货币映射
        }
        return currency_map.get(currency_name, None)

    def get_currency_conversion(self, amount, source_currency, target_currency):
        url = f"https://api.exchangerate-api.com/v4/latest/{source_currency}"
        try:
            response = requests.get(url)
            data = response.json()
            if response.status_code == 200 and "rates" in data:
                rate = data["rates"].get(target_currency)
                if rate:
                    return amount * rate
        except Exception as e:
            logger.error(f"货币转换失败: {e}")
        return None
