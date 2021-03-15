use Sanctions;

drop table if exists Sanctions;
drop table if exists alternative_names;
drop table if exists Companies;
drop table if exists Records;
drop table if exists Users;
drop table if exists SSW_lists;
drop table if exists Sources;
drop table if exists unstructured_names;
drop table if exists Connections;

create table Sources(
	id int primary key identity(1,1),
	name nvarchar (100) not null
);

insert into Sources (name) values ('X-com'), ('AB'), ('User');

create table SSW_lists(
	id int primary key identity(1,1),
	name nvarchar(100) not null unique
);

create table Users(
	id int primary key identity(1,1),
	name nvarchar(100)
);

create table Records(
	id int primary key identity(1,1),
	is_active bit not null default 0,
	created_at datetime not null default GetDate(),
	updated_at datetime not null default GetDate(),
	source int not null default 0,
	source_code nvarchar(max),
	ssw int,
	#user int not null,
	foreign key (#user) references Users(id),
	foreign key (source) references Sources(id),
	foreign key (ssw) references SSW_lists(id)
);


create table Companies(
	id int primary key identity(1,1),
	record int not null,
	company_type bit not null default 0,
	last_name nvarchar(max),
	first_name nvarchar(max),
	patronymic nvarchar(max),
	other nvarchar(max),
	org_form nvarchar(200),
	name_russian nvarchar(max),
	name_full nvarchar(max),
	name_translit nvarchar(max),
	name_main_engl nvarchar(max),
	name_main_rus nvarchar(max),
	birth_date datetime,
	inn nvarchar (20),
	ogrn nvarchar (50),
	pin nvarchar(7),
	address nvarchar(max),
	resident nvarchar(150),
	additional_info nvarchar(max),
	foreign key (record) references Records(id)
);


create table Connections(
		id int primary key identity(1,1),
	main_company int,
	child_company int,
	foreign key (main_company) references Companies(id)

);
create table Sanctions(
	id int primary key identity(1,1),
	code int,
	country nvarchar(200),
	program nvarchar(max),
	type bit default 0,
	child_company int,
	parent_company nvarchar(max),
	foreign key (child_company) references Companies(id),
);

create table alternative_names (
	id int primary key identity(1,1),
	name nvarchar(max) not null,
	company int not null,
	is_active bit not null default 1,
	foreign key (company) references Companies(id)
);
create table unstructured_names (
	id int primary key identity(1,1),
	name_list nvarchar(max) not null,
	company int not null,
	foreign key (company) references Companies(id)
);
go -- Создание триггеров невозможно в общем скрипте, отделяем их в отдельный билд
	create trigger on_record_update on Records
	after update
	as
		update Records set updated_at = GetDate()
		where id in (select id from inserted); -- обновляемые значения хранятся во временной таблице INSERTED. Реализация через in сделана что бы при обновлении нескольких значений сразу updated_at обновился у всех