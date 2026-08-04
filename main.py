# main.py (최종 완성본: 스테이지 선택 반복 충돌 및 모든 버그 해결 버전)
import json
import os
import random
import sys
import threading
import discord
from discord.ext import commands
from flask import Flask

# 1. Flask 서버 설정 (Render Health Check용)
app = Flask(__name__)


@app.route("/")
def home():
  return "OK", 200


def run_flask():
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


# 2. 디스코드 봇 설정
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "cats_data.json"
data_lock = threading.Lock()

# --- 게임 데이터 (스킬 및 몬스터) ---
ALL_SKILLS = [
    {"name": "야성 각성", "desc": "잠재된 야성을 깨워 적을 강하게 할큅니다."},
    {"name": "뒷발 팡팡 난타", "desc": "강력한 뒷발로 적을 연속으로 걷어찹니다."},
    {"name": "질풍의 발톱", "desc": "바람처럼 빠른 속도로 적의 허를 찌릅니다."},
    {"name": "회전 묘기 펀치", "desc": "공중을 돌며 강력한 일격을 날립니다."},
    {"name": "치명적인 스크래치", "desc": "적의 급소를 정확히 노려 깊은 상처를 냅니다."},
]

SKILL_DICT = {s["name"]: s for s in ALL_SKILLS}

MONSTERS = {}

# 최대 300 스테이지(30챕터)까지 구조화
for st in range(1, 301):
  chapter = (st - 1) // 10 + 1
  sub = (st - 1) % 10 + 1

  is_antarctic = chapter % 2 == 0

  if sub == 10:
    if chapter == 1:
      MONSTERS[st] = {
          "name": "맹독 독수리 여왕 '하피'",
          "hp": 180,
          "max_hp": 180,
          "atk": 22,
          "exp": 150,
          "gold": 120,
          "is_boss": True,
          "boss_quote": "하늘의 영토에 감히 발을 들인 댓가를 치러라!",
          "image": "https://images.unsplash.com/photo-1534188331102-17849e5d4b1a?q=80&w=1000",
      }
    elif chapter == 2:
      MONSTERS[st] = {
          "name": "개구리 왕자",
          "hp": 720,
          "max_hp": 720,
          "atk": 60,
          "exp": 600,
          "gold": 550,
          "is_boss": True,
          "is_frog_prince": True,
          "boss_quote": "개굴개굴! 내 혀 맛을 보여주마!",
          "image": "https://images.unsplash.com/photo-1534188331102-17849e5d4b1a?q=80&w=1000",
      }
    elif chapter == 4:
      MONSTERS[st] = {
          "name": "월광의 여인 '명월'",
          "hp": 2000,
          "max_hp": 2000,
          "atk": 120,
          "exp": 1500,
          "gold": 1400,
          "is_boss": True,
          "is_myungwol": True,
          "boss_quote": "어두운 밤길을 밝히는 달빛이... 아름답지 않나요? 자, 이 밤의 끝을 함께해요.",
          "image": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?q=80&w=1000",
      }
    elif chapter == 5:
      MONSTERS[st] = {
          "name": "개구리 왕자",
          "hp": 1200,
          "max_hp": 1200,
          "atk": 70,
          "exp": 800,
          "gold": 750,
          "is_boss": True,
          "is_frog_prince": True,
          "boss_quote": "개굴개굴! 연못의 왕자님 몸이다!",
          "image": "https://images.unsplash.com/photo-1534188331102-17849e5d4b1a?q=80&w=1000",
      }
    elif chapter == 10:
      MONSTERS[st] = {
          "name": "천년묵은 구미호",
          "hp": 3000,
          "max_hp": 3000,
          "atk": 160,
          "exp": 1500,
          "gold": 1400,
          "is_boss": True,
          "boss_quote": "감히 내 영역에... 꼬리 아홉 개의 불꽃을 보여주마!",
          "image": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?q=80&w=1000",
      }
    elif chapter == 15:
      MONSTERS[st] = {
          "name": "거대 바다표범",
          "hp": 4500,
          "max_hp": 4500,
          "atk": 210,
          "exp": 2200,
          "gold": 2000,
          "is_boss": True,
          "boss_quote": "크르릉! 얼어붙은 바다의 영토에 웬 녀석이냐!",
          "image": "https://images.unsplash.com/photo-1534188331102-17849e5d4b1a?q=80&w=1000",
      }
    elif chapter == 20:
      MONSTERS[st] = {
          "name": "황제 펭귄 군주",
          "hp": 6000,
          "max_hp": 6000,
          "atk": 280,
          "exp": 3000,
          "gold": 3000,
          "is_boss": True,
          "boss_quote": "노는 게 제일 좋아!",
          "image": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?q=80&w=1000",
      }
    elif chapter == 30:
      MONSTERS[st] = {
          "name": "최종 영역의 수호자 '제니스'",
          "hp": 10000,
          "max_hp": 10000,
          "atk": 400,
          "exp": 5000,
          "gold": 5000,
          "is_boss": True,
          "boss_quote": "모험의 끝에 도달한 것을 치하한다. 하지만 여기서 멈출 것이다!",
          "image": "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?q=80&w=1000",
      }
    else:
      MONSTERS[st] = {
          "name": f"챕터 {chapter} 수호자",
          "hp": 400 * chapter,
          "max_hp": 400 * chapter,
          "atk": 30 + chapter * 12,
          "exp": 200 * chapter,
          "gold": 200 * chapter,
          "is_boss": True,
          "boss_quote": "나를 넘어서지 못한다!",
          "image": "https://images.unsplash.com/photo-1534188331102-17849e5d4b1a?q=80&w=1000",
      }
  else:
    if chapter == 3:
      m_names = [
          "실 끊어진 태엽 인형",
          "기괴한 도자기 인형",
          "저주받은 마리오네트",
      ]
    elif chapter == 4:
      m_names = ["그림자 요괴", "달빛 유령", "환영의 여우비"]
    elif chapter == 30:
      m_names = ["차원 경비병", "공간 왜곡 슬라임", "시간의 파편"]
    elif is_antarctic:
      m_names = ["설원 늑대", "아이스 좀비", "설인 (예티)"]
    else:
      m_names = ["아기 원숭이", "정글 가지뱀", "나무늘보"]

    m_name = m_names[(st + sub) % len(m_names)]
    monster_data = {
        "name": m_name,
        "hp": 20 + st * 12,
        "max_hp": 20 + st * 12,
        "atk": 8 + st * 4,
        "exp": 25 + st * 5,
        "gold": 20 + st * 4,
        "image": "https://images.unsplash.com/photo-1540573133985-87b6da6d54a9?q=80&w=1000",
    }

    if m_name == "기괴한 도자기 인형":
      monster_data["is_puppet"] = True
    elif m_name == "저주받은 마리오네트":
      monster_data["is_cursed_witch"] = True

    MONSTERS[st] = monster_data


def get_monster(stage):
  s = min(stage, 300)
  return MONSTERS.get(s, MONSTERS[1]).copy()


SHOP_ITEMS = {
    "싸구려 생선 통조림": {
        "price": 120,
        "desc": "전투 중 HP를 30 회복합니다.",
        "type": "heal",
        "value": 30,
    },
    "츄르": {
        "price": 2000,
        "desc": "전투 중 HP를 300 대량 회복합니다.",
        "type": "heal",
        "value": 300,
    },
    "신선한 캣닢": {
        "price": 180,
        "desc": "다음 1턴 동안 공격력이 1.1배 증가합니다.",
        "type": "buff_atk",
    },
    "코코넛 껍질": {
        "price": 150,
        "desc": "적의 다음 공격 데미지를 10% 감소시킵니다.",
        "type": "defend",
    },
    "반짝이는 털뭉치": {
        "price": 165,
        "desc": "다음 1턴 동안 적의 공격력을 20% 감소시킵니다.",
        "type": "debuff_enemy",
    },
}

SHOP_EQUIPMENTS = {
    "튼튼한 나뭇가지": {
        "slot": "weapon",
        "price": 450,
        "atk": 5,
        "desc": "공격력 +5 증가 (중복 구매 가능)",
    },
    "상어 이빨 단검": {
        "slot": "weapon",
        "price": 1200,
        "atk": 12,
        "desc": "공격력 +12 증가 (중복 구매 가능)",
    },
    "황금 발톱 블레이드": {
        "slot": "weapon",
        "price": 3000,
        "atk": 25,
        "desc": "공격력 +25 증가 (중복 구매 가능)",
    },
    "질긴 잎사귀 갑옷": {
        "slot": "armor",
        "price": 375,
        "hp": 30,
        "desc": "최대 체력 +30 증가 (중복 구매 가능)",
    },
    "거북 껍데기 방어구": {
        "slot": "armor",
        "price": 1050,
        "hp": 70,
        "desc": "최대 체력 +70 증가 (중복 구매 가능)",
    },
    "정글 왕의 망토": {
        "slot": "armor",
        "price": 2700,
        "hp": 150,
        "desc": "최대 체력 +150 증가 (중복 구매 가능)",
    },
}


def load_data():
  with data_lock:
    if not os.path.exists(DATA_FILE):
      return {}
    try:
      with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
    except Exception:
      return {}


def save_data(data):
  with data_lock:
    try:
      with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
      print(f"❌ 데이터 저장 오류: {e}")


def format_stage_name(stage_num):
  chapter = (stage_num - 1) // 10 + 1
  sub = (stage_num - 1) % 10 + 1
  return f"Stage {chapter}-{sub}"


def check_and_apply_level_up(cat):
  unlocked_msg = ""
  while cat["level"] < 200:
    req_exp = cat["level"] * 250
    if cat["exp"] >= req_exp:
      cat["exp"] -= req_exp
      cat["level"] += 1
      cat["max_hp"] += 20
      cat["hp"] = cat["max_hp"]
      cat["atk"] += 5

      if cat["level"] % 5 == 0:
        available_skills = [
            s["name"]
            for s in ALL_SKILLS
            if s["name"] not in cat["unlocked_pool"]
        ]
        if available_skills:
          new_skill = random.choice(available_skills)
          cat["skills"].append(new_skill)
          cat["unlocked_pool"].append(new_skill)
          unlocked_msg += f"\n🎉 **[스킬 해금!]** 새로운 스킬 **[{new_skill}]**을(를) 배웠습니다!"
    else:
      break

  if cat["level"] >= 200:
    cat["level"] = 200
    cat["exp"] = 0

  return unlocked_msg


@bot.event
async def on_ready():
  print(f"Logged in as {bot.user} (ID: {bot.user.id})")
  try:
    synced = await bot.tree.sync()
    print(f"✅ 글로벌 슬래시 명령어 {len(synced)}개 동기화 완료!")
  except Exception as e:
    print(f"❌ 명령어 동기화 실패: {e}")
  print("====== 🐾 고양이 키우기 봇 준비 완료! ======")


# --- 1. 스테이지 선택 뷰 (재사용 충돌 방지 안전 버전) ---
class StageSelect(discord.ui.Select):

  def __init__(self, max_stage):
    options = []
    available_stages = [1]
    for s in range(11, 301, 10):
      if s <= max_stage:
        available_stages.append(s)

    if max_stage not in available_stages and max_stage <= 300:
      available_stages.append(max_stage)

    available_stages = sorted(list(set(available_stages)))

    for s in available_stages:
      s_name = format_stage_name(s)
      chapter_num = (s - 1) // 10 + 1
      options.append(
          discord.SelectOption(
              label=f"🚩 {s_name} (챕터 {chapter_num} 시작)",
              description=f"제{chapter_num}구역 모험 시작점",
              value=str(s),
          )
      )

    super().__init__(
        placeholder="이동할 챕터(시작 스테이지)를 선택하세요...",
        min_values=1,
        max_values=1,
        options=options,
    )

  async def callback(self, interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    data = load_data()
    cat = data.get(user_id)
    if not cat:
      await interaction.response.send_message(
          "고양이 정보를 찾을 수 없습니다.", ephemeral=True
      )
      return

    stage_num = int(self.values[0])
    cat["stage"] = stage_num
    save_data(data)

    enemy = get_monster(cat["stage"])
    st_title = format_stage_name(cat["stage"])
    chapter_num = (cat["stage"] - 1) // 10 + 1
    theme_icon = "🧊 지역" if chapter_num % 2 == 0 else "🌴 지역"

    embed = discord.Embed(
        title=f"{theme_icon} {st_title} 탐험 중...",
        description=(
            f"야생 **{enemy['name']}**이(가) 나타났다!\n\n🐾 **내 고양이 정보**\n• 이름: {cat['name']} (Lv.{cat['level']})\n• 체력: ❤️ {cat['hp']} / {cat['max_hp']}\n• 공격력: ⚔️ {cat['atk']}\n\n👾 **적 정보**\n• 이름: {enemy['name']}\n• 체력: ❤️ {enemy['hp']} / {enemy['max_hp']}\n• 공격력: ⚔️ {enemy['atk']}"
        ),
        color=discord.Color.purple()
        if enemy.get("is_boss")
        else discord.Color.orange(),
    )
    if enemy.get("boss_quote"):
      embed.add_field(
          name="💬 보스의 한마디",
          value=f'*"{enemy["boss_quote"]}"*',
          inline=False,
      )
    embed.set_thumbnail(url=enemy["image"])

    view = BattleView(user_id, enemy)
    await interaction.response.edit_message(embed=embed, view=view)


class StageSelectView(discord.ui.View):

  def __init__(self, max_stage):
    super().__init__(timeout=180)
    self.add_item(StageSelect(max_stage))


class AbandonConfirmView(discord.ui.View):

  def __init__(self, user_id):
    super().__init__(timeout=60)
    self.user_id = user_id

  @discord.ui.button(label="😭 정말로 놓아주기", style=discord.ButtonStyle.danger)
  async def confirm_abandon(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    if str(interaction.user.id) != self.user_id:
      await interaction.response.send_message(
          "본인의 고양이만 조작할 수 있습니다!", ephemeral=True
      )
      return

    data = load_data()
    if self.user_id in data:
      cat_name = data[self.user_id]["name"]
      del data[self.user_id]
      save_data(data)

      embed = discord.Embed(
          title="💔 고양이와 이별했습니다...",
          description=(
              f"**{cat_name}**이(가) 모험의 땅 너머로 자유롭게 떠났습니다.\n`/입양` 명령어로 새로운 고양이를 맞이할 수 있습니다."
          ),
          color=discord.Color.red(),
      )
      await interaction.response.edit_message(
          content=None, embed=embed, view=None
      )


# --- 2. 상점 선택 뷰 ---
class ShopSelect(discord.ui.Select):

  def __init__(self, user_id):
    options = []
    for item_name, info in SHOP_ITEMS.items():
      options.append(
          discord.SelectOption(
              label=f"[소모품] {item_name} ({info['price']} Gold)",
              description=info["desc"],
              value=f"item_{item_name}",
          )
      )
    for eq_name, info in SHOP_EQUIPMENTS.items():
      slot_str = "무기" if info["slot"] == "weapon" else "방어구"
      options.append(
          discord.SelectOption(
              label=f"[{slot_str}] {eq_name} ({info['price']} Gold)",
              description=info["desc"],
              value=f"eq_{eq_name}",
          )
      )

    super().__init__(
        placeholder="구매할 소모품 또는 장비를 선택하세요...",
        min_values=1,
        max_values=1,
        options=options,
    )
    self.user_id = user_id

  async def callback(self, interaction: discord.Interaction):
    data = load_data()
    cat = data[self.user_id]
    chosen_val = self.values[0]

    if chosen_val.startswith("item_"):
      chosen_item = chosen_val.replace("item_", "", 1)
      item_info = SHOP_ITEMS[chosen_item]

      if cat["gold"] < item_info["price"]:
        await interaction.response.send_message(
            "❌ 골드가 부족합니다! 모험을 더 돌고 와주세요.", ephemeral=True
        )
        return

      cat["gold"] -= item_info["price"]
      cat["inventory"][chosen_item] += 1
      save_data(data)

      await interaction.response.send_message(
          f"🛒 **[{chosen_item}]**을(를) 구매했습니다! (보유 골드: {cat['gold']} Gold, 현재 보유량: {cat['inventory'][chosen_item]}개)",
          ephemeral=True,
      )

    elif chosen_val.startswith("eq_"):
      chosen_eq = chosen_val.replace("eq_", "", 1)
      eq_info = SHOP_EQUIPMENTS[chosen_eq]
      slot = eq_info["slot"]

      if cat["gold"] < eq_info["price"]:
        await interaction.response.send_message(
            "❌ 골드가 부족합니다! 모험을 더 돌고 와주세요.", ephemeral=True
        )
        return

      cat["gold"] -= eq_info["price"]

      if chosen_eq not in cat["equipment_counts"]:
        cat["equipment_counts"][chosen_eq] = 0
      cat["equipment_counts"][chosen_eq] += 1

      if slot == "weapon":
        cat["atk"] += eq_info["atk"]
        stat_msg = f"공격력 +{eq_info['atk']} (총 보유 개수: {cat['equipment_counts'][chosen_eq]}개)"
      elif slot == "armor":
        cat["max_hp"] += eq_info["hp"]
        stat_msg = f"최대 체력 +{eq_info['hp']} (총 보유 개수: {cat['equipment_counts'][chosen_eq]}개)"

      save_data(data)

      await interaction.response.send_message(
          f"🛡️ **[{chosen_eq}]** 구매 완료! {stat_msg} (남은 골드: {cat['gold']} Gold)",
          ephemeral=True,
      )


class ShopView(discord.ui.View):

  def __init__(self, user_id):
    super().__init__(timeout=180)
    self.user_id = user_id
    self.add_item(ShopSelect(user_id))

  @discord.ui.button(
      label="🏠 로비로 돌아가기",
      style=discord.ButtonStyle.secondary,
      row=1,
  )
  async def back_to_lobby(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    if str(interaction.user.id) != self.user_id:
      await interaction.response.send_message(
          "본인의 고양이만 조작할 수 있습니다!", ephemeral=True
      )
      return

    data = load_data()
    cat = data[self.user_id]
    req_exp = cat["level"] * 250 if cat["level"] < 200 else 0
    skills_text = (
        ", ".join([f"`{s}`" for s in cat["skills"]])
        if cat["skills"]
        else "아직 배운 스킬이 없습니다."
    )
    st_name = format_stage_name(cat["stage"])
    max_st_name = format_stage_name(cat.get("max_stage", 1))

    embed = discord.Embed(
        title=f"🏡 {cat['name']}의 메인 로비",
        description="안전한 마을 홈 화면입니다.",
        color=discord.Color.blue(),
    )
    embed.add_field(name="레벨", value=f"Lv.{cat['level']} / 200", inline=True)
    embed.add_field(
        name="스테이지",
        value=f"🚩 {st_name} (최고기록: {max_st_name})",
        inline=True,
    )
    embed.add_field(
        name="다음 레벨업까지 EXP",
        value=f"{cat['exp']} / {req_exp}"
        if cat["level"] < 200
        else "최대 레벨 도달",
        inline=True,
    )
    embed.add_field(
        name="체력 (HP)", value=f"❤️ {cat['hp']} / {cat['max_hp']}", inline=True
    )
    embed.add_field(name="공격력", value=f"⚔️ {cat['atk']}", inline=True)
    embed.add_field(name="보유 골드", value=f"💰 {cat['gold']} Gold", inline=True)
    embed.add_field(name="⚡ 보유 스킬 목록", value=skills_text, inline=False)
    embed.set_thumbnail(
        url="https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?q=80&w=1000"
    )
    await interaction.response.edit_message(
        content=None, embed=embed, view=LobbyView(self.user_id)
    )


class ItemSelect(discord.ui.Select):

  def __init__(self, enemy, user_id):
    data = load_data()
    cat = data[user_id]
    options = []

    for item_name, count in cat["inventory"].items():
      if count > 0:
        options.append(
            discord.SelectOption(
                label=f"{item_name} (보유: {count}개)",
                description=SHOP_ITEMS[item_name]["desc"],
                value=item_name,
            )
        )

    if not options:
      options.append(
          discord.SelectOption(
              label="사용 가능한 아이템 없음",
              description="상점에서 아이템을 구매하세요.",
              value="none",
          )
      )

    super().__init__(
        placeholder="사용할 아이템을 선택하세요...",
        min_values=1,
        max_values=1,
        options=options,
    )
    self.enemy = enemy
    self.user_id = user_id

  async def callback(self, interaction: discord.Interaction):
    if self.values[0] == "none":
      await interaction.response.send_message(
          "❌ 보유 중인 아이템이 없습니다!", ephemeral=True
      )
      return

    data = load_data()
    cat = data[self.user_id]
    chosen_item = self.values[0]

    if cat["inventory"].get(chosen_item, 0) <= 0:
      await interaction.response.send_message(
          f"❌ **[{chosen_item}]** 아이템이 부족합니다!", ephemeral=True
      )
      return

    cat["inventory"][chosen_item] -= 1
    item_info = SHOP_ITEMS[chosen_item]
    item_type = item_info["type"]
    log_msg = ""

    if item_type == "heal":
      heal_amt = item_info["value"]
      cat["hp"] = min(cat["max_hp"], cat["hp"] + heal_amt)
      log_msg = f"🧪 **{cat['name']}**이(가) **[{chosen_item}]**을(를) 사용해 체력을 **+{heal_amt}** 회복했다! (❤️ {cat['hp']}/{cat['max_hp']})"
    elif item_type == "buff_atk":
      cat["temp_atk_buff"] = 1.1
      log_msg = f"🌿 **{cat['name']}**이(가) **[{chosen_item}]**을(를) 섭취했다! 이번 턴 공격력이 **1.1배** 상승합니다!"
    elif item_type == "defend":
      cat["temp_defend"] = True
      log_msg = f"🥥 **{cat['name']}**이(가) **[{chosen_item}]**(으)로 방어 태세를 갖췄다! 적의 다음 공격 데미지가 **10% 감소**합니다."
    elif item_type == "debuff_enemy":
      self.enemy["temp_debuff"] = True
      log_msg = f"🧶 **{cat['name']}**이(가) **[{chosen_item}]**을(를) 던져 적의 주의를 흐렸다! 적의 다음 공격력이 **20% 감소**합니다."

    c_dmg = max(1, random.randint(self.enemy["atk"] - 2, self.enemy["atk"] + 2))
    if self.enemy.get("temp_debuff"):
      c_dmg = int(c_dmg * 0.8)
      self.enemy.pop("temp_debuff", None)
    if cat.get("temp_defend"):
      c_dmg = int(c_dmg * 0.9)
      cat.pop("temp_defend", None)

    cat["hp"] = max(0, cat["hp"] - c_dmg)
    counter_log = f"👾 {self.enemy['name']}의 반격! **{c_dmg}**의 피해를 입었습니다."

    if cat["hp"] <= 0:
      lost_gold = cat["gold"] // 2
      cat["gold"] -= lost_gold
      cat["stage"] = 1
      cat["hp"] = cat["max_hp"]
      cat["skill_cooldown"] = False
      save_data(data)
      embed = discord.Embed(
          title="💀 전투 패배...",
          description=(
              f"{log_msg}\n\n쓰러졌습니다... 체력이 완전히 회복되어 로비로 돌아왔습니다. (골드 50% 분실: **-{lost_gold} Gold**)"
          ),
          color=discord.Color.red(),
      )
      await interaction.response.edit_message(embed=embed, view=LobbyView(self.user_id))
      return

    save_data(data)
    next_view = BattleView(self.user_id, self.enemy)
    await interaction.response.edit_message(
        embed=next_view.create_embed(f"{log_msg}\n{counter_log}"), view=next_view
    )


class ItemSelectView(discord.ui.View):

  def __init__(self, enemy, user_id):
    super().__init__(timeout=180)
    self.add_item(ItemSelect(enemy, user_id))


class LobbyView(discord.ui.View):

  def __init__(self, user_id):
    super().__init__(timeout=180)
    self.user_id = user_id

  @discord.ui.button(
      label="⚔️ 모험 출발 (현재 스테이지)",
      style=discord.ButtonStyle.success,
      row=0,
  )
  async def start_adventure_btn(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    if str(interaction.user.id) != self.user_id:
      await interaction.response.send_message(
          "본인의 고양이만 조작할 수 있습니다!", ephemeral=True
      )
      return

    data = load_data()
    cat = data[self.user_id]
    enemy = get_monster(cat["stage"])
    st_title = format_stage_name(cat["stage"])
    chapter_num = (cat["stage"] - 1) // 10 + 1
    theme_icon = "🧊 지역" if chapter_num % 2 == 0 else "🌴 지역"

    embed = discord.Embed(
        title=f"{theme_icon} {st_title} 탐험 중...",
        description=(
            f"야생 **{enemy['name']}**이(가) 나타났다!\n\n🐾 **내 고양이 정보**\n• 이름: {cat['name']} (Lv.{cat['level']})\n• 체력: ❤️ {cat['hp']} / {cat['max_hp']}\n• 공격력: ⚔️ {cat['atk']}\n\n👾 **적 정보**\n• 이름: {enemy['name']}\n• 체력: ❤️ {enemy['hp']} / {enemy['max_hp']}\n• 공격력: ⚔️ {enemy['atk']}"
        ),
        color=discord.Color.purple()
        if enemy.get("is_boss")
        else discord.Color.orange(),
    )
    if enemy.get("boss_quote"):
      embed.add_field(
          name="💬 보스의 한마디",
          value=f'*"{enemy["boss_quote"]}"*',
          inline=False,
      )
    embed.set_thumbnail(url=enemy["image"])

    view = BattleView(self.user_id, enemy)
    await interaction.response.edit_message(embed=embed, view=view)

  @discord.ui.button(
      label="🚩 스테이지 선택", style=discord.ButtonStyle.primary, row=0
  )
  async def select_stage_btn(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    if str(interaction.user.id) != self.user_id:
      await interaction.response.send_message(
          "본인의 고양이만 조작할 수 있습니다!", ephemeral=True
      )
      return

    data = load_data()
    cat = data.get(self.user_id, {})

    max_stage = cat.get("max_stage", 1)
    if not isinstance(max_stage, int):
      max_stage = 1

    # 매번 새로운 뷰 객체를 생성하여 충돌 방지
    view = StageSelectView(max_stage)
    max_st_name = format_stage_name(max_stage)

    await interaction.response.edit_message(
        content=f"🗺️ 도전할 챕터를 선택하세요! (최고 기록: {max_st_name})",
        view=view,
    )

  @discord.ui.button(
      label="🛒 잡화 및 장비 상점", style=discord.ButtonStyle.secondary, row=1
  )
  async def shop_btn(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    if str(interaction.user.id) != self.user_id:
      await interaction.response.send_message(
          "본인의 고양이만 조작할 수 있습니다!", ephemeral=True
      )
      return

    data = load_data()
    cat = data[self.user_id]

    eq_summary = (
        ", ".join([f"{k} {v}개" for k, v in cat["equipment_counts"].items() if v > 0])
        or "구매한 장비 없음"
    )

    embed = discord.Embed(
        title="🛒 모험 상점 (소모품 & 장비)",
        description=(
            f"환영합니다! 골드를 소모해 장비를 무한 중복 구매하고 스펙을 키우세요.\n💰 보유 골드: **{cat['gold']} Gold**\n\n🛡️ **구매한 장비 현황**:\n{eq_summary}\n\n🎒 **보유 소모품**:\n• 싸구려 생선 통조림: {cat['inventory']['싸구려 생선 통조림']}개\n• 츄르: {cat['inventory']['츄르']}개\n• 신선한 캣닢: {cat['inventory']['신선한 캣닢']}개\n• 코코넛 껍질: {cat['inventory']['코코넛 껍질']}개\n• 반짝이는 털뭉치: {cat['inventory']['반짝이는 털뭉치']}개"
        ),
        color=discord.Color.gold(),
    )
    await interaction.response.edit_message(
        content=None, embed=embed, view=ShopView(self.user_id)
    )

  @discord.ui.button(label="📜 내 정보", style=discord.ButtonStyle.primary, row=1)
  async def info_btn(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    if str(interaction.user.id) != self.user_id:
      await interaction.response.send_message(
          "본인의 고양이만 조작할 수 있습니다!", ephemeral=True
      )
      return

    data = load_data()
    cat = data[self.user_id]
    req_exp = cat["level"] * 250 if cat["level"] < 200 else 0
    skills_text = (
        ", ".join([f"`{s}`" for s in cat["skills"]])
        if cat["skills"]
        else "아직 배운 스킬이 없습니다."
    )
    inv_text = ", ".join(
        [f"{k} {v}개" for k, v in cat["inventory"].items() if v > 0]
    )
    if not inv_text:
      inv_text = "보유 중인 아이템이 없습니다."

    eq_summary = (
        ", ".join([f"{k} {v}개" for k, v in cat["equipment_counts"].items() if v > 0])
        or "없음"
    )

    st_name = format_stage_name(cat["stage"])
    max_st_name = format_stage_name(cat.get("max_stage", 1))

    curse_left = cat.get("curse_turns", 0)
    curse_text = (
        f"💀 저주 걸림 (남은 스테이지: {curse_left}회)"
        if curse_left > 0
        else "정상 (저주 없음)"
    )

    embed = discord.Embed(
        title=f"🏡 {cat['name']}의 메인 로비",
        description="안전한 마을 홈 화면입니다.",
        color=discord.Color.blue(),
    )
    embed.add_field(name="레벨", value=f"Lv.{cat['level']} / 200", inline=True)
    embed.add_field(
        name="스테이지",
        value=f"🚩 {st_name} (최고기록: {max_st_name})",
        inline=True,
    )
    embed.add_field(
        name="다음 레벨업까지 EXP",
        value=f"{cat['exp']} / {req_exp}"
        if cat["level"] < 200
        else "최대 레벨 도달",
        inline=True,
    )
    embed.add_field(
        name="체력 (HP)", value=f"❤️ {cat['hp']} / {cat['max_hp']}", inline=True
    )
    embed.add_field(name="공격력", value=f"⚔️ {cat['atk']}", inline=True)
    embed.add_field(name="보유 골드", value=f"💰 {cat['gold']} Gold", inline=True)
    embed.add_field(name="상태 이상", value=curse_text, inline=True)
    embed.add_field(name="🛡️ 장비 보유 현황", value=eq_summary, inline=False)
    embed.add_field(name="⚡ 보유 스킬", value=skills_text, inline=False)
    embed.add_field(name="🎒 보유 아이템", value=inv_text, inline=False)
    embed.set_thumbnail(
        url="https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?q=80&w=1000"
    )
    await interaction.response.edit_message(content=None, embed=embed, view=self)

  @discord.ui.button(
      label="💔 고양이와 이별", style=discord.ButtonStyle.danger, row=2
  )
  async def abandon_btn(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    if str(interaction.user.id) != self.user_id:
      await interaction.response.send_message(
          "본인의 고양이만 조작할 수 있습니다!", ephemeral=True
      )
      return

    data = load_data()
    cat = data[self.user_id]
    embed = discord.Embed(
        title="⚠️ 고양이와 정말로 이별하시겠습니까?",
        description=(
            f"**{cat['name']}**이를(를) 떠나보내면 지금까지 키운 정보가 **모두 삭제**됩니다."
        ),
        color=discord.Color.red(),
    )
    await interaction.response.edit_message(
        content=None, embed=embed, view=AbandonConfirmView(self.user_id)
    )


class StageWinView(discord.ui.View):

  def __init__(self, user_id):
    super().__init__(timeout=180)
    self.user_id = user_id

  @discord.ui.button(
      label="🚩 다음 스테이지 계속", style=discord.ButtonStyle.success
  )
  async def next_adventure(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    if str(interaction.user.id) != self.user_id:
      await interaction.response.send_message(
          "본인의 고양이만 조작할 수 있습니다!", ephemeral=True
      )
      return

    data = load_data()
    cat = data[self.user_id]

    if cat.get("curse_turns", 0) > 0:
      cat["curse_turns"] -= 1

    if cat["stage"] < 300:
      cat["stage"] += 1
      cat["max_stage"] = max(cat.get("max_stage", 1), cat["stage"])

    enemy = get_monster(cat["stage"])
    save_data(data)

    st_title = format_stage_name(cat["stage"])
    chapter_num = (cat["stage"] - 1) // 10 + 1
    theme_icon = "🧊 지역" if chapter_num % 2 == 0 else "🌴 지역"

    embed = discord.Embed(
        title=f"{theme_icon} {st_title} 탐험 중...",
        description=(
            f"야생 **{enemy['name']}**이(가) 나타났다!\n\n🐾 **내 고양이 정보**\n• 이름: {cat['name']} (Lv.{cat['level']})\n• 체력: ❤️ {cat['hp']} / {cat['max_hp']}\n• 공격력: ⚔️ {cat['atk']}\n\n👾 **적 정보**\n• 이름: {enemy['name']}\n• 체력: ❤️ {enemy['hp']} / {enemy['max_hp']}\n• 공격력: ⚔️ {enemy['atk']}"
        ),
        color=discord.Color.purple()
        if enemy.get("is_boss")
        else discord.Color.orange(),
    )
    if enemy.get("boss_quote"):
      embed.add_field(
          name="💬 보스의 한마디",
          value=f'*"{enemy["boss_quote"]}"*',
          inline=False,
      )
    embed.set_thumbnail(url=enemy["image"])
    await interaction.response.edit_message(
        embed=embed, view=BattleView(self.user_id, enemy)
    )

  @discord.ui.button(
      label="🏠 메인 로비로 복귀", style=discord.ButtonStyle.secondary
  )
  async def go_lobby(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    if str(interaction.user.id) != self.user_id:
      await interaction.response.send_message(
          "본인의 고양이만 조작할 수 있습니다!", ephemeral=True
      )
      return

    data = load_data()
    cat = data[self.user_id]

    embed = discord.Embed(
        title=f"🏡 {cat['name']}의 메인 로비",
        description="안전한 홈 화면으로 복귀했습니다. (현재 체력은 유지됩니다)",
        color=discord.Color.blue(),
    )
    await interaction.response.edit_message(
        content=None, embed=embed, view=LobbyView(self.user_id)
    )


class SkillSelect(discord.ui.Select):

  def __init__(self, skills, enemy, user_id):
    options = [
        discord.SelectOption(
            label=s_name,
            description=SKILL_DICT.get(s_name, {}).get(
                "desc", "신비로운 모험 스킬"
            ),
        )
        for s_name in skills
    ]
    super().__init__(
        placeholder="사용할 스킬을 선택하세요...",
        min_values=1,
        max_values=1,
        options=options,
    )
    self.enemy = enemy
    self.user_id = user_id

  async def callback(self, interaction: discord.Interaction):
    data = load_data()
    cat = data[self.user_id]
    chosen_skill = self.values[0]

    if cat.get("skill_cooldown", False):
      await interaction.response.send_message(
          "❌ 스킬을 사용한 직후에는 **일반 공격**이나 **아이템**으로 한 턴 쉬어야 합니다!",
          ephemeral=True,
      )
      return

    if self.enemy.get("is_frog_prince"):
      cat["skill_cooldown"] = False
      c_dmg = max(1, random.randint(self.enemy["atk"] - 2, self.enemy["atk"] + 2))
      cat["hp"] = max(0, cat["hp"] - c_dmg)
      save_data(data)

      log_msg = f'🐸 개구리 왕자: **"개굴! 촵촵!"**\n> 혀 채찍에 휘감겨 스킬이 취소되고 기절했습니다! (반격 피해: **{c_dmg}**)'

      if cat["hp"] <= 0:
        lost_gold = cat["gold"] // 2
        cat["gold"] -= lost_gold
        cat["stage"] = 1
        cat["hp"] = cat["max_hp"]
        save_data(data)
        embed = discord.Embed(
            title="💀 전투 패배...",
            description=(
                f"{log_msg}\n\n쓰러졌습니다... 체력이 완전히 회복되어 로비로 돌아왔습니다. (골드 50% 분실: **-{lost_gold} Gold**)"
            ),
            color=discord.Color.red(),
        )
        await interaction.response.edit_message(
            embed=embed, view=LobbyView(self.user_id)
        )
        return

      next_view = BattleView(self.user_id, self.enemy)
      await interaction.response.edit_message(
          embed=next_view.create_embed(log_msg), view=next_view
      )
      return

    if self.enemy.get("is_myungwol"):
      mask_turn = random.choice(["laugh", "tear", "mirror", "fear"])
      self.enemy["current_mask"] = mask_turn

      if mask_turn == "tear":
        cat["skill_cooldown"] = True
        log_msg = (
            "💧 **[눈물의 가면]** 명월이 서글픈 울음소리로 파동을 일으켰다!\n> 고양이의 마력이 흐트러져 **이번 스킬 데미지가 반으로 깎이고 쿨타임이 적용**됩니다!"
        )
        multiplier = 0.75
      else:
        multiplier = 1.5
        log_msg = f"⚡ **{cat['name']}**의 스킬 **[{chosen_skill}]** 발동!"
    else:
      multiplier = 1.5
      log_msg = f"⚡ **{cat['name']}**의 스킬 **[{chosen_skill}]** 발동!"

    base_atk = cat["atk"]
    if cat.get("temp_atk_buff"):
      base_atk = int(base_atk * cat["temp_atk_buff"])
      cat.pop("temp_atk_buff", None)

    if cat.get("curse_turns", 0) > 0:
      base_atk = int(base_atk * 0.7)
      log_msg += "\n💀 *[저주 영향]* 몸이 무거워져 스킬 피해가 감소합니다!"

    dmg = int(base_atk * multiplier)

    if self.enemy.get("is_myungwol") and self.enemy.get(
        "current_mask"
    ) == "mirror":
      mirror_dmg = int(dmg * 0.5)
      cat["hp"] = max(0, cat["hp"] - mirror_dmg)
      log_msg += f"\n🪞 **[거울의 가면]** 명월이 행동을 똑같이 따라 했다! 반사 피해로 **{mirror_dmg}**를 입었다!"

    self.enemy["hp"] -= dmg
    cat["skill_cooldown"] = True
    log_msg += f"\n💥 적에게 **{dmg}**의 피해를 입혔다!"

    if self.enemy.get("is_puppet") and self.enemy["hp"] <= 0:
      if not self.enemy.get("puppet_revived"):
        self.enemy["hp"] = int(self.enemy["max_hp"] * 0.5)
        self.enemy["puppet_revived"] = True
        cat["skill_cooldown"] = False

        revive_msg = (
            f"{log_msg}\n\n🏺 **[꼭두각시 인형 특수능력]**\n> 적이 쓰러지는 순간, **\"와장창!\"** 소리와 함께 사방으로 흩어졌던 도자기 파편들이 기괴하게 모여들며 **다시 부활**했다! (HP 50% 회복)"
        )
        next_view = BattleView(self.user_id, self.enemy)
        await interaction.response.edit_message(
            embed=next_view.create_embed(revive_msg), view=next_view
        )
        return

    if self.enemy["hp"] <= 0 and self.enemy.get("is_myungwol"):
      if not self.enemy.get("true_face_triggered"):
        self.enemy["hp"] = 1
        self.enemy["true_face_triggered"] = True

        cat_name = cat["name"]
        true_face_msg = (
            "🎭 **[가면의 파괴]**\n> 명월의 체력이 다 닳자, 등 뒤에 떠 있던 수많은 달 가면들이 유리조각처럼 **와장창 산산조각** 나며 바닥에 떨어졌다!\n> 캄캄한 어둠 속에서 오직 눈부시게 아름다운 그녀의 진짜 얼굴 하나만이 고요히 드러난다.\n> 🩸 *"
            f'"{cat_name}야... 이 달빛이... 내 진짜 얼굴이야."'
        )

        next_view = BattleView(self.user_id, self.enemy)
        await interaction.response.edit_message(
            embed=next_view.create_embed(true_face_msg), view=next_view
        )
        return

    if self.enemy["hp"] <= 0:
      cat["stage"] += 1
      cat["max_stage"] = max(cat.get("max_stage", 1), cat["stage"])
      cat["gold"] += self.enemy.get("gold", 50)
      cat["exp"] += self.enemy.get("exp", 40)
      cat["skill_cooldown"] = False
      lvl_msg = check_and_apply_level_up(cat)
      save_data(data)

      st_name = format_stage_name(cat["stage"])
      embed = discord.Embed(
          title=(
              "🎉 챕터 보스 처치 승리!"
              if self.enemy.get("is_boss")
              else "🎉 전투 승리!"
          ),
          description=(
              f"{log_msg}\n\n야생 {self.enemy['name']}을(를) 물리쳤습니다!\n🚩 다음 스테이지: **{st_name}**\n💰 보상 획득!{lvl_msg}"
          ),
          color=discord.Color.green(),
      )
      await interaction.response.edit_message(
          embed=embed, view=StageWinView(self.user_id)
      )
      return

    c_dmg = max(1, random.randint(self.enemy["atk"] - 2, self.enemy["atk"] + 2))
    cat["hp"] = max(0, cat["hp"] - c_dmg)
    counter_log = f"👾 {self.enemy['name']}의 반격! **{c_dmg}**의 피해를 입었습니다."

    if cat["hp"] <= 0:
      lost_gold = cat["gold"] // 2
      cat["gold"] -= lost_gold
      cat["stage"] = 1
      cat["hp"] = cat["max_hp"]
      cat["skill_cooldown"] = False
      save_data(data)
      embed = discord.Embed(
          title="💀 전투 패배...",
          description=(
              f"{log_msg}\n\n쓰러졌습니다... 체력이 완전히 회복되어 로비로 돌아왔습니다. (골드 50% 분실: **-{lost_gold} Gold**)"
          ),
          color=discord.Color.red(),
      )
      await interaction.response.edit_message(
          embed=embed, view=LobbyView(self.user_id)
      )
      return

    save_data(data)
    next_view = BattleView(self.user_id, self.enemy)
    await interaction.response.edit_message(
        embed=next_view.create_embed(f"{log_msg}\n{counter_log}"), view=next_view
    )


class SkillSelectView(discord.ui.View):

  def __init__(self, skills, enemy, user_id):
    super().__init__(timeout=180)
    self.add_item(SkillSelect(skills, enemy, user_id))


class BattleView(discord.ui.View):

  def __init__(self, user_id, enemy):
    super().__init__(timeout=180)
    self.user_id = user_id
    self.enemy = enemy

  def create_embed(self, description=""):
    data = load_data()
    cat = data[self.user_id]
    req_exp = cat["level"] * 250 if cat["level"] < 200 else 0
    hp_percent = max(0, self.enemy["hp"]) / self.enemy["max_hp"]
    filled = int(hp_percent * 10)
    hp_bar = "█" * filled + "░" * (10 - filled)
    st_title = format_stage_name(cat["stage"])

    embed = discord.Embed(
        title=f"⚔️ [{st_title}] 전투 중!",
        description=description
        or f"야생 **{self.enemy['name']}**이(가) 나타났다!",
        color=discord.Color.purple()
        if self.enemy.get("is_boss")
        else discord.Color.orange(),
    )
    if self.enemy.get("boss_quote"):
      embed.add_field(
          name="💬 보스의 한마디",
          value=f'*"{self.enemy["boss_quote"]}"*',
          inline=False,
      )

    exp_str = f"{cat['exp']} / {req_exp}" if cat["level"] < 200 else "MAX"
    embed.add_field(
        name=f"🐱 {cat['name']} (Lv.{cat['level']})",
        value=(
            f"❤️ HP: `{cat['hp']}/{cat['max_hp']}`\n⚔️ 공격력: `{cat['atk']}`\n📈 EXP: `{exp_str}`"
        ),
        inline=True,
    )
    embed.add_field(
        name=f"👾 {self.enemy['name']}",
        value=(
            f"❤️ HP: `{self.enemy['hp']}/{self.enemy['max_hp']}`\n`[{hp_bar}]`"
        ),
        inline=True,
    )
    if "image" in self.enemy:
      embed.set_thumbnail(url=self.enemy["image"])
    embed.set_footer(text=f"💰 보유 골드: {cat['gold']} Gold")
    return embed

  @discord.ui.button(label="⚔️ 일반 공격", style=discord.ButtonStyle.primary)
  async def normal_attack(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    if str(interaction.user.id) != self.user_id:
      await interaction.response.send_message(
          "본인의 고양이만 조작할 수 있습니다!", ephemeral=True
      )
      return

    data = load_data()
    cat = data[self.user_id]
    cat["skill_cooldown"] = False

    log_msg = ""
    base_atk = cat["atk"]
    if cat.get("temp_atk_buff"):
      base_atk = int(base_atk * cat["temp_atk_buff"])
      cat.pop("temp_atk_buff", None)

    if self.enemy.get("is_cursed_witch") and not self.enemy.get(
        "curse_applied"
    ):
      self.enemy["curse_applied"] = True
      cat["curse_turns"] = 5
      log_msg += "🔮 **[저주받은 마리오네트]**가 음산한 주술을 걸었다!\n> 💀 **고양이에게 저주가 내려져 5스테이지 동안 공격력이 30% 감소합니다!**\n"

    if cat.get("curse_turns", 0) > 0:
      base_atk = int(base_atk * 0.7)

    if self.enemy.get("is_myungwol"):
      mask_turn = random.choice(["laugh", "tear", "mirror", "fear"])
      self.enemy["current_mask"] = mask_turn

      if mask_turn == "laugh":
        log_msg += "😁 **[웃음의 가면]** 명월이 가볍게 미소 지으며 은신했다!\n> 고양이의 공격이 빗나갔습니다! (피해량 0)\n"
        dmg = 0
      elif mask_turn == "mirror":
        dmg = random.randint(base_atk - 2, base_atk + 3)
        mirror_dmg = int(dmg * 0.5)
        cat["hp"] = max(0, cat["hp"] - mirror_dmg)
        log_msg += f"🐾 **{cat['name']}**의 공격! **{dmg}** 피해!\n🪞 **[거울의 가면]** 명월이 흉내 내어 반사 피해 **{mirror_dmg}**를 입혔다!\n"
      elif mask_turn == "fear":
        dmg = random.randint(base_atk - 2, base_atk + 3)
        cat["skill_cooldown"] = True
        log_msg += f"🐾 **{cat['name']}**의 공격! **{dmg}** 피해!\n😱 **[공포의 가면]** 명월의 서늘한 시선에 공포에 질렸다! **다음 1턴 동안 행동이 봉인**됩니다!\n"
      else:
        dmg = random.randint(base_atk - 2, base_atk + 3)
        log_msg += f"🐾 **{cat['name']}**의 날렵한 공격! **{dmg}**의 피해를 입혔다!\n"
    else:
      dmg = random.randint(base_atk - 2, base_atk + 3)
      log_msg += f"🐾 **{cat['name']}**의 날렵한 공격! **{dmg}**의 피해를 입혔다!\n"

    self.enemy["hp"] -= dmg

    if self.enemy.get("is_puppet") and self.enemy["hp"] <= 0:
      if not self.enemy.get("puppet_revived"):
        self.enemy["hp"] = int(self.enemy["max_hp"] * 0.5)
        self.enemy["puppet_revived"] = True

        revive_msg = (
            f"{log_msg}\n\n🏺 **[꼭두각시 인형 특수능력]**\n> 적이 쓰러지는 순간, **\"와장창!\"** 소리와 함께 사방으로 흩어졌던 도자기 파편들이 기괴하게 모여들며 **다시 부활**했다! (HP 50% 회복)"
        )
        next_view = BattleView(self.user_id, self.enemy)
        await interaction.response.edit_message(
            embed=next_view.create_embed(revive_msg), view=next_view
        )
        return

    if self.enemy["hp"] <= 0 and self.enemy.get("is_myungwol"):
      if not self.enemy.get("true_face_triggered"):
        self.enemy["hp"] = 1
        self.enemy["true_face_triggered"] = True

        cat_name = cat["name"]
        true_face_msg = (
            "🎭 **[가면의 파괴]**\n> 명월의 체력이 다 닳자, 등 뒤에 떠 있던 수많은 달 가면들이 유리조각처럼 **와장창 산산조각** 나며 바닥에 떨어졌다!\n> 캄캄한 어둠 속에서 오직 눈부시게 아름다운 그녀의 진짜 얼굴 하나만이 고요히 드러난다.\n> 🩸 *"
            f'"{cat_name}야... 이 달빛이... 내 진짜 얼굴이야."'
        )

        next_view = BattleView(self.user_id, self.enemy)
        await interaction.response.edit_message(
            embed=next_view.create_embed(true_face_msg), view=next_view
        )
        return

    if self.enemy["hp"] <= 0:
      cat["stage"] += 1
      cat["max_stage"] = max(cat.get("max_stage", 1), cat["stage"])
      cat["gold"] += self.enemy.get("gold", 30)
      cat["exp"] += self.enemy.get("exp", 50)
      cat["skill_cooldown"] = False
      lvl_msg = check_and_apply_level_up(cat)
      save_data(data)

      st_name = format_stage_name(cat["stage"])
      embed = discord.Embed(
          title="🎉 전투 승리!",
          description=(
              f"{log_msg}\n\n야생 {self.enemy['name']}을(를) 물리쳤습니다!\n🚩 다음 스테이지: **{st_name}**\n💰 보상 획득!{lvl_msg}"
          ),
          color=discord.Color.green(),
      )
      await interaction.response.edit_message(
          embed=embed, view=StageWinView(self.user_id)
      )
      return

    c_dmg = max(1, random.randint(self.enemy["atk"] - 2, self.enemy["atk"] + 2))
    cat["hp"] = max(0, cat["hp"] - c_dmg)
    counter_log = f"👾 {self.enemy['name']}의 반격! **{c_dmg}**의 피해를 입었습니다."

    if cat["hp"] <= 0:
      lost_gold = cat["gold"] // 2
      cat["gold"] -= lost_gold
      cat["stage"] = 1
      cat["hp"] = cat["max_hp"]
      cat["skill_cooldown"] = False
      save_data(data)
      embed = discord.Embed(
          title="💀 전투 패배...",
          description=(
              f"{log_msg}{counter_log}\n\n쓰러졌습니다... 체력이 완전히 회복되어 로비로 돌아왔습니다. (골드 50% 분실: **-{lost_gold} Gold**)"
          ),
          color=discord.Color.red(),
      )
      await interaction.response.edit_message(
          embed=embed, view=LobbyView(self.user_id)
      )
      return

    save_data(data)
    await interaction.response.edit_message(
        embed=self.create_embed(f"{log_msg}\n{counter_log}"), view=self
    )

  @discord.ui.button(label="⚡ 스킬 사용", style=discord.ButtonStyle.success)
  async def use_skill_btn(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    if str(interaction.user.id) != self.user_id:
      await interaction.response.send_message(
          "본인의 고양이만 조작할 수 있습니다!", ephemeral=True
      )
      return

    data = load_data()
    cat = data[self.user_id]
    if not cat["skills"]:
      await interaction.response.send_message(
          "❌ 아직 배운 스킬이 없습니다! 레벨업을 해보세요.", ephemeral=True
      )
      return

    if cat.get("skill_cooldown", False):
      await interaction.response.send_message(
          "❌ 공포에 질렸거나 스킬 직후입니다! **일반 공격**이나 **아이템**으로 턴을 보내주세요.",
          ephemeral=True,
      )
      return

    await interaction.response.edit_message(
        content=f"🐾 **{cat['name']}**의 스킬 창입니다. 사용할 스킬을 골라주세요:",
        view=SkillSelectView(cat["skills"], self.enemy, self.user_id),
    )

  @discord.ui.button(label="🎒 아이템", style=discord.ButtonStyle.primary)
  async def use_item_btn(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    if str(interaction.user.id) != self.user_id:
      await interaction.response.send_message(
          "본인의 고양이만 조작할 수 있습니다!", ephemeral=True
      )
      return

    data = load_data()
    cat = data[self.user_id]
    total_items = sum(cat["inventory"].values())
    if total_items <= 0:
      await interaction.response.send_message(
          "❌ 보유 중인 아이템이 없습니다! 로비 상점에서 구매해주세요.",
          ephemeral=True,
      )
      return

    await interaction.response.edit_message(
        content="🎒 전투 인벤토리입니다. 사용할 아이템을 선택하세요:",
        view=ItemSelectView(self.enemy, self.user_id),
    )

  @discord.ui.button(label="🏃 도망치기", style=discord.ButtonStyle.danger)
  async def run_away_btn(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    if str(interaction.user.id) != self.user_id:
      await interaction.response.send_message(
          "본인의 고양이만 조작할 수 있습니다!", ephemeral=True
      )
      return

    data = load_data()
    cat = data[self.user_id]
    cat["stage"] = 1
    cat["hp"] = cat["max_hp"]
    cat["skill_cooldown"] = False
    save_data(data)

    embed = discord.Embed(
        title="🏃💨 무사히 도망쳤다!",
        description=(
            "안전한 로비(Stage 1-1)로 복귀했습니다. (체력이 모두 회복되었습니다!)"
        ),
        color=discord.Color.blurple(),
    )
    await interaction.response.edit_message(
        content=None, embed=embed, view=LobbyView(self.user_id)
    )


# --- 슬래시 명령어들 ---
@bot.tree.command(name="입양", description="나만의 아기 고양이를 입양합니다!")
async def adopt_cat(interaction: discord.Interaction, name: str):
  user_id = str(interaction.user.id)
  data = load_data()

  if user_id in data:
    await interaction.response.send_message(
        "❌ 이미 입양한 고양이가 있습니다! `/로비` 명령어로 확인해보세요.",
        ephemeral=False,
    )
    return

  data[user_id] = {
      "name": name,
      "level": 1,
      "hp": 80,
      "max_hp": 80,
      "atk": 15,
      "exp": 0,
      "gold": 100,
      "stage": 1,
      "max_stage": 1,
      "skills": [],
      "unlocked_pool": [],
      "skill_cooldown": False,
      "curse_turns": 0,
      "equipment_counts": {},
      "inventory": {
          "싸구려 생선 통조림": 1,
          "츄르": 0,
          "신선한 캣닢": 0,
          "코코넛 껍질": 0,
          "반짝이는 털뭉치": 0,
      },
  }
  save_data(data)

  embed = discord.Embed(
      title="🎉 축하합니다! 새로운 아기 고양이를 입양했습니다!",
      description=(
          f"🐾 이름: **{name}**\n❤️ 체력: 80/80 | ⚔️ 공격력: 15\n🎒 환영 선물로 [싸구려 생선 통조림] 1개를 지급했습니다!"
      ),
      color=discord.Color.gold(),
  )
  embed.set_thumbnail(
      url="https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?q=80&w=1000"
  )
  await interaction.response.send_message(
      embed=embed, view=LobbyView(user_id), ephemeral=False
  )


@bot.tree.command(
    name="로비", description="안전한 마을 메인 로비 화면으로 이동합니다."
)
async def open_lobby(interaction: discord.Interaction):
  user_id = str(interaction.user.id)
  data = load_data()

  if user_id not in data:
    await interaction.response.send_message(
        "❌ 아직 입양한 고양이가 없습니다! 먼저 `/입양 [이름]`을 해주세요.",
        ephemeral=False,
    )
    return

  cat = data[user_id]
  req_exp = cat["level"] * 250 if cat["level"] < 200 else 0
  skills_text = (
      ", ".join([f"`{s}`" for s in cat["skills"]])
      if cat["skills"]
      else "아직 배운 스킬이 없습니다."
  )
  inv_text = ", ".join(
      [f"{k} {v}개" for k, v in cat["inventory"].items() if v > 0]
  )
  if not inv_text:
    inv_text = "보유 중인 아이템이 없습니다."

  eq_summary = (
      ", ".join([f"{k} {v}개" for k, v in cat["equipment_counts"].items() if v > 0])
      or "없음"
  )

  st_name = format_stage_name(cat["stage"])
  max_st_name = format_stage_name(cat.get("max_stage", 1))

  curse_left = cat.get("curse_turns", 0)
  curse_text = (
      f"💀 저주 걸림 (남은 스테이지: {curse_left}회)"
      if curse_left > 0
      else "정상 (저주 없음)"
  )

  embed = discord.Embed(
      title=f"🏡 {cat['name']}의 메인 로비",
      description="안전한 마을 홈 화면입니다.",
      color=discord.Color.blue(),
  )
  embed.add_field(name="레벨", value=f"Lv.{cat['level']} / 200", inline=True)
  embed.add_field(
      name="스테이지",
      value=f"🚩 {st_name} (최고기록: {max_st_name})",
      inline=True,
  )
  embed.add_field(
      name="다음 레벨업까지 EXP",
      value=f"{cat['exp']} / {req_exp}"
      if cat["level"] < 200
      else "최대 레벨 도달",
      inline=True,
  )
  embed.add_field(
      name="체력 (HP)", value=f"❤️ {cat['hp']} / {cat['max_hp']}", inline=True
  )
  embed.add_field(name="공격력", value=f"⚔️ {cat['atk']}", inline=True)
  embed.add_field(name="보유 골드", value=f"💰 {cat['gold']} Gold", inline=True)
  embed.add_field(name="상태 이상", value=curse_text, inline=True)
  embed.add_field(name="🛡️ 장비 보유 현황", value=eq_summary, inline=False)
  embed.add_field(name="⚡ 보유 스킬", value=skills_text, inline=False)
  embed.add_field(name="🎒 보유 아이템", value=inv_text, inline=False)
  embed.set_thumbnail(
      url="https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?q=80&w=1000"
  )
  await interaction.response.send_message(
      embed=embed, view=LobbyView(user_id), ephemeral=False
  )


# --- 테스트용 레벨업 및 스테이지 이동 명령어 ---
@bot.tree.command(
    name="레벨업",
    description="[테스트용] 지정한 수만큼 고양이를 레벨업시킵니다. (최대 200)",
)
async def test_level_up(
    interaction: discord.Interaction, levels: int = 1
):
  user_id = str(interaction.user.id)
  data = load_data()

  if user_id not in data:
    await interaction.response.send_message(
        "❌ 먼저 `/입양 [이름]`으로 고양이를 생성해주세요!", ephemeral=True
    )
    return

  cat = data[user_id]
  target_level = min(200, cat["level"] + levels)
  actual_gained = target_level - cat["level"]

  if actual_gained <= 0:
    await interaction.response.send_message(
        "❌ 이미 최고 레벨(Lv.200)에 도달해 있습니다!", ephemeral=True
    )
    return

  cat["level"] = target_level
  cat["max_hp"] += actual_gained * 20
  cat["hp"] = cat["max_hp"]
  cat["atk"] += actual_gained * 5

  unlocked_skills = []
  for s in ALL_SKILLS:
    if s["name"] not in cat["unlocked_pool"] and len(cat["skills"]) < 5:
      cat["skills"].append(s["name"])
      cat["unlocked_pool"].append(s["name"])
      unlocked_skills.append(s["name"])

  unlocked_stage_target = min(300, ((cat["level"] - 1) // 5) * 10 + 1)
  if unlocked_stage_target > cat.get("max_stage", 1):
    cat["max_stage"] = unlocked_stage_target

  save_data(data)

  skill_text = (
      f"\n🎉 **[스킬 해금]** {', '.join(unlocked_skills)}"
      if unlocked_skills
      else ""
  )
  embed = discord.Embed(
      title="✨ [테스트] 레벨업 완료!",
      description=(
          f"**{cat['name']}**의 레벨이 **Lv.{cat['level']}**이 되었습니다!{skill_text}\n\n• 체력: ❤️ {cat['hp']}/{cat['max_hp']}\n• 공격력: ⚔️ {cat['atk']}"
      ),
      color=discord.Color.green(),
  )
  await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(
    name="스테이지이동",
    description="[테스트용] 원하는 스테이지(1~300)로 즉시 이동합니다.",
)
async def test_move_stage(interaction: discord.Interaction, stage: int):
  user_id = str(interaction.user.id)
  data = load_data()

  if user_id not in data:
    await interaction.response.send_message(
        "❌ 먼저 `/입양 [이름]`으로 고양이를 생성해주세요!", ephemeral=True
    )
    return

  if not (1 <= stage <= 300):
    await interaction.response.send_message(
        "❌ 스테이지 번호는 1부터 300 사이여야 합니다!", ephemeral=True
    )
    return

  cat = data[user_id]
  cat["stage"] = stage
  if stage > cat.get("max_stage", 1):
    cat["max_stage"] = stage
  save_data(data)

  st_title = format_stage_name(stage)
  await interaction.response.send_message(
      f"✨ [테스트] 고양이가 **{st_title}**(스테이지 {stage})로 이동했습니다!\n`/로비`에서 '모험 출발'을 누르면 바로 전투가 시작됩니다.",
      ephemeral=True,
  )


# --- 메인 실행 ---
if __name__ == "__main__":
  flask_thread = threading.Thread(target=run_flask, daemon=True)
  flask_thread.start()

  BOT_TOKEN = os.environ.get("BOT_TOKEN")
  if not BOT_TOKEN:
    print("❌ [Fatal Error] BOT_TOKEN 환경 변수가 설정되어 있지 않습니다!")
    sys.exit(1)

  print("🚀 디스코드 봇에 연결을 시도합니다...")
  bot.run(BOT_TOKEN)