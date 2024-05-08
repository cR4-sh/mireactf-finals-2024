#ifndef __ACMS_COMMAND__
#define __ACMS_COMMAND__

#include <libpq-fe.h>

#include <acms_message.h>

typedef void (*command_handler)(acms_logger*, PGconn*, char**);

void create_user(acms_logger* logger, PGconn* conn, char** user_uuid);
void show_profile(acms_logger* logger, PGconn* conn, char** user_uuid);
void login(acms_logger* logger, PGconn* conn, char** user_uuid);
void logout(acms_logger* logger, PGconn* conn, char** user_uuid);
void create_group(acms_logger* logger, PGconn* conn, char** user_uuid);
void add_group_user(acms_logger* logger, PGconn* conn, char** user_uuid);
void show_group(acms_logger* logger, PGconn* conn, char** user_uuid);
void add_device(acms_logger* logger, PGconn* conn, char** user_uuid);
void get_device(acms_logger* logger, PGconn* conn, char** user_uuid);
void device_control(acms_logger* logger, PGconn* conn, char** user_uuid);
void add_log(acms_logger* logger, PGconn* conn, char** user_uuid);
void delete_log(acms_logger* logger, PGconn* conn, char** user_uuid);
void show_journal(acms_logger* logger, PGconn* conn, char** user_uuid);
void clear_logs(acms_logger* logger, PGconn* conn, char** user_uuid);

#endif