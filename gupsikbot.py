import discord
from discord.ext import commands
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

# .env 불러오기
load_dotenv()
API_KEY = os.getenv("NEIS_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 🔹 학교 코드 가져오기
def get_school_code(school_name):
    url = f"https://open.neis.go.kr/hub/schoolInfo?KEY={API_KEY}&Type=json&SCHUL_NM={school_name}"
    response = requests.get(url)
    data = response.json()

    if "RESULT" in data:
        return None, None

    if "schoolInfo" not in data:
        return None, None

    schools = data["schoolInfo"][1]["row"]
    for school in schools:
        if "고등학교" in school["SCHUL_NM"]:
            return school["ATPT_OFCDC_SC_CODE"], school["SD_SCHUL_CODE"]

    return None, None

# 🔹 급식 정보 가져오기
def get_meal_info(school_name):
    atpt_code, schul_code = get_school_code(school_name)
    if not atpt_code or not schul_code:
        return "❌ 올바른 고등학교를 찾을 수 없습니다."

    today = datetime.now().strftime("%Y%m%d")
    url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?KEY={API_KEY}&Type=json&ATPT_OFCDC_SC_CODE={atpt_code}&SD_SCHUL_CODE={schul_code}&MLSV_YMD={today}"
    response = requests.get(url)
    data = response.json()

    if "RESULT" in data:
        return f"❌ API 오류: {data['RESULT']['MESSAGE']}"

    if "mealServiceDietInfo" not in data:
        return "❌ 급식 정보를 찾을 수 없습니다."

    meals = data["mealServiceDietInfo"][1]["row"]
    menu_text = f"📌 {school_name} 급식 메뉴 ({today})\n\n"
    for meal in meals:
        menu = meal["DDISH_NM"].replace("<br/>", "\n")
        menu_text += f"{menu}"
    return menu_text

# 🔹 디스코드 명령어
@bot.command()
async def 급식(ctx, *, school_name: str):
    await ctx.send("🔍 급식 정보를 불러오는 중...")
    result = get_meal_info(school_name)
    await ctx.send(result)

@bot.event
async def on_ready():
    print(f"✅ 로그인 완료: {bot.user}")

# 🔹 여기에 디스코드 봇 토큰 입력
bot.run(DISCORD_TOKEN)
