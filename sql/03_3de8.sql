-- PGSQL
start transaction;
-- Remove foreign key constraints against openidserver_trustedroot table
alter table openidserver_djangoiduser_trusted_roots drop constraint "openidserver_djangoiduser_trusted_roots_trustedroot_id_fkey";
-- Remove existing primary key constraint
alter table openidserver_trustedroot drop constraint "openidserver_trustedroot_pkey";
alter table openidserver_trustedroot add column "id" integer;
-- Create new primary key values for existing entries
create sequence new_openid_tr_seq START 1;
update "openidserver_trustedroot" set "id" = nextval('new_openid_tr_seq');
drop sequence new_openid_tr_seq;
-- Add primary key constraint
alter table "openidserver_trustedroot" add constraint "openidserver_trustedroot_pkey" PRIMARY KEY ("id");
alter table "openidserver_djangoiduser_trusted_roots" rename "trustedroot_id" to "old_trustedroot_id";
alter table "openidserver_djangoiduser_trusted_roots" add "trustedroot_id" integer;
-- Relate old keys (URLs) to new keys (integers)
update "openidserver_djangoiduser_trusted_roots" set "trustedroot_id" = (select "id" from "openidserver_trustedroot" where "old_trustedroot_id" = "root");
alter table "openidserver_djangoiduser_trusted_roots" drop "old_trustedroot_id";
-- Add foreign key constraint to openidserver_trustedroot table
alter table "openidserver_djangoiduser_trusted_roots" add constraint "openidserver_djangoiduser_trusted_roots_trustedroot_id_fkey" FOREIGN KEY ("trustedroot_id") REFERENCES "openidserver_trustedroot" ("id") DEFERRABLE INITIALLY DEFERRED;
commit;
