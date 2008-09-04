-- PGSQL
ALTER TABLE "blog_post" ADD COLUMN "upd_date" timestamptz;
UPDATE "blog_post" SET "upd_date" = "date";
ALTER TABLE "blog_post" ALTER COLUMN "upd_date" SET NOT NULL;

ALTER TABLE "comment_nodes" ADD COLUMN "upd_date" timestamptz;
UPDATE "comment_nodes" SET "upd_date" = "pub_date";
ALTER TABLE "comment_nodes" ALTER COLUMN "upd_date" SET NOT NULL;