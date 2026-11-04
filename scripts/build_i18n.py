#!/usr/bin/env python3
"""Generate data/i18n.json: category, rarity and attribute labels for the UI.

Item names come from the game export (scripts/export_translations.py); this file
covers the terms the original TIDBI UI keeps in code: tree categories, rarity,
stats, requirements, elements, sort orders and card headings.

Keys map to the app's language ids: en, zh-Hans, zh-Hant, ru, de, ja, pl.
English is the fallback for every missing translation.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "i18n.json"

# (key, en, zh-Hans, zh-Hant, ru, de, ja, pl)
TERMS: list[tuple[str, str, str, str, str, str, str, str]] = [
    # --- tree categories ---------------------------------------------------
    ("tree.all", "All Items", "全部物品", "全部物品", "Все предметы", "Alle Gegenstände", "すべてのアイテム", "Wszystkie przedmioty"),
    ("tree.armor", "Armor", "护甲", "護甲", "Броня", "Rüstung", "防具", "Zbroja"),
    ("tree.helmets", "Helmets", "头盔", "頭盔", "Шлемы", "Helme", "兜", "Hełmy"),
    ("tree.chest", "Chest Armor", "胸甲", "胸甲", "Нагрудники", "Brustrüstung", "胴防具", "Napierśniki"),
    ("tree.shoulders", "Shoulder Armor", "护肩", "護肩", "Наплечники", "Schulterrüstung", "肩防具", "Naramienniki"),
    ("tree.belts", "Belts", "腰带", "腰帶", "Пояса", "Gürtel", "ベルト", "Pasy"),
    ("tree.gloves", "Gloves", "手套", "手套", "Перчатки", "Handschuhe", "手袋", "Rękawice"),
    ("tree.pants", "Pants", "裤子", "褲子", "Штаны", "Hosen", "ズボン", "Spodnie"),
    ("tree.boots", "Boots", "靴子", "靴子", "Сапоги", "Stiefel", "ブーツ", "Buty"),
    ("tree.shields", "Shields", "盾牌", "盾牌", "Щиты", "Schilde", "盾", "Tarcze"),
    ("tree.weapons", "Weapons", "武器", "武器", "Оружие", "Waffen", "武器", "Broń"),
    ("tree.one_handed", "One handed", "单手", "單手", "Одноручное", "Einhand", "片手", "Jednoręczne"),
    ("tree.two_handed", "Two handed", "双手", "雙手", "Двуручное", "Zweihand", "両手", "Dwuręczne"),
    ("tree.axes", "Axes", "斧", "斧", "Топоры", "Äxte", "斧", "Topory"),
    ("tree.swords", "Swords", "剑", "劍", "Мечи", "Schwerter", "剣", "Miecze"),
    ("tree.maces", "Maces", "锤", "錘", "Булавы", "Streitkolben", "メイス", "Buzdygany"),
    ("tree.wands", "Wands", "法杖", "法杖", "Жезлы", "Zauberstäbe", "ワンド", "Różdżki"),
    ("tree.pistols", "Pistols", "手枪", "手槍", "Пистолеты", "Pistolen", "ピストル", "Pistolety"),
    ("tree.claws", "Claws", "爪", "爪", "Когти", "Klauen", "爪", "Pazury"),
    ("tree.bows", "Bows", "弓", "弓", "Луки", "Bögen", "弓", "Łuki"),
    ("tree.crossbows", "Crossbows", "弩", "弩", "Арбалеты", "Armbrüste", "クロスボウ", "Kusze"),
    ("tree.greataxes", "Greataxes", "巨斧", "巨斧", "Секиры", "Großäxte", "大斧", "Wielkie topory"),
    ("tree.greathammers", "Greathammers", "巨锤", "巨錘", "Молоты", "Großhämmer", "大槌", "Wielkie młoty"),
    ("tree.greatswords", "Greatswords", "巨剑", "巨劍", "Двуручные мечи", "Großschwerter", "大剣", "Wielkie miecze"),
    ("tree.polearms", "Polearms", "长柄武器", "長柄武器", "Древковое оружие", "Stangenwaffen", "長柄武器", "Broń drzewcowa"),
    ("tree.staffs", "Staffs", "长杖", "長杖", "Посохи", "Stäbe", "スタッフ", "Kostury"),
    ("tree.cannons", "Cannons", "火炮", "火砲", "Пушки", "Kanonen", "大砲", "Armaty"),
    ("tree.shotgonnes", "Shotgonnes", "散弹枪", "散彈槍", "Дробовики", "Schrotflinten", "散弾銃", "Strzelby"),
    ("tree.accessories", "Accessories", "饰品", "飾品", "Аксессуары", "Accessoires", "アクセサリー", "Akcesoria"),
    ("tree.rings", "Rings", "戒指", "戒指", "Кольца", "Ringe", "指輪", "Pierścienie"),
    ("tree.necklaces", "Necklaces", "项链", "項鍊", "Ожерелья", "Halsketten", "ネックレス", "Naszyjniki"),
    ("tree.collars", "Collars", "项圈", "項圈", "Ошейники", "Halsbänder", "首輪", "Obroże"),
    ("tree.tags", "Tags", "铭牌", "銘牌", "Бирки", "Anhänger", "タグ", "Znaczniki"),
    ("tree.consumables", "Consumables", "消耗品", "消耗品", "Расходники", "Verbrauchsgüter", "消耗品", "Przedmioty jednorazowe"),
    ("tree.potions", "Potions", "药水", "藥水", "Зелья", "Tränke", "ポーション", "Mikstury"),
    ("tree.fish", "Fish", "鱼", "魚", "Рыба", "Fische", "魚", "Ryby"),
    ("tree.maps", "Maps", "地图", "地圖", "Карты", "Karten", "マップ", "Mapy"),
    ("tree.scrolls", "Scrolls", "卷轴", "卷軸", "Свитки", "Schriftrollen", "巻物", "Zwoje"),
    ("tree.spells", "Spells", "法术", "法術", "Заклинания", "Zauber", "呪文", "Czary"),
    ("tree.socketables", "Socketables", "镶嵌物", "鑲嵌物", "Камни", "Sockelsteine", "ソケット", "Klejnoty"),
    ("tree.classes", "Classes", "职业", "職業", "Классы", "Klassen", "クラス", "Klasy"),
    ("tree.cls_berserker", "Berserker", "狂战士", "狂戰士", "Берсерк", "Berserker", "バーサーカー", "Berserker"),
    ("tree.cls_engineer", "Engineer", "工程师", "工程師", "Инженер", "Ingenieur", "エンジニア", "Inżynier"),
    ("tree.cls_outlander", "Outlander", "漂泊者", "漂泊者", "Чужак", "Fremdling", "アウトランダー", "Wędrowiec"),
    ("tree.cls_embermage", "Embermage", "余烬法师", "餘燼法師", "Маг углей", "Glutmagier", "エンバーマイジ", "Mag Żaru"),
    ("tree.for_pets", "For Pets", "宠物", "寵物", "Питомцы", "Begleiter", "ペット", "Zwierzęta"),
    ("tree.quest_items", "Quest Items", "任务物品", "任務物品", "Квестовые предметы", "Questgegenstände", "クエストアイテム", "Przedmioty zadań"),
    ("tree.sets", "Sets", "套装", "套裝", "Комплекты", "Sets", "セット", "Zestawy"),
    ("tree.favorites", "Favorites", "收藏", "收藏", "Избранное", "Favoriten", "お気に入り", "Ulubione"),

    # --- rarity -----------------------------------------------------------
    ("rarity.Common", "Common", "普通", "普通", "Обычный", "Gewöhnlich", "コモン", "Zwykły"),
    ("rarity.Rare", "Rare", "稀有", "稀有", "Редкий", "Selten", "レア", "Rzadki"),
    ("rarity.Unique", "Unique", "独特", "獨特", "Уникальный", "Einzigartig", "ユニーク", "Unikatowy"),
    ("rarity.Legendary", "Legendary", "传奇", "傳奇", "Легендарный", "Legendär", "レジェンダリー", "Legendarny"),
    ("rarity.Quest item", "Quest item", "任务物品", "任務物品", "Квестовый предмет", "Questgegenstand", "クエストアイテム", "Przedmiot zadania"),
    ("rarity.Quest", "Quest item", "任务物品", "任務物品", "Квестовый предмет", "Questgegenstand", "クエストアイテム", "Przedmiot zadania"),

    # --- stats (Data filter, table, card) ---------------------------------
    ("stat.Level", "Level", "等级", "等級", "Уровень", "Stufe", "レベル", "Poziom"),
    ("stat.DPS", "DPS", "DPS", "DPS", "DPS", "DPS", "DPS", "DPS"),
    ("stat.Physical Damage", "Physical Damage", "物理伤害", "物理傷害", "Физический урон", "Physischer Schaden", "物理ダメージ", "Obrażenia fizyczne"),
    ("stat.Ice Damage", "Ice Damage", "冰霜伤害", "冰霜傷害", "Урон льдом", "Eisschaden", "冷気ダメージ", "Obrażenia od zimna"),
    ("stat.Fire Damage", "Fire Damage", "火焰伤害", "火焰傷害", "Урон огнём", "Feuerschaden", "火ダメージ", "Obrażenia od ognia"),
    ("stat.Electric Damage", "Electric Damage", "闪电伤害", "閃電傷害", "Урон электричеством", "Blitzschaden", "電撃ダメージ", "Obrażenia od elektryczności"),
    ("stat.Poison Damage", "Poison Damage", "毒素伤害", "毒素傷害", "Урон ядом", "Giftschaden", "毒ダメージ", "Obrażenia od trucizny"),
    ("stat.Physical Armor", "Physical Armor", "物理护甲", "物理護甲", "Физическая броня", "Physische Rüstung", "物理防御", "Pancerz fizyczny"),
    ("stat.Ice Armor", "Ice Armor", "冰霜护甲", "冰霜護甲", "Броня от льда", "Eisrüstung", "冷気防御", "Pancerz od zimna"),
    ("stat.Fire Armor", "Fire Armor", "火焰护甲", "火焰護甲", "Броня от огня", "Feuerrüstung", "火防御", "Pancerz od ognia"),
    ("stat.Electric Armor", "Electric Armor", "闪电护甲", "閃電護甲", "Броня от электричества", "Blitzrüstung", "電撃防御", "Pancerz od elektryczności"),
    ("stat.Poison Armor", "Poison Armor", "毒素护甲", "毒素護甲", "Броня от яда", "Giftresistenz", "毒防御", "Pancerz od trucizny"),
    ("stat.Block Chance", "Block Chance", "格挡几率", "格擋機率", "Шанс блокировки", "Blockchance", "ブロック率", "Szansa bloku"),

    # --- requirements -----------------------------------------------------
    ("req.Level", "Level", "等级", "等級", "Уровень", "Stufe", "レベル", "Poziom"),
    ("req.Strength", "Strength", "力量", "力量", "Сила", "Stärke", "筋力", "Siła"),
    ("req.Dexterity", "Dexterity", "敏捷", "敏捷", "Ловкость", "Geschick", "敏捷", "Zręczność"),
    ("req.Focus", "Focus", "专注", "專注", "Концентрация", "Fokus", "集中", "Skupienie"),
    ("req.Vitality", "Vitality", "体力", "體力", "Живучесть", "Vitalität", "体力", "Witalność"),
    ("req.Class", "Class", "职业", "職業", "Класс", "Klasse", "クラス", "Klasa"),

    # --- damage / armor elements -----------------------------------------
    ("element.Physical", "Physical", "物理", "物理", "Физический", "Physisch", "物理", "Fizyczne"),
    ("element.Ice", "Ice", "冰霜", "冰霜", "Лёд", "Eis", "冷気", "Zimno"),
    ("element.Fire", "Fire", "火焰", "火焰", "Огонь", "Feuer", "火", "Ogień"),
    ("element.Electric", "Electric", "闪电", "閃電", "Электричество", "Blitz", "電撃", "Elektryczność"),
    ("element.Poison", "Poison", "毒素", "毒素", "Яд", "Gift", "毒", "Trucizna"),

    # --- sort orders ------------------------------------------------------
    ("sort.type", "by Type", "按类型", "按類型", "По типу", "Nach Typ", "種類順", "Według typu"),
    ("sort.level", "by Level", "按等级", "按等級", "По уровню", "Nach Stufe", "レベル順", "Według poziomu"),
    ("sort.dps", "by DPS", "按 DPS", "按 DPS", "По DPS", "Nach DPS", "DPS順", "Według DPS"),

    # --- card headings and fields ----------------------------------------
    ("label.name", "Name", "名称", "名稱", "Название", "Name", "名前", "Nazwa"),
    ("label.speed", "Speed", "速度", "速度", "Скорость", "Geschwindigkeit", "速度", "Szybkość"),
    ("label.rarity", "Rarity", "稀有度", "稀有度", "Редкость", "Seltenheit", "レア度", "Rzadkość"),
    ("label.set", "Set", "套装", "套裝", "Комплект", "Set", "セット", "Zestaw"),
    ("label.description", "Description", "描述", "描述", "Описание", "Beschreibung", "説明", "Opis"),
    ("label.damage", "Damage", "伤害", "傷害", "Урон", "Schaden", "ダメージ", "Obrażenia"),
    ("label.armor", "Armor", "护甲", "護甲", "Броня", "Rüstung", "防御", "Pancerz"),
    ("label.requirements", "Requirements", "需求", "需求", "Требования", "Anforderungen", "必要条件", "Wymagania"),
    ("label.sockets", "Sockets", "插槽", "插槽", "Гнёзда", "Sockel", "ソケット", "Gniazda"),
    ("label.block", "Block", "格挡", "格擋", "Блок", "Block", "ブロック", "Blok"),
    ("label.random", "Random enchantments", "随机词缀", "隨機詞綴", "Случайные чары", "Zufällige Verzauberungen", "ランダムエンチャント", "Losowe zaklęcia"),
    ("label.setbonuses", "Set bonuses", "套装奖励", "套裝獎勵", "Бонусы комплекта", "Set-Boni", "セットボーナス", "Bonusy zestawu"),
    ("label.allnames", "All languages", "所有语言", "所有語言", "Все языки", "Alle Sprachen", "すべての言語", "Wszystkie języki"),
    ("label.consolemodel", "Console / Model", "内部名 / 模型", "內部名 / 模型", "Консоль / модель", "Konsole / Modell", "コンソール / モデル", "Konsola / model"),
    ("label.console", "Console", "内部名", "內部名", "Консоль", "Konsole", "コンソール", "Konsola"),
    ("label.model", "Model", "模型", "模型", "Модель", "Modell", "モデル", "Model"),

    # --- filter panel / status -------------------------------------------
    ("ui.type_rarity", "Type / Rarity", "类型 / 稀有度", "類型 / 稀有度", "Тип / редкость", "Typ / Seltenheit", "種類 / レア度", "Typ / rzadkość"),
    ("ui.data", "Data", "数据", "資料", "Данные", "Daten", "データ", "Dane"),
    ("ui.requires", "Requires", "需求", "需求", "Требования", "Anforderungen", "必要条件", "Wymagania"),
    ("ui.effects", "Effects", "词缀", "詞綴", "Эффекты", "Effekte", "効果", "Efekty"),
    ("ui.options", "Options", "选项", "選項", "Параметры", "Optionen", "オプション", "Opcje"),
    ("ui.sorting", "Sorting", "排序", "排序", "Сортировка", "Sortierung", "並び替え", "Sortowanie"),
    ("ui.list", "List", "列表", "列表", "Список", "Liste", "リスト", "Lista"),
    ("ui.items", "items", "件物品", "件物品", "предметов", "Gegenstände", "件", "przedmiotów"),
    ("ui.shown", "shown", "已显示", "已顯示", "показано", "angezeigt", "表示中", "pokazano"),
    ("ui.filters", "filters", "个筛选", "個篩選", "фильтров", "Filter", "フィルター", "filtrów"),
    ("ui.select_item", "Select an item", "选择一个物品", "選擇一個物品", "Выберите предмет", "Gegenstand wählen", "アイテムを選択", "Wybierz przedmiot"),
    ("ui.copy", "Copy", "复制", "複製", "Копировать", "Kopieren", "コピー", "Kopiuj"),
    ("ui.copied", "Copied", "已复制", "已複製", "Скопировано", "Kopiert", "コピーしました", "Skopiowano"),

    # --- unit types not in the tree --------------------------------------
    ("unit.dynamite", "Dynamite", "炸药", "炸藥", "Динамит", "Dynamit", "ダイナマイト", "Dynamit"),
    ("unit.location item", "Location Item", "场景物品", "場景物品", "Предмет локации", "Ortsgegenstand", "ロケーションアイテム", "Przedmiot lokacji"),

    # --- affix prefixes ---------------------------------------------------
    ("affix.weapon", "Weapon", "武器", "武器", "Оружие", "Waffe", "武器", "Broń"),
    ("affix.armor_trinket", "Armor/Trinket", "护甲/饰品", "護甲/飾品", "Броня/аксессуар", "Rüstung/Accessoire", "防具/アクセサリー", "Zbroja/Akcesorium"),
    ("affix.armor", "Armor", "护甲", "護甲", "Броня", "Rüstung", "防具", "Zbroja"),
    ("affix.trinket", "Trinket", "饰品", "飾品", "Аксессуар", "Accessoire", "アクセサリー", "Akcesorium"),
]

LANGS = ["en", "zh-Hans", "zh-Hant", "ru", "de", "ja", "pl"]


def main() -> None:
    data: dict[str, dict[str, str]] = {}
    for row in TERMS:
        key, *values = row
        data[key] = dict(zip(LANGS, values))
    OUT.write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"  i18n.json {OUT.stat().st_size / 1024:8.1f} KiB, {len(data)} keys")


if __name__ == "__main__":
    main()
