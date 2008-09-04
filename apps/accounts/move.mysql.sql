-- PGSQL
-- Changing user table
ALTER TABLE auth_user ADD COLUMN site varchar(200);
ALTER TABLE auth_user ADD COLUMN email_new varchar(200);
UPDATE auth_user SET site = '' WHERE site IS NULL;
UPDATE auth_user SET email_new = '' WHERE email_new IS NULL;
ALTER TABLE auth_user MODIFY site VARCHAR(200) NOT NULL;
ALTER TABLE auth_user MODIFY email_new VARCHAR(200) NOT NULL;

-- Adding data from old user profile
UPDATE user_profile p, auth_user u SET u.site = p.site, u.email_new = u.email_new WHERE u.id = p.user_id;
UPDATE auth_user SET first_name = COALESCE(NULLIF(TRIM(CONCAT(COALESCE(first_name, '') , ' ' , COALESCE(last_name, ''))), ''), username);

