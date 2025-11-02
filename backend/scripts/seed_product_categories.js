/**
 * product_categories.json をSupabase(PostgreSQL)に投入するシードスクリプト
 *
 * 使い方:
 *   node scripts/seed_product_categories.js
 */
const { PrismaClient } = require('@prisma/client');
const fs = require('fs');
const path = require('path');

const prisma = new PrismaClient();

async function main() {
  const dataPath = path.join(__dirname, '..', 'app', 'data', 'product_categories.json');
  const raw = fs.readFileSync(dataPath, 'utf-8');
  const categories = JSON.parse(raw);

  // 既存データをクリアしてから投入
  await prisma.productCategory.deleteMany();
  console.log('🧹 product_categories テーブルを初期化しました');

  for (const category of categories) {
    await prisma.productCategory.create({
      data: {
        name: category.name,
        manufacturer: category.manufacturer,
        series: category.series,
        ceilingHeightMin: category.ceiling_height_min,
        ceilingHeightMax: category.ceiling_height_max,
        suitableFor: category.suitable_for,
        description: category.description || null,
      },
    });
    console.log(`✅ ${category.name} を投入しました`);
  }
}

main()
  .catch((error) => {
    console.error('❌ シード処理でエラーが発生しました', error);
    process.exitCode = 1;
  })
  .finally(async () => {
    await prisma.$disconnect();
  });


