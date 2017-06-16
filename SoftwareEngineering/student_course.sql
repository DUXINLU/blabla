drop table if exists student_course;
create table student_course(
sid integer,
cid integer,
score integer,
primary key (sid,cid)
);