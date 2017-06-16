drop table if exists teacher_course;
create table teacher_course(
tid integer,
cid integer,
primary key (tid,cid)
);