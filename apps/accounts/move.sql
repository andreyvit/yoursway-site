-- PGSQL
-- Changing user table
ALTER TABLE auth_user ADD COLUMN site varchar(200);
ALTER TABLE auth_user ADD COLUMN email_new varchar(75);
UPDATE auth_user SET site = '';
UPDATE auth_user SET email_new = '';
ALTER TABLE auth_user ALTER COLUMN site SET NOT NULL;
ALTER TABLE auth_user ALTER COLUMN email_new SET NOT NULL;

-- Adding data from old user profile
UPDATE auth_user SET site = user_profile.site, email_new = user_profile.email_new FROM user_profile WHERE auth_user.id = user_profile.user_id;
UPDATE auth_user SET first_name = COALESCE(NULLIF(BTRIM(COALESCE(first_name, '') || ' ' || COALESCE(last_name, '')), ''), username);

