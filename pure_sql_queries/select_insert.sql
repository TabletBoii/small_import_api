SELECT * FROM web_user

SELECT * FROM web_resource_type

SELECT * FROM web_access

INSERT INTO web_resource_type(
	name
) VALUES ('report')

INSERT INTO web_resource(
	name,
	type
) VALUES ('report_avg_time', 1)

INSERT INTO web_user(
	name,
	hashed_password,
	description
) VALUES ('matvienko', 'tsdfk2349fM()FM@#f0sd', 'Никита Матвиенко Директор по качеству')

INSERT INTO web_access(
	user_inc,
	web_resource_inc,
	has_access
) VALUES (
	1, 1, true
)

DROP TABLE web_access