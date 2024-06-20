create table roles (
id serial primary key,
name varchar(50)
);

insert into roles(name)
values ('blogger'),('admin'),('superadmin');


create table users (
id serial primary key,
first_name varchar(50),
second_name varchar(150),
email varchar(50) UNIQUE,
nickname varchar(50) UNIQUE,
pasword_hash varchar(150),
role_id int references roles(id),
is_banned boolean,
created_at date
);


create table topics (
id serial primary key,
title varchar(50)
);


create table posts (
id serial primary key,
title varchar(50),
topic_id int references topics(id),
content varchar(50),
file_path varchar(150), 
created_at date,
user_id int references users(id)
);


create table subscription (
id serial primary key,
subscriber_id int references users(id),
subscribed_id int references users(id)
);