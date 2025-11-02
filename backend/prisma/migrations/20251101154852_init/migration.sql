-- CreateTable
CREATE TABLE "product_categories" (
    "id" SERIAL NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "manufacturer" VARCHAR(100) NOT NULL,
    "series" VARCHAR(100) NOT NULL,
    "ceiling_height_min" DOUBLE PRECISION NOT NULL,
    "ceiling_height_max" DOUBLE PRECISION NOT NULL,
    "suitable_for" JSONB NOT NULL,
    "description" TEXT,

    CONSTRAINT "product_categories_pkey" PRIMARY KEY ("id")
);
