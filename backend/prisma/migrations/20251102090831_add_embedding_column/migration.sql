-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- AlterTable
ALTER TABLE "product_categories" ADD COLUMN IF NOT EXISTS "embedding" vector(1536);
