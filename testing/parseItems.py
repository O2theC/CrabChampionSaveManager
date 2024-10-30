from bs4 import BeautifulSoup

# Example HTML content (replace this with your actual HTML content)
html_content = ""

with open("./testing/weaponmods.html","r") as f:
    html_content = f.read()



# Create a BeautifulSoup object
# Create a BeautifulSoup object
soup = BeautifulSoup(html_content, 'html.parser')

# Find all elements with the class 'v-expansion-panel-title__overlay'
overlay_elements = soup.find_all('span', class_='v-expansion-panel-title__overlay')

# Loop through each overlay element and get the text between it and the next 'v-expansion-panel-title__icon'
items = []

unlockedItems = [
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_BouncingShot.DA_WeaponMod_BouncingShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_AcceleratingShot.DA_WeaponMod_AcceleratingShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_ZigZagShot.DA_WeaponMod_ZigZagShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_SpiralShot.DA_WeaponMod_SpiralShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_SnakeShot.DA_WeaponMod_SnakeShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_ChaoticShot.DA_WeaponMod_ChaoticShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_BoomerangShot.DA_WeaponMod_BoomerangShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_OrbitingShot.DA_WeaponMod_OrbitingShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_RecoilShot.DA_WeaponMod_RecoilShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_FastShot.DA_WeaponMod_FastShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_HealthShot.DA_WeaponMod_HealthShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_BigMag.DA_WeaponMod_BigMag",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_HighCaliber.DA_WeaponMod_HighCaliber",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_WindUp.DA_WeaponMod_WindUp",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_SteadyShot.DA_WeaponMod_SteadyShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_TrickShot.DA_WeaponMod_TrickShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_AerialShot.DA_WeaponMod_AerialShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_GripTape.DA_WeaponMod_GripTape",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_BlindFire.DA_WeaponMod_BlindFire",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_MoneyShot.DA_WeaponMod_MoneyShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_TimeShot.DA_WeaponMod_TimeShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_TimeBolt.DA_WeaponMod_TimeBolt",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_UltraShot.DA_WeaponMod_UltraShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_SharpShot.DA_WeaponMod_SharpShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_GlueShot.DA_WeaponMod_GlueShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_BigShot.DA_WeaponMod_BigShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_StreakShot.DA_WeaponMod_StreakShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_MagShot.DA_WeaponMod_MagShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_Uppercut.DA_WeaponMod_Uppercut",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_HeavyShot.DA_WeaponMod_HeavyShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_HeavyHitter.DA_WeaponMod_HeavyHitter",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_RapidFire.DA_WeaponMod_RapidFire",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_LightShot.DA_WeaponMod_LightShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_EscalatingShot.DA_WeaponMod_EscalatingShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_IceShot.DA_WeaponMod_IceShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_FireShot.DA_WeaponMod_FireShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_LightningShot.DA_WeaponMod_LightningShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_PoisonShot.DA_WeaponMod_PoisonShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_ArcaneShot.DA_WeaponMod_ArcaneShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_RandomShot.DA_WeaponMod_RandomShot",
      "/Game/Blueprint/Pickup/WeaponMod/Rare/DA_WeaponMod_ReloadArc.DA_WeaponMod_ReloadArc",
      "/Game/Blueprint/Pickup/WeaponMod/Epic/DA_WeaponMod_ArcShot.DA_WeaponMod_ArcShot",
      "/Game/Blueprint/Pickup/WeaponMod/Epic/DA_WeaponMod_SplitShot.DA_WeaponMod_SplitShot",
      "/Game/Blueprint/Pickup/WeaponMod/Epic/DA_WeaponMod_ScatterShot.DA_WeaponMod_ScatterShot",
      "/Game/Blueprint/Pickup/WeaponMod/Epic/DA_WeaponMod_TargetingShot.DA_WeaponMod_TargetingShot",
      "/Game/Blueprint/Pickup/WeaponMod/Epic/DA_WeaponMod_LinkShot.DA_WeaponMod_LinkShot",
      "/Game/Blueprint/Pickup/WeaponMod/Epic/DA_WeaponMod_DrillShot.DA_WeaponMod_DrillShot",
      "/Game/Blueprint/Pickup/WeaponMod/Epic/DA_WeaponMod_DamageShot.DA_WeaponMod_DamageShot",
      "/Game/Blueprint/Pickup/WeaponMod/Epic/DA_WeaponMod_Supercharged.DA_WeaponMod_Supercharged",
      "/Game/Blueprint/Pickup/WeaponMod/Epic/DA_WeaponMod_Juiced.DA_WeaponMod_Juiced",
      "/Game/Blueprint/Pickup/WeaponMod/Epic/DA_WeaponMod_AuraShot.DA_WeaponMod_AuraShot",
      "/Game/Blueprint/Pickup/WeaponMod/Epic/DA_WeaponMod_PiercingShot.DA_WeaponMod_PiercingShot",
      "/Game/Blueprint/Pickup/WeaponMod/Epic/DA_WeaponMod_BubbleShot.DA_WeaponMod_BubbleShot",
      "/Game/Blueprint/Pickup/WeaponMod/Epic/DA_WeaponMod_PumpkinShot.DA_WeaponMod_PumpkinShot",
      "/Game/Blueprint/Pickup/WeaponMod/Epic/DA_WeaponMod_DaggerArc.DA_WeaponMod_DaggerArc",
      "/Game/Blueprint/Pickup/WeaponMod/Epic/DA_WeaponMod_PiercingWave.DA_WeaponMod_PiercingWave",
      "/Game/Blueprint/Pickup/WeaponMod/Epic/DA_WeaponMod_ArcaneBlast.DA_WeaponMod_ArcaneBlast",
      "/Game/Blueprint/Pickup/WeaponMod/Epic/DA_WeaponMod_ShotgunBlast.DA_WeaponMod_ShotgunBlast",
      "/Game/Blueprint/Pickup/WeaponMod/Epic/DA_WeaponMod_MaceShot.DA_WeaponMod_MaceShot",
      "/Game/Blueprint/Pickup/WeaponMod/Epic/DA_WeaponMod_FireworkShot.DA_WeaponMod_FireworkShot",
      "/Game/Blueprint/Pickup/WeaponMod/Epic/DA_WeaponMod_SparkShot.DA_WeaponMod_SparkShot",
      "/Game/Blueprint/Pickup/WeaponMod/Legendary/DA_WeaponMod_Firepower.DA_WeaponMod_Firepower",
      "/Game/Blueprint/Pickup/WeaponMod/Legendary/DA_WeaponMod_XShot.DA_WeaponMod_XShot",
      "/Game/Blueprint/Pickup/WeaponMod/Legendary/DA_WeaponMod_SquareShot.DA_WeaponMod_SquareShot",
      "/Game/Blueprint/Pickup/WeaponMod/Legendary/DA_WeaponMod_HomingShot.DA_WeaponMod_HomingShot",
      "/Game/Blueprint/Pickup/WeaponMod/Legendary/DA_WeaponMod_DoubleTap.DA_WeaponMod_DoubleTap",
      "/Game/Blueprint/Pickup/WeaponMod/Legendary/DA_WeaponMod_SplashDamage.DA_WeaponMod_SplashDamage",
      "/Game/Blueprint/Pickup/WeaponMod/Legendary/DA_WeaponMod_ProximityBarrage.DA_WeaponMod_ProximityBarrage",
      "/Game/Blueprint/Pickup/WeaponMod/Legendary/DA_WeaponMod_HomingBlades.DA_WeaponMod_HomingBlades",
      "/Game/Blueprint/Pickup/WeaponMod/Legendary/DA_WeaponMod_BombShot.DA_WeaponMod_BombShot",
      "/Game/Blueprint/Pickup/WeaponMod/Legendary/DA_WeaponMod_LandmineShot.DA_WeaponMod_LandmineShot",
      "/Game/Blueprint/Pickup/WeaponMod/Legendary/DA_WeaponMod_TorpedoShot.DA_WeaponMod_TorpedoShot",
      "/Game/Blueprint/Pickup/WeaponMod/Legendary/DA_WeaponMod_FireballShot.DA_WeaponMod_FireballShot",
      "/Game/Blueprint/Pickup/WeaponMod/Legendary/DA_WeaponMod_SharpenedAxe.DA_WeaponMod_SharpenedAxe",
      "/Game/Blueprint/Pickup/WeaponMod/Legendary/DA_WeaponMod_SporeShot.DA_WeaponMod_SporeShot",
      "/Game/Blueprint/Pickup/WeaponMod/Legendary/DA_WeaponMod_IceStorm.DA_WeaponMod_IceStorm",
      "/Game/Blueprint/Pickup/WeaponMod/Legendary/DA_WeaponMod_FireStorm.DA_WeaponMod_FireStorm",
      "/Game/Blueprint/Pickup/WeaponMod/Legendary/DA_WeaponMod_PoisonStorm.DA_WeaponMod_PoisonStorm",
      "/Game/Blueprint/Pickup/WeaponMod/Legendary/DA_WeaponMod_IceStrike.DA_WeaponMod_IceStrike",
      "/Game/Blueprint/Pickup/WeaponMod/Legendary/DA_WeaponMod_FireStrike.DA_WeaponMod_FireStrike"
    ]

for overlay in overlay_elements:
    # Find the next 'v-expansion-panel-title__icon' element
    next_icon = overlay.find_next('span', class_='v-expansion-panel-title__icon')
    
    # Extract the text between the overlay and the icon
    text_between = overlay.next_sibling
    collected_text = []
    
    # Traverse all siblings between overlay and icon
    while text_between and text_between != next_icon:
        if isinstance(text_between, str):  # Make sure we get text nodes, not other tags
            collected_text.append(text_between.strip())
        text_between = text_between.next_sibling
    items.append(''.join(collected_text).replace(" ",""))
for cat in ["Damage","Economy","Elemental","Health","Luck","Skill","Speed"]:
    try:
        items.remove(cat)
    except:
        pass
    
def isUNlocked(item):
    item = item.replace(" ","")
    for uitem in unlockedItems:
        if item in uitem:
            return True
    return False
    
# Join and print the collected text
for item in items:
    print(item," - ",isUNlocked(item))
# print('\n'.join(items))