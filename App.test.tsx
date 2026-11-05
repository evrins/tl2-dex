import { Db } from "tidbi/native";
import { expect, open, test } from "nsh/test";

test("renders the item database from base.mdb", async () => {
  const app = await open("./App.tsx");
  const texts = app.texts();
  expect(texts).toContain("Torchlight II · Item Database");
  expect(texts).toContain("Select an item");
  expect(texts).toContain("6050 / 6050 items");
  expect(texts).toContain("6050 items · 81 Sets · 1054 icons");
  expect(texts).toContain("All Items");
  expect(texts).toContain("Favorites");
  expect(texts).toContain("简体中文");
  expect(texts).toContain("繁體中文");
});

test("tree nodes and the filter tab drive the query", async () => {
  const app = await open("./App.tsx");
  await app.press("Bows");
  expect(app.texts()).toContain("Bows");
  await app.press("Filter");
  const texts = app.texts();
  expect(texts).toContain("Type / Rarity");
  expect(texts).toContain("Only Set Items");
  expect(texts).toContain("Live search");
  expect(texts).toContain("Dodge chance");
});

test("rarity chips apply as soon as they are picked", async () => {
  const app = await open("./App.tsx");
  await app.press("Filter");
  await app.press("Rare");
  await app.wait(200);
  const texts = app.texts();
  expect(texts).toContain("1 filters");
  expect(texts).not.toContain("Clear list");
  expect(texts.join("\n")).toMatch(/\b[1-9]\d* \/ 6050 items/);
  await app.press("Rare");
  await app.wait(200);
  expect(app.texts()).toContain("0 filters");
  expect(app.texts()).toContain("6050 / 6050 items");
});

test("categories, rarity and stats follow the language", async () => {
  const app = await open("./App.tsx");
  await app.press("简体中文");
  await app.wait(200);
  let texts = app.texts();
  expect(texts).toContain("全部物品");
  expect(texts).toContain("武器");
  expect(texts).toContain("贵族");
  await app.press("筛选");
  texts = app.texts();
  expect(texts).toContain("类型 / 稀有度");
  expect(texts).toContain("稀有");
  expect(texts).toContain("等级");
  expect(texts).toContain("物理伤害");
  expect(texts).toContain("敏捷");
  // Affix chips follow the language too, not the English pattern label.
  expect(texts).toContain("闪避几率");
  expect(texts).not.toContain("Dodge chance");
});

test("toolbar and panel controls follow the language", async () => {
  const app = await open("./App.tsx", { width: 1200, height: 900 });
  await app.press("简体中文");
  await app.wait(200);
  let texts = app.texts();
  expect(texts).toContain("搜索");
  expect(texts).toContain("显示文本");
  expect(texts).toContain("关于");
  expect(texts).toContain("物品树");
  expect(texts).toContain("筛选");
  expect(texts).toContain("语言：");
  await app.press("筛选");
  texts = app.texts();
  expect(texts).toContain("仅套装物品");
  expect(texts).toContain("在选中节点中搜索");
  expect(texts).toContain("任一条件匹配（或）");
  expect(texts).toContain("实时搜索");
  expect(texts).toContain("按类型");
  await app.press("物品树");
  await app.press("关于");
  expect(app.texts()).toContain("确定");
});

test("tree categories collapse and expand from their arrows", async () => {
  const app = await open("./App.tsx");
  expect(app.shows("Bows")).toBe(true);
  await app.press("id:tree-fold-weapons");
  expect(app.shows("Bows")).toBe(false);
  // Folding does not select: the whole database is still the queried node.
  expect(app.texts()).toContain("6050 / 6050 items");
  await app.press("id:tree-fold-weapons");
  expect(app.shows("Bows")).toBe(true);
});

test("native module serves localized item detail, icons and queries", () => {
  const d = JSON.parse(Db.detail("crossbow_m01", "zh-Hans"));
  expect(d.n).toBe("农夫弩");
  expect(d.en).toBe("Peasant Crossbow");
  expect(d.names["zh-Hant"]).toBe("農夫弩");
  expect(d.names["ru"]).toBe("Арбалет крестьянина");
  expect(d.dps).toBe(34);
  expect(Db.icon("icon_weapon_crossbow02")).toBe(
    "asset:/@nsh-app-tl2-dex/icons/icon_weapon_crossbow02.png",
  );
  // The database stores lowercase names; the asset files are mixed case.
  expect(Db.icon("icons_gem_06b")).toBe(
    "asset:/@nsh-app-tl2-dex/icons/icons_gem_06B.png",
  );
  // 18 names in the 2014 data have no file; they get the tool's placeholder.
  expect(Db.icon("amulet3")).toBe("asset:/@nsh-app-tl2-dex/icons/IG_skill_empty_result.png");
  const q = JSON.parse(Db.query(JSON.stringify({ node: "all", q: "农夫", filters: [], lang: "zh-Hans" })));
  expect(q.total).toBeGreaterThan(0);
  const en = JSON.parse(Db.query(JSON.stringify({ node: "all", q: "Peasant", filters: [], lang: "en" })));
  expect(en.rows.some((r: Array<string | number | boolean>) => r[1] === "Peasant Crossbow")).toBe(true);
  const byId = JSON.parse(Db.query(JSON.stringify({ node: "all", q: "CROSSBOW_M01", filters: [], lang: "en" })));
  expect(byId.rows.some((r: Array<string | number | boolean>) => r[0] === "crossbow_m01")).toBe(true);

  const options = JSON.parse(Db.options());
  expect(options.setNames["Aristocrat"]["zh-Hans"]).toBe("贵族");
  expect(options.setNames["The Asphyx"]["ru"]).toBe("Асфиксия");

  const unique = JSON.parse(Db.detail("crossbow_u01", "zh-Hans"));
  expect(unique.description).toBe("给它上好发条让它飞吧。");
  expect(unique.effects.some((e: string) => e.includes("物理伤害"))).toBe(true);
});
