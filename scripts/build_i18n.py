#!/usr/bin/env python3
"""Generate data/i18n.json: category, rarity, attribute and control labels for the UI.

Item names come from the game export (scripts/export_translations.py); this file
covers the terms the original TIDBI UI keeps in code: tree categories, rarity,
stats, requirements, elements, sort orders, card headings and the labels of
interface controls (buttons, placeholders, checkboxes and toasts).

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
    ("tree.shoulders", "Shoulder Armor", "肩甲", "肩甲", "Наплечники", "Schulterrüstung", "肩防具", "Naramienniki"),
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
    ("tree.maces", "Maces", "钉头锤", "釘頭錘", "Булавы", "Streitkolben", "メイス", "Buzdygany"),
    ("tree.wands", "Wands", "魔杖", "魔杖", "Жезлы", "Zauberstäbe", "ワンド", "Różdżki"),
    ("tree.pistols", "Pistols", "手枪", "手槍", "Пистолеты", "Pistolen", "ピストル", "Pistolety"),
    ("tree.claws", "Claws", "爪", "爪", "Когти", "Klauen", "爪", "Pazury"),
    ("tree.bows", "Bows", "弓", "弓", "Луки", "Bögen", "弓", "Łuki"),
    ("tree.crossbows", "Crossbows", "弩", "弩", "Арбалеты", "Armbrüste", "クロスボウ", "Kusze"),
    ("tree.greataxes", "Greataxes", "巨斧", "巨斧", "Секиры", "Großäxte", "大斧", "Wielkie topory"),
    ("tree.greathammers", "Greathammers", "巨锤", "巨錘", "Молоты", "Großhämmer", "大槌", "Wielkie młoty"),
    ("tree.greatswords", "Greatswords", "巨剑", "巨劍", "Двуручные мечи", "Großschwerter", "大剣", "Wielkie miecze"),
    ("tree.polearms", "Polearms", "长柄武器", "長柄武器", "Древковое оружие", "Stangenwaffen", "長柄武器", "Broń drzewcowa"),
    ("tree.staffs", "Staffs", "法杖", "法杖", "Посохи", "Stäbe", "スタッフ", "Kostury"),
    ("tree.cannons", "Cannons", "火炮", "火砲", "Пушки", "Kanonen", "大砲", "Armaty"),
    ("tree.shotgonnes", "Shotgonnes", "散弹枪", "散彈槍", "Дробовики", "Schrotflinten", "散弾銃", "Strzelby"),
    ("tree.accessories", "Accessories", "饰品", "飾品", "Аксессуары", "Accessoires", "アクセサリー", "Akcesoria"),
    ("tree.rings", "Rings", "戒指", "戒指", "Кольца", "Ringe", "指輪", "Pierścienie"),
    ("tree.necklaces", "Necklaces", "项链", "項鍊", "Ожерелья", "Halsketten", "ネックレス", "Naszyjniki"),
    ("tree.collars", "Collars", "项圈", "項圈", "Ошейники", "Halsbänder", "首輪", "Obroże"),
    ("tree.tags", "Tags", "铭牌", "銘牌", "Бирки", "Anhänger", "タグ", "Znaczniki"),
    ("tree.consumables", "Consumables", "消耗品", "消耗品", "Расходники", "Verbrauchsgüter", "消耗品", "Przedmioty jednorazowe"),
    ("tree.potions", "Potions", "药剂", "藥劑", "Зелья", "Tränke", "ポーション", "Mikstury"),
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

    # --- toolbar and panel buttons ---------------------------------------
    ("ui.search", "Search", "搜索", "搜尋", "Поиск", "Suchen", "検索", "Szukaj"),
    ("ui.clear_search", "Clear search", "清除搜索", "清除搜尋", "Очистить поиск", "Suche löschen", "検索をクリア", "Wyczyść wyszukiwanie"),
    ("ui.search_placeholder", "Search name or internal id (any language)…", "搜索名称或内部名（任意语言）…", "搜尋名稱或內部名（任意語言）…", "Поиск по названию или внутреннему ID (любой язык)…", "Name oder interne ID suchen (beliebige Sprache)…", "名前または内部名を検索（全言語）…", "Szukaj nazwy lub wewnętrznego ID (dowolny język)…"),
    ("ui.show_picture", "Show picture", "显示图片", "顯示圖片", "Показать изображение", "Bild anzeigen", "画像を表示", "Pokaż obraz"),
    ("ui.show_text", "Show text", "显示文本", "顯示文字", "Показать текст", "Text anzeigen", "テキストを表示", "Pokaż tekst"),
    ("ui.about", "About", "关于", "關於", "О программе", "Über", "情報", "O programie"),
    ("ui.ok", "OK", "确定", "確定", "ОК", "OK", "OK", "OK"),
    ("ui.language", "Language:", "语言：", "語言：", "Язык:", "Sprache:", "言語:", "Język:"),
    ("ui.names_source", "names from MEDIA/TRANSLATIONS", "名称来自 MEDIA/TRANSLATIONS", "名稱來自 MEDIA/TRANSLATIONS", "названия из MEDIA/TRANSLATIONS", "Namen aus MEDIA/TRANSLATIONS", "名前の出典: MEDIA/TRANSLATIONS", "nazwy z MEDIA/TRANSLATIONS"),
    ("ui.item_tree", "Item Tree", "物品树", "物品樹", "Дерево предметов", "Gegenstandsbaum", "アイテムツリー", "Drzewo przedmiotów"),
    ("ui.filter", "Filter", "筛选", "篩選", "Фильтр", "Filter", "フィルター", "Filtr"),
    ("ui.add", "+ Add", "+ 添加", "+ 新增", "+ Добавить", "+ Hinzufügen", "+ 追加", "+ Dodaj"),
    ("ui.only_sets", "Only Set Items", "仅套装物品", "僅套裝物品", "Только комплекты", "Nur Set-Gegenstände", "セット品のみ", "Tylko przedmioty z zestawów"),
    ("ui.search_node", "Search in the selected node", "在选中节点中搜索", "在選取節點中搜尋", "Искать в выбранном узле", "Im ausgewählten Knoten suchen", "選択ノード内を検索", "Szukaj w wybranym węźle"),
    ("ui.match_any", "Result of any option (OR)", "任一条件匹配（或）", "任一條件符合（或）", "Любое условие (ИЛИ)", "Beliebiges Kriterium (ODER)", "いずれかに一致（OR）", "Dowolny warunek (OR)"),
    ("ui.live_search", "Live search", "实时搜索", "即時搜尋", "Живой поиск", "Live-Suche", "ライブ検索", "Szukaj na żywo"),
    ("ui.clear_list", "Clear list", "清空列表", "清空列表", "Очистить список", "Liste leeren", "リストを消去", "Wyczyść listę"),
    ("ui.lock", "Lock", "锁定", "鎖定", "Заблокировать", "Sperren", "ロック", "Zablokuj"),
    ("ui.unlock", "Unlock", "解锁", "解鎖", "Разблокировать", "Entsperren", "ロック解除", "Odblokuj"),
    ("ui.copy_name", "Copy name", "复制名称", "複製名稱", "Копировать название", "Namen kopieren", "名前をコピー", "Kopiuj nazwę"),
    ("ui.fav", "☆ Fav", "☆ 收藏", "☆ 收藏", "☆ В избранное", "☆ Favorit", "☆ お気に入り", "☆ Ulubione"),
    ("ui.unfav", "★ Unfav", "★ 取消收藏", "★ 取消收藏", "★ Убрать", "★ Entfernen", "★ 解除", "★ Usuń"),
    ("ui.min", "min", "最小", "最小", "мин.", "Min.", "最小", "min."),
    ("ui.max", "max", "最大", "最大", "макс.", "Max.", "最大", "maks."),
    ("ui.icons", "icons", "个图标", "個圖示", "иконок", "Symbole", "アイコン", "ikon"),
    ("ui.fav_added", "Added to Favorites", "已加入收藏", "已加入收藏", "Добавлено в избранное", "Zu Favoriten hinzugefügt", "お気に入りに追加しました", "Dodano do ulubionych"),
    ("ui.fav_removed", "Removed from Favorites", "已移出收藏", "已移出收藏", "Удалено из избранного", "Aus Favoriten entfernt", "お気に入りから削除しました", "Usunięto z ulubionych"),
    ("ui.console_copied", "Console name copied", "已复制内部名", "已複製內部名", "Имя консоли скопировано", "Konsolenname kopiert", "コンソール名をコピーしました", "Skopiowano nazwę konsoli"),

    # --- unit types not in the tree --------------------------------------
    ("unit.dynamite", "Dynamite", "炸药", "炸藥", "Динамит", "Dynamit", "ダイナマイト", "Dynamit"),
    ("unit.location item", "Location Item", "场景物品", "場景物品", "Предмет локации", "Ortsgegenstand", "ロケーションアイテム", "Przedmiot lokacji"),

    # --- affix prefixes ---------------------------------------------------
    ("affix.weapon", "Weapon", "武器", "武器", "Оружие", "Waffe", "武器", "Broń"),
    ("affix.armor_trinket", "Armor/Trinket", "护甲/饰品", "護甲/飾品", "Броня/аксессуар", "Rüstung/Accessoire", "防具/アクセサリー", "Zbroja/Akcesorium"),
    ("affix.armor", "Armor", "护甲", "護甲", "Броня", "Rüstung", "防具", "Zbroja"),
    ("affix.trinket", "Trinket", "饰品", "飾品", "Аксессуар", "Accessoire", "アクセサリー", "Akcesorium"),

    # --- affix filter chips ------------------------------------------------
    # Keyed by `label` in data/effect_patterns.json (the LIKE pattern is what
    # the query uses; the label is only displayed). `en` is that label.
    ("effect.Augmented Weapon", "Augmented Weapon", "增强武器", "增強武器", "Усиленное оружие", "Verbesserte Waffe", "強化武器", "Wzmocniona broń"),
    ("effect.Strength", "Strength", "力量", "力量", "Сила", "Stärke", "筋力", "Siła"),
    ("effect.Dexterity", "Dexterity", "敏捷", "敏捷", "Ловкость", "Geschick", "器用さ", "Zręczność"),
    ("effect.Focus", "Focus", "专注", "專注", "Концентрация", "Fokus", "集中力", "Skupienie"),
    ("effect.Vitality", "Vitality", "体力", "體力", "Живучесть", "Vitalität", "生命力", "Witalność"),
    ("effect.Physical Armor", "Physical Armor", "物理防御", "物理防禦", "Физическая броня", "Physische Rüstung", "物理抵抗", "Pancerz fizyczny"),
    ("effect.Physical Armor for", "Physical Armor for", "限时物理防御", "限時物理防禦", "Временная физическая броня", "Zeitliche physische Rüstung", "物理防御（時間制）", "Pancerz fizyczny (czasowy)"),
    ("effect.to Bow, Crossbow, Pistol and Wand range", "to Bow, Crossbow, Pistol and Wand range", "弓/弩/手枪/魔杖射程", "弓/弩/手槍/魔杖射程", "Дальность лука, арбалета, пистоля и жезла", "Reichweite für Bogen, Armbrust, Pistole und Zauberstab", "ボウ・クロスボウ・ピストル・ワンドの射程", "Zasięg łuku, kuszy, pistoletu i różdżki"),
    ("effect.seconds of Burn/Shock/Freeze/Poison", "seconds of Burn/Shock/Freeze/Poison", "燃烧/电击/冰冻/中毒持续时间", "燃燒/電擊/冰凍/中毒持續時間", "Длительность горения/удара током/заморозки/отравления", "Dauer von Verbrennen/Elektroschock/Einfrieren/Vergiften", "燃焼/ショック/凍結/毒の持続時間", "Czas trwania podpalenia/porażenia/zamrożenia/zatrucia"),
    ("effect.increase in the amount of experience gained", "increase in the amount of experience gained", "获得的经验值", "獲得的經驗值", "Получаемый опыт", "Erhaltene Erfahrung", "獲得経験値", "Zyskiwane doświadczenie"),
    ("effect.increase in the amount of experience gained for", "increase in the amount of experience gained for", "限时经验值增益", "限時經驗值增益", "Временный бонус к опыту", "Zeitlicher Erfahrungsbonus", "経験値（時間制）", "Doświadczenie (czasowe)"),
    ("effect.increase in magic-finding Luck", "increase in magic-finding Luck", "魔法物品发现率", "魔法物品發現率", "Шанс найти магические предметы", "Glück beim Magiefinden", "マジックアイテム発見率", "Szczęście do magicznych przedmiotów"),
    ("effect.increase in the amount of gold found", "increase in the amount of gold found", "金币获取量", "金幣獲取量", "Найденное золото", "Gefundene Goldmenge", "Gold獲得量", "Znajdowane złoto"),
    ("effect.Dodge chance", "Dodge chance", "闪避几率", "閃避機率", "Шанс уклонения", "Ausweichchance", "回避率", "Szansa na unik"),
    ("effect.Knockback", "Knockback", "击退", "擊退", "Отбрасывание", "Zurückstoßen", "ノックバック", "Odepchnięcie"),
    ("effect.Health", "Health", "生命值", "生命值", "Здоровье", "Gesundheit", "HP", "Zdrowie"),
    ("effect.Mana", "Mana", "魔法值", "魔法值", "Мана", "Mana", "マナ", "Mana"),
    ("effect.Fire Armor", "Fire Armor", "火焰防御", "火焰防禦", "Защита от огня", "Feuerpanzer", "炎耐性", "Ochrona przed ogniem"),
    ("effect.Ice Armor", "Ice Armor", "冰霜防御", "冰霜防禦", "Защита ото льда", "Eispanzer", "氷耐性", "Ochrona przed lodem"),
    ("effect.Electric Armor", "Electric Armor", "闪电防御", "閃電防禦", "Защита от электричества", "Elektropanzer", "電気耐性", "Ochrona przed elektrycznością"),
    ("effect.Poison Armor", "Poison Armor", "毒素防御", "毒素防禦", "Защита от яда", "Giftpanzer", "毒耐性", "Ochrona przed trucizną"),
    ("effect.Health steal to master on Hit", "Health steal to master on Hit", "命中时为主人偷取生命", "命中時為主人偷取生命", "Похищение здоровья хозяину при ударе", "Gesundheitsraub für Meister bei Treffer", "命中時に主人のHPを吸収", "Kradzież zdrowia dla pana na trafienie"),
    ("effect.pet and minion Armor", "pet and minion Armor", "宠物和召唤兽防御", "寵物和召喚獸防禦", "Броня питомцев и помощников", "Rüstung von Begleitern und Dienern", "ペットと下僕の抵抗", "Pancerz zwierzaka i przywołanych istot"),
    ("effect.pet and minion Health", "pet and minion Health", "宠物和召唤兽生命值", "寵物和召喚獸生命值", "Здоровье питомцев и помощников", "Gesundheit von Begleitern und Dienern", "ペットと下僕のHP", "Zdrowie zwierzaka i przywołanych istot"),
    ("effect.pet and minion Speed", "pet and minion Speed", "宠物和召唤兽速度", "寵物和召喚獸速度", "Скорость питомцев и помощников", "Geschwindigkeit von Begleitern und Dienern", "ペットと下僕の速度", "Szybkość zwierzaka i przywołanych istot"),
    ("effect.pet and minion Damage", "pet and minion Damage", "宠物和召唤兽伤害", "寵物和召喚獸傷害", "Урон питомцев и помощников", "Schaden von Begleitern und Dienern", "ペットと下僕のダメージ", "Obrażenia zwierzaka i przywołanych istot"),
    ("effect.decreased pet town travel time", "decreased pet town travel time", "宠物回城时间缩短", "寵物回城時間縮短", "Время похода питомца в город сокращено", "Kürzere Begleiter-Reisedauer zur Stadt", "ペットのお使い時間短縮", "Krótszy czas podróży zwierzaka do miasta"),
    ("effect.bonus to Critical Damage", "bonus to Critical Damage", "暴击伤害加成", "爆擊傷害加成", "Бонус к критическому урону", "Bonus auf kritischen Schaden", "クリティカルダメージ増加", "Bonus do obrażeń krytycznych"),
    ("effect.Critical Hit Chance", "Critical Hit Chance", "暴击率", "爆擊率", "Шанс критического удара", "Chance auf kritischen Treffer", "クリティカル率", "Szansa na trafienie krytyczne"),
    ("effect.All Damage", "All Damage", "所有伤害", "所有傷害", "Весь урон", "Gesamtschaden", "全ダメージ", "Wszystkie obrażenia"),
    ("effect.Ice Damage", "Ice Damage", "冰霜伤害", "冰霜傷害", "Урон льдом", "Eisschaden", "冷気ダメージ", "Obrażenia od zimna"),
    ("effect.Ice Damage for", "Ice Damage for", "限时冰霜伤害", "限時冰霜傷害", "Временный урон льдом", "Zeitlicher Eisschaden", "冷気ダメージ（時間制）", "Obrażenia od zimna (czasowe)"),
    ("effect.Fire Damage", "Fire Damage", "火焰伤害", "火焰傷害", "Урон огнём", "Feuerschaden", "火ダメージ", "Obrażenia od ognia"),
    ("effect.Fire Damage for", "Fire Damage for", "限时火焰伤害", "限時火焰傷害", "Временный урон огнём", "Zeitlicher Feuerschaden", "火ダメージ（時間制）", "Obrażenia od ognia (czasowe)"),
    ("effect.Electric Damage", "Electric Damage", "闪电伤害", "閃電傷害", "Урон электричеством", "Blitzschaden", "電撃ダメージ", "Obrażenia od elektryczności"),
    ("effect.Electric Damage for", "Electric Damage for", "限时闪电伤害", "限時閃電傷害", "Временный урон электричеством", "Zeitlicher Blitzschaden", "電撃ダメージ（時間制）", "Obrażenia od elektryczności (czasowe)"),
    ("effect.Poison Damage", "Poison Damage", "毒素伤害", "毒素傷害", "Урон ядом", "Giftschaden", "毒ダメージ", "Obrażenia od trucizny"),
    ("effect.Poison Damage for", "Poison Damage for", "限时毒素伤害", "限時毒素傷害", "Временный урон ядом", "Zeitlicher Giftschaden", "毒ダメージ（時間制）", "Obrażenia od trucizny (czasowe)"),
    ("effect.Attack Speed", "Attack Speed", "攻击速度", "攻擊速度", "Скорость атаки", "Angriffsgeschwindigkeit", "攻撃スピード", "Szybkość ataku"),
    ("effect.Attack Speed for", "Attack Speed for", "限时攻击速度", "限時攻擊速度", "Временная скорость атаки", "Zeitliche Angriffsgeschwindigkeit", "攻撃スピード（時間制）", "Szybkość ataku (czasowa)"),
    ("effect.Cast Speed", "Cast Speed", "施法速度", "施法速度", "Скорость заклинаний", "Zaubertempo", "詠唱速度", "Szybkość rzucania czarów"),
    ("effect.faster movement speed", "faster movement speed", "移动速度", "移動速度", "Скорость движения", "Bewegungsgeschwindigkeit", "移動速度", "Szybkość ruchu"),
    ("effect.Melee Weapon Damage bonus", "Melee Weapon Damage bonus", "近战武器伤害加成", "近戰武器傷害加成", "Бонус к урону в ближнем бою", "Bonus auf Nahkampfwaffenschaden", "近接武器ダメージボーナス", "Bonus do obrażeń w zwarciu"),
    ("effect.Ranged Weapon Damage bonus", "Ranged Weapon Damage bonus", "远程武器伤害加成", "遠程武器傷害加成", "Бонус к урону в стрелковом бою", "Bonus auf Fernkampfwaffenschaden", "遠距離武器ダメージボーナス", "Bonus do obrażeń dystansowych"),
    ("effect.Wand and Staff Damage bonus", "Wand and Staff Damage bonus", "魔杖和法杖伤害加成", "魔杖和法杖傷害加成", "Бонус к урону жезлов и посохов", "Bonus auf Zauberstab- und Stabschaden", "ワンドとスタッフのダメージボーナス", "Bonus do obrażeń różdżki i kostura"),
    ("effect.Damage bonus when dual-wielding", "Damage bonus when dual-wielding", "双持伤害加成", "雙持傷害加成", "Бонус к урону при бое двумя оружиями", "Schadensbonus bei zwei Waffen", "二刀流ダメージボーナス", "Bonus do obrażeń przy dwóch broniach"),
    ("effect.chance to Execute", "chance to Execute", "猛击几率", "猛擊機率", "Шанс казни", "Chance auf Exekutieren", "発動確率", "Szansa na egzekucję"),
    ("effect.Damage to secondary targets", "Damage to secondary targets", "对次要目标的伤害", "對次要目標的傷害", "Урон дополнительным целям", "Schaden an Nebenzielen", "二次ターゲットへのダメージ", "Obrażenia dla celów w strefie rażenia"),
    ("effect.Charge rate increased by", "Charge rate increased by", "怒气积累速度", "怒氣積累速度", "Скорость набора заряда", "Aufladungsrate", "チャージ蓄積速度", "Szybkość gromadzenia ładunku"),
    ("effect.Charge decay rate decreased by", "Charge decay rate decreased by", "怒气消退速度", "怒氣消退速度", "Скорость рассеивания заряда", "Aufladungsverfallsrate", "チャージ減衰速度", "Spadek poziomu ładunku"),
    ("effect.Potion effectiveness", "Potion effectiveness", "药剂效果", "藥劑效果", "Эффективность зелий", "Effektivität von Tränken", "ポーション効果", "Skuteczność mikstur"),
    ("effect.chance to reflect missiles at   weapon DPS for", "chance to reflect missiles at   weapon DPS for", "反弹远程攻击几率", "反彈遠程攻擊機率", "Шанс отразить снаряд", "Chance, Geschosse zurückzuwerfen", "遠距離攻撃反射率", "Szansa na odbicie pocisków"),
    ("effect.Health/sec for every monster within meters", "Health/sec for every monster within meters", "范围内每个怪物提供的每秒生命回复", "範圍內每個怪物提供的每秒生命回復", "Здоровье/сек. за каждого монстра в радиусе", "Gesundheit/Sek. pro Monster im Umkreis", "範囲内のモンスター毎の毎秒HP回復", "Zdrowie/s za każdego potwora w promieniu"),
    ("effect.-  Physical Damage Taken for each monster within", "-  Physical Damage Taken for each monster within", "范围内每个怪物降低所受物理伤害", "範圍內每個怪物降低所受物理傷害", "Получаемый физический урон за каждого монстра в радиусе", "Erlittener Physisch-Schaden pro Monster im Umkreis", "範囲内のモンスター毎に物理ダメージ軽減", "Otrzymane obrażenia fizyczne za każdego potwora w promieniu"),
    ("effect.increased Fishing Luck", "increased Fishing Luck", "钓鱼运气", "釣魚運氣", "Рыбацкое везение", "Anglerglück", "釣り運", "Szczęście wędkarskie"),
    ("effect.Block Chance", "Block Chance", "格挡几率", "格擋機率", "Шанс блокировки", "Blockchance", "ブロック率", "Szansa na blok"),
    ("effect.chance to Block for", "chance to Block for", "限时格挡几率", "限時格擋機率", "Временный шанс блокировки", "Zeitliche Blockchance", "ブロック率（時間制）", "Szansa na blok (czasowa)"),
    ("effect.Slow Resistance", "Slow Resistance", "减速抵抗", "減速抵抗", "Сопротивление замедлению", "Resistenz gegen Verlangsamung", "減速耐性", "Odporność na spowolnienie"),
    ("effect.Immobilization Resistance", "Immobilization Resistance", "定身抵抗", "定身抵抗", "Сопротивление обездвиживанию", "Resistenz gegen Bewegungsunfähigkeit", "束縛抵抗", "Odporność na unieruchomienie"),
    ("effect.chance to Freeze", "chance to Freeze", "冰冻几率", "冰凍機率", "Шанс заморозить", "Chance auf Einfrieren", "凍結確率", "Szansa na zamrożenie"),
    ("effect.chance to Burn", "chance to Burn", "燃烧几率", "燃燒機率", "Шанс поджечь", "Chance auf Verbrennen", "燃焼確率", "Szansa na podpalenie"),
    ("effect.chance to Poison", "chance to Poison", "中毒几率", "中毒機率", "Шанс отравить", "Chance auf Vergiften", "毒状態にする確率", "Szansa na zatrucie"),
    ("effect.chance to Shock", "chance to Shock", "电击几率", "電擊機率", "Шанс ударить током", "Chance auf Elektroschock", "ショック状態にする確率", "Szansa na porażenie"),
    ("effect.chance that target Flees", "chance that target Flees", "目标逃跑几率", "目標逃跑機率", "Шанс обратить цель в бегство", "Chance, dass Ziel flieht", "ターゲット逃亡確率", "Szansa, że cel ucieknie"),
    ("effect.chance to Stun target", "chance to Stun target", "击晕目标几率", "擊暈目標機率", "Шанс оглушить цель", "Chance auf Betäubung des Ziels", "ターゲット気絶確率", "Szansa na ogłuszenie celu"),
    ("effect.chance to immobilize Target", "chance to immobilize Target", "定身目标几率", "定身目標機率", "Шанс обездвижить цель", "Chance auf Bewegungsunfähigkeit des Ziels", "ターゲット束縛確率", "Szansa na unieruchomienie celu"),
    ("effect.chance to break enemy shields", "chance to break enemy shields", "击破敌人盾牌几率", "擊破敵人盾牌機率", "Шанс разбить щит врага", "Chance, gegnerische Schilde zu durchbrechen", "敵の盾破壊確率", "Szansa na zniszczenie tarczy wroga"),
    ("effect.Interrupt chance", "Interrupt chance", "中断施法几率", "中斷施法機率", "Шанс прервать действия врага", "Chance auf Unterbrechung", "妨害率", "Szansa na przerwanie"),
    ("effect.chance to charm target for", "chance to charm target for", "魅惑目标几率", "魅惑目標機率", "Шанс переманить цель", "Chance, das Ziel zu betören", "ターゲット魅了確率", "Szansa na zauroczenie celu"),
    ("effect.chance to cast Eviscerate", "chance to cast Eviscerate", "施放开膛破肚几率", "施放開膛破肚機率", "Шанс «Потрошения»", "Chance auf Ausweiden", "イヴィサレート発動確率", "Szansa na Patroszenie"),
    ("effect.chance to cast AxeThrow", "chance to cast AxeThrow", "施放投斧几率", "施放投斧機率", "Шанс «Броска топора»", "Chance auf Axtwurf", "アックススロー発動確率", "Szansa na AxeThrow"),
    ("effect.chance to cast Call Forth the Skull when you get hit", "chance to cast Call Forth the Skull when you get hit", "被击中时施放召唤头骨几率", "被擊中時施放召喚頭骨機率", "Шанс «Вызывать череп» при ударе", "Chance auf Herbeirufung des Schädels bei Treffer", "攻撃を受けた時にスカルを呼ぶ発動確率", "Szansa na Przyzwanie czaszki po trafieniu"),
    ("effect.chance to cast Fully Heal Self when you get hit", "chance to cast Fully Heal Self when you get hit", "被击中时施放自身痊愈几率", "被擊中時施放自身痊癒機率", "Шанс «Полного исцеления» при ударе", "Chance auf Vollständige Selbstheilung bei Treffer", "攻撃を受けた時に完全な自己回復を発動する確率", "Szansa na Pełne samoleczenie po trafieniu"),
    ("effect.chance to cast Shed Poison Spore when you get hit", "chance to cast Shed Poison Spore when you get hit", "被击中时施放剧毒孢子几率", "被擊中時施放劇毒孢子機率", "Шанс «Ядовитой споры» при ударе", "Chance auf Giftsporen verteilen bei Treffer", "攻撃を受けた時に毒胞子放出を発動する確率", "Szansa na Ciskanie trującymi zarodnikami po trafieniu"),
    ("effect.chance to cast Chaotic Rift on strike", "chance to cast Chaotic Rift on strike", "攻击时施放混乱裂痕几率", "攻擊時施放混亂裂痕機率", "Шанс «Царства хаоса» при атаке", "Chance auf Chaosriss bei Treffer", "攻撃時にカオティックリフトを発動する確率", "Szansa na Chaotyczną rozpadlinę po trafieniu"),
    ("effect.chance to cast Raise Shadowling on kill", "chance to cast Raise Shadowling on kill", "击杀时施放召唤影魔几率", "擊殺時施放召喚影魔機率", "Шанс «Вызова теневика» при убийстве", "Chance auf Schattenling erwecken bei Tötung", "討伐時にレイズシャドウリングを発動する確率", "Szansa na Przyzwanie cienistych sług po zabiciu"),
    ("effect.chance to cast Meteor Strike on kill", "chance to cast Meteor Strike on kill", "击杀时施放流星之击几率", "擊殺時施放流星之擊機率", "Шанс «Удара метеорита» при убийстве", "Chance auf Meteorschlag bei Tötung", "討伐時にメテオストライクを発動する確率", "Szansa na Meteor po zabiciu"),
    ("effect.chance to cast Meteor Strike from target", "chance to cast Meteor Strike from target", "以目标为起点施放流星之击几率", "以目標為起點施放流星之擊機率", "Шанс «Удара метеорита» вокруг цели", "Chance auf Meteorschlag vom Ziel", "ターゲット地点にメテオストライクを発動する確率", "Szansa na Meteor od celu"),
    ("effect.chance to cast Thunder from target", "chance to cast Thunder from target", "以目标为起点施放雷霆几率", "以目標為起點施放雷霆機率", "Шанс «Грома» вокруг цели", "Chance auf Donner vom Ziel", "ターゲット地点にサンダーを発動する確率", "Szansa na Grom od celu"),
    ("effect.chance to cast Acid Rain from target", "chance to cast Acid Rain from target", "以目标为起点施放酸雨几率", "以目標為起點施放酸雨機率", "Шанс «Кислотного дождя» вокруг цели", "Chance auf Säureregen vom Ziel", "ターゲット地点にアシッドレインを発動する確率", "Szansa na Kwaśny deszcz od celu"),
    ("effect.chance to cast Glacial Spike from target", "chance to cast Glacial Spike from target", "以目标为起点施放冰川之刺几率", "以目標為起點施放冰川之刺機率", "Шанс «Ледяного шипа» вокруг цели", "Chance auf Gletscherstachel vom Ziel", "ターゲット地点にグレーシャルスパイクを発動する確率", "Szansa na Glacjalny kolec od celu"),
    ("effect.chance to cast Lightning from target", "chance to cast Lightning from target", "以目标为起点施放雷电几率", "以目標為起點施放雷電機率", "Шанс «Молнии» вокруг цели", "Chance auf Blitz vom Ziel", "ターゲット地点にライトニングを発動する確率", "Szansa na Błyskawicę od celu"),
    ("effect.chance to cast Scalding Geyser from target", "chance to cast Scalding Geyser from target", "以目标为起点施放灼热喷涌几率", "以目標為起點施放灼熱噴湧機率", "Шанс «Обжигающего гейзера» вокруг цели", "Chance auf Verbrühenden Geysir vom Ziel", "ターゲット地点に火傷のガイザーを発動する確率", "Szansa na Parzący gejzer od celu"),
    ("effect.chance to cast Fire Storm from target", "chance to cast Fire Storm from target", "以目标为起点施放火焰风暴几率", "以目標為起點施放火焰風暴機率", "Шанс «Огненной бури» вокруг цели", "Chance auf Feuersturm vom Ziel", "ターゲット地点にファイアストームを発動する確率", "Szansa na Ognistą burzę od celu"),
    ("effect.chance to cast Blinding Cloud from target", "chance to cast Blinding Cloud from target", "以目标为起点施放致盲之云几率", "以目標為起點施放致盲之雲機率", "Шанс «Ослепляющего облака» вокруг цели", "Chance auf Blendende Wolke vom Ziel", "ターゲット地点に目くらましの雲を発動する確率", "Szansa na Oślepiającą mgłę od celu"),
    ("effect.-  to all item character stat requirements", "-  to all item character stat requirements", "降低所有物品属性需求", "降低所有物品屬性需求", "Снижение требований всех предметов", "Geringere Gegenstandsanforderungen", "全アイテムのステータス条件低下", "Obniżone wymagania wszystkich przedmiotów"),
    ("effect.All Damage Taken is reduced by", "All Damage Taken is reduced by", "承受的所有伤害降低", "承受的所有傷害降低", "Получаемый урон снижается", "Erlittener Gesamtschaden wird verringert", "受ける全ダメージ減少", "Otrzymywane obrażenia zmniejszone"),
    ("effect.Ice Damage Taken is reduced by", "Ice Damage Taken is reduced by", "承受的冰霜伤害降低", "承受的冰霜傷害降低", "Получаемый урон льдом снижается", "Erlittener Eisschaden wird verringert", "受ける冷気ダメージ減少", "Otrzymywane obrażenia od zimna zmniejszone"),
    ("effect.Fire Damage Taken is reduced by", "Fire Damage Taken is reduced by", "承受的火焰伤害降低", "承受的火焰傷害降低", "Получаемый урон огнём снижается", "Erlittener Feuerschaden wird verringert", "受ける火ダメージ減少", "Otrzymywane obrażenia od ognia zmniejszone"),
    ("effect.Electric Damage Taken is reduced by", "Electric Damage Taken is reduced by", "承受的闪电伤害降低", "承受的閃電傷害降低", "Получаемый урон электричеством снижается", "Erlittener Blitzschaden wird verringert", "受ける電撃ダメージ減少", "Otrzymywane obrażenia od elektryczności zmniejszone"),
    ("effect.Poison Damage Taken is reduced by", "Poison Damage Taken is reduced by", "承受的毒素伤害降低", "承受的毒素傷害降低", "Получаемый урон ядом снижается", "Erlittener Giftschaden wird verringert", "受ける毒ダメージ減少", "Otrzymywane obrażenia od trucizny zmniejszone"),
    ("effect.-  to All Armor per hit", "-  to All Armor per hit", "每次命中降低所有防御", "每次命中降低所有防禦", "Снижение всей брони за удар", "Rüstungsabzug pro Treffer", "命中毎に全防御低下", "Obniżenie całego pancerza za trafienie"),
    ("effect.reduction in Fumble Chance", "reduction in Fumble Chance", "笨拙几率降低", "笨拙機率降低", "Снижение шанса неточного удара", "Geringere Patzerchance", "失敗率低下", "Zmniejszona szansa na krytyczny pech"),
    ("effect.Physical Damage Reflected", "Physical Damage Reflected", "反弹物理伤害", "反彈物理傷害", "Отражение физического урона", "Zurückgeworfener Physisch-Schaden", "物理ダメージ反射", "Odbicie obrażeń fizycznych"),
    ("effect.Health recovery over", "Health recovery over", "生命回复", "生命回復", "Восстановление здоровья", "Gesundheitswiederherstellung", "HP回復", "Regeneracja zdrowia"),
    ("effect.Mana recovery per second", "Mana recovery per second", "每秒魔法回复", "每秒魔法回復", "Восстановление маны в секунду", "Manawiederherstellung pro Sekunde", "毎秒マナ回復", "Regeneracja many na sekundę"),
    ("effect.Health stolen on hit", "Health stolen on hit", "命中时偷取生命", "命中時偷取生命", "Похищение здоровья при ударе", "Gesundheit bei Treffer gestohlen", "命中時HP吸収", "Kradzież zdrowia przy trafieniu"),
    ("effect.Mana stolen on hit", "Mana stolen on hit", "命中时偷取魔法", "命中時偷取魔法", "Похищение маны при ударе", "Mana bei Treffer gestohlen", "命中時マナ吸収", "Kradzież many przy trafieniu"),
    ("effect.Knock Back Resistance", "Knock Back Resistance", "击退抵抗", "擊退抵抗", "Сопротивление отбрасыванию", "Zurückstoßen-Resistenz", "ノックバック抵抗", "Odporność na odepchnięcie"),
    ("effect.Explosion On Death", "Explosion On Death", "死亡时爆炸", "死亡時爆炸", "Взрыв при смерти", "Explosion beim Tod", "死亡時に爆発", "Eksplozja po śmierci"),
    ("effect.Silence for", "Silence for", "沉默", "沉默", "Немота", "Verstummen", "沈黙", "Cisza"),
    ("effect.Physical Damage for", "Physical Damage for", "限时物理伤害", "限時物理傷害", "Временный физический урон", "Zeitlicher Physisch-Schaden", "物理ダメージ（時間制）", "Obrażenia fizyczne (czasowe)"),
    ("effect.improvement in vendor prices", "improvement in vendor prices", "商店价格优惠", "商店價格優惠", "Выгодные цены у торговцев", "Bessere Händlerpreise", "販売価格割引", "Lepsze ceny u kupców"),
    ("effect.Physical Damage", "Physical Damage", "物理伤害", "物理傷害", "Физический урон", "Physisch-Schaden", "物理ダメージ", "Obrażenia fizyczne"),
]

LANGS = ["en", "zh-Hans", "zh-Hant", "ru", "de", "ja", "pl"]


def main() -> None:
    data: dict[str, dict[str, str]] = {}
    for row in TERMS:
        key, *values = row
        data[key] = dict(zip(LANGS, values))
    # The effect chips are keyed by the pattern table's `label`; fail loudly
    # instead of silently rendering English when the two drift apart.
    patterns = json.loads((ROOT / "data" / "effect_patterns.json").read_text(encoding="utf-8"))
    labels = {p["label"] for p in patterns}
    keys = {key[len("effect."):] for key in data if key.startswith("effect.")}
    if labels != keys:
        raise SystemExit(
            f"effect label mismatch: missing={sorted(labels - keys)} extra={sorted(keys - labels)}"
        )
    OUT.write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print(f"  i18n.json {OUT.stat().st_size / 1024:8.1f} KiB, {len(data)} keys")


if __name__ == "__main__":
    main()
